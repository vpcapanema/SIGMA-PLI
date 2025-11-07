from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import graph

app = FastAPI(
    title="SIGMA-PLI API",
    description="API do Sistema de Governança e Metadados para PLI",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(graph.router)

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API do SIGMA-PLI"}

@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}
