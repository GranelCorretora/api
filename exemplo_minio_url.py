"""
Exemplo prático: Como obter URLs do MinIO da API

Este exemplo mostra como fazer requisições para obter URLs públicas
dos documentos armazenados no MinIO.
"""

import requests
import json

def gerar_documento_com_url_minio():
    """Gera documento e retorna a URL do MinIO"""
    
    # Dados do documento
    dados_fatura = {
        "template_name": "fatura",
        "data": {
            "cliente": "Empresa XYZ Ltda",
            "numero_fatura": "FAT-2025-URL-001",
            "descricao": "Serviços com URL do MinIO",
            "itens": [
                {"descricao": "Desenvolvimento de API", "valor": 5000.00},
                {"descricao": "Integração MinIO", "valor": 1500.00}
            ]
        },
        "output_format": "pdf",
        "upload_to_minio": True  # 🔥 IMPORTANTE: Ativar upload para MinIO
    }
    
    # Fazer requisição para a API
    response = requests.post("http://localhost:8000/generate", json=dados_fatura)
    
    if response.status_code == 200:
        resultado = response.json()
        
        print("✅ Documento gerado com sucesso!")
        print(f"📄 Template: {resultado['template_name']}")
        print(f"📁 Arquivo local: {resultado['local_path']}")
        print(f"☁️  Upload MinIO: {resultado['uploaded_to_minio']}")
        
        # 🎯 AQUI ESTÁ A URL DO MINIO!
        if resultado.get('minio_url'):
            print(f"\n🔗 URL do MinIO:")
            print(f"   {resultado['minio_url']}")
            print("\n💡 Esta URL pode ser:")
            print("   - Enviada por email")
            print("   - Salva no banco de dados")
            print("   - Usada para download direto")
            print("   - Compartilhada com clientes")
            
            return resultado['minio_url']
        else:
            print("❌ Erro: URL do MinIO não retornada")
            if resultado.get('upload_error'):
                print(f"   Erro: {resultado['upload_error']}")
            return None
    else:
        print(f"❌ Erro na API: {response.status_code}")
        print(f"   Detalhes: {response.text}")
        return None

def exemplo_uso_em_sistema():
    """Exemplo de como usar a URL em um sistema real"""
    
    print("🏗️  EXEMPLO DE USO EM SISTEMA REAL")
    print("="*50)
    
    # Gerar documento e obter URL
    url_minio = gerar_documento_com_url_minio()
    
    if url_minio:
        print("\n📋 CASOS DE USO DA URL:")
        print("-" * 30)
        
        # Caso 1: Salvar no banco de dados
        print("1️⃣  Salvar no banco de dados:")
        print(f"   INSERT INTO documentos (url, tipo) VALUES ('{url_minio}', 'fatura')")
        
        # Caso 2: Enviar por email
        print("\n2️⃣  Enviar por email:")
        print("   Assunto: Sua fatura está pronta")
        print(f"   Link para download: {url_minio[:50]}...")
        
        # Caso 3: API de resposta
        print("\n3️⃣  Retornar em API:")
        api_response = {
            "documento_id": "12345",
            "status": "gerado",
            "download_url": url_minio,
            "expira_em": "7 dias"
        }
        print(f"   {json.dumps(api_response, indent=2, ensure_ascii=False)}")
        
        # Caso 4: Frontend/JavaScript
        print("\n4️⃣  Usar no frontend:")
        print("   ```javascript")
        print(f"   const downloadUrl = '{url_minio}';")
        print("   window.open(downloadUrl, '_blank');")
        print("   ```")

def configurar_minio_personalizado():
    """Mostra como configurar MinIO personalizado"""
    
    print("\n⚙️  CONFIGURAÇÃO PERSONALIZADA DO MINIO")
    print("="*50)
    
    print("📝 Variáveis de ambiente (.env):")
    print("""
MINIO_ENDPOINT=meu-servidor.com:9000
MINIO_ACCESS_KEY=minha_chave
MINIO_SECRET_KEY=minha_chave_secreta
MINIO_BUCKET_NAME=meus-documentos
MINIO_SECURE=true
""")
    
    print("🔧 A API automaticamente usa essas configurações!")
    print("✨ As URLs retornadas serão do seu servidor MinIO!")

if __name__ == "__main__":
    print("🚀 DEMONSTRAÇÃO: URLS DO MINIO")
    print("="*50)
    
    # Exemplo principal
    exemplo_uso_em_sistema()
    
    # Configuração personalizada
    configurar_minio_personalizado()
    
    print("\n✨ RESUMO:")
    print("- A API retorna automaticamente a URL do MinIO")
    print("- Use upload_to_minio: true na requisição")
    print("- A URL fica disponível no campo 'minio_url'")
    print("- URLs são válidas por 7 dias (configurável)")
    print("- Perfeito para sistemas de download e compartilhamento!") 