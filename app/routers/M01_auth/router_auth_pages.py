"""Rotas que servem as páginas (templates) do módulo M01_auth.

Inclui rotas públicas (login/recuperar/cadastro) e rotas da área administrativa
do módulo (dashboard-related pages) que requerem autenticação.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.schemas.M01_auth.schema_auth import AuthenticatedUser
from app.utils.auth_session import require_authenticated_user


templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/auth/login")
async def auth_login_page(request: Request):
    """Página pública de login."""
    return templates.TemplateResponse(
        "pages/M01_auth/template_auth_login_pagina.html",
        {
            "request": request,
            "title": "SIGMA-PLI | Autenticação",
            "year": datetime.utcnow().year,
        },
    )


@router.get("/login")
async def login_alias(request: Request):
    """Alias amigável para a página de login já existente em /auth/login."""
    # redirecionar para a rota canônica
    return templates.TemplateResponse(
        "pages/M01_auth/template_auth_login_pagina.html",
        {
            "request": request,
            "title": "SIGMA-PLI | Autenticação",
            "year": datetime.utcnow().year,
        },
    )


@router.get("/auth")
async def auth_index_page(request: Request):
    """Página inicial do módulo de autenticação (index)."""
    return templates.TemplateResponse(
        "pages/M01_auth/template_auth_index_pagina.html",
        {
            "request": request,
            "title": "SIGMA-PLI | Início",
            "year": datetime.utcnow().year,
        },
    )


@router.get("/auth/index")
async def auth_index_alias(request: Request):
    """Alias para /auth - Página inicial do módulo de autenticação."""
    return templates.TemplateResponse(
        "pages/M01_auth/template_auth_index_pagina.html",
        {
            "request": request,
            "title": "SIGMA-PLI | Início",
            "year": datetime.utcnow().year,
        },
    )


@router.get("/auth/recuperar-senha")
async def recuperar_senha_page(request: Request):
    """Página pública de recuperação de senha."""
    return templates.TemplateResponse(
        "pages/M01_auth/template_auth_recuperar_senha_pagina.html",
        {
            "request": request,
            "title": "Recuperar Senha | SIGMA-PLI",
            "year": datetime.utcnow().year,
        },
    )


@router.get("/auth/logout")
async def logout_page(request: Request) -> RedirectResponse:
    """Executa logout e redireciona para a página de login."""
    redirect = RedirectResponse(
        url="/auth/login",
        status_code=302,
    )
    redirect.delete_cookie("auth_token", path="/")
    return redirect


## removido: páginas públicas de cadastro movidas para app/routers/M01_auth/public


# Rotas de cadastro público movidas para M01_auth/public/*


@router.get("/auth/admin-login")
async def admin_login_page(request: Request):
    """Página de login administrativo."""
    return templates.TemplateResponse(
        "pages/M01_auth/template_auth_admin_login_pagina.html",
        {
            "request": request,
            "title": "Login Admin | SIGMA-PLI",
            "year": datetime.utcnow().year,
        },
    )


@router.get("/auth/sobre")
async def sobre_page(request: Request):
    """Página pública sobre o sistema."""
    return templates.TemplateResponse(
        "pages/M01_auth/template_auth_sobre_pagina.html",
        {
            "request": request,
            "title": "Sobre | SIGMA-PLI",
            "year": datetime.utcnow().year,
        },
    )


# ============================================================================
# PÁGINAS PÚBLICAS STANDALONE (acesso sem autenticação)
# ============================================================================


@router.get("/acesso-negado")
async def acesso_negado_page(request: Request):
    """Página pública de erro 403 - Acesso Negado."""
    return templates.TemplateResponse(
        "pages/M01_auth/public/template_public_acesso_negado_pagina.html",
        {
            "request": request,
            "title": "Acesso Negado | SIGMA-PLI",
            "year": datetime.utcnow().year,
        },
    )


@router.get("/email-verificado")
async def email_verificado_page(request: Request):
    """Página pública de sucesso - Email Verificado."""
    return templates.TemplateResponse(
        "pages/M01_auth/public/template_public_email_verificado_pagina.html",
        {
            "request": request,
            "title": "Email Verificado | SIGMA-PLI",
            "year": datetime.utcnow().year,
        },
    )


@router.get("/selecionar-perfil")
async def selecionar_perfil_page(request: Request):
    """Página pública de seleção de perfil (quando usuário tem múltiplos acessos)."""
    return templates.TemplateResponse(
        "pages/M01_auth/public/template_public_selecionar_perfil_pagina.html",
        {
            "request": request,
            "title": "Selecionar Perfil | SIGMA-PLI",
            "year": datetime.utcnow().year,
        },
    )


@router.get("/recursos")
async def recursos_page(request: Request):
    """Página pública informativa sobre recursos e funcionalidades do sistema."""
    return templates.TemplateResponse(
        "pages/M01_auth/public/template_public_recursos_pagina.html",
        {
            "request": request,
            "title": "Recursos | SIGMA-PLI",
            "year": datetime.utcnow().year,
        },
    )


@router.get("/dashboard")
async def dashboard_page(
    request: Request, user: AuthenticatedUser = Depends(require_authenticated_user)
):
    """Dashboard principal - requer autenticação."""
    return templates.TemplateResponse(
        "pages/M01_auth/app/template_dashboard_pagina.html",
        {
            "request": request,
            "title": "Dashboard | SIGMA-PLI",
            "user": user,
            "year": datetime.utcnow().year,
        },
    )


@router.get("/admin/panel")
async def admin_panel_page(
    request: Request, user: AuthenticatedUser = Depends(require_authenticated_user)
):
    """Painel administrativo - requer autenticação de admin."""
    return templates.TemplateResponse(
        "pages/M01_auth/admin/template_admin_panel_pagina.html",
        {
            "request": request,
            "title": "Painel Admin | SIGMA-PLI",
            "user": user,
            "year": datetime.utcnow().year,
        },
    )


@router.get("/meus-dados")
async def meus_dados_page(
    request: Request, user: AuthenticatedUser = Depends(require_authenticated_user)
):
    return templates.TemplateResponse(
        "pages/M01_auth/app/template_meus_dados_pagina.html",
        {
            "request": request,
            "title": "Meus Dados | SIGMA-PLI",
            "user": user,
            "year": datetime.utcnow().year,
        },
    )


# Página restrita de pessoa física movida para M01_auth/restrito/*


# Página restrita de pessoa jurídica movida para M01_auth/restrito/*


# Página restrita de usuários movida para M01_auth/restrito/*


@router.get("/solicitacoes-cadastro")
async def solicitacoes_cadastro_page(
    request: Request, user: AuthenticatedUser = Depends(require_authenticated_user)
):
    return templates.TemplateResponse(
        "pages/M01_auth/app/template_solicitacoes_cadastro_pagina.html",
        {
            "request": request,
            "title": "Solicitações | SIGMA-PLI",
            "user": user,
            "year": datetime.utcnow().year,
        },
    )


@router.get("/sessions-manager")
async def sessions_manager_page(
    request: Request, user: AuthenticatedUser = Depends(require_authenticated_user)
):
    return templates.TemplateResponse(
        "pages/M01_auth/app/template_sessions_manager_pagina.html",
        {
            "request": request,
            "title": "Sessões | SIGMA-PLI",
            "user": user,
            "year": datetime.utcnow().year,
        },
    )
