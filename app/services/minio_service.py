from minio import Minio
from minio.error import S3Error
import os
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

class MinIOService:
    def __init__(self):
        # Configurações do MinIO (podem ser definidas via variáveis de ambiente)
        self.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME", "documents")
        self.secure = os.getenv("MINIO_SECURE", "False").lower() == "true"
        
        # Inicializar cliente MinIO
        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )
        
        # Executor para operações síncronas
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def ensure_bucket_exists(self) -> bool:
        """Garante que o bucket existe, criando se necessário"""
        try:
            def _check_bucket():
                if not self.client.bucket_exists(self.bucket_name):
                    self.client.make_bucket(self.bucket_name)
                    return True
                return False
            
            # Executar em thread separada
            loop = asyncio.get_event_loop()
            created = await loop.run_in_executor(self.executor, _check_bucket)
            
            if created:
                print(f"Bucket '{self.bucket_name}' criado com sucesso")
            else:
                print(f"Bucket '{self.bucket_name}' já existe")
            
            return True
            
        except S3Error as e:
            print(f"Erro ao verificar/criar bucket: {e}")
            return False
    
    async def upload_file(self, file_path: str, object_name: str) -> str:
        """
        Faz upload de um arquivo para o MinIO
        
        Args:
            file_path: Caminho local do arquivo
            object_name: Nome do objeto no MinIO
            
        Returns:
            URL do arquivo no MinIO
        """
        try:
            def _upload():
                # Fazer upload do arquivo
                self.client.fput_object(
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    file_path=file_path
                )
                
                # Gerar URL pressinada (válida por 7 dias)
                from datetime import timedelta
                url = self.client.presigned_get_object(
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    expires=timedelta(days=7)
                )
                return url
            
            # Executar em thread separada
            loop = asyncio.get_event_loop()
            url = await loop.run_in_executor(self.executor, _upload)
            
            print(f"Arquivo '{file_path}' enviado para MinIO como '{object_name}'")
            return url
            
        except S3Error as e:
            raise Exception(f"Erro ao fazer upload para MinIO: {e}")
    
    async def delete_file(self, object_name: str) -> bool:
        """Remove um arquivo do MinIO"""
        try:
            def _delete():
                self.client.remove_object(
                    bucket_name=self.bucket_name,
                    object_name=object_name
                )
                return True
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self.executor, _delete)
            
            print(f"Arquivo '{object_name}' removido do MinIO")
            return result
            
        except S3Error as e:
            print(f"Erro ao remover arquivo do MinIO: {e}")
            return False
    
    async def list_files(self, prefix: str = "") -> list:
        """Lista arquivos no bucket"""
        try:
            def _list():
                objects = self.client.list_objects(
                    bucket_name=self.bucket_name,
                    prefix=prefix,
                    recursive=True
                )
                return [obj.object_name for obj in objects]
            
            loop = asyncio.get_event_loop()
            files = await loop.run_in_executor(self.executor, _list)
            return files
            
        except S3Error as e:
            print(f"Erro ao listar arquivos do MinIO: {e}")
            return []
    
    def get_public_url(self, object_name: str) -> Optional[str]:
        """Gera URL pública para um objeto (se o bucket for público)"""
        try:
            if self.secure:
                protocol = "https"
            else:
                protocol = "http"
            
            return f"{protocol}://{self.endpoint}/{self.bucket_name}/{object_name}"
        except Exception as e:
            print(f"Erro ao gerar URL pública: {e}")
            return None 