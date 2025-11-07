from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Inicializar FastAPI
app = FastAPI(
    title="SIGMA-PLI API",
    description="Sistema de Gestão de Metadados e Repositório Interativo",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    """Página inicial"""
    return templates.TemplateResponse("pages/M00_home/template_home_index_pagina.html", {
        "request": request,
        "title": "SIGMA-PLI - Sistema de Gestão de Metadados",
        "description": "Sistema de Gestão de Metadados e Repositório Interativo para PLI"
    })

@app.get("/health")
async def health_check():
    """Endpoint de saúde do sistema"""
    return {
        "status": "healthy",
        "service": "SIGMA-PLI Backend",
        "version": "1.0.0"
    }