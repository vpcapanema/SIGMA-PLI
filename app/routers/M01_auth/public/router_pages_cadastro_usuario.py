"""
Páginas públicas - Cadastro de Usuário
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field, AliasChoices

from app.utils.normalizers import normalize_usuario_payload
from app.services.M01_auth.service_auth import AuthService

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Páginas Públicas | Usuário"])


# Schemas
class UsuarioCreate(BaseModel):
    """Schema de criação de usuário"""

    # IDs de vinculação
    pessoa_fisica_id: str = Field(
        validation_alias=AliasChoices("pessoa_fisica_id", "pessoa_id")
    )
    instituicao_id: str

    # Dados profissionais
    email_institucional: EmailStr = Field(
        validation_alias=AliasChoices("email_institucional", "email")
    )
    telefone_institucional: Optional[str] = None
    cargo: Optional[str] = None

    # Dados de acesso
    tipo_usuario: str  # ADMIN, GESTOR, ANALISTA, OPERADOR, VISUALIZADOR
    username: str
    senha: str = Field(validation_alias=AliasChoices("senha", "password"))

    # Termos
    termo_privacidade: bool
    termo_uso: bool


class CadastroResponse(BaseModel):
    """Response de cadastro"""

    success: bool
    message: str


# Endpoints
@router.get("/auth/cadastro-usuario")
async def cadastro_usuario_page(request: Request):
    """Página de cadastro de usuário"""
    return templates.TemplateResponse(
        "pages/M01_auth/template_auth_cadastro_usuario_pagina.html",
        {
            "request": request,
            "title": "Cadastro de Usuário | SIGMA-PLI",
            "year": datetime.utcnow().year,
        },
    )


@router.get("/auth/registrar-se")
async def registrar_se_page(request: Request):
    """Alias para página de cadastro de usuário"""
    return templates.TemplateResponse(
        "pages/M01_auth/template_auth_cadastro_usuario_pagina.html",
        {
            "request": request,
            "title": "Cadastro de Usuário | SIGMA-PLI",
            "year": datetime.utcnow().year,
        },
    )


@router.post("/api/cadastro/usuario", response_model=CadastroResponse)
async def cadastrar_usuario(data: UsuarioCreate):
    """
    Endpoint de registro de novo usuário

    Valida IDs de pessoa física e instituição, verifica duplicatas de email e username,
    e cria novo usuário no banco de dados.

    Args:
        data: Dados de cadastro do usuário

    Returns:
        CadastroResponse com sucesso e mensagem
    """
    # Normalizar payload recebido (aceita aliases)
    raw = data.model_dump(exclude_none=True)
    norm = normalize_usuario_payload(raw)

    # Validar presença explícita dos IDs obrigatórios
    if not norm.get("pessoa_id") or not norm.get("instituicao_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Campos obrigatórios ausentes: pessoa_fisica_id e instituicao_id "
                "devem ser informados."
            ),
        )

    # Validar termos
    if not data.termo_privacidade or not data.termo_uso:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="É necessário aceitar os termos de uso e política de privacidade",
        )

    # Validar tipo de usuário
    tipos_validos = ["ADMIN", "GESTOR", "ANALISTA", "OPERADOR", "VISUALIZADOR"]
    if norm.get("tipo_usuario") not in tipos_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de usuário inválido. Valores aceitos: {', '.join(tipos_validos)}",
        )

    try:
        success, message = await AuthService.register_user(
            username=str(norm.get("username") or ""),
            senha=str(norm.get("senha") or ""),
            pessoa_id=str(norm.get("pessoa_id") or ""),
            instituicao_id=str(norm.get("instituicao_id") or ""),
            tipo_usuario=str(norm.get("tipo_usuario") or ""),
            email_institucional=str(norm.get("email_institucional") or ""),
            telefone_institucional=norm.get("telefone_institucional"),
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        return CadastroResponse(
            success=True,
            message=message,
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar usuário: {str(e)}",
        )
