"""SIGMA-PLI - M02: Dashboard principal."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.schemas.M01_auth.schema_auth import AuthenticatedUser
from app.utils.auth_session import (
    require_active_session,
    require_authenticated_user,
)


templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/dashboard")
async def dashboard_page(
    request: Request,
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    """Renderiza página inicial do dashboard."""

    return templates.TemplateResponse(
        "pages/M02_dashboard/template_dashboard_index_pagina.html",
        {
            "request": request,
            "title": "SIGMA-PLI | Dashboard",
            "user": user,
            "year": datetime.utcnow().year,
        },
    )


@router.get("/api/v1/dashboard/session")
async def dashboard_session(
    session=Depends(require_active_session),
) -> JSONResponse:
    """Retorna informações resumidas da sessão atual."""

    return JSONResponse(
        {
            "session_id": session.session_id,
            "expires_at": session.expires_at.isoformat(),
        }
    )
