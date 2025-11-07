"""
SIGMA-PLI - M08: Administração
Router para páginas administrativas (HTML/Templates)
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.middleware.auth_middleware import require_admin, require_admin_or_gestor
from app.schemas.M01_auth.schema_auth import AuthenticatedUser


router = APIRouter(prefix="/admin", tags=["Admin - Páginas"])

# Templates
templates = Jinja2Templates(directory="templates")


@router.get("/panel", response_class=HTMLResponse, summary="Painel Administrativo")
async def admin_panel(
    request: Request, current_user: AuthenticatedUser = Depends(require_admin)
):
    """
    Painel administrativo principal

    **Permissão requerida:** ADMIN (nível 5)

    Renderiza: `templates/pages/M01_auth/admin/template_admin_panel_pagina.html`
    """
    return templates.TemplateResponse(
        "pages/M01_auth/admin/template_admin_panel_pagina.html",
        {
            "request": request,
            "user": current_user,
            "page_title": "Painel Administrativo",
        },
    )


@router.get("/usuarios", response_class=HTMLResponse, summary="Gestão de Usuários")
async def admin_usuarios(
    request: Request, current_user: AuthenticatedUser = Depends(require_admin_or_gestor)
):
    """
    Página de gestão de usuários

    **Permissão requerida:** GESTOR ou ADMIN (nível 4+)

    TODO: Criar template `template_admin_usuarios_pagina.html`
    """
    return templates.TemplateResponse(
        "pages/M01_auth/admin/template_admin_usuarios_pagina.html",
        {"request": request, "user": current_user, "page_title": "Gestão de Usuários"},
    )


@router.get(
    "/solicitacoes-cadastro",
    response_class=HTMLResponse,
    summary="Solicitações de Cadastro",
)
async def admin_solicitacoes(
    request: Request, current_user: AuthenticatedUser = Depends(require_admin_or_gestor)
):
    """
    Página de aprovação de solicitações de cadastro

    **Permissão requerida:** GESTOR ou ADMIN (nível 4+)

    TODO: Criar template `template_admin_solicitacoes_pagina.html`
    """
    return templates.TemplateResponse(
        "pages/M01_auth/admin/template_admin_solicitacoes_pagina.html",
        {
            "request": request,
            "user": current_user,
            "page_title": "Solicitações de Cadastro",
        },
    )


@router.get(
    "/sessions-manager", response_class=HTMLResponse, summary="Gerenciador de Sessões"
)
async def admin_sessions(
    request: Request, current_user: AuthenticatedUser = Depends(require_admin)
):
    """
    Página de gerenciamento de sessões ativas

    **Permissão requerida:** ADMIN (nível 5)

    TODO: Criar template `template_admin_sessions_pagina.html`
    """
    return templates.TemplateResponse(
        "pages/M01_auth/admin/template_admin_sessions_pagina.html",
        {
            "request": request,
            "user": current_user,
            "page_title": "Gerenciador de Sessões",
        },
    )
