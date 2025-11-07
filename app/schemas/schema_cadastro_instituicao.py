"""SIGMA-PLI - Schemas de Instituição"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class InstituicaoCreate(BaseModel):
    """Schema para criação de instituição"""

    # Dados básicos (obrigatórios)
    nome: str = Field(
        ..., min_length=3, max_length=255, description="Nome da instituição"
    )
    cnpj: str = Field(
        ..., min_length=14, max_length=18, description="CNPJ da instituição"
    )
    email: EmailStr = Field(..., description="Email principal")
    telefone: str = Field(
        ..., min_length=10, max_length=20, description="Telefone principal"
    )

    # Dados da empresa
    razao_social: Optional[str] = Field(None, max_length=255)
    nome_fantasia: Optional[str] = Field(None, max_length=255)
    sigla: Optional[str] = Field(None, max_length=10)
    tipo: Optional[str] = Field(
        None, description="Tipo: PUBLICA, PRIVADA, MISTA, ONG, ASSOCIACAO"
    )
    porte_empresa: Optional[str] = Field(None, max_length=50)
    data_abertura: Optional[date] = None
    situacao_receita_federal: str = Field(default="ATIVA", max_length=50)

    # Informações fiscais
    inscricao_estadual: Optional[str] = Field(None, max_length=50)
    inscricao_municipal: Optional[str] = Field(None, max_length=50)
    natureza_juridica: Optional[str] = Field(None, max_length=100)
    regime_tributario: Optional[str] = Field(None, max_length=50)

    # Contato adicional
    email_secundario: Optional[EmailStr] = None
    telefone_secundario: Optional[str] = Field(None, max_length=20)
    site: Optional[str] = Field(None, max_length=255)

    # Endereço (obrigatórios)
    cep: str = Field(..., min_length=8, max_length=10)
    logradouro: str = Field(..., max_length=255)
    numero: str = Field(..., max_length=20)
    bairro: str = Field(..., max_length=100)
    cidade: str = Field(..., max_length=100)
    uf: str = Field(..., min_length=2, max_length=2)

    # Endereço (opcionais)
    complemento: Optional[str] = Field(None, max_length=100)
    pais: str = Field(default="Brasil", max_length=100)

    # Status
    ativa: bool = Field(default=True)

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, v: str) -> str:
        """Valida e limpa o CNPJ"""
        # Remove formatação
        cnpj = re.sub(r"[^\d]", "", v)

        # Verifica tamanho
        if len(cnpj) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")

        # Verifica se não são todos iguais
        if cnpj == cnpj[0] * 14:
            raise ValueError("CNPJ inválido")

        return cnpj

    @field_validator("telefone", "telefone_secundario")
    @classmethod
    def validate_telefone(cls, v: Optional[str]) -> Optional[str]:
        """Limpa formatação de telefone"""
        if v is None:
            return None
        # Remove formatação
        return re.sub(r"[^\d]", "", v)

    @field_validator("cep")
    @classmethod
    def validate_cep(cls, v: str) -> str:
        """Limpa formatação de CEP"""
        # Remove formatação
        cep = re.sub(r"[^\d]", "", v)

        if len(cep) != 8:
            raise ValueError("CEP deve ter 8 dígitos")

        return cep

    @field_validator("uf")
    @classmethod
    def validate_uf(cls, v: str) -> str:
        """Valida UF"""
        v = v.upper()
        ufs_validas = [
            "AC",
            "AL",
            "AP",
            "AM",
            "BA",
            "CE",
            "DF",
            "ES",
            "GO",
            "MA",
            "MT",
            "MS",
            "MG",
            "PA",
            "PB",
            "PR",
            "PE",
            "PI",
            "RJ",
            "RN",
            "RS",
            "RO",
            "RR",
            "SC",
            "SP",
            "SE",
            "TO",
        ]

        if v not in ufs_validas:
            raise ValueError(
                f'UF inválida. Deve ser uma das seguintes: {", ".join(ufs_validas)}'
            )

        return v


class InstituicaoResponse(BaseModel):
    """Schema para resposta de instituição"""

    id: UUID
    nome: str
    razao_social: Optional[str]
    nome_fantasia: Optional[str]
    sigla: Optional[str]
    cnpj: str
    tipo: Optional[str]
    email: str
    telefone: str
    site: Optional[str]
    ativa: bool
    created_at: datetime

    # Endereço resumido
    cidade: Optional[str]
    uf: Optional[str]

    class Config:
        from_attributes = True


class InstituicaoDetail(InstituicaoResponse):
    """Schema para detalhes completos de instituição"""

    # Dados da empresa
    porte_empresa: Optional[str]
    data_abertura: Optional[date]
    situacao_receita_federal: Optional[str]

    # Informações fiscais
    inscricao_estadual: Optional[str]
    inscricao_municipal: Optional[str]
    natureza_juridica: Optional[str]
    regime_tributario: Optional[str]

    # Contato completo
    email_secundario: Optional[str]
    telefone_secundario: Optional[str]

    # Endereço completo
    cep: Optional[str]
    logradouro: Optional[str]
    numero: Optional[str]
    complemento: Optional[str]
    bairro: Optional[str]
    pais: Optional[str]
