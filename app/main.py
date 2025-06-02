from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router

app = FastAPI(
    title="API de Geração de Imagens",
    description="API para gerar imagens a partir de templates HTML",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "API de Geração de Imagens",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Olá, {name}!"} 