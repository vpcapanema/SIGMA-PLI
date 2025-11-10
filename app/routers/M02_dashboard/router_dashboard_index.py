"""
SIGMA-PLI - M02: Dashboard
Router para painel inicial do usuário com sessão e atalhos
"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard")
async def dashboard_page(request: Request):
    """Página do Dashboard - Painel inicial do usuário"""
    return templates.TemplateResponse(
        "pages/M02_dashboard/template_dashboard_index_pagina.html",
        {
            "request": request,
            "title": "Dashboard | SIGMA-PLI",
            "description": "Painel inicial com sessão e atalhos personalizados",
        },
    )
