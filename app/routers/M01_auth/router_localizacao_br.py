"""
Routers para APIs de localização brasileira
Endpoints para obter UFs e Municípios via IBGE

Endpoints:
- GET /api/v1/localizacao/ufs - Lista todas as UFs
- GET /api/v1/localizacao/municipios/{uf} - Lista municípios de um UF
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import logging

from app.services.M01_auth.service_localizacao_br import LocalizacaoBRService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/localizacao", tags=["Localização Brasil"])


# Schemas
class UFResponse(BaseModel):
    """Resposta com dados de UF"""

    sigla: str
    nome: str


class MunicipioResponse(BaseModel):
    """Resposta com dados de Município"""

    id: int
    nome: str


class UFListResponse(BaseModel):
    """Resposta com lista de UFs"""

    total: int
    ufs: List[UFResponse]
    mensagem: str = "UFs carregados com sucesso"


class MunicipioListResponse(BaseModel):
    """Resposta com lista de Municípios"""

    uf: str
    total: int
    municipios: List[MunicipioResponse]
    mensagem: str = "Municípios carregados com sucesso"


# Endpoints


@router.get("/ufs", response_model=UFListResponse)
async def obter_ufs():
    """
    Retorna lista de todas as UFs brasileiras

    Returns:
        ```json
        {
            "total": 27,
            "ufs": [
                {"sigla": "AC", "nome": "Acre"},
                {"sigla": "AL", "nome": "Alagoas"},
                ...
            ],
            "mensagem": "UFs carregados com sucesso"
        }
        ```

    Fonte: API IBGE (Instituto Brasileiro de Geografia e Estatística)
    """
    try:
        ufs = await LocalizacaoBRService.obter_ufs()

        if not ufs:
            raise HTTPException(status_code=500, detail="Erro ao carregar UFs")

        return UFListResponse(
            total=len(ufs),
            ufs=[UFResponse(sigla=uf["sigla"], nome=uf["nome"]) for uf in ufs],
            mensagem="UFs carregados com sucesso",
        )

    except Exception as e:
        logger.error(f"❌ Erro ao obter UFs: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao carregar UFs")


@router.get("/municipios/{uf}", response_model=MunicipioListResponse)
async def obter_municipios(uf: str):
    """
    Retorna lista de municípios de um UF específico

    Args:
        uf: Sigla do UF (ex: "SP", "RJ", "MG")

    Returns:
        ```json
        {
            "uf": "SP",
            "total": 645,
            "municipios": [
                {"id": 3509007, "nome": "Abadia de Goiás"},
                {"id": 3509056, "nome": "Abadiânia"},
                ...
            ],
            "mensagem": "Municípios carregados com sucesso"
        }
        ```

    Exemplo:
        `GET /api/v1/localizacao/municipios/SP`

    Fonte: API IBGE (Instituto Brasileiro de Geografia e Estatística)
    """
    try:
        # Validar UF
        uf = uf.upper().strip()
        if len(uf) != 2:
            raise HTTPException(
                status_code=400, detail="UF deve ter 2 caracteres (ex: SP, RJ)"
            )

        municipios = await LocalizacaoBRService.obter_municipios(uf)

        if not municipios:
            raise HTTPException(
                status_code=404, detail=f"Nenhum município encontrado para o UF {uf}"
            )

        return MunicipioListResponse(
            uf=uf,
            total=len(municipios),
            municipios=[
                MunicipioResponse(id=int(mun["id"]), nome=mun["nome"]) for mun in municipios
            ],
            mensagem="Municípios carregados com sucesso",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao obter municípios de {uf}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao carregar municípios")
