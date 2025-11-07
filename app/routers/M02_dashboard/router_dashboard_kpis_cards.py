"""
SIGMA-PLI - M02: Dashboard
Router para dashboard pessoal e KPIs
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def dashboard_status():
    """Status do módulo dashboard"""
    return {"module": "M02_dashboard", "status": "under_construction"}