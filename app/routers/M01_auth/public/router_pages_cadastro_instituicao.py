"""
Páginas e APIs públicas - Cadastro de Instituição (Pessoa Jurídica)
"""

from typing import Optional
from datetime import datetime, date
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field

from app.services.M01_auth.service_pessoa import PessoaService
from app.utils.normalizers import normalize_instituicao_payload

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Páginas Públicas | Instituição"])


# Schemas
class InstituicaoCreate(BaseModel):
    """Schema para criação de Instituição (empresas, órgãos públicos, autarquias, fundações)"""

    # Dados da Instituição
    razao_social: str = Field(
        ..., min_length=3, max_length=255, description="Razão social da instituição"
    )
    cnpj: str = Field(..., min_length=14, max_length=18)
    email: EmailStr
    nome_fantasia: Optional[str] = Field(
        None, max_length=255, description="Nome fantasia"
    )
    tipo_instituicao: Optional[str] = Field(
        None,
        max_length=100,
        description="Ex: Empresa Privada, Órgão Público, Autarquia, Fundação",
    )
    esfera_administrativa: Optional[str] = Field(
        None, max_length=50, description="Federal, Estadual, Municipal (se aplicável)"
    )
    inscricao_estadual: Optional[str] = Field(None, max_length=20)
    inscricao_municipal: Optional[str] = Field(None, max_length=20)
    data_fundacao: Optional[date] = None
    porte_empresa: Optional[str] = Field(
        None, description="Micro, Pequena, Média, Grande"
    )
    natureza_juridica: Optional[str] = Field(None, max_length=100)
    atividade_principal: Optional[str] = Field(None, max_length=255)

    # Contato
    telefone: Optional[str] = Field(None, max_length=20)
    telefone_secundario: Optional[str] = Field(None, max_length=20)
    email_secundario: Optional[EmailStr] = None
    site: Optional[str] = Field(None, max_length=255)

    # Endereço
    cep: Optional[str] = Field(None, max_length=10)
    logradouro: Optional[str] = Field(None, max_length=255)
    numero: Optional[str] = Field(None, max_length=20)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    uf: Optional[str] = Field(None, max_length=2)
    pais: Optional[str] = "Brasil"


class CadastroResponse(BaseModel):
    """Response de criação de instituição"""

    success: bool
    message: str
    pessoa_id: str


@router.get("/auth/cadastro-pessoa-juridica")
async def cadastro_instituicao_page(request: Request):
    return templates.TemplateResponse(
        "pages/M01_auth/template_auth_cadastro_instituicao_pagina.html",
        {
            "request": request,
            "title": "Cadastro de Instituição | SIGMA-PLI",
            "year": datetime.utcnow().year,
        },
    )


@router.get("/auth/cadastro-instituicao")
async def cadastro_instituicao_alias(request: Request):
    return templates.TemplateResponse(
        "pages/M01_auth/template_auth_cadastro_instituicao_pagina.html",
        {
            "request": request,
            "title": "Cadastro de Instituição | SIGMA-PLI",
            "year": datetime.utcnow().year,
        },
    )


# API Endpoints
@router.post("/api/cadastro/instituicao", response_model=CadastroResponse)
async def cadastrar_instituicao(data: InstituicaoCreate):
    """
    Cadastrar Instituição (empresas, órgãos públicos, autarquias, fundações, etc.)

    Args:
        data: Dados da instituição

    Returns:
        CadastroResponse com ID da instituição criada
    """
    # Verificar se CNPJ já existe
    existing = await PessoaService.get_pessoa_by_cnpj(data.cnpj)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ já cadastrado no sistema",
        )

    # Verificar se email já existe
    existing_email = await PessoaService.get_pessoa_by_email(data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado no sistema",
        )

    try:
        # Normalizar payload (aceita variações camelCase se vierem do front)
        norm = normalize_instituicao_payload(data.model_dump())

        pessoa_id = await PessoaService.create_instituicao(
            razao_social=str(norm.get("razao_social") or "").strip(),
            cnpj=str(norm.get("cnpj") or "").strip(),
            email=str(norm.get("email") or "").strip(),
            nome_fantasia=norm.get("nome_fantasia"),
            tipo_instituicao=norm.get("tipo_instituicao"),
            esfera_administrativa=norm.get("esfera_administrativa"),
            inscricao_estadual=norm.get("inscricao_estadual"),
            inscricao_municipal=norm.get("inscricao_municipal"),
            data_fundacao=norm.get("data_fundacao"),
            porte_empresa=norm.get("porte_empresa"),
            natureza_juridica=norm.get("natureza_juridica"),
            atividade_principal=norm.get("atividade_principal"),
            telefone=norm.get("telefone"),
            telefone_secundario=norm.get("telefone_secundario"),
            email_secundario=norm.get("email_secundario"),
            site=norm.get("site"),
            cep=norm.get("cep"),
            logradouro=norm.get("logradouro"),
            numero=norm.get("numero"),
            complemento=norm.get("complemento"),
            bairro=norm.get("bairro"),
            cidade=norm.get("cidade"),
            uf=norm.get("uf"),
            pais=norm.get("pais"),
        )

        return CadastroResponse(
            success=True,
            message="Instituição cadastrada com sucesso",
            pessoa_id=str(pessoa_id),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cadastrar instituição: {str(e)}",
        )
