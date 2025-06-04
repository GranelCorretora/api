# API de Geração de Documentos

## Descrição

Esta API permite gerar documentos PDF e imagens (PNG/JPEG) a partir de templates HTML. Inclui integração com MinIO para armazenamento de arquivos.

## Funcionalidades

- ✅ Geração de PDFs e imagens a partir de templates HTML
- ✅ Templates prontos: Fatura e Certificado
- ✅ Integração com MinIO para armazenamento
- ✅ API RESTful com FastAPI
- ✅ Documentação automática com Swagger
- ✅ Validação de dados com Pydantic

## Instalação

### 1. Instalar dependências Python

```bash
pip install -r requirements.txt
```

### 2. Instalar dependências do sistema (para WeasyPrint)

#### Ubuntu/Debian:
```bash
sudo apt-get install python3-dev python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
```

#### macOS:
```bash
brew install pango
```

#### Windows:
Siga as instruções em: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows

### 3. Instalar Poppler (para conversão PDF → Imagem)

#### Ubuntu/Debian:
```bash
sudo apt-get install poppler-utils
```

#### macOS:
```bash
brew install poppler
```

#### Windows:
1. Baixe o Poppler: https://poppler.freedesktop.org/
2. Adicione ao PATH do sistema

## Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` com as seguintes configurações:

```env
# Configurações do MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=documents
MINIO_SECURE=False

# Configurações da API
API_HOST=0.0.0.0
API_PORT=8000
```

### MinIO (Opcional)

Se você quiser usar o MinIO local para testes:

```bash
# Usando Docker
docker run -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio server /data --console-address ":9001"
```

## Execução

```bash
# Executar a API
python app/main.py

# Ou usando uvicorn diretamente
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

A API estará disponível em: http://localhost:8000

## Documentação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### GET /
Health check da API

### GET /templates
Lista todos os templates disponíveis

**Resposta:**
```json
{
  "templates": [
    {
      "id": "fatura",
      "name": "Fatura",
      "description": "Template para geração de faturas com itens dinâmicos",
      "required_fields": ["cliente", "itens"],
      "optional_fields": ["descricao", "valor", "data_atual", "numero_fatura"],
      "example_data": { ... }
    }
  ]
}
```

### POST /generate
Gera um documento a partir de um template

**Parâmetros:**
- `template_name`: Nome do template (fatura, certificado)
- `data`: Dados para preenchimento
- `output_format`: Formato de saída (pdf, png, jpeg)
- `upload_to_minio`: Se deve fazer upload para MinIO

**Exemplo de requisição - Fatura:**
```json
{
  "template_name": "fatura",
  "data": {
    "cliente": "João Silva",
    "numero_fatura": "FAT-2024-001",
    "descricao": "Serviços de consultoria",
    "valor": 1500.00,
    "itens": [
      {"descricao": "Consultoria técnica", "valor": 1000.00},
      {"descricao": "Documentação", "valor": 500.00}
    ]
  },
  "output_format": "pdf",
  "upload_to_minio": true
}
```

**Exemplo de requisição - Certificado:**
```json
{
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
  "upload_to_minio": false
}
```

**Resposta:**
```json
{
  "success": true,
  "template_name": "fatura",
  "output_format": "pdf",
  "generated_at": "2024-12-15T10:30:00",
  "local_path": "/path/to/generated/file.pdf",
  "uploaded_to_minio": true,
  "minio_url": "https://minio.example.com/documents/file.pdf"
}
```

### GET /download/{filename}
Download direto de arquivo gerado

## Templates Disponíveis

### 1. Fatura (`fatura`)

**Campos obrigatórios:**
- `cliente`: Nome do cliente
- `itens`: Lista de itens da fatura
  - `descricao`: Descrição do item
  - `valor`: Valor do item

**Campos opcionais:**
- `numero_fatura`: Número da fatura
- `descricao`: Descrição geral dos serviços
- `valor`: Valor total (calculado automaticamente se não fornecido)
- `data_atual`: Data da fatura (data atual se não fornecida)

### 2. Certificado (`certificado`)

**Campos obrigatórios:**
- `participante`: Nome do participante
- `curso`: Nome do curso

**Campos opcionais:**
- `instrutor`: Nome do instrutor
- `data_conclusao`: Data de conclusão
- `endereco`: Endereço do local (para gerar mapa)
- `latitude`: Latitude (alternativa ao endereço)
- `longitude`: Longitude (alternativa ao endereço)
- `carga_horaria`: Carga horária do curso

## Estrutura do Projeto

```
app/
├── main.py                      # Arquivo principal da API
├── schemas/
│   └── generate_request.py      # Schemas Pydantic
├── services/
│   ├── document_generator.py    # Geração de documentos
│   └── minio_service.py         # Integração com MinIO
├── templates/
│   ├── template_manager.py      # Gerenciamento de templates
│   └── html/
│       ├── fatura.html          # Template de fatura
│       └── certificado.html     # Template de certificado
temp/                            # Arquivos temporários gerados
```

## Exemplos de Teste

### Teste com curl

```bash
# Gerar fatura em PDF
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "fatura",
    "data": {
      "cliente": "João Silva",
      "itens": [
        {"descricao": "Consultoria", "valor": 1000.00},
        {"descricao": "Desenvolvimento", "valor": 500.00}
      ]
    },
    "output_format": "pdf",
    "upload_to_minio": false
  }'
```

### Teste com Python

```python
import requests

# Dados para fatura
data = {
    "template_name": "fatura",
    "data": {
        "cliente": "João Silva",
        "numero_fatura": "FAT-2024-001",
        "itens": [
            {"descricao": "Consultoria técnica", "valor": 1000.00},
            {"descricao": "Documentação", "valor": 500.00}
        ]
    },
    "output_format": "pdf",
    "upload_to_minio": False
}

response = requests.post("http://localhost:8000/generate", json=data)
print(response.json())
```

## Personalização

### Adicionando Novos Templates

1. Crie um arquivo HTML em `app/templates/html/`
2. Adicione a configuração em `app/templates/template_manager.py`
3. Implemente lógica específica em `app/services/document_generator.py` se necessário

### Configurando Mapa Real

Para usar mapas reais no certificado, substitua a função `_generate_static_map` em `DocumentGenerator` por uma integração com:
- Google Maps Static API
- Mapbox Static Images API
- OpenStreetMap

## Troubleshooting

### Erro ao gerar PDF
- Verifique se todas as dependências do WeasyPrint estão instaladas
- No Windows, certifique-se de que o GTK+ está instalado

### Erro ao converter PDF para imagem
- Verifique se o Poppler está instalado e no PATH
- No Windows, baixe o Poppler e adicione ao PATH

### Erro de conexão com MinIO
- Verifique se o MinIO está rodando
- Confirme as credenciais nas variáveis de ambiente
- Teste a conectividade manualmente

## Licença

Este projeto é fornecido como exemplo educacional. 