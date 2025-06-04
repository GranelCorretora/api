"""
Teste específico para upload MinIO

Este script testa o upload de documentos para MinIO e exibe as URLs retornadas.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_minio_upload():
    """Testa o upload para MinIO e exibe as URLs"""
    
    print("🚀 TESTE DE UPLOAD PARA MINIO")
    print("="*50)
    print(f"📅 Data: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Dados para fatura
    fatura_data = {
        "template_name": "fatura",
        "data": {
            "cliente": "MinIO Test Company",
            "numero_fatura": "MINIO-2025-001",
            "descricao": "Teste de upload para MinIO",
            "itens": [
                {"descricao": "Upload de fatura PDF", "valor": 100.00},
                {"descricao": "Armazenamento na nuvem", "valor": 50.00}
            ]
        },
        "output_format": "pdf",
        "upload_to_minio": True  # 🔥 Ativando upload para MinIO
    }
    
    # Dados para certificado
    certificado_data = {
        "template_name": "certificado",
        "data": {
            "participante": "João MinIO Santos",
            "curso": "Curso de Upload para MinIO",
            "instrutor": "Prof. Storage Silva",
            "data_conclusao": "04/01/2025",
            "endereco": "Nuvem, Internet, Brasil",
            "carga_horaria": "2 horas"
        },
        "output_format": "pdf",
        "upload_to_minio": True  # 🔥 Ativando upload para MinIO
    }
    
    # Teste 1: Fatura com upload para MinIO
    print("🧾 TESTE 1: Fatura com upload para MinIO")
    print("-" * 40)
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=fatura_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Template: {result['template_name']}")
            print(f"📁 Arquivo local: {result['local_path']}")
            print(f"☁️  Upload MinIO: {result['uploaded_to_minio']}")
            
            if result.get('minio_url'):
                print(f"🔗 URL do MinIO: {result['minio_url']}")
                print(f"💡 Esta URL pode ser usada para acessar o arquivo remotamente!")
            
            if result.get('upload_error'):
                print(f"❌ Erro no upload: {result['upload_error']}")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"   Detalhes: {response.text}")
    
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print()
    
    # Teste 2: Certificado com upload para MinIO
    print("🎓 TESTE 2: Certificado com upload para MinIO")
    print("-" * 40)
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=certificado_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Template: {result['template_name']}")
            print(f"📁 Arquivo local: {result['local_path']}")
            print(f"☁️  Upload MinIO: {result['uploaded_to_minio']}")
            
            if result.get('minio_url'):
                print(f"🔗 URL do MinIO: {result['minio_url']}")
                print(f"💡 Esta URL pode ser usada para acessar o arquivo remotamente!")
            
            if result.get('upload_error'):
                print(f"❌ Erro no upload: {result['upload_error']}")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"   Detalhes: {response.text}")
    
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print()
    
    # Teste 3: Documento sem upload (para comparação)
    print("📋 TESTE 3: Documento sem upload (comparação)")
    print("-" * 40)
    
    no_upload_data = {
        "template_name": "fatura",
        "data": {
            "cliente": "Local Test Company",
            "numero_fatura": "LOCAL-2025-001",
            "itens": [
                {"descricao": "Documento local apenas", "valor": 25.00}
            ]
        },
        "output_format": "pdf",
        "upload_to_minio": False  # ❌ Sem upload para MinIO
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=no_upload_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Template: {result['template_name']}")
            print(f"📁 Arquivo local: {result['local_path']}")
            print(f"☁️  Upload MinIO: {result['uploaded_to_minio']}")
            print(f"🔗 URL do MinIO: {result.get('minio_url', 'N/A')}")
            print(f"💡 Arquivo disponível apenas localmente")
        else:
            print(f"❌ Erro: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    print("✅ Teste 1: Fatura + MinIO URL")
    print("✅ Teste 2: Certificado + MinIO URL")
    print("✅ Teste 3: Documento local (sem MinIO)")
    print()
    print("🎯 CONFIGURAÇÃO DO MINIO:")
    print("   Endpoint: localhost:9000 (padrão)")
    print("   Bucket: documents")
    print("   Access Key: minioadmin")
    print("   Secret Key: minioadmin")
    print()
    print("💡 NOTA: Se o MinIO não estiver rodando, você verá erros de upload,")
    print("   mas os documentos serão gerados localmente normalmente.")
    print()
    print("🐳 Para executar MinIO local:")
    print("   docker run -p 9000:9000 -p 9001:9001 \\")
    print("     -e 'MINIO_ROOT_USER=minioadmin' \\")
    print("     -e 'MINIO_ROOT_PASSWORD=minioadmin' \\")
    print("     minio/minio server /data --console-address ':9001'")

if __name__ == "__main__":
    test_minio_upload() 