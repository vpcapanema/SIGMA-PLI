"""
SIGMA-PLI - Schemas para Pessoa Física
Com validação e criptografia de dados sensíveis
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.security.validators import (
    validar_cpf,
    validar_telefone,
    limpar_cpf,
    limpar_telefone,
)


class PessoaFisicaBase(BaseModel):
    """Schema base para Pessoa Física"""

    nome_completo: str = Field(
        ..., min_length=3, max_length=255, description="Nome completo"
    )
    data_nascimento: Optional[datetime] = Field(None, description="Data de nascimento")
    sexo: Optional[str] = Field(None, regex="^[MF]$", description="M ou F")


class PessoaFisicaCreate(PessoaFisicaBase):
    """Schema para criação de Pessoa Física"""

    cpf: str = Field(..., description="CPF (11 dígitos)")
    telefone: str = Field(..., description="Telefone (10 ou 11 dígitos)")
    email: str = Field(..., description="E-mail")

    @validator("cpf", pre=True)
    def validar_cpf_field(cls, v):
        """Validar e limpar CPF"""
        if not v:
            raise ValueError("CPF é obrigatório")

        cpf_limpo = limpar_cpf(v)

        if not validar_cpf(cpf_limpo):
            raise ValueError("CPF inválido")

        return cpf_limpo

    @validator("telefone", pre=True)
    def validar_telefone_field(cls, v):
        """Validar e limpar telefone"""
        if not v:
            raise ValueError("Telefone é obrigatório")

        telefone_limpo = limpar_telefone(v)

        if not validar_telefone(telefone_limpo):
            raise ValueError("Telefone inválido (10 ou 11 dígitos)")

        return telefone_limpo

    @validator("email")
    def validar_email(cls, v):
        """Validar email básico"""
        if "@" not in v or "." not in v:
            raise ValueError("E-mail inválido")
        return v.lower()

    class Config:
        schema_extra = {
            "example": {
                "nome_completo": "João da Silva Santos",
                "cpf": "12345678900",
                "telefone": "11987654321",
                "email": "joao@example.com",
                "data_nascimento": "1990-01-15",
                "sexo": "M",
            }
        }


class PessoaFisicaUpdate(BaseModel):
    """Schema para atualização de Pessoa Física"""

    nome_completo: Optional[str] = Field(None, min_length=3, max_length=255)
    telefone: Optional[str] = Field(None)
    data_nascimento: Optional[datetime] = None
    sexo: Optional[str] = Field(None, regex="^[MF]$")

    @validator("telefone", pre=True)
    def validar_telefone_field(cls, v):
        """Validar telefone se fornecido"""
        if v is None:
            return None

        telefone_limpo = limpar_telefone(v)

        if not validar_telefone(telefone_limpo):
            raise ValueError("Telefone inválido")

        return telefone_limpo

    class Config:
        schema_extra = {
            "example": {"nome_completo": "João Silva", "telefone": "11999999999"}
        }


class PessoaFisicaResponse(PessoaFisicaBase):
    """Schema para resposta de Pessoa Física (sem dados sensíveis)"""

    id: str = Field(..., description="ID único da pessoa")
    email: str
    cpf_display: Optional[str] = Field(
        None, description="CPF mascarado (últimos 2 dígitos)"
    )
    telefone_display: Optional[str] = Field(None, description="Telefone formatado")
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "nome_completo": "João Silva",
                "email": "joao@example.com",
                "cpf_display": "******.***-00",
                "telefone_display": "(11) 98765-4321",
                "criado_em": "2025-11-04T10:30:00",
                "atualizado_em": "2025-11-04T10:30:00",
            }
        }


class PessoaFisicaDetailedResponse(PessoaFisicaResponse):
    """Schema detalhado (apenas para admin/proprietário)"""

    cpf_criptografado: Optional[str] = Field(None, description="CPF criptografado")
    telefone_criptografado: Optional[str] = Field(
        None, description="Telefone criptografado"
    )


# ============================================
# Schemas para Pessoa Jurídica
# ============================================


class PessoaJuridicaBase(BaseModel):
    """Schema base para Pessoa Jurídica"""

    nome_empresa: str = Field(..., min_length=3, max_length=255)
    nome_fantasia: Optional[str] = Field(None, max_length=255)


class PessoaJuridicaCreate(PessoaJuridicaBase):
    """Schema para criação de Pessoa Jurídica"""

    cnpj: str = Field(..., description="CNPJ (14 dígitos)")
    telefone: str = Field(..., description="Telefone (10 ou 11 dígitos)")
    email: str = Field(..., description="E-mail")

    @validator("cnpj", pre=True)
    def validar_cnpj_field(cls, v):
        """Validar CNPJ"""
        from app.security.validators import validar_cnpj, limpar_cnpj

        if not v:
            raise ValueError("CNPJ é obrigatório")

        cnpj_limpo = limpar_cnpj(v)

        if not validar_cnpj(cnpj_limpo):
            raise ValueError("CNPJ inválido")

        return cnpj_limpo

    @validator("telefone", pre=True)
    def validar_telefone_field(cls, v):
        """Validar telefone"""
        if not v:
            raise ValueError("Telefone é obrigatório")

        telefone_limpo = limpar_telefone(v)

        if not validar_telefone(telefone_limpo):
            raise ValueError("Telefone inválido")

        return telefone_limpo

    class Config:
        schema_extra = {
            "example": {
                "nome_empresa": "Empresa XYZ LTDA",
                "nome_fantasia": "XYZ Soluções",
                "cnpj": "12345678000100",
                "telefone": "1140002000",
                "email": "contato@xyz.com",
            }
        }


class PessoaJuridicaResponse(PessoaJuridicaBase):
    """Schema para resposta de Pessoa Jurídica"""

    id: str
    email: str
    cnpj_display: Optional[str] = Field(None, description="CNPJ mascarado")
    telefone_display: Optional[str] = Field(None, description="Telefone formatado")
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True
