from fastapi import APIRouter, HTTPException, Depends
from app.schemas.templates import BusinessCardTemplate, ProductAdTemplate, EventInviteTemplate, ImageResponse
from app.services.template_service import template_service
from app.services.minio_service import minio_service
from typing import Union, Dict, Any
from fastapi.responses import JSONResponse
from pydantic import create_model, BaseModel
import re

router = APIRouter()

def create_dynamic_model(template_name: str) -> BaseModel:
    """Create a Pydantic model dynamically based on template variables"""
    template_content = template_service.templates[template_name]
    
    # Extract variables from template using regex
    variables = set(re.findall(r'\{\{(\w+)\}\}', template_content))
    
    # Create field definitions (all as string type for simplicity)
    fields = {var: (str, ...) for var in variables}
    
    # Create and return the model
    return create_model(f'{template_name.title()}Template', **fields)

@router.get("/templates", response_model=list[str])
async def list_templates():
    """List all available templates"""
    return template_service.get_available_templates()

@router.post("/gerar-imagem/{template_name}", response_model=ImageResponse)
async def gerar_imagem(
    template_name: str,
    data: Dict[str, Any]
):
    try:
        # Check if template exists
        if template_name not in template_service.templates:
            raise HTTPException(
                status_code=404,
                detail=f"Template '{template_name}' não encontrado. Templates disponíveis: {', '.join(template_service.get_available_templates())}"
            )

        # Create dynamic model for the template
        TemplateModel = create_dynamic_model(template_name)
        
        try:
            # Validate data against the dynamic model
            validated_data = TemplateModel(**data)
        except Exception as validation_error:
            raise HTTPException(
                status_code=400,
                detail=f"Dados inválidos para o template '{template_name}'. Erro: {str(validation_error)}"
            )

        # Generate image from template
        image_data = await template_service.render_template(template_name, validated_data.dict())

        # Upload to MinIO
        image_url = minio_service.upload_image(image_data)

        return ImageResponse(imageUrl=image_url)

    except Exception as e:
        # Ensure cleanup in case of error
        template_service.cleanup()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.on_event("shutdown")
def shutdown_event():
    """Cleanup WebDriver resources on application shutdown"""
    template_service.cleanup() 