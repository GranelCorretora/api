import requests
import json

def test_api():
    """Testa a API de geração de documentos"""
    
    # Testar endpoint de health check
    print("🔍 Testando endpoint de health check...")
    try:
        response = requests.get("http://localhost:8000/")
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Resposta: {response.json()}")
        print()
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return
    
    # Testar listagem de templates
    print("🔍 Testando listagem de templates...")
    try:
        response = requests.get("http://localhost:8000/templates")
        print(f"✅ Status: {response.status_code}")
        templates = response.json()
        print(f"📋 Templates disponíveis: {len(templates['templates'])}")
        for template in templates['templates']:
            print(f"   - {template['id']}: {template['name']}")
        print()
    except Exception as e:
        print(f"❌ Erro ao listar templates: {e}")
        return
    
    # Testar geração de fatura
    print("🔍 Testando geração de fatura...")
    fatura_data = {
        "template_name": "fatura",
        "data": {
            "cliente": "João Silva",
            "numero_fatura": "FAT-2024-001",
            "descricao": "Serviços de consultoria em Python",
            "itens": [
                {"descricao": "Consultoria técnica", "valor": 1000.00},
                {"descricao": "Documentação do projeto", "valor": 500.00},
                {"descricao": "Treinamento da equipe", "valor": 800.00}
            ]
        },
        "output_format": "pdf",
        "upload_to_minio": False
    }
    
    try:
        response = requests.post("http://localhost:8000/generate", json=fatura_data)
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Resultado:")
            print(f"   - Sucesso: {result.get('success')}")
            print(f"   - Template: {result.get('template_name')}")
            print(f"   - Formato: {result.get('output_format')}")
            print(f"   - Arquivo: {result.get('local_path')}")
        else:
            print(f"❌ Erro na requisição:")
            try:
                error_detail = response.json()
                print(f"   - Detalhes: {error_detail}")
            except:
                print(f"   - Texto do erro: {response.text}")
        print()
    except Exception as e:
        print(f"❌ Erro ao gerar fatura: {e}")
    
    # Testar geração de certificado
    print("🔍 Testando geração de certificado...")
    certificado_data = {
        "template_name": "certificado",
        "data": {
            "participante": "Maria Santos",
            "curso": "Curso de Python Avançado",
            "instrutor": "Prof. Carlos Silva",
            "data_conclusao": "15/12/2024",
            "endereco": "São Paulo, SP, Brasil",
            "carga_horaria": "40 horas"
        },
        "output_format": "pdf",
        "upload_to_minio": False
    }
    
    try:
        response = requests.post("http://localhost:8000/generate", json=certificado_data)
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Resultado:")
            print(f"   - Sucesso: {result.get('success')}")
            print(f"   - Template: {result.get('template_name')}")
            print(f"   - Formato: {result.get('output_format')}")
            print(f"   - Arquivo: {result.get('local_path')}")
        else:
            print(f"❌ Erro na requisição:")
            try:
                error_detail = response.json()
                print(f"   - Detalhes: {error_detail}")
            except:
                print(f"   - Texto do erro: {response.text}")
        print()
    except Exception as e:
        print(f"❌ Erro ao gerar certificado: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes da API de Geração de Documentos\n")
    test_api()
    print("✨ Testes concluídos!") 