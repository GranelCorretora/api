import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Literal
import asyncio
from concurrent.futures import ThreadPoolExecutor
import platform
import uuid
import subprocess
import sys
import requests
from io import BytesIO

from jinja2 import Environment, FileSystemLoader
from PIL import Image, ImageDraw, ImageFont
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
                # Para imagens, usar geração direta sem depender de Poppler
                if output_format in ["png", "jpeg"]:
                    await self._generate_image_direct(template_name, data, output_path, output_format)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Erro ao gerar documento: {str(e)}")
    
    async def _generate_image_direct(self, template_name: str, data: Dict[str, Any], output_path: str, format: str):
        """Gera imagem diretamente usando PIL (sem precisar de PDF intermediário)"""
        def _create_image():
            # Processar dados
            processed_data = self._process_template_data_sync(template_name, data)
            
            # Configurações da imagem
            width, height = 800, 1200  # A4-like proportions
            background_color = "white"
            text_color = "black"
            
            # Criar imagem
            img = Image.new('RGB', (width, height), color=background_color)
            draw = ImageDraw.Draw(img)
            
            # Tentar usar fonte personalizada, senão usar padrão
            try:
                title_font = ImageFont.truetype("arial.ttf", 36)
                header_font = ImageFont.truetype("arial.ttf", 24)
                normal_font = ImageFont.truetype("arial.ttf", 16)
                small_font = ImageFont.truetype("arial.ttf", 12)
            except:
                # Fallback para fonte padrão
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                normal_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            y_position = 50
            
            if template_name == "fatura":
                y_position = self._draw_fatura_image(draw, processed_data, width, y_position, 
                                                  title_font, header_font, normal_font, small_font, text_color)
            elif template_name == "certificado":
                y_position = self._draw_certificado_image(draw, processed_data, width, y_position, 
                                                        title_font, header_font, normal_font, small_font, text_color)
            elif template_name == "fique_de_olho":
                y_position = self._draw_fique_de_olho_image(draw, processed_data, width, y_position, 
                                                          title_font, header_font, normal_font, small_font, text_color)
            elif template_name == "catalogo_produtos":
                y_position = self._draw_catalogo_produtos_image(draw, processed_data, width, y_position, 
                                                              title_font, header_font, normal_font, small_font, text_color)
            
            # Salvar imagem
            if format.lower() == "jpeg" and img.mode != "RGB":
                img = img.convert("RGB")
            img.save(output_path, format.upper(), quality=95)
        
        # Executar em thread separada
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, _create_image)
    
    def _draw_fatura_image(self, draw, data, width, y_pos, title_font, header_font, normal_font, small_font, text_color):
        """Desenha fatura na imagem"""
        # Título
        title = "FATURA"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2, y_pos), title, fill=text_color, font=title_font)
        y_pos += 80
        
        # Informações da empresa
        draw.text((50, y_pos), "Sua Empresa", fill=text_color, font=header_font)
        y_pos += 35
        draw.text((50, y_pos), "CNPJ: 00.000.000/0001-00", fill=text_color, font=normal_font)
        y_pos += 25
        draw.text((50, y_pos), "Endereço: Rua Exemplo, 123 - São Paulo/SP", fill=text_color, font=normal_font)
        y_pos += 50
        
        # Cliente
        draw.text((50, y_pos), f"Cliente: {data.get('cliente', '')}", fill=text_color, font=header_font)
        y_pos += 40
        
        # Número da fatura
        if data.get('numero_fatura'):
            draw.text((50, y_pos), f"Fatura Nº: {data['numero_fatura']}", fill=text_color, font=normal_font)
            y_pos += 30
        
        # Descrição
        if data.get('descricao'):
            draw.text((50, y_pos), f"Descrição: {data['descricao']}", fill=text_color, font=normal_font)
            y_pos += 40
        
        # Itens
        if data.get('itens'):
            draw.text((50, y_pos), "ITENS:", fill=text_color, font=header_font)
            y_pos += 35
            
            # Cabeçalho da tabela
            draw.rectangle([50, y_pos, width-50, y_pos+25], fill="lightgray")
            draw.text((60, y_pos+5), "#", fill="black", font=normal_font)
            draw.text((100, y_pos+5), "Descrição", fill="black", font=normal_font)
            draw.text((width-150, y_pos+5), "Valor", fill="black", font=normal_font)
            y_pos += 30
            
            total = 0
            for i, item in enumerate(data['itens'], 1):
                valor = item.get('valor', 0)
                total += valor
                valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                
                # Linha da tabela
                if i % 2 == 0:
                    draw.rectangle([50, y_pos, width-50, y_pos+25], fill="lightblue")
                
                draw.text((60, y_pos+5), str(i), fill=text_color, font=normal_font)
                draw.text((100, y_pos+5), item.get('descricao', ''), fill=text_color, font=normal_font)
                draw.text((width-150, y_pos+5), valor_formatado, fill=text_color, font=normal_font)
                y_pos += 30
            
            # Total
            y_pos += 20
            total_formatado = f"TOTAL: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            draw.text((width-200, y_pos), total_formatado, fill=text_color, font=header_font)
            y_pos += 40
        
        # Data
        draw.text((50, y_pos), f"Data: {data.get('data_atual', '')}", fill=text_color, font=normal_font)
        
        return y_pos
    
    def _draw_certificado_image(self, draw, data, width, y_pos, title_font, header_font, normal_font, small_font, text_color):
        """Desenha certificado na imagem"""
        y_pos += 100  # Espaço extra no topo
        
        # Título
        title = "CERTIFICADO"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2, y_pos), title, fill=text_color, font=title_font)
        y_pos += 60
        
        subtitle = "de Conclusão"
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=header_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(((width - subtitle_width) // 2, y_pos), subtitle, fill=text_color, font=header_font)
        y_pos += 80
        
        # Conteúdo
        text = "Certificamos que"
        text_bbox = draw.textbbox((0, 0), text, font=normal_font)
        text_width = text_bbox[2] - text_bbox[0]
        draw.text(((width - text_width) // 2, y_pos), text, fill=text_color, font=normal_font)
        y_pos += 60
        
        # Nome do participante
        participante = data.get('participante', '')
        participante_bbox = draw.textbbox((0, 0), participante, font=header_font)
        participante_width = participante_bbox[2] - participante_bbox[0]
        draw.text(((width - participante_width) // 2, y_pos), participante, fill=text_color, font=header_font)
        y_pos += 60
        
        text2 = "concluiu com êxito o curso"
        text2_bbox = draw.textbbox((0, 0), text2, font=normal_font)
        text2_width = text2_bbox[2] - text2_bbox[0]
        draw.text(((width - text2_width) // 2, y_pos), text2, fill=text_color, font=normal_font)
        y_pos += 60
        
        # Nome do curso
        curso = data.get('curso', '')
        curso_bbox = draw.textbbox((0, 0), curso, font=header_font)
        curso_width = curso_bbox[2] - curso_bbox[0]
        draw.text(((width - curso_width) // 2, y_pos), curso, fill=text_color, font=header_font)
        y_pos += 80
        
        # Informações adicionais
        if data.get('instrutor'):
            instrutor_text = f"Instrutor: {data['instrutor']}"
            draw.text((50, y_pos), instrutor_text, fill=text_color, font=normal_font)
            y_pos += 30
        
        if data.get('carga_horaria'):
            carga_text = f"Carga Horária: {data['carga_horaria']}"
            draw.text((50, y_pos), carga_text, fill=text_color, font=normal_font)
            y_pos += 30
        
        # Data
        data_conclusao = data.get('data_conclusao', data.get('data_atual', ''))
        data_text = f"Data: {data_conclusao}"
        draw.text((50, y_pos), data_text, fill=text_color, font=normal_font)
        y_pos += 30
        
        # Local
        if data.get('endereco'):
            local_text = f"Local: {data['endereco']}"
            draw.text((50, y_pos), local_text, fill=text_color, font=normal_font)
            y_pos += 30
        
        return y_pos
    
    def _draw_fique_de_olho_image(self, draw, data, width, y_pos, title_font, header_font, normal_font, small_font, text_color):
        """Desenha boletim Fique de Olho na imagem"""
        # Configurações específicas do template
        bg_color = (0, 0, 0, 190)  # Fundo escuro semi-transparente
        green_color = "#2e7d32"
        
        # Simular o fundo escuro
        draw.rectangle([40, y_pos, width-40, y_pos + 800], fill=(20, 20, 20), outline=None)
        
        y_pos += 100  # Espaço para a logo
        
        # Título "Fique de Olho"
        title = "Fique de Olho!"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2, y_pos), title, fill="white", font=title_font)
        y_pos += 80
        
        # Dia da semana
        dia_semana = data.get('dia_semana', 'Segunda-feira')
        dia_bbox = draw.textbbox((0, 0), dia_semana, font=header_font)
        dia_width = dia_bbox[2] - dia_bbox[0]
        draw.text(((width - dia_width) // 2, y_pos), dia_semana, fill="white", font=header_font)
        y_pos += 60
        
        # Linha decorativa
        draw.rectangle([width//2 - 30, y_pos, width//2 + 30, y_pos + 3], fill="white")
        y_pos += 40
        
        # Lista de notícias
        if data.get('lista_noticias'):
            for item in data['lista_noticias']:
                # Flag (emoji)
                x_offset = 60
                if item.get('flag'):
                    try:
                        # Tentar desenhar emoji como texto
                        draw.text((x_offset, y_pos), item['flag'], fill="white", font=normal_font)
                        x_offset += 30
                    except:
                        # Se falhar, usar bullet point
                        draw.text((x_offset, y_pos), "•", fill="white", font=normal_font)
                        x_offset += 20
                else:
                    # Bullet point para itens sem flag
                    draw.text((x_offset, y_pos), "•", fill="white", font=normal_font)
                    x_offset += 20
                
                # Texto da notícia
                texto = item.get('texto', '')
                # Quebrar texto se for muito longo
                if len(texto) > 40:
                    words = texto.split(' ')
                    lines = []
                    current_line = ""
                    for word in words:
                        if len(current_line + word) <= 40:
                            current_line += word + " "
                        else:
                            lines.append(current_line.strip())
                            current_line = word + " "
                    if current_line:
                        lines.append(current_line.strip())
                    
                    for i, line in enumerate(lines):
                        draw.text((x_offset, y_pos + i * 25), line, fill="white", font=normal_font)
                    y_pos += len(lines) * 25 + 15
                else:
                    draw.text((x_offset, y_pos), texto, fill="white", font=normal_font)
                    y_pos += 40
        
        # Pontos decorativos
        y_pos += 30
        dot_x = width // 2 - 20
        for i in range(3):
            if i == 2:  # último ponto inativo
                draw.ellipse([dot_x, y_pos, dot_x + 12, y_pos + 12], fill="#b0b7c3")
            else:
                draw.ellipse([dot_x, y_pos, dot_x + 12, y_pos + 12], fill="#2947a9")
            dot_x += 20
        
        y_pos += 40
        
        # Footer
        footer = "@granelcorretora"
        footer_bbox = draw.textbbox((0, 0), footer, font=normal_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        draw.text(((width - footer_width) // 2, y_pos), footer, fill="white", font=normal_font)
        
        return y_pos
    
    def _draw_catalogo_produtos_image(self, draw, data, width, y_pos, title_font, header_font, normal_font, small_font, text_color):
        """Desenha catálogo de produtos na imagem"""
        # Título
        title = "CATÁLOGO DE PRODUTOS"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2, y_pos), title, fill="#2196F3", font=title_font)
        y_pos += 60
        
        # Data de geração
        if data.get('data_geracao'):
            date_text = f"Atualizado em: {data['data_geracao']}"
            date_bbox = draw.textbbox((0, 0), date_text, font=normal_font)
            date_width = date_bbox[2] - date_bbox[0]
            draw.text(((width - date_width) // 2, y_pos), date_text, fill="gray", font=normal_font)
            y_pos += 50
        
        # Iterar sobre fabricantes
        for fabricante in data.get('catalogo_fabricantes', []):
            # Nome do fabricante
            draw.text((50, y_pos), fabricante['nome_fabricante'], fill="#1976D2", font=header_font)
            y_pos += 40
            
            # Linha divisória
            draw.line([50, y_pos, width-50, y_pos], fill="#E0E0E0", width=2)
            y_pos += 20
            
            # Produtos em grid 2x2
            products = fabricante.get('produtos', [])
            col_width = (width - 120) // 2  # 2 colunas com margem
            
            for i in range(0, len(products), 2):
                row_products = products[i:i+2]
                
                # Desenhar produtos lado a lado
                for col, produto in enumerate(row_products):
                    x_start = 50 + (col * (col_width + 20))
                    
                    # Caixa do produto
                    box_height = 140
                    draw.rectangle([x_start, y_pos, x_start + col_width, y_pos + box_height], 
                                 outline="#E0E0E0", fill="#F5F5F5", width=1)
                    
                    # Área da imagem fake
                    img_height = 60
                    draw.rectangle([x_start + 10, y_pos + 10, x_start + col_width - 10, y_pos + 10 + img_height], 
                                 outline="#2196F3", fill="#BBDEFB", width=1)
                    
                    # Texto "PRODUTO" na imagem
                    img_text = "PRODUTO"
                    img_bbox = draw.textbbox((0, 0), img_text, font=small_font)
                    img_text_width = img_bbox[2] - img_bbox[0]
                    draw.text((x_start + (col_width - img_text_width) // 2, y_pos + 35), 
                             img_text, fill="#1976D2", font=small_font)
                    
                    # Informações do produto
                    info_y = y_pos + 80
                    
                    # Nome do produto (limitado)
                    product_name = produto['nome_produto']
                    if len(product_name) > 25:
                        product_name = product_name[:25] + "..."
                    
                    name_bbox = draw.textbbox((0, 0), product_name, font=normal_font)
                    name_width = name_bbox[2] - name_bbox[0]
                    draw.text((x_start + (col_width - name_width) // 2, info_y), 
                             product_name, fill="black", font=normal_font)
                    info_y += 25
                    
                    # Código do produto
                    code_text = f"Cód: {produto['codigo_produto']}"
                    code_bbox = draw.textbbox((0, 0), code_text, font=small_font)
                    code_width = code_bbox[2] - code_bbox[0]
                    draw.text((x_start + (col_width - code_width) // 2, info_y), 
                             code_text, fill="gray", font=small_font)
                    info_y += 20
                    
                    # Preço
                    preco_formatado = f"R$ {produto['preco_sugerido_reais']:.2f}".replace(".", ",")
                    price_bbox = draw.textbbox((0, 0), preco_formatado, font=header_font)
                    price_width = price_bbox[2] - price_bbox[0]
                    draw.text((x_start + (col_width - price_width) // 2, info_y), 
                             preco_formatado, fill="#4CAF50", font=header_font)
                
                y_pos += box_height + 25
        
        # Rodapé
        y_pos += 30
        footer_text = f"© {data.get('ano_atual', '2025')} - Todos os direitos reservados"
        footer_bbox = draw.textbbox((0, 0), footer_text, font=small_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        draw.text(((width - footer_width) // 2, y_pos), footer_text, fill="gray", font=small_font)
        
        return y_pos
    
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
            elif template_name == "fique_de_olho":
                self._build_fique_de_olho_reportlab(story, styles, processed_data)
            elif template_name == "catalogo_produtos":
                self._build_catalogo_produtos_reportlab(story, styles, processed_data)
            
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
    
    def _build_fique_de_olho_reportlab(self, story, styles, data):
        """Constrói fique de olho usando ReportLab"""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import inch
        
        # Título
        title_style = styles['Title']
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph("Fique de Olho!", title_style))
        story.append(Spacer(1, 0.5*inch))
        
        # Conteúdo
        story.append(Paragraph("Dia da semana: " + data.get('dia_semana', 'Segunda-feira'), styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Lista de notícias
        if data.get('lista_noticias'):
            for item in data['lista_noticias']:
                story.append(Paragraph(item.get('texto', ''), styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        # Pontos decorativos
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("•" * 3, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Footer
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("@granelcorretora", styles['Normal']))
    
    def _build_catalogo_produtos_reportlab(self, story, styles, data):
        """Constrói catálogo de produtos usando ReportLab"""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image as RLImage
        from reportlab.lib import colors
        from reportlab.lib.units import inch, cm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.graphics.shapes import Drawing, Rect, String
        from reportlab.graphics import renderPDF
        from io import BytesIO
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=28,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2196F3')
        )
        story.append(Paragraph("CATÁLOGO DE PRODUTOS", title_style))
        
        # Data de geração
        if data.get('data_geracao'):
            date_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'],
                fontSize=12,
                alignment=TA_CENTER,
                textColor=colors.grey,
                spaceAfter=30
            )
            story.append(Paragraph(f"Atualizado em: {data['data_geracao']}", date_style))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Estilo do fabricante
        manufacturer_style = ParagraphStyle(
            'Manufacturer',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1976D2'),
            spaceBefore=25,
            spaceAfter=15,
            alignment=TA_LEFT
        )
        
        # Para cada fabricante
        for fabricante in data.get('catalogo_fabricantes', []):
            story.append(Paragraph(fabricante['nome_fabricante'], manufacturer_style))
            
            # Criar uma grade de produtos (2 colunas)
            products = fabricante.get('produtos', [])
            
            # Processar produtos em pares para layout de 2 colunas
            for i in range(0, len(products), 2):
                row_products = products[i:i+2]
                
                # Criar dados da tabela para esta linha
                table_data = []
                
                # Linha com imagens
                img_row = []
                for produto in row_products:
                    try:
                        # Tentar baixar a imagem real da URL
                        image_url = produto.get('url_imagem_placeholder', '')
                        if image_url:
                            img_buffer = self._download_image_from_url(image_url, max_size=(120, 80))
                            
                            if img_buffer:
                                # Usar a imagem real baixada
                                img = RLImage(img_buffer, width=100, height=67)
                                img_row.append(img)
                            else:
                                # Fallback: criar placeholder simples
                                d = Drawing(120, 80)
                                d.add(Rect(0, 0, 120, 80, fillColor=colors.lightblue, strokeColor=colors.blue, strokeWidth=1))
                                d.add(String(60, 45, "IMAGEM", textAnchor='middle', fontSize=10, fillColor=colors.blue))
                                d.add(String(60, 30, produto['codigo_produto'], textAnchor='middle', fontSize=8, fillColor=colors.darkblue))
                                
                                img_buffer = BytesIO()
                                renderPDF.drawToFile(d, img_buffer, fmt='PNG')
                                img_buffer.seek(0)
                                
                                img = RLImage(img_buffer, width=100, height=67)
                                img_row.append(img)
                        else:
                            # Sem URL de imagem: usar placeholder
                            d = Drawing(120, 80)
                            d.add(Rect(0, 0, 120, 80, fillColor=colors.lightgrey, strokeColor=colors.grey, strokeWidth=1))
                            d.add(String(60, 45, "SEM IMAGEM", textAnchor='middle', fontSize=9, fillColor=colors.darkgrey))
                            d.add(String(60, 30, produto['codigo_produto'], textAnchor='middle', fontSize=8, fillColor=colors.darkgrey))
                            
                            img_buffer = BytesIO()
                            renderPDF.drawToFile(d, img_buffer, fmt='PNG')
                            img_buffer.seek(0)
                            
                            img = RLImage(img_buffer, width=100, height=67)
                            img_row.append(img)
                            
                    except Exception as e:
                        print(f"⚠️ Erro ao processar imagem do produto {produto.get('codigo_produto', '')}: {e}")
                        # Fallback final: usar texto
                        placeholder_style = ParagraphStyle(
                            'PlaceholderStyle',
                            parent=styles['Normal'],
                            fontSize=10,
                            alignment=TA_CENTER,
                            textColor=colors.blue,
                            backColor=colors.lightblue
                        )
                        img_row.append(Paragraph("[ERRO NA IMAGEM]", placeholder_style))
                
                # Preencher linha se houver apenas 1 produto
                while len(img_row) < 2:
                    img_row.append("")
                
                table_data.append(img_row)
                
                # Linha com informações dos produtos
                info_row = []
                for produto in row_products:
                    # Criar célula com informações do produto
                    product_name = produto['nome_produto']
                    if len(product_name) > 35:
                        product_name = product_name[:35] + "..."
                    
                    preco_formatado = f"R$ {produto['preco_sugerido_reais']:.2f}".replace(".", ",")
                    
                    # Criar parágrafos separados para melhor controle
                    name_style = ParagraphStyle(
                        'ProductName',
                        parent=styles['Normal'],
                        fontSize=12,
                        alignment=TA_CENTER,
                        textColor=colors.black,
                        spaceAfter=3
                    )
                    
                    code_style = ParagraphStyle(
                        'ProductCode',
                        parent=styles['Normal'],
                        fontSize=9,
                        alignment=TA_CENTER,
                        textColor=colors.grey,
                        spaceAfter=3
                    )
                    
                    price_style = ParagraphStyle(
                        'ProductPrice',
                        parent=styles['Normal'],
                        fontSize=14,
                        alignment=TA_CENTER,
                        textColor=colors.HexColor('#4CAF50'),
                        spaceAfter=0
                    )
                    
                    # Criar conteúdo da célula usando uma tabela interna
                    cell_data = [
                        [Paragraph(f"<b>{product_name}</b>", name_style)],
                        [Paragraph(f"Cod: {produto['codigo_produto']}", code_style)],
                        [Paragraph(f"<b>{preco_formatado}</b>", price_style)]
                    ]
                    
                    cell_table = Table(cell_data, colWidths=[2.5*inch])
                    cell_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('PADDING', (0, 0), (-1, -1), 2),
                    ]))
                    
                    info_row.append(cell_table)
                
                # Preencher linha se houver apenas 1 produto
                while len(info_row) < 2:
                    info_row.append("")
                
                table_data.append(info_row)
                
                # Criar tabela
                product_table = Table(table_data, colWidths=[2.7*inch, 2.7*inch])
                product_table.setStyle(TableStyle([
                    # Estilo geral
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),  # Imagens centralizadas
                    ('VALIGN', (0, 1), (-1, 1), 'TOP'),     # Texto no topo
                    
                    # Bordas elegantes
                    ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#E0E0E0')),
                    ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#E0E0E0')),
                    ('LINEBETWEEN', (0, 0), (0, -1), 1, colors.HexColor('#E0E0E0')),
                    
                    # Padding
                    ('PADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),  # Padding embaixo das imagens
                    ('TOPPADDING', (0, 1), (-1, 1), 8),    # Padding em cima do texto
                    
                    # Efeito sombra sutil
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F5F5')),  # Fundo das imagens
                ]))
                
                story.append(product_table)
                story.append(Spacer(1, 20))
        
        # Rodapé
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        story.append(Paragraph(
            f"© {data.get('ano_atual', '2024')} - Todos os direitos reservados",
            footer_style
        ))
    
    async def _convert_pdf_to_image(self, pdf_path: str, output_path: str, format: str):
        """Converte PDF para imagem (método alternativo sem Poppler)"""
        def _convert():
            try:
                # Tentar usar pdf2image (requer Poppler)
                from pdf2image import convert_from_path
                images = convert_from_path(pdf_path, dpi=300)
                
                if images:
                    image = images[0]
                    if format.lower() == "jpeg" and image.mode != "RGB":
                        image = image.convert("RGB")
                    image.save(output_path, format.upper())
                    return
            except ImportError:
                print("⚠️  pdf2image não disponível (requer Poppler)")
            except Exception as e:
                print(f"⚠️  Erro ao converter PDF: {e}")
            
            # Fallback: criar imagem de placeholder informativa
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 20)
                small_font = ImageFont.truetype("arial.ttf", 14)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Mensagem informativa
            text1 = "⚠️ Conversão PDF→Imagem não disponível"
            text2 = "Para gerar imagens, use geração direta:"
            text3 = "Este PDF foi gerado com sucesso!"
            text4 = f"Arquivo: {os.path.basename(pdf_path)}"
            
            draw.text((50, 200), text1, fill="red", font=font)
            draw.text((50, 250), text2, fill="black", font=small_font)
            draw.text((50, 300), text3, fill="green", font=small_font)
            draw.text((50, 350), text4, fill="blue", font=small_font)
            
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
    
    def _download_image_from_url(self, url: str, max_size: tuple = (300, 200)) -> BytesIO:
        """
        Download an image from URL and return it as BytesIO
        """
        try:
            # Set a timeout and user agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10, stream=True)
            response.raise_for_status()
            
            # Load image
            img = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary  
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to BytesIO
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            print(f"⚠️ Erro ao baixar imagem de {url}: {e}")
            return None 