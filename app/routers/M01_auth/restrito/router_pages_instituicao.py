"""
Páginas restritas (pós-login) - Gerenciamento de Instituição
"""

from datetime import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from app.schemas.M01_auth.schema_auth import AuthenticatedUser
from app.utils.auth_session import require_authenticated_user


templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Área Restrita | Instituição"])


@router.get("/pessoa-juridica")
async def pessoa_juridica_page(
    request: Request, user: AuthenticatedUser = Depends(require_authenticated_user)
):
    return templates.TemplateResponse(
        "pages/M01_auth/app/template_pessoa_juridica_pagina.html",
        {
            "request": request,
            "title": "Pessoa Jurídica | SIGMA-PLI",
            "user": user,
            "year": datetime.utcnow().year,
        },
    )
