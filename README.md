# Projeto FastAPI

Este é um projeto básico usando FastAPI.

## Requisitos

- Python 3.7+
- pip (gerenciador de pacotes Python)

## Instalação

1. Instale as dependências do projeto:
```bash
pip install -r requirements.txt
```

## Como Executar

1. Para iniciar o servidor:
```bash
uvicorn main:app --reload
```

2. Acesse a API:
- Interface Swagger UI: http://localhost:8000/docs
- Interface ReDoc: http://localhost:8000/redoc
- Endpoint principal: http://localhost:8000/
- Endpoint de exemplo: http://localhost:8000/hello/seu-nome

## Endpoints Disponíveis

- `GET /`: Retorna uma mensagem de boas-vindas
- `GET /hello/{name}`: Retorna uma saudação personalizada com o nome fornecido 