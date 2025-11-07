"""
SIGMA-PLI - M06: Institucional
Router para produtos, entregas e documentos normativos
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def institucional_status():
    """Status do módulo institucional"""
    return {"module": "M06_institucional", "status": "under_construction"}