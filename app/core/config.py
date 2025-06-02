# app/core/config.py
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "MZNXR4TRAanC9DKg0MrTr")
        self.MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "Uz9ThwJoZYE5wVTe4i8daNrY0L0Lx6FaVJsdDmB")
        self.MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "imagens-geradas")
        self.MINIO_USE_SSL = os.getenv("MINIO_USE_SSL", "false").lower() == "true"

@lru_cache()
def get_settings() -> Settings:
    return Settings()