"""
Router para APIs externas de CPF e CEP.
Endpoints públicos para validação e consulta de dados.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import logging

from app.services.M01_auth.service_external_apis import (
    CPFService,
    CEPService,
    AddressService,
    CNPJService,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/externas",
    tags=["APIs Externas"],
    responses={404: {"description": "Não encontrado"}},
)


# ============================================================================
# SCHEMAS
# ============================================================================


class CPFValidationRequest(BaseModel):
    """Requisição de validação de CPF"""

    cpf: str = Field(
        ..., min_length=11, max_length=14, description="CPF com ou sem formatação"
    )


class CPFValidationResponse(BaseModel):
    """Resposta de validação de CPF"""

    valido: bool
    cpf: Optional[str] = None
    mensagem: str


class CEPConsultaRequest(BaseModel):
    """Requisição de consulta de CEP"""

    cep: str = Field(
        ..., min_length=8, max_length=10, description="CEP com ou sem formatação"
    )


class CEPConsultaResponse(BaseModel):
    """Resposta de consulta de CEP"""

    cep: Optional[str] = None
    logradouro: Optional[str] = None
    bairro: Optional[str] = None
    localidade: Optional[str] = None
    uf: Optional[str] = None
    complemento: Optional[str] = None
    erro: bool = False
    mensagem: Optional[str] = None


class CNPJValidationRequest(BaseModel):
    """Requisição de validação de CNPJ"""

    cnpj: str = Field(
        ..., min_length=14, max_length=18, description="CNPJ com ou sem formatação"
    )


class CNPJValidationResponse(BaseModel):
    """Resposta de validação e consulta de CNPJ"""

    valido: bool
    cnpj: Optional[str] = None
    nome: Optional[str] = None
    nome_fantasia: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    cep: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    mensagem: str


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/cpf/validar", response_model=CPFValidationResponse)
async def validar_cpf(request: CPFValidationRequest):
    """
    Valida um CPF usando algoritmo de dígitos verificadores.

    Retorna:
    - `valido: true` se o CPF é válido
    - `valido: false` se o CPF é inválido
    """
    try:
        resultado = await CPFService.consultar_cpf(request.cpf)

        if resultado is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao validar CPF",
            )

        return CPFValidationResponse(
            valido=resultado.get("valido", False),
            cpf=resultado.get("cpf"),
            mensagem=resultado.get("mensagem", ""),
        )

    except Exception as e:
        logger.error(f"Erro ao validar CPF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao validar CPF: {str(e)}",
        )


@router.post("/cep/consultar", response_model=CEPConsultaResponse)
async def consultar_cep(request: CEPConsultaRequest):
    """
    Consulta dados de endereço pelo CEP usando a API ViaCEP.

    Retorna:
    - `cep`: CEP formatado
    - `logradouro`: Nome da rua/avenida
    - `bairro`: Nome do bairro
    - `localidade`: Cidade
    - `uf`: Estado (sigla)
    - `complemento`: Informações adicionais
    - `erro`: True se CEP não encontrado

    Exemplo de requisição:
    ```json
    {
        "cep": "01310-100"
    }
    ```
    """
    try:
        resultado = await CEPService.consultar_cep(request.cep)

        if resultado is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao consultar CEP",
            )

        # Se houve erro na consulta
        if resultado.get("erro"):
            return CEPConsultaResponse(
                erro=True, mensagem=resultado.get("mensagem", "CEP não encontrado")
            )

        # Sucesso na consulta
        return CEPConsultaResponse(
            cep=resultado.get("cep"),
            logradouro=resultado.get("logradouro"),
            bairro=resultado.get("bairro"),
            localidade=resultado.get("localidade"),
            uf=resultado.get("uf"),
            complemento=resultado.get("complemento"),
            erro=False,
        )

    except Exception as e:
        logger.error(f"Erro ao consultar CEP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao consultar CEP: {str(e)}",
        )


@router.post("/endereco/validar")
async def validar_endereco(request: CEPConsultaRequest):
    """
    Valida e consulta endereço pelo CEP.
    Integra validação com fallback para entrada manual.
    """
    try:
        resultado = await AddressService.validar_e_consultar_endereco(request.cep)
        return resultado

    except Exception as e:
        logger.error(f"Erro ao validar endereço: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao validar endereço: {str(e)}",
        )


@router.post("/cnpj/validar", response_model=CNPJValidationResponse)
async def validar_cnpj(request: CNPJValidationRequest):
    """
    Valida um CNPJ e consulta dados na Receita Federal via API ReceitaWS.

    Retorna:
    - `valido: true` e todos os dados se o CNPJ é válido e encontrado
    - `valido: false` se o CNPJ tem formato inválido
    - `valido: true` sem dados se encontrado mas sem informações públicas

    Campos retornados:
    - nome, nome_fantasia
    - logradouro, numero, complemento, bairro, municipio, uf, cep
    - telefone, email
    """
    try:
        resultado = await CNPJService.consultar_cnpj(request.cnpj)

        if resultado is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao validar CNPJ",
            )

        return CNPJValidationResponse(
            valido=resultado.get("valido", False),
            cnpj=resultado.get("cnpj"),
            nome=resultado.get("nome"),
            nome_fantasia=resultado.get("nome_fantasia"),
            logradouro=resultado.get("logradouro"),
            numero=resultado.get("numero"),
            complemento=resultado.get("complemento"),
            bairro=resultado.get("bairro"),
            municipio=resultado.get("municipio"),
            uf=resultado.get("uf"),
            cep=resultado.get("cep"),
            telefone=resultado.get("telefone"),
            email=resultado.get("email"),
            mensagem=resultado.get("mensagem", ""),
        )

    except Exception as e:
        logger.error(f"Erro ao validar CNPJ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao validar CNPJ: {str(e)}",
        )
