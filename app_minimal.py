from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    """Endpoint de saúde do sistema"""
    return {
        "status": "healthy",
        "service": "SIGMA-PLI Backend",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Página inicial"""
    return {"message": "SIGMA-PLI API funcionando!"}