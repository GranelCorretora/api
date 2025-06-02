from pydantic import BaseModel, EmailStr
from typing import Optional

class BusinessCardTemplate(BaseModel):
    nome_empresa: str
    nome_pessoa: str
    cargo: str
    telefone: str
    email: str

class ProductAdTemplate(BaseModel):
    nome_produto: str
    url_imagem_produto: str
    preco: str
    descricao_curta: str

class EventInviteTemplate(BaseModel):
    cor_fundo: str
    cor_texto: str
    titulo_evento: str
    data_evento: str
    local_evento: str
    mensagem_adicional: str

class ImageResponse(BaseModel):
    imageUrl: str 