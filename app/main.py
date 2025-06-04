from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import os
import tempfile
import asyncio
from datetime import datetime

from .services.document_generator import DocumentGenerator
from .services.minio_service import MinIOService
from .schemas.generate_request import GenerateRequest
from .templates.template_manager import TemplateManager

app = FastAPI(
    title="Document Generator API",
    description="API para geração de documentos PDF e imagens a partir de templates HTML",
    version="1.0.0"
)

# Inicializar serviços
document_generator = DocumentGenerator()
minio_service = MinIOService()
template_manager = TemplateManager()

@app.on_event("startup")
async def startup_event():
    """Inicializar recursos na inicialização da aplicação"""
    await minio_service.ensure_bucket_exists()

@app.get("/")
async def root():
    """Endpoint de health check"""
    return {"message": "Document Generator API está funcionando!"}

@app.get("/templates")
async def list_templates():
    """Lista todos os templates disponíveis"""
    templates = template_manager.list_templates()
    return {"templates": templates}

@app.post("/generate")
async def generate_document(request: GenerateRequest):
    """
    Gera um documento PDF ou imagem a partir de um template HTML
    
    - **template_name**: Nome do template (fatura, certificado)
    - **data**: Dados para preenchimento do template
    - **output_format**: Formato de saída (pdf, png, jpeg)
    - **upload_to_minio**: Se deve fazer upload para o MinIO
    """
    try:
        # Verificar se o template existe
        if not template_manager.template_exists(request.template_name):
            raise HTTPException(
                status_code=404,
                detail=f"Template '{request.template_name}' não encontrado"
            )
        
        # Gerar o documento
        output_path = await document_generator.generate_document(
            template_name=request.template_name,
            data=request.data,
            output_format=request.output_format
        )
        
        result = {
            "success": True,
            "template_name": request.template_name,
            "output_format": request.output_format,
            "generated_at": datetime.now().isoformat(),
            "local_path": output_path
        }
        
        # Upload para MinIO se solicitado
        if request.upload_to_minio:
            try:
                minio_url = await minio_service.upload_file(
                    file_path=output_path,
                    object_name=f"documents/{os.path.basename(output_path)}"
                )
                result["minio_url"] = minio_url
                result["uploaded_to_minio"] = True
            except Exception as e:
                result["upload_error"] = str(e)
                result["uploaded_to_minio"] = False
        else:
            result["uploaded_to_minio"] = False
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar documento: {str(e)}"
        )

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download direto de arquivo gerado"""
    file_path = os.path.join("temp", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
