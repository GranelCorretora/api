from pydantic import BaseModel, Field
from typing import Dict, Any, Literal, Optional

class GenerateRequest(BaseModel):
    template_name: str = Field(
        ..., 
        description="Nome do template (fatura, certificado)",
        example="fatura"
    )
    data: Dict[str, Any] = Field(
        ..., 
        description="Dados para preenchimento do template",
        example={
            "cliente": "João Silva",
            "descricao": "Serviços de consultoria",
            "valor": 1500.00,
            "itens": [
                {"descricao": "Consultoria técnica", "valor": 1000.00},
                {"descricao": "Documentação", "valor": 500.00}
            ]
        }
    )
    output_format: Literal["pdf", "png", "jpeg"] = Field(
        default="pdf",
        description="Formato de saída do documento"
    )
    upload_to_minio: bool = Field(
        default=False,
        description="Se deve fazer upload do arquivo para o MinIO"
    )

class GenerateResponse(BaseModel):
    success: bool
    template_name: str
    output_format: str
    generated_at: str
    local_path: str
    uploaded_to_minio: bool
    minio_url: Optional[str] = None
    upload_error: Optional[str] = None 