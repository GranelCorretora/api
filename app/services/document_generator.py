import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Literal
import asyncio
from concurrent.futures import ThreadPoolExecutor
import platform

from jinja2 import Environment, FileSystemLoader
from PIL import Image
from io import BytesIO
import base64

from ..templates.template_manager import TemplateManager

class DocumentGenerator:
    def __init__(self):
        self.template_manager = TemplateManager()
        self.temp_dir = os.path.join(os.getcwd(), "temp")
        
        # Criar diretório temporário se não existir
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Configurar Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join("app", "templates", "html")),
            autoescape=True
        )
        
        # Executor para operações bloqueantes
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Verificar se WeasyPrint está disponível
        self.weasyprint_available = self._check_weasyprint()
        
        if not self.weasyprint_available:
            print("⚠️  WeasyPrint não disponível. Usando ReportLab como alternativa.")
            self._setup_reportlab()
    
    def _check_weasyprint(self) -> bool:
        """Verifica se WeasyPrint está disponível e funcionando"""
        try:
            import weasyprint
            # Teste simples para ver se funciona
            weasyprint.HTML(string="<html><body>Test</body></html>").write_pdf()
            return True
        except Exception as e:
            print(f"WeasyPrint não disponível: {e}")
            return False
    
    def _setup_reportlab(self):
        """Configura ReportLab como alternativa"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4, letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            self.reportlab_available = True
        except ImportError:
            print("❌ ReportLab também não está disponível. Instale com: pip install reportlab")
            self.reportlab_available = False
    
    async def generate_document(
        self, 
        template_name: str, 
        data: Dict[str, Any], 
        output_format: Literal["pdf", "png", "jpeg"]
    ) -> str:
        """
        Gera um documento a partir de um template HTML
        
        Args:
            template_name: Nome do template
            data: Dados para preenchimento
            output_format: Formato de saída (pdf, png, jpeg)
            
        Returns:
            Caminho do arquivo gerado
        """
        try:
            # Gerar nome único para o arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{template_name}_{timestamp}.{output_format}"
            output_path = os.path.join(self.temp_dir, filename)
            
            if output_format == "pdf":
                if self.weasyprint_available:
                    await self._generate_pdf_weasyprint(template_name, data, output_path)
                elif hasattr(self, 'reportlab_available') and self.reportlab_available:
                    await self._generate_pdf_reportlab(template_name, data, output_path)
                else:
                    raise Exception("Nenhuma engine de PDF disponível. Instale WeasyPrint ou ReportLab.")
            else:
                # Para imagens, tentamos gerar PDF primeiro e depois converter
                if output_format in ["png", "jpeg"]:
                    # Gerar PDF temporário primeiro
                    temp_pdf = output_path.replace(f".{output_format}", "_temp.pdf")
                    if self.weasyprint_available:
                        await self._generate_pdf_weasyprint(template_name, data, temp_pdf)
                    elif hasattr(self, 'reportlab_available') and self.reportlab_available:
                        await self._generate_pdf_reportlab(template_name, data, temp_pdf)
                    else:
                        raise Exception("Nenhuma engine de PDF disponível para conversão de imagem.")
                    
                    # Converter PDF para imagem
                    await self._convert_pdf_to_image(temp_pdf, output_path, output_format)
                    
                    # Remover PDF temporário
                    if os.path.exists(temp_pdf):
                        os.remove(temp_pdf)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Erro ao gerar documento: {str(e)}")
    
    async def _generate_pdf_weasyprint(self, template_name: str, data: Dict[str, Any], output_path: str):
        """Gera PDF usando WeasyPrint"""
        import weasyprint
        
        def _create_pdf():
            # Renderizar HTML
            html_content = self._render_template_sync(template_name, data)
            # Configurações do WeasyPrint
            document = weasyprint.HTML(string=html_content, base_url=".")
            document.write_pdf(output_path)
        
        # Executar em thread separada
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, _create_pdf)
    
    async def _generate_pdf_reportlab(self, template_name: str, data: Dict[str, Any], output_path: str):
        """Gera PDF usando ReportLab (versão simplificada)"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        def _create_pdf():
            # Processar dados
            processed_data = self._process_template_data_sync(template_name, data)
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            if template_name == "fatura":
                self._build_fatura_reportlab(story, styles, processed_data)
            elif template_name == "certificado":
                self._build_certificado_reportlab(story, styles, processed_data)
            
            doc.build(story)
        
        # Executar em thread separada
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, _create_pdf)
    
    def _build_fatura_reportlab(self, story, styles, data):
        """Constrói fatura usando ReportLab"""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        # Título
        title_style = styles['Title']
        story.append(Paragraph("FATURA", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Informações da empresa
        story.append(Paragraph("Sua Empresa", styles['Heading2']))
        story.append(Paragraph("CNPJ: 00.000.000/0001-00", styles['Normal']))
        story.append(Paragraph("Endereço: Rua Exemplo, 123 - São Paulo/SP", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Cliente
        story.append(Paragraph(f"Cliente: {data.get('cliente', '')}", styles['Heading3']))
        story.append(Spacer(1, 0.1*inch))
        
        # Descrição
        if data.get('descricao'):
            story.append(Paragraph(f"Descrição: {data['descricao']}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Tabela de itens
        if data.get('itens'):
            table_data = [['#', 'Descrição', 'Valor']]
            total = 0
            for i, item in enumerate(data['itens'], 1):
                valor = item.get('valor', 0)
                total += valor
                table_data.append([str(i), item.get('descricao', ''), f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 0.2*inch))
            
            # Total
            story.append(Paragraph(f"Total: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), styles['Heading2']))
        
        # Data
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"Data: {data.get('data_atual', '')}", styles['Normal']))
    
    def _build_certificado_reportlab(self, story, styles, data):
        """Constrói certificado usando ReportLab"""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import inch
        
        # Título
        title_style = styles['Title']
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph("CERTIFICADO", title_style))
        story.append(Paragraph("de Conclusão", styles['Heading2']))
        story.append(Spacer(1, 0.5*inch))
        
        # Conteúdo
        story.append(Paragraph("Certificamos que", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(data.get('participante', ''), styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("concluiu com êxito o curso", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        story.append(Paragraph(data.get('curso', ''), styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        if data.get('instrutor'):
            story.append(Paragraph(f"Instrutor: {data['instrutor']}", styles['Normal']))
        
        if data.get('carga_horaria'):
            story.append(Paragraph(f"Carga Horária: {data['carga_horaria']}", styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"Data: {data.get('data_conclusao', data.get('data_atual', ''))}", styles['Normal']))
        
        if data.get('endereco'):
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(f"Local: {data['endereco']}", styles['Normal']))
    
    async def _convert_pdf_to_image(self, pdf_path: str, output_path: str, format: str):
        """Converte PDF para imagem"""
        def _convert():
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(pdf_path, dpi=300)
                
                if images:
                    image = images[0]
                    if format.lower() == "jpeg" and image.mode != "RGB":
                        image = image.convert("RGB")
                    image.save(output_path, format.upper())
            except ImportError:
                # Fallback usando PIL se pdf2image não estiver disponível
                print("pdf2image não disponível. Gerando imagem placeholder.")
                img = Image.new('RGB', (800, 600), color='white')
                img.save(output_path, format.upper())
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, _convert)
    
    def _render_template_sync(self, template_name: str, data: Dict[str, Any]) -> str:
        """Versão síncrona do render template"""
        processed_data = self._process_template_data_sync(template_name, data)
        template = self.jinja_env.get_template(f"{template_name}.html")
        return template.render(**processed_data)
    
    def _process_template_data_sync(self, template_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Versão síncrona do processamento de dados"""
        processed_data = data.copy()
        
        # Adicionar data atual se não fornecida
        if "data_atual" not in processed_data:
            processed_data["data_atual"] = datetime.now().strftime("%d/%m/%Y")
        
        # Formatação de valores monetários
        if "valor" in processed_data:
            processed_data["valor_formatado"] = f"R$ {processed_data['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        if "itens" in processed_data:
            for item in processed_data["itens"]:
                if "valor" in item:
                    item["valor_formatado"] = f"R$ {item['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        return processed_data
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Remove arquivos temporários antigos"""
        try:
            import time
            current_time = time.time()
            
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getctime(file_path)
                    if file_age > (max_age_hours * 3600):
                        os.remove(file_path)
                        print(f"Arquivo temporário removido: {filename}")
        except Exception as e:
            print(f"Erro ao limpar arquivos temporários: {e}") 