"""
SIGMA-PLI - M07: Ferramentas
Router para hub de ferramentas (GeoServer, ETL, etc)
"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/ferramentas")
async def ferramentas_page(request: Request):
    """Página de Ferramentas - Hub de GeoServer, ETL e outras ferramentas"""
    return templates.TemplateResponse(
        "pages/M07_ferramentas/template_ferramentas_hub_pagina.html",
        {
            "request": request,
            "title": "Ferramentas | SIGMA-PLI",
            "description": "Hub de ferramentas: GeoServer, ETL e gerenciamento de dados",
        },
    )
