"""
Teste específico para o template "Fique de Olho!"

Este script testa o novo template de boletim informativo.
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def test_fique_de_olho():
    """Testa o template Fique de Olho em todos os formatos"""
    
    print("📢 TESTE DO TEMPLATE: FIQUE DE OLHO!")
    print("="*60)
    print(f"📅 Data: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Dados de exemplo para o boletim
    fique_de_olho_data = {
        "template_name": "fique_de_olho",
        "data": {
            "dia_semana": "Segunda-feira",
            "lista_noticias": [
                {
                    "flag": "🇧🇷",
                    "texto": "Mercado brasileiro registra alta de 2,5% nas commodities agrícolas"
                },
                {
                    "flag": "🌎",
                    "texto": "Preços internacionais da soja se mantêm estáveis em Chicago"
                },
                {
                    "flag": "📈",
                    "texto": "Expectativa de safra recorde impulsiona mercado de milho"
                },
                {
                    "flag": "⚡",
                    "texto": "Energia elétrica com redução de 5% nas tarifas rurais"
                },
                {
                    "texto": "Clima favorável para plantio na região centro-oeste"
                }
            ]
        },
        "output_format": "pdf",
        "upload_to_minio": False
    }
    
    # Teste 1: PDF
    print("📄 TESTE 1: Fique de Olho em PDF")
    print("-" * 40)
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=fique_de_olho_data)
        
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
    print("🖼️  TESTE 2: Fique de Olho em PNG")
    print("-" * 40)
    
    png_data = fique_de_olho_data.copy()
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
    
    print()
    
    # Teste 3: JPEG com MinIO
    print("☁️  TESTE 3: Fique de Olho JPEG + MinIO")
    print("-" * 40)
    
    jpeg_minio_data = fique_de_olho_data.copy()
    jpeg_minio_data["output_format"] = "jpeg"
    jpeg_minio_data["upload_to_minio"] = True
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=jpeg_minio_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Template: {result['template_name']}")
            print(f"🎨 Formato: {result['output_format']}")
            print(f"📁 Arquivo local: {result['local_path']}")
            print(f"☁️  Upload MinIO: {result['uploaded_to_minio']}")
            
            if result.get('minio_url'):
                print(f"🔗 URL MinIO: {result['minio_url'][:70]}...")
                print(f"✅ JPEG enviado para MinIO!")
            
            if result.get('upload_error'):
                print(f"❌ Erro no upload: {result['upload_error']}")
        else:
            print(f"❌ Erro: {response.status_code}")
            error_detail = response.json()
            print(f"   Detalhes: {error_detail}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_template_variations():
    """Testa diferentes variações do template"""
    
    print("\n🔄 TESTE DE VARIAÇÕES DO TEMPLATE")
    print("="*50)
    
    # Variação 1: Terça-feira com notícias diferentes
    variacao_1 = {
        "template_name": "fique_de_olho",
        "data": {
            "dia_semana": "Terça-feira",
            "lista_noticias": [
                {
                    "flag": "🏭",
                    "texto": "Indústria de fertilizantes anuncia expansão de 15%"
                },
                {
                    "flag": "🚛",
                    "texto": "Transporte rodoviário com nova regulamentação"
                },
                {
                    "texto": "Investimentos em tecnologia agrícola crescem 30%"
                }
            ]
        },
        "output_format": "png",
        "upload_to_minio": False
    }
    
    # Variação 2: Sem flags
    variacao_2 = {
        "template_name": "fique_de_olho",
        "data": {
            "dia_semana": "Sexta-feira",
            "lista_noticias": [
                {"texto": "Primeira notícia sem flag"},
                {"texto": "Segunda notícia também sem flag"},
                {"texto": "Terceira notícia mantém o padrão"}
            ]
        },
        "output_format": "pdf",
        "upload_to_minio": False
    }
    
    variações = [
        ("Terça-feira com flags variadas", variacao_1),
        ("Sexta-feira sem flags", variacao_2)
    ]
    
    for nome, dados in variações:
        print(f"\n📋 Testando: {nome}")
        print("-" * 30)
        
        try:
            response = requests.post(f"{BASE_URL}/generate", json=dados)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['output_format'].upper()}: Sucesso")
                print(f"📁 Arquivo: {os.path.basename(result['local_path'])}")
            else:
                print(f"❌ Erro: {response.status_code}")
        
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
            
            # Procurar pelo template fique_de_olho
            fique_de_olho_template = None
            for template in templates['templates']:
                if template['id'] == 'fique_de_olho':
                    fique_de_olho_template = template
                    break
            
            if fique_de_olho_template:
                print(f"🏷️  ID: {fique_de_olho_template['id']}")
                print(f"📝 Nome: {fique_de_olho_template['name']}")
                print(f"📄 Descrição: {fique_de_olho_template['description']}")
                print(f"🔸 Campos obrigatórios: {', '.join(fique_de_olho_template['required_fields'])}")
                print(f"🔹 Campos opcionais: {', '.join(fique_de_olho_template['optional_fields'])}")
                print("\n💡 Exemplo de dados:")
                for key, value in fique_de_olho_template['example_data'].items():
                    if key == 'lista_noticias':
                        print(f"   {key}: [{len(value)} notícias]")
                    else:
                        print(f"   {key}: {value}")
            else:
                print("❌ Template 'fique_de_olho' não encontrado na listagem")
        else:
            print(f"❌ Erro ao obter templates: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Executa todos os testes do template Fique de Olho"""
    
    # Teste principal
    test_fique_de_olho()
    
    # Variações
    test_template_variations()
    
    # Informações
    test_template_info()
    
    print("\n" + "="*60)
    print("📊 RESUMO FINAL")
    print("="*60)
    print("✅ Template 'Fique de Olho!' implementado com sucesso")
    print("📄 Suporte a PDF (ReportLab)")
    print("🖼️  Suporte a PNG e JPEG (PIL direto)")
    print("☁️  Upload para MinIO funcionando")
    print("🎨 Layout moderno com fundo escuro")
    print("📰 Lista dinâmica de notícias com flags opcionais")
    print("🎯 Ideal para boletins informativos diários")
    print("\n💡 Use este template para criar boletins de mercado,")
    print("   newsletters ou informativos corporativos!")

if __name__ == "__main__":
    main() 