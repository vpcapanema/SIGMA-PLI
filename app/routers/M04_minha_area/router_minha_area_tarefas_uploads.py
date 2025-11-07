"""
SIGMA-PLI - M04: Minha Área
Router para tarefas pessoais, uploads e aprovações
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def minha_area_status():
    """Status do módulo minha área"""
    return {"module": "M04_minha_area", "status": "under_construction"}