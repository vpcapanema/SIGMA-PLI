"""
SIGMA-PLI - M07: Ferramentas Avançadas
Router para hub de aplicações e ferramentas
"""

from fastapi import APIRouter, Request, Body
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def ferramentas_hub(request: Request):
    """Hub de ferramentas e aplicações"""
    return templates.TemplateResponse(
        "pages/M07_ferramentas/template_ferramentas_hub_pagina.html",
        {"request": request, "title": "Ferramentas & Aplicações - SIGMA-PLI"},
    )


@router.get("/od", response_class=HTMLResponse)
async def ferramentas_od_calculator(request: Request):
    """Página: Calculadora OD (Origem-Destino)"""
    return templates.TemplateResponse(
        "pages/M07_ferramentas/template_ferramentas_od_calculator_pagina.html",
        {"request": request, "title": "Calculadora OD | Ferramentas - SIGMA-PLI"},
    )


@router.post("/api/v1/ferramentas/od/calculate")
async def api_ferramentas_od_calculate(payload: dict = Body(...)):
    """Simulate an OD calculation endpoint. Returns a mocked response."""
    # In a real implementation, this would accept CSV or layer references and perform geospatial processing.
    # For now, return a sample response to support the front-end.
    return {
        "success": True,
        "message": "OD calculation simulated",
        "result": {
            "total_pairs": 2,
            "pairs": [
                {"origin": "A", "destination": "B", "trips": 123},
                {"origin": "A", "destination": "C", "trips": 45},
            ],
        },
    }
