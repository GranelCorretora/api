# API de Geração de Imagens com Templates

Esta API permite gerar imagens a partir de templates HTML predefinidos e fazer upload para o MinIO.

## Requisitos

- Python 3.7+
- pip (gerenciador de pacotes Python)
- wkhtmltopdf (necessário para o imgkit)
- MinIO Server

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Instale o wkhtmltopdf:
- Windows: Baixe e instale do site oficial: https://wkhtmltopdf.org/downloads.html
- Linux: `sudo apt-get install wkhtmltopdf`
- Mac: `brew install wkhtmltopdf`

6. Configure as variáveis de ambiente no arquivo `.env`:
```env
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=seu_access_key
MINIO_SECRET_KEY=seu_secret_key
MINIO_BUCKET_NAME=imagens-geradas
MINIO_USE_SSL=false
```

## Como Executar

1. Inicie o servidor MinIO (em um terminal separado)

2. Para iniciar a API:
```bash
uvicorn main:app --reload
```

3. Acesse a documentação da API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints Disponíveis

### POST /api/v1/gerar-imagem/{template_id}

Gera uma imagem a partir de um template e faz upload para o MinIO.

Templates disponíveis:

1. Cartão de Visita
```json
{
    "nome_empresa": "Empresa Exemplo",
    "nome_pessoa": "João Silva",
    "cargo": "Desenvolvedor",
    "telefone": "(11) 98765-4321",
    "email": "joao@exemplo.com"
}
```

2. Anúncio de Produto
```json
{
    "nome_produto": "Produto Incrível",
    "url_imagem_produto": "https://exemplo.com/imagem.jpg",
    "preco": "99,90",
    "descricao_curta": "O melhor produto do mercado!"
}
```

3. Convite para Evento
```json
{
    "cor_fundo": "#2c3e50",
    "cor_texto": "#ffffff",
    "titulo_evento": "Grande Evento",
    "data_evento": "01/01/2024",
    "local_evento": "Local do Evento",
    "mensagem_adicional": "Não perca este evento incrível!"
}
```

## Resposta

A API retorna a URL da imagem gerada no MinIO:

```json
{
    "imageUrl": "http://localhost:9000/imagens-geradas/nome-do-arquivo.png"
}
``` 