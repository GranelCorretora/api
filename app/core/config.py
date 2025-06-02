# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict # MODIFICADO AQUI
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv() # Você já está carregando as variáveis do .env aqui, o que é bom.

class Settings(BaseSettings):
    # MinIO Settings
    # Seus campos permanecem os mesmos, usando os.getenv com padrões
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "MZNXR4TRAanC9DKg0MrTr")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "Uz9ThwJoZYE5wVTe4i8daNrY0L0Lx6FaVJsdDmB")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "imagens-geradas")
    MINIO_USE_SSL: bool = os.getenv("MINIO_USE_SSL", "false").lower() == "true"

    # MODIFICADO AQUI: A classe interna 'Config' foi substituída por 'model_config'
    model_config = SettingsConfigDict(case_sensitive=True)

@lru_cache()
def get_settings():
    return Settings()