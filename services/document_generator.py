import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Literal
import asyncio
from concurrent.futures import ThreadPoolExecutor

from jinja2 import Environment, FileSystemLoader
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from ..templates.template_manager import TemplateManager

class DocumentGenerator:
    def __init__(self):
        self.template_manager = TemplateManager()
        self.temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Configurar Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join("app", "templates", "html")),
            autoescape=True
        )
        
        # Executor para operações bloqueantes
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def generate_document(
        self, 
        template_name: str, 
        data: Dict[str, Any], 
        output_format: Literal["pdf", "png", "jpeg"]
    ) -> str:
        """
        Gera um documento a partir de um template
        
        Args:
            template_name: Nome do template
            data: Dados para preenchimento
            output_format: Formato de saída
            
        Returns:
            Caminho do arquivo gerado
        """
        try:
            # Gerar nome único para o arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{template_name}_{timestamp}.{output_format}"
            output_path = os.path.join(self.temp_dir, filename)
            
            if output_format == "pdf":
                await self._generate_pdf_simple(template_name, data, output_path)
            else:
                await self._generate_image_direct(template_name, data, output_path, output_format)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Erro ao gerar documento: {str(e)}")

    async def _generate_pdf_simple(self, template_name: str, data: Dict[str, Any], output_path: str):
        """Gera PDF usando ReportLab com abordagem simplificada"""
        def _create_pdf():
            # Criar o documento
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )
            
            # Lista de elementos
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            
            # Estilo do título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Estilo do fabricante
            manufacturer_style = ParagraphStyle(
                'Manufacturer',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#2196F3'),
                spaceBefore=20,
                spaceAfter=10
            )
            
            # Estilo do produto
            product_style = ParagraphStyle(
                'Product',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                spaceBefore=5,
                spaceAfter=5
            )
            
            # Título do catálogo
            elements.append(Paragraph("Catálogo de Produtos", title_style))
            elements.append(Paragraph(f"Atualizado em: {data.get('data_geracao', '')}", styles['Normal']))
            
            # Para cada fabricante
            for fabricante in data.get('catalogo_fabricantes', []):
                elements.append(Paragraph(fabricante['nome_fabricante'], manufacturer_style))
                
                # Para cada produto
                for produto in fabricante.get('produtos', []):
                    # Criar tabela para o produto
                    product_data = [
                        [Paragraph(f"<b>Código:</b> {produto['codigo_produto']}", product_style),
                         Paragraph(f"<b>Unidade:</b> {produto['unidade']}", product_style)]
                    ]
                    
                    if produto.get('categoria'):
                        product_data[0].append(Paragraph(f"<b>Categoria:</b> {produto['categoria']}", product_style))
                    
                    product_data.extend([
                        [Paragraph(f"<b>{produto['nome_produto']}</b>", product_style)],
                        [Paragraph(produto['descricao_curta'], product_style)],
                        [Paragraph(f"<b>Preço:</b> R$ {produto['preco_sugerido_reais']:.2f}", product_style)]
                    ])
                    
                    # Estilo da tabela
                    table_style = TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ('PADDING', (0, 0), (-1, -1), 6),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ])
                    
                    # Criar e adicionar tabela
                    product_table = Table(product_data, colWidths=[doc.width/2.0]*2)
                    product_table.setStyle(table_style)
                    elements.append(product_table)
                    elements.append(Spacer(1, 10))
            
            # Rodapé
            elements.append(Spacer(1, 20))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            elements.append(Paragraph(
                f"© {data.get('ano_atual', '2024')} - Todos os direitos reservados",
                footer_style
            ))
            
            # Construir o documento
            try:
                doc.build(elements)
            except Exception as e:
                print(f"Erro ao gerar PDF: {str(e)}")
                raise
        
        # Executar em thread separada
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, _create_pdf)

    async def _generate_image_direct(self, template_name: str, data: Dict[str, Any], output_path: str, format: str):
        """Gera imagem diretamente usando PIL"""
        def _create_image():
            # Configurações da imagem
            width, height = 1000, 1500  # Tamanho A4 proporcional
            background_color = "white"
            text_color = "black"
            
            # Criar imagem
            img = Image.new('RGB', (width, height), color=background_color)
            draw = ImageDraw.Draw(img)
            
            try:
                title_font = ImageFont.truetype("arial.ttf", 36)
                header_font = ImageFont.truetype("arial.ttf", 24)
                normal_font = ImageFont.truetype("arial.ttf", 16)
            except:
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                normal_font = ImageFont.load_default()
            
            # Título
            draw.text((50, 50), "Catálogo de Produtos", fill=text_color, font=title_font)
            draw.text((50, 100), f"Atualizado em: {data.get('data_geracao', '')}", fill=text_color, font=normal_font)
            
            y_pos = 150
            
            # Iterar sobre fabricantes
            for fabricante in data.get('catalogo_fabricantes', []):
                draw.text((50, y_pos), fabricante['nome_fabricante'], fill=text_color, font=header_font)
                y_pos += 40
                
                # Produtos
                for produto in fabricante.get('produtos', []):
                    # Borda do produto
                    draw.rectangle([50, y_pos, width-50, y_pos+150], outline="black")
                    
                    # Informações do produto
                    draw.text((60, y_pos+10), f"Código: {produto['codigo_produto']}", fill=text_color, font=normal_font)
                    draw.text((60, y_pos+35), produto['nome_produto'], fill=text_color, font=header_font)
                    draw.text((60, y_pos+70), produto['descricao_curta'], fill=text_color, font=normal_font)
                    draw.text((60, y_pos+100), f"R$ {produto['preco_sugerido_reais']:.2f}", fill=text_color, font=header_font)
                    draw.text((60, y_pos+130), f"Unidade: {produto['unidade']}", fill=text_color, font=normal_font)
                    
                    if produto.get('categoria'):
                        draw.text((width-200, y_pos+10), produto['categoria'], fill=text_color, font=normal_font)
                    
                    y_pos += 170
            
            # Rodapé
            footer_text = f"© {data.get('ano_atual', '2024')} - Todos os direitos reservados"
            draw.text((50, height-50), footer_text, fill=text_color, font=normal_font)
            
            # Salvar imagem
            if format.lower() == "jpeg" and img.mode != "RGB":
                img = img.convert("RGB")
            img.save(output_path, format.upper(), quality=95)
        
        # Executar em thread separada
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, _create_image) 