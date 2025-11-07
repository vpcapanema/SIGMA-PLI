"""
Páginas e APIs públicas - Cadastro de Pessoa Física
"""

from typing import Optional
from datetime import datetime, date
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field

from app.services.M01_auth.service_pessoa import PessoaService

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Páginas Públicas | Pessoa Física"])


# Schemas
class PessoaFisicaCreate(BaseModel):
    """Schema para criação de Pessoa Física"""

    # Dados Pessoais
    nome_completo: str = Field(..., min_length=3, max_length=255)
    cpf: str = Field(..., min_length=11, max_length=14)
    email: EmailStr
    data_nascimento: Optional[date] = None
    nome_social: Optional[str] = Field(None, max_length=255)
    sexo: Optional[str] = None
    estado_civil: Optional[str] = None
    nacionalidade: Optional[str] = "BRASILEIRA"
    naturalidade: Optional[str] = Field(None, max_length=100)

    # Filiação
    nome_pai: Optional[str] = Field(None, max_length=255)
    nome_mae: Optional[str] = Field(None, max_length=255)

    # Documentos
    rg: Optional[str] = Field(None, max_length=20)
    orgao_expeditor: Optional[str] = Field(None, max_length=20)
    uf_rg: Optional[str] = Field(None, max_length=2)
    data_expedicao_rg: Optional[date] = None
    titulo_eleitor: Optional[str] = Field(None, max_length=20)
    zona_eleitoral: Optional[str] = Field(None, max_length=10)
    secao_eleitoral: Optional[str] = Field(None, max_length=10)
    pis_pasep: Optional[str] = Field(None, max_length=20)

    # Contato
    telefone_principal: Optional[str] = Field(None, max_length=20)
    telefone_secundario: Optional[str] = Field(None, max_length=20)
    email_secundario: Optional[EmailStr] = None

    # Profissionais
    profissao: Optional[str] = Field(None, max_length=100)
    escolaridade: Optional[str] = None
    renda_mensal: Optional[float] = Field(None, ge=0)

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
    """Response de criação de pessoa"""

    success: bool
    message: str
    pessoa_id: str


@router.get("/auth/cadastro-pessoa-fisica")
async def cadastro_pessoa_fisica_page(request: Request):
    return templates.TemplateResponse(
        "pages/M01_auth/template_auth_cadastro_pessoa_pagina.html",
        {
            "request": request,
            "title": "Cadastro Pessoa Física | SIGMA-PLI",
            "year": datetime.utcnow().year,
        },
    )


@router.get("/auth/cadastro-pessoa")
async def cadastro_pessoa_alias(request: Request):
    return templates.TemplateResponse(
        "pages/M01_auth/template_auth_cadastro_pessoa_pagina.html",
        {
            "request": request,
            "title": "Cadastro Pessoa Física | SIGMA-PLI",
            "year": datetime.utcnow().year,
        },
    )


# API Endpoints
@router.post("/api/cadastro/pessoa-fisica", response_model=CadastroResponse)
async def cadastrar_pessoa_fisica(data: PessoaFisicaCreate):
    """
    Cadastrar Pessoa Física

    Args:
        data: Dados da pessoa física

    Returns:
        CadastroResponse com ID da pessoa criada
    """
    # Verificar se CPF já existe
    existing = await PessoaService.get_pessoa_by_cpf(data.cpf)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado no sistema",
        )

    # Verificar se email já existe
    existing_email = await PessoaService.get_pessoa_by_email(data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado no sistema",
        )

    try:
        pessoa_id = await PessoaService.create_pessoa_fisica(**data.model_dump())

        return CadastroResponse(
            success=True,
            message="Pessoa Física cadastrada com sucesso",
            pessoa_id=str(pessoa_id),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cadastrar pessoa física: {str(e)}",
        )
