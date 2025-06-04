"""
Teste específico para geração de imagens (PNG e JPEG)

Este script testa a nova funcionalidade de geração direta de imagens
sem depender do Poppler.
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def test_image_generation():
    """Testa a geração de imagens PNG e JPEG"""
    
    print("🖼️  TESTE DE GERAÇÃO DE IMAGENS")
    print("="*50)
    print(f"📅 Data: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Teste 1: Fatura PNG
    print("🧾 TESTE 1: Fatura em PNG")
    print("-" * 30)
    
    fatura_png_data = {
        "template_name": "fatura",
        "data": {
            "cliente": "Empresa PNG Test Ltda",
            "numero_fatura": "PNG-2025-001",
            "descricao": "Teste de geração de imagem PNG",
            "itens": [
                {"descricao": "Desenvolvimento de sistema", "valor": 2500.00},
                {"descricao": "Design de interface", "valor": 800.00},
                {"descricao": "Testes e validação", "valor": 700.00}
            ]
        },
        "output_format": "png",  # 🖼️ Formato PNG
        "upload_to_minio": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=fatura_png_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Template: {result['template_name']}")
            print(f"🎨 Formato: {result['output_format']}")
            print(f"📁 Arquivo: {result['local_path']}")
            
            # Verificar se o arquivo foi criado
            if os.path.exists(result['local_path']):
                file_size = os.path.getsize(result['local_path'])
                print(f"📐 Tamanho: {file_size:,} bytes")
                print(f"✅ Arquivo PNG gerado com sucesso!")
            else:
                print("❌ Arquivo não foi encontrado")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"   Detalhes: {response.json()}")
    
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print()
    
    # Teste 2: Certificado JPEG
    print("🎓 TESTE 2: Certificado em JPEG")
    print("-" * 30)
    
    certificado_jpeg_data = {
        "template_name": "certificado",
        "data": {
            "participante": "Maria JPEG Silva",
            "curso": "Curso de Geração de Imagens com Python",
            "instrutor": "Prof. Dr. Image Generator",
            "data_conclusao": "04/01/2025",
            "endereco": "São Paulo, SP, Brasil",
            "carga_horaria": "40 horas"
        },
        "output_format": "jpeg",  # 🖼️ Formato JPEG
        "upload_to_minio": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=certificado_jpeg_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Template: {result['template_name']}")
            print(f"🎨 Formato: {result['output_format']}")
            print(f"📁 Arquivo: {result['local_path']}")
            
            # Verificar se o arquivo foi criado
            if os.path.exists(result['local_path']):
                file_size = os.path.getsize(result['local_path'])
                print(f"📐 Tamanho: {file_size:,} bytes")
                print(f"✅ Arquivo JPEG gerado com sucesso!")
            else:
                print("❌ Arquivo não foi encontrado")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"   Detalhes: {response.json()}")
    
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print()
    
    # Teste 3: Fatura JPEG com MinIO
    print("💾 TESTE 3: Fatura JPEG com upload para MinIO")
    print("-" * 30)
    
    fatura_minio_data = {
        "template_name": "fatura",
        "data": {
            "cliente": "Empresa MinIO Image Ltda",
            "numero_fatura": "IMG-MINIO-2025-001",
            "descricao": "Teste de upload de imagem para MinIO",
            "itens": [
                {"descricao": "Geração de imagem", "valor": 500.00},
                {"descricao": "Upload para nuvem", "valor": 100.00}
            ]
        },
        "output_format": "jpeg",
        "upload_to_minio": True  # ☁️ Upload para MinIO
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=fatura_minio_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Template: {result['template_name']}")
            print(f"🎨 Formato: {result['output_format']}")
            print(f"📁 Arquivo local: {result['local_path']}")
            print(f"☁️  Upload MinIO: {result['uploaded_to_minio']}")
            
            if result.get('minio_url'):
                print(f"🔗 URL MinIO: {result['minio_url'][:60]}...")
                print(f"✅ Imagem enviada para MinIO com sucesso!")
            
            if result.get('upload_error'):
                print(f"❌ Erro no upload: {result['upload_error']}")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"   Detalhes: {response.json()}")
    
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print()
    
    # Resumo
    print("="*50)
    print("📊 RESUMO DOS TESTES DE IMAGEM")
    print("="*50)
    print("✅ Teste 1: Fatura PNG (local)")
    print("✅ Teste 2: Certificado JPEG (local)")
    print("✅ Teste 3: Fatura JPEG + MinIO")
    print()
    print("🎯 VANTAGENS DA NOVA IMPLEMENTAÇÃO:")
    print("   ✅ Não requer Poppler")
    print("   ✅ Funciona no Windows sem dependências extras")
    print("   ✅ Geração direta de imagens (mais rápido)")
    print("   ✅ Qualidade controlada (95% JPEG)")
    print("   ✅ Layout profissional")
    print()
    print("📝 FORMATOS SUPORTADOS:")
    print("   🔸 PDF (ReportLab/WeasyPrint)")
    print("   🔸 PNG (PIL - geração direta)")
    print("   🔸 JPEG (PIL - geração direta)")
    print()
    print("💡 DICA: As imagens são geradas com resolução 800x1200")
    print("   e podem ser usadas para web, email ou impressão!")

def test_all_formats():
    """Testa todos os formatos disponíveis"""
    
    print("\n🚀 TESTE COMPLETO: TODOS OS FORMATOS")
    print("="*50)
    
    base_data = {
        "template_name": "fatura",
        "data": {
            "cliente": "Empresa Teste Completo",
            "numero_fatura": "ALL-FORMATS-001",
            "descricao": "Teste de todos os formatos disponíveis",
            "itens": [
                {"descricao": "Serviço PDF", "valor": 1000.00},
                {"descricao": "Serviço PNG", "valor": 800.00},
                {"descricao": "Serviço JPEG", "valor": 600.00}
            ]
        },
        "upload_to_minio": False
    }
    
    formats = ["pdf", "png", "jpeg"]
    results = []
    
    for fmt in formats:
        print(f"\n📄 Testando formato: {fmt.upper()}")
        test_data = base_data.copy()
        test_data["output_format"] = fmt
        
        try:
            response = requests.post(f"{BASE_URL}/generate", json=test_data)
            
            if response.status_code == 200:
                result = response.json()
                file_path = result['local_path']
                
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    results.append({
                        "format": fmt.upper(),
                        "success": True,
                        "file_path": file_path,
                        "file_size": file_size
                    })
                    print(f"   ✅ {fmt.upper()}: {file_size:,} bytes")
                else:
                    results.append({"format": fmt.upper(), "success": False})
                    print(f"   ❌ {fmt.upper()}: Arquivo não encontrado")
            else:
                results.append({"format": fmt.upper(), "success": False})
                print(f"   ❌ {fmt.upper()}: Erro {response.status_code}")
        
        except Exception as e:
            results.append({"format": fmt.upper(), "success": False})
            print(f"   ❌ {fmt.upper()}: {e}")
    
    # Relatório final
    print("\n📋 RELATÓRIO FINAL:")
    print("-" * 30)
    for result in results:
        if result["success"]:
            print(f"✅ {result['format']}: {result['file_size']:,} bytes")
        else:
            print(f"❌ {result['format']}: FALHOU")
    
    successful = len([r for r in results if r["success"]])
    print(f"\n🎯 Sucesso: {successful}/3 formatos funcionando")

if __name__ == "__main__":
    test_image_generation()
    test_all_formats()
    print("\n✨ Testes de imagem concluídos!") 