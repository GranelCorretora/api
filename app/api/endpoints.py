from fastapi import APIRouter, HTTPException, Depends
from app.schemas.templates import BusinessCardTemplate, ProductAdTemplate, EventInviteTemplate, ImageResponse
from app.services.template_service import template_service
from app.services.minio_service import minio_service
from typing import Union
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/gerar-imagem/{template_id}", response_model=ImageResponse)
async def gerar_imagem(
    template_id: int,
    data: Union[BusinessCardTemplate, ProductAdTemplate, EventInviteTemplate]
):
    try:
        # Validate template ID
        if template_id not in [1, 2, 3]:
            raise HTTPException(status_code=404, detail="Template não encontrado")

        # Generate image from template
        image_data = await template_service.render_template(template_id, data.dict())

        # Upload to MinIO
        image_url = minio_service.upload_image(image_data)

        return ImageResponse(imageUrl=image_url)

    except Exception as e:
        # Ensure cleanup in case of error
        template_service.cleanup()
        raise HTTPException(status_code=500, detail=str(e))

@router.on_event("shutdown")
def shutdown_event():
    """Cleanup WebDriver resources on application shutdown"""
    template_service.cleanup() 