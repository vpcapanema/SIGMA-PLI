"""
SIGMA-PLI - M04: Calendário
Modelos Pydantic para eventos do calendário
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date as date_type, time as time_type
from enum import Enum
import uuid


class EventType(str, Enum):
    """Tipos de eventos possíveis"""

    ENTREGA = "entrega"
    REUNIAO = "reuniao"
    HOMEOFFICE = "homeoffice"


class EventoBase(BaseModel):
    """Modelo base para evento do calendário"""

    type: EventType = Field(..., description="Tipo do evento")
    title: str = Field(
        ..., min_length=3, max_length=200, description="Título do evento"
    )
    user: str = Field(
        ..., min_length=2, max_length=100, description="Responsável pelo evento"
    )
    date: date_type = Field(..., description="Data do evento (YYYY-MM-DD)")
    startTime: str = Field(
        ...,
        pattern=r"^([01]\d|2[0-3]):([0-5]\d)$",
        description="Hora de início (HH:MM)",
    )
    endTime: str = Field(
        ...,
        pattern=r"^([01]\d|2[0-3]):([0-5]\d)$",
        description="Hora de término (HH:MM)",
    )
    location: Optional[str] = Field(None, max_length=200, description="Local do evento")
    notes: Optional[str] = Field(
        None, max_length=1000, description="Observações do evento"
    )
    module: Optional[str] = Field(
        None, max_length=100, description="Módulo relacionado"
    )
    isHomeOfficeReminder: bool = Field(
        False, description="Flag indicando se é lembrete de Home Office"
    )
    linkedEventId: Optional[str] = Field(
        None, description="ID do evento vinculado (para lembretes)"
    )

    @validator("endTime")
    def validate_end_time(cls, v, values):
        """Valida que horário de término é posterior ao de início"""
        if "startTime" in values and v <= values["startTime"]:
            raise ValueError("Horário de término deve ser posterior ao de início")
        return v

    @validator("date")
    def validate_date_not_past(cls, v):
        """Valida que a data não é muito antiga (permite até 1 ano no passado)"""
        from datetime import date, timedelta

        one_year_ago = date.today() - timedelta(days=365)
        if v < one_year_ago:
            raise ValueError("Data não pode ser superior a 1 ano no passado")
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "type": "entrega",
                "title": "Entrega do Relatório Mensal",
                "user": "André Silva",
                "date": "2025-11-25",
                "startTime": "14:00",
                "endTime": "15:00",
                "location": "Reunião Online",
                "notes": "Apresentar indicadores do mês de novembro",
                "module": "M05_relatorios",
                "isHomeOfficeReminder": False,
                "linkedEventId": None,
            }
        }


class EventoCreate(EventoBase):
    """Modelo para criação de evento"""

    pass


class EventoUpdate(BaseModel):
    """Modelo para atualização parcial de evento"""

    type: Optional[EventType] = None
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    user: Optional[str] = Field(None, min_length=2, max_length=100)
    date: Optional[date_type] = None
    startTime: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    endTime: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    location: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=1000)
    module: Optional[str] = Field(None, max_length=100)

    class Config:
        from_attributes = True


class EventoResponse(EventoBase):
    """Modelo de resposta para evento"""

    id: str = Field(..., description="ID único do evento")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de última atualização")

    class Config:
        from_attributes = True


class EventosList(BaseModel):
    """Lista de eventos com metadados"""

    eventos: List[EventoResponse]
    total: int
    filtered: Optional[int] = None

    class Config:
        from_attributes = True


class EventoSearchParams(BaseModel):
    """Parâmetros de busca/filtro de eventos"""

    type: Optional[EventType] = None
    user: Optional[str] = None
    module: Optional[str] = None
    date_start: Optional[date_type] = None
    date_end: Optional[date_type] = None
    limit: int = Field(100, ge=1, le=500)
    offset: int = Field(0, ge=0)

    class Config:
        from_attributes = True


class ShareLinkResponse(BaseModel):
    """Resposta para geração de link de compartilhamento"""

    evento_id: str
    share_url: str
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True
