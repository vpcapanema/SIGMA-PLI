"""
SIGMA-PLI - M07: Ferramentas Avançadas
Router para hub de aplicações e ferramentas
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def ferramentas_hub(request: Request):
    """Hub de ferramentas e aplicações"""
    return templates.TemplateResponse(
        "pages/M07_ferramentas/template_ferramentas_hub_pagina.html",
        {
            "request": request,
            "title": "Ferramentas & Aplicações - SIGMA-PLI"
        }
    )
