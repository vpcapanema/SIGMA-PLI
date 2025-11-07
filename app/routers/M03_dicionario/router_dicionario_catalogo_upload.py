"""
SIGMA-PLI - M03: Dicionário & Repositório
Router para catálogo, upload e metadados
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def dicionario_status():
    """Status do módulo dicionário"""
    return {"module": "M03_dicionario", "status": "under_construction"}