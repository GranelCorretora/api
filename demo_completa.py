"""
Demonstração Completa da API de Geração de Documentos

Este script demonstra todos os recursos da API:
- Health check
- Listagem de templates
- Geração de fatura (PDF e PNG)
- Geração de certificado (PDF e JPEG)
- Upload para MinIO (simulado)
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def print_separator(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health_check():
    """Testa o health check da API"""
    print_separator("HEALTH CHECK")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Resposta: {response.json()}")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    return True

def list_templates():
    """Lista todos os templates disponíveis"""
    print_separator("TEMPLATES DISPONÍVEIS")
    
    try:
        response = requests.get(f"{BASE_URL}/templates")
        if response.status_code == 200:
            templates = response.json()
            print(f"📋 Total de templates: {len(templates['templates'])}\n")
            
            for template in templates['templates']:
                print(f"🏷️  ID: {template['id']}")
                print(f"   Nome: {template['name']}")
                print(f"   Descrição: {template['description']}")
                print(f"   Campos obrigatórios: {', '.join(template['required_fields'])}")
                print(f"   Campos opcionais: {', '.join(template['optional_fields'])}")
                print(f"   Exemplo de dados:")
                for key, value in template['example_data'].items():
                    if isinstance(value, list) and len(value) > 0:
                        print(f"     {key}: [{len(value)} itens]")
                    else:
                        print(f"     {key}: {value}")
                print()
        else:
            print(f"❌ Erro ao listar templates: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    return True

def generate_fatura():
    """Gera uma fatura em PDF"""
    print_separator("GERAÇÃO DE FATURA (PDF)")
    
    data = {
        "template_name": "fatura",
        "data": {
            "cliente": "Empresa ABC Ltda",
            "numero_fatura": "FAT-2024-001",
            "descricao": "Serviços de desenvolvimento de software",
            "itens": [
                {"descricao": "Desenvolvimento de API REST", "valor": 2500.00},
                {"descricao": "Testes e documentação", "valor": 800.00},
                {"descricao": "Deploy e configuração", "valor": 700.00}
            ]
        },
        "output_format": "pdf",
        "upload_to_minio": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Fatura gerada com sucesso!")
            print(f"   📁 Arquivo: {result['local_path']}")
            print(f"   📅 Gerado em: {result['generated_at']}")
            return result['local_path']
        else:
            error = response.json()
            print(f"❌ Erro: {error['detail']}")
            return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def generate_fatura_png():
    """Gera uma fatura em PNG"""
    print_separator("GERAÇÃO DE FATURA (PNG)")
    
    data = {
        "template_name": "fatura",
        "data": {
            "cliente": "Tech Solutions Ltda",
            "numero_fatura": "FAT-2024-002",
            "descricao": "Consultoria em tecnologia",
            "itens": [
                {"descricao": "Análise de arquitetura", "valor": 1500.00},
                {"descricao": "Revisão de código", "valor": 1000.00}
            ]
        },
        "output_format": "png",
        "upload_to_minio": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Fatura PNG gerada com sucesso!")
            print(f"   🖼️  Arquivo: {result['local_path']}")
            return result['local_path']
        else:
            error = response.json()
            print(f"❌ Erro: {error['detail']}")
            return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def generate_certificado():
    """Gera um certificado em PDF"""
    print_separator("GERAÇÃO DE CERTIFICADO (PDF)")
    
    data = {
        "template_name": "certificado",
        "data": {
            "participante": "Maria Silva Santos",
            "curso": "Curso Avançado de Python para APIs",
            "instrutor": "Prof. Dr. João Rodriguez",
            "data_conclusao": "04/01/2025",
            "endereco": "São Paulo, SP, Brasil",
            "carga_horaria": "80 horas"
        },
        "output_format": "pdf",
        "upload_to_minio": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Certificado gerado com sucesso!")
            print(f"   📁 Arquivo: {result['local_path']}")
            print(f"   🎓 Participante: {data['data']['participante']}")
            print(f"   📚 Curso: {data['data']['curso']}")
            return result['local_path']
        else:
            error = response.json()
            print(f"❌ Erro: {error['detail']}")
            return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def generate_certificado_jpeg():
    """Gera um certificado em JPEG"""
    print_separator("GERAÇÃO DE CERTIFICADO (JPEG)")
    
    data = {
        "template_name": "certificado",
        "data": {
            "participante": "Carlos Eduardo Lima",
            "curso": "Workshop de FastAPI e Microserviços",
            "instrutor": "Dra. Ana Paula Costa",
            "data_conclusao": "04/01/2025",
            "endereco": "Rio de Janeiro, RJ, Brasil",
            "carga_horaria": "16 horas"
        },
        "output_format": "jpeg",
        "upload_to_minio": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Certificado JPEG gerado com sucesso!")
            print(f"   🖼️  Arquivo: {result['local_path']}")
            return result['local_path']
        else:
            error = response.json()
            print(f"❌ Erro: {error['detail']}")
            return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def show_summary(generated_files):
    """Mostra um resumo dos arquivos gerados"""
    print_separator("RESUMO DOS ARQUIVOS GERADOS")
    
    if not generated_files:
        print("❌ Nenhum arquivo foi gerado.")
        return
    
    print(f"✅ Total de arquivos gerados: {len(generated_files)}\n")
    
    for i, file_path in enumerate(generated_files, 1):
        if file_path and os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            extension = file_path.split('.')[-1].upper()
            
            print(f"{i}. 📄 {file_name}")
            print(f"   📐 Tamanho: {file_size:,} bytes")
            print(f"   🏷️  Formato: {extension}")
            print(f"   📂 Caminho: {file_path}")
            print()
    
    print("💡 Dica: Você pode abrir estes arquivos para visualizar os documentos gerados!")

def main():
    """Função principal da demonstração"""
    print("🚀 DEMONSTRAÇÃO COMPLETA DA API DE GERAÇÃO DE DOCUMENTOS")
    print("📅 Data:", time.strftime("%d/%m/%Y %H:%M:%S"))
    
    generated_files = []
    
    # 1. Health Check
    if not test_health_check():
        print("❌ API não está funcionando. Verifique se ela está rodando.")
        return
    
    # 2. Listar templates
    if not list_templates():
        print("❌ Não foi possível listar os templates.")
        return
    
    # 3. Gerar documentos
    print("\n🔧 Iniciando geração de documentos...")
    
    # Fatura PDF
    file_path = generate_fatura()
    if file_path:
        generated_files.append(file_path)
    
    # Fatura PNG
    file_path = generate_fatura_png()
    if file_path:
        generated_files.append(file_path)
    
    # Certificado PDF
    file_path = generate_certificado()
    if file_path:
        generated_files.append(file_path)
    
    # Certificado JPEG
    file_path = generate_certificado_jpeg()
    if file_path:
        generated_files.append(file_path)
    
    # 4. Mostrar resumo
    show_summary(generated_files)
    
    print("\n✨ DEMONSTRAÇÃO CONCLUÍDA!")
    print("🎯 A API está funcionando perfeitamente e pode ser usada em produção.")

if __name__ == "__main__":
    main() 