from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from app.services.document_generator import DocumentGenerator
from app.templates.template_manager import TemplateManager

app = FastAPI(title="Document Generator API")

# Criar diretório temp se não existir
os.makedirs("temp", exist_ok=True)

# Instanciar geradores
document_generator = DocumentGenerator()
template_manager = TemplateManager()

class GenerateRequest(BaseModel):
    template_name: str
    data: Dict[str, Any]
    output_format: str
    upload_to_minio: bool = False

@app.post("/generate")
async def generate_document(request: GenerateRequest):
    try:
        # Validar template
        if not template_manager.template_exists(request.template_name):
            raise HTTPException(status_code=404, detail=f"Template '{request.template_name}' não encontrado")
        
        # Validar dados
        is_valid, errors = template_manager.validate_template_data(request.template_name, request.data)
        if not is_valid:
            raise HTTPException(status_code=400, detail={"message": "Dados inválidos", "errors": errors})
        
        # Gerar documento
        output_path = await document_generator.generate_document(
            template_name=request.template_name,
            data=request.data,
            output_format=request.output_format
        )
        
        return {
            "success": True,
            "template_name": request.template_name,
            "output_format": request.output_format,
            "generated_at": datetime.now().isoformat(),
            "local_path": output_path,
            "uploaded_to_minio": False  # Por enquanto, sem suporte a MinIO
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar documento: {str(e)}")

@app.get("/templates")
async def list_templates():
    """Lista todos os templates disponíveis"""
    try:
        templates = template_manager.list_templates()
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar templates: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 