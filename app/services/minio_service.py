from minio import Minio
from minio.error import S3Error
from app.core.config import get_settings
import uuid

settings = get_settings()

class MinioService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Ensure the configured bucket exists, create if it doesn't"""
        try:
            if not self.client.bucket_exists(settings.MINIO_BUCKET_NAME):
                self.client.make_bucket(settings.MINIO_BUCKET_NAME)
        except S3Error as e:
            raise Exception(f"Failed to create/check bucket: {str(e)}")

    def upload_image(self, image_data: bytes, content_type: str = "image/png") -> str:
        """Upload an image to MinIO and return its URL"""
        try:
            # Generate a unique filename
            filename = f"{uuid.uuid4()}.png"
            
            # Upload the image
            self.client.put_object(
                bucket_name=settings.MINIO_BUCKET_NAME,
                object_name=filename,
                data=image_data,
                length=len(image_data),
                content_type=content_type
            )

            # Generate URL
            url = f"http{'s' if settings.MINIO_USE_SSL else ''}://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{filename}"
            return url

        except S3Error as e:
            raise Exception(f"Failed to upload image: {str(e)}")

# Create a singleton instance
minio_service = MinioService() 