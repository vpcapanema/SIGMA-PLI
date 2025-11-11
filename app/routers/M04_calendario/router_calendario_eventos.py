"""
SIGMA-PLI - M04: Calendário
Router para gerenciamento de eventos do calendário
"""

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from datetime import date, datetime

from app.models.schemas.calendario import (
    EventoCreate,
    EventoUpdate,
    EventoResponse,
    EventosList,
    EventoSearchParams,
    EventType,
    ShareLinkResponse,
)
from app.services.M04_calendario.service_calendario_eventos import (
    get_calendario_service,
)
from app.services.service_feriados import FeriadoService


router = APIRouter()
templates = Jinja2Templates(directory="templates")


# ========================================
# ENDPOINTS DE UI (PÁGINAS)
# ========================================


@router.get("/calendario")
async def calendario_page(request: Request):
    """Página principal do calendário"""
    return templates.TemplateResponse(
        "pages/M04_calendario/template_calendario_index.html",
        {
            "request": request,
            "title": "Calendário PLI | SIGMA-PLI",
            "description": "Sistema de gerenciamento de eventos e prazos do PLI-SP 2050",
        },
    )


# ========================================
# ENDPOINTS DE API REST
# ========================================


@router.get(
    "/api/v1/calendario/eventos", response_model=EventosList, tags=["Calendário"]
)
async def get_all_eventos(
    type: Optional[EventType] = Query(None, description="Filtrar por tipo de evento"),
    user: Optional[str] = Query(
        None, description="Filtrar por responsável (busca parcial)"
    ),
    module: Optional[str] = Query(None, description="Filtrar por módulo"),
    date_start: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    date_end: Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=500, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
):
    """
    Retorna lista de eventos do calendário com suporte a filtros e paginação.

    **Filtros disponíveis:**
    - `type`: Tipo do evento (entrega, reuniao, homeoffice)
    - `user`: Nome do responsável (busca parcial, case-insensitive)
    - `module`: Módulo relacionado (ex: M00_home, M02_cadastros)
    - `date_start`: Data inicial para filtro de período
    - `date_end`: Data final para filtro de período

    **Paginação:**
    - `limit`: Máximo de eventos retornados (padrão: 100, máx: 500)
    - `offset`: Posição inicial (padrão: 0)
    """
    service = get_calendario_service()

    # Se não há filtros, retorna todos
    if not any([type, user, module, date_start, date_end]):
        eventos = service.get_all_eventos()
        return EventosList(eventos=eventos, total=len(eventos))

    # Aplica filtros via search
    search_params = EventoSearchParams(
        type=type,
        user=user,
        module=module,
        date_start=date_start,
        date_end=date_end,
        limit=limit,
        offset=offset,
    )

    eventos_filtered = service.search_eventos(search_params)
    total_eventos = len(service.get_all_eventos())

    return EventosList(
        eventos=eventos_filtered, total=total_eventos, filtered=len(eventos_filtered)
    )


@router.post(
    "/api/v1/calendario/eventos",
    response_model=EventoResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Calendário"],
)
async def create_evento(evento: EventoCreate):
    """
    Cria um novo evento no calendário.

    **Comportamentos automáticos:**
    - Se `type` for "homeoffice", um lembrete de confirmação será criado automaticamente 2 dias antes
    - O lembrete terá `isHomeOfficeReminder=true` e `linkedEventId` apontando para o evento original

    **Validações:**
    - `endTime` deve ser posterior a `startTime`
    - `date` não pode ser superior a 1 ano no passado
    - Campos obrigatórios: type, title, user, date, startTime, endTime
    """
    service = get_calendario_service()

    try:
        novo_evento = service.create_evento(evento)
        return novo_evento
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar evento: {str(e)}",
        )


@router.get(
    "/api/v1/calendario/eventos/{evento_id}",
    response_model=EventoResponse,
    tags=["Calendário"],
)
async def get_evento_by_id(evento_id: str):
    """
    Retorna um evento específico por ID.

    **Formato do ID:** evt-{hash}-{timestamp}
    """
    service = get_calendario_service()
    evento = service.get_evento_by_id(evento_id)

    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento {evento_id} não encontrado",
        )

    return evento


@router.put(
    "/api/v1/calendario/eventos/{evento_id}",
    response_model=EventoResponse,
    tags=["Calendário"],
)
async def update_evento(evento_id: str, evento_update: EventoUpdate):
    """
    Atualiza um evento existente (atualização parcial).

    Apenas os campos fornecidos serão atualizados. Campos omitidos permanecem inalterados.
    """
    service = get_calendario_service()

    try:
        updated_evento = service.update_evento(evento_id, evento_update)

        if not updated_evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evento {evento_id} não encontrado",
            )

        return updated_evento
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar evento: {str(e)}",
        )


@router.delete(
    "/api/v1/calendario/eventos/{evento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Calendário"],
)
async def delete_evento(evento_id: str):
    """
    Remove um evento do calendário.

    **Comportamento em cascata:**
    - Se o evento for do tipo "homeoffice" e não for um lembrete, todos os lembretes vinculados serão removidos automaticamente
    - Se for um lembrete, apenas ele será removido
    """
    service = get_calendario_service()

    deleted = service.delete_evento(evento_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento {evento_id} não encontrado",
        )

    return None  # 204 No Content


# ========================================
# ENDPOINTS AUXILIARES
# ========================================


@router.get(
    "/api/v1/calendario/eventos/date/{target_date}",
    response_model=List[EventoResponse],
    tags=["Calendário"],
)
async def get_eventos_by_date(target_date: date):
    """
    Retorna todos os eventos de uma data específica.

    **Formato da data:** YYYY-MM-DD
    """
    service = get_calendario_service()
    eventos = service.get_eventos_by_date(target_date)
    return eventos


@router.get(
    "/api/v1/calendario/upcoming",
    response_model=List[EventoResponse],
    tags=["Calendário"],
)
async def get_upcoming_eventos(
    days: int = Query(3, ge=1, le=30, description="Número de dias futuros")
):
    """
    Retorna eventos próximos (nos próximos N dias).

    Útil para notificações e alertas de eventos iminentes.
    """
    service = get_calendario_service()
    eventos = service.get_upcoming_eventos(days)
    return eventos


@router.get("/api/v1/calendario/stats", tags=["Calendário"])
async def get_statistics():
    """
    Retorna estatísticas dos eventos do calendário.

    **Métricas retornadas:**
    - `total`: Total de eventos cadastrados
    - `entregas`: Quantidade de entregas
    - `reunioes`: Quantidade de reuniões
    - `homeOffice`: Quantidade de dias de home office
    - `thisMonth`: Eventos no mês atual
    """
    service = get_calendario_service()
    stats = service.get_statistics()
    return stats


@router.post(
    "/api/v1/calendario/eventos/{evento_id}/share",
    response_model=ShareLinkResponse,
    tags=["Calendário"],
)
async def generate_share_link(evento_id: str):
    """
    Gera um link de compartilhamento para o evento.

    **Nota:** Implementação placeholder. Em produção, deve gerar token único e armazenar no banco.
    """
    service = get_calendario_service()
    evento = service.get_evento_by_id(evento_id)

    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento {evento_id} não encontrado",
        )

    # TODO: Implementar geração real de token e armazenamento
    share_url = f"https://sigma-pli.sp.gov.br/calendario/share/{evento_id}"

    return ShareLinkResponse(
        evento_id=evento_id,
        share_url=share_url,
        expires_at=None,  # Implementar expiração futuramente
    )


# ========================================
# ENDPOINTS DE FERIADOS
# ========================================


@router.get("/api/v1/calendario/feriados/{ano}", tags=["Calendário", "Feriados"])
async def get_feriados_ano(ano: int):
    """
    Retorna todos os feriados de um ano específico.

    Inclui:
    - Feriados nacionais
    - Feriados estaduais (São Paulo)
    - Feriados municipais (São Paulo)
    """
    feriados = FeriadoService.obter_todos_feriados(ano)

    # Formata para JSON
    return {
        "ano": ano,
        "total": len(feriados),
        "feriados": [
            {
                "data": f["data"].isoformat(),
                "nome": f["nome"],
                "tipo": f["tipo"],
                "tipo_feriado": f["tipo_feriado"],
            }
            for f in feriados
        ],
    }


@router.get("/api/v1/calendario/feriados/{ano}/{mes}", tags=["Calendário", "Feriados"])
async def get_feriados_mes(ano: int, mes: int):
    """
    Retorna feriados de um mês específico.
    """
    if mes < 1 or mes > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mês deve estar entre 1 e 12",
        )

    feriados = FeriadoService.obter_feriados_mes(ano, mes)

    return {
        "ano": ano,
        "mes": mes,
        "total": len(feriados),
        "feriados": [
            {
                "data": f["data"].isoformat(),
                "nome": f["nome"],
                "tipo": f["tipo"],
                "tipo_feriado": f["tipo_feriado"],
            }
            for f in feriados
        ],
    }


@router.get("/api/v1/calendario/feriados/proximo", tags=["Calendário", "Feriados"])
async def get_proximo_feriado():
    """
    Retorna o próximo feriado a partir da data atual.
    """
    feriado = FeriadoService.obter_proximo_feriado()

    if not feriado:
        return {"proximo_feriado": None}

    hoje = date.today()
    dias_ate = (feriado["data"] - hoje).days

    return {
        "proximo_feriado": {
            "data": feriado["data"].isoformat(),
            "nome": feriado["nome"],
            "tipo": feriado["tipo"],
            "tipo_feriado": feriado["tipo_feriado"],
            "dias_ate": dias_ate,
        }
    }


@router.get(
    "/api/v1/calendario/feriados/verificar/{data}", tags=["Calendário", "Feriados"]
)
async def verificar_feriado(data: str):
    """
    Verifica se uma data específica é feriado.

    Formato da data: YYYY-MM-DD
    """
    try:
        data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data inválido. Use YYYY-MM-DD",
        )

    feriado = FeriadoService.eh_feriado(data_obj)

    if feriado:
        return {
            "eh_feriado": True,
            "data": data,
            "feriado": {
                "nome": feriado["nome"],
                "tipo": feriado["tipo"],
                "tipo_feriado": feriado["tipo_feriado"],
            },
        }

    return {"eh_feriado": False, "data": data}
