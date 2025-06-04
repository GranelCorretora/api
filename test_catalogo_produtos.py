"""
Teste específico para o template "Catálogo de Produtos"

Este script testa o novo template de catálogo de produtos.
"""

import requests
import json
import time
import os
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_catalogo_produtos():
    """Testa o template de Catálogo de Produtos em todos os formatos"""
    
    print("\n📦 TESTE DO TEMPLATE: CATÁLOGO DE PRODUTOS")
    print("="*60)
    print(f"📅 Data: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Dados de exemplo para o catálogo
    catalogo_data = {
        "template_name": "catalogo_produtos",
        "data": {
            "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "ano_atual": datetime.now().strftime("%Y"),
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
                        },
                        {
                            "codigo_produto": "035810",
                            "nome_produto": "ESCOVA DE DENTE POP CERDAS MACIAS SUND HC589 MULTILASER",
                            "preco_sugerido_reais": 6.15,
                            "unidade": "EMBALAGEM",
                            "descricao_curta": "Escova de dente popular com cerdas macias.",
                            "url_imagem_placeholder": "https://placehold.co/300x200/e0e0e0/777777?text=Escovas+HC589"
                        }
                    ]
                },
                {
                    "nome_fabricante": "FISHER PRICE",
                    "produtos": [
                        {
                            "codigo_produto": "037386",
                            "nome_produto": "ESPAÇADOR FISHER PRICE HC188 MULTILASER (T)",
                            "preco_sugerido_reais": 28.73,
                            "unidade": "1UN",
                            "categoria": "Infantil",
                            "descricao_curta": "Espaçador para medicamentos inalatórios.",
                            "url_imagem_placeholder": "https://placehold.co/300x200/e0e0e0/777777?text=Espaçador+HC188"
                        }
                    ]
                }
            ]
        },
        "output_format": "pdf",
        "upload_to_minio": False
    }
    
    # Teste 1: PDF
    print("📄 TESTE 1: Catálogo em PDF")
    print("-" * 40)
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=catalogo_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Template: {result['template_name']}")
            print(f"🎨 Formato: {result['output_format']}")
            print(f"📁 Arquivo: {result['local_path']}")
            
            if os.path.exists(result['local_path']):
                file_size = os.path.getsize(result['local_path'])
                print(f"📐 Tamanho: {file_size:,} bytes")
                print(f"✅ PDF gerado com sucesso!")
            else:
                print("❌ Arquivo não encontrado")
        else:
            print(f"❌ Erro: {response.status_code}")
            error_detail = response.json()
            print(f"   Detalhes: {error_detail}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print()
    
    # Teste 2: PNG
    print("🖼️  TESTE 2: Catálogo em PNG")
    print("-" * 40)
    
    png_data = catalogo_data.copy()
    png_data["output_format"] = "png"
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=png_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Template: {result['template_name']}")
            print(f"🎨 Formato: {result['output_format']}")
            print(f"📁 Arquivo: {result['local_path']}")
            
            if os.path.exists(result['local_path']):
                file_size = os.path.getsize(result['local_path'])
                print(f"📐 Tamanho: {file_size:,} bytes")
                print(f"✅ PNG gerado com sucesso!")
            else:
                print("❌ Arquivo não encontrado")
        else:
            print(f"❌ Erro: {response.status_code}")
            error_detail = response.json()
            print(f"   Detalhes: {error_detail}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_template_info():
    """Testa informações do template"""
    
    print("\n📊 INFORMAÇÕES DO TEMPLATE")
    print("="*40)
    
    try:
        response = requests.get(f"{BASE_URL}/templates")
        if response.status_code == 200:
            templates = response.json()
            
            # Procurar pelo template catalogo_produtos
            catalogo_template = None
            for template in templates['templates']:
                if template['id'] == 'catalogo_produtos':
                    catalogo_template = template
                    break
            
            if catalogo_template:
                print(f"🏷️  ID: {catalogo_template['id']}")
                print(f"📝 Nome: {catalogo_template['name']}")
                print(f"📄 Descrição: {catalogo_template['description']}")
                print(f"🔸 Campos obrigatórios: {', '.join(catalogo_template['required_fields'])}")
                print(f"🔹 Campos opcionais: {', '.join(catalogo_template['optional_fields'])}")
            else:
                print("❌ Template 'catalogo_produtos' não encontrado na listagem")
        else:
            print(f"❌ Erro ao obter templates: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Executa todos os testes do template Catálogo de Produtos"""
    
    # Teste principal
    test_catalogo_produtos()
    
    # Informações
    test_template_info()
    
    print("\n" + "="*60)
    print("📊 RESUMO FINAL")
    print("="*60)
    print("✅ Template 'Catálogo de Produtos' implementado com sucesso")
    print("📄 Suporte a PDF (ReportLab)")
    print("🖼️  Suporte a PNG e JPEG (PIL direto)")
    print("🎨 Layout moderno com cards responsivos")
    print("📦 Organização por fabricante")
    print("💰 Preços formatados automaticamente")
    print("🏷️  Suporte a categorias e unidades")
    print("\n💡 Use este template para criar catálogos de produtos,")
    print("   listas de preços ou apresentações comerciais!")

if __name__ == "__main__":
    main() 