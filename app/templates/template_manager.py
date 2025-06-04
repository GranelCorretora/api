import os
from typing import List, Dict, Any

class TemplateManager:
    def __init__(self):
        self.templates_dir = os.path.join("app", "templates", "html")
        self.available_templates = {
            "fatura": {
                "name": "Fatura",
                "description": "Template para geração de faturas com itens dinâmicos",
                "required_fields": ["cliente", "itens"],
                "optional_fields": ["descricao", "valor", "data_atual", "numero_fatura"],
                "example_data": {
                    "cliente": "João Silva",
                    "numero_fatura": "FAT-2024-001",
                    "descricao": "Serviços de consultoria",
                    "valor": 1500.00,
                    "itens": [
                        {"descricao": "Consultoria técnica", "valor": 1000.00},
                        {"descricao": "Documentação", "valor": 500.00}
                    ]
                }
            },
            "certificado": {
                "name": "Certificado",
                "description": "Template para certificados com mapa de localização",
                "required_fields": ["participante", "curso"],
                "optional_fields": ["instrutor", "data_conclusao", "endereco", "latitude", "longitude"],
                "example_data": {
                    "participante": "Maria Santos",
                    "curso": "Curso de Python Avançado",
                    "instrutor": "Prof. Carlos Silva",
                    "data_conclusao": "15/12/2024",
                    "endereco": "São Paulo, SP, Brasil",
                    "carga_horaria": "40 horas"
                }
            },
            "fique_de_olho": {
                "name": "Fique de Olho!",
                "description": "Template para boletim informativo com lista de notícias",
                "required_fields": ["dia_semana", "lista_noticias"],
                "optional_fields": ["titulo_customizado"],
                "example_data": {
                    "dia_semana": "Segunda-feira",
                    "lista_noticias": [
                        {"flag": "🇧🇷", "texto": "Mercado brasileiro em alta"},
                        {"flag": "🌎", "texto": "Commodities internacionais estáveis"},
                        {"flag": "📈", "texto": "Soja com expectativa de crescimento"},
                        {"texto": "Notícia sem bandeira exemplo"}
                    ]
                }
            },
            "catalogo_produtos": {
                "name": "Catálogo de Produtos",
                "description": "Template para catálogo de produtos organizados por fabricante",
                "required_fields": ["catalogo_fabricantes"],
                "optional_fields": ["data_geracao", "ano_atual"],
                "example_data": {
                    "data_geracao": "15/03/2024 14:30",
                    "ano_atual": "2024",
                    "catalogo_fabricantes": [
                        {
                            "nome_fabricante": "MULTILASER",
                            "produtos": [
                                {
                                    "codigo_produto": "035734",
                                    "nome_produto": "ESCOVA DE DENTE SOFT C/ LIMPADOR DE LÍN. HC591 2UND",
                                    "preco_sugerido_reais": 6.06,
                                    "unidade": "2UN",
                                    "descricao_curta": "Escova de dente macia com limpador de língua.",
                                    "url_imagem_placeholder": "https://placehold.co/300x200/e0e0e0/777777?text=Escovas+HC591"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """Lista todos os templates disponíveis com suas informações"""
        templates = []
        for template_id, template_info in self.available_templates.items():
            template_data = {
                "id": template_id,
                "name": template_info["name"],
                "description": template_info["description"],
                "required_fields": template_info["required_fields"],
                "optional_fields": template_info["optional_fields"],
                "example_data": template_info["example_data"]
            }
            templates.append(template_data)
        return templates
    
    def template_exists(self, template_name: str) -> bool:
        """Verifica se um template existe"""
        return template_name in self.available_templates
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Obtém informações sobre um template específico"""
        if template_name in self.available_templates:
            return self.available_templates[template_name]
        return {}
    
    def validate_template_data(self, template_name: str, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Valida se os dados fornecidos são adequados para o template
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        if not self.template_exists(template_name):
            return False, [f"Template '{template_name}' não existe"]
        
        template_info = self.available_templates[template_name]
        errors = []
        
        # Verificar campos obrigatórios
        for field in template_info["required_fields"]:
            if field not in data:
                errors.append(f"Campo obrigatório '{field}' não fornecido")
            elif not data[field]:
                errors.append(f"Campo obrigatório '{field}' está vazio")
        
        # Validações específicas por template
        if template_name == "fatura":
            if "itens" in data and isinstance(data["itens"], list):
                for i, item in enumerate(data["itens"]):
                    if not isinstance(item, dict):
                        errors.append(f"Item {i+1} deve ser um objeto")
                    elif "descricao" not in item or "valor" not in item:
                        errors.append(f"Item {i+1} deve conter 'descricao' e 'valor'")
        
        return len(errors) == 0, errors 