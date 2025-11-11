"""
SIGMA-PLI - M04: Calendário
Serviço de gerenciamento de eventos
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import uuid
from app.models.schemas.calendario import (
    EventoCreate,
    EventoUpdate,
    EventoResponse,
    EventType,
    EventoSearchParams,
)


class CalendarioEventosService:
    """Serviço para gerenciamento de eventos do calendário"""

    def __init__(self):
        """
        Inicializa o serviço.
        Por enquanto usa armazenamento em memória.
        TODO: Integrar com PostgreSQL quando a tabela for criada.
        """
        self._eventos: Dict[str, Dict[str, Any]] = {}
        self._init_sample_data()

    def _init_sample_data(self):
        """Inicializa com alguns eventos de exemplo"""
        sample_eventos = [
            {
                "type": "entrega",
                "title": "Entrega Relatório Mensal",
                "user": "André Silva",
                "date": "2025-11-25",
                "startTime": "14:00",
                "endTime": "15:00",
                "location": "Online",
                "notes": "Relatório de indicadores de novembro",
                "module": "M05_relatorios",
                "isHomeOfficeReminder": False,
                "linkedEventId": None,
            },
            {
                "type": "reuniao",
                "title": "Reunião de Planejamento",
                "user": "Antonio Costa",
                "date": "2025-11-20",
                "startTime": "10:00",
                "endTime": "11:30",
                "location": "Sala de Reuniões",
                "notes": "Planejamento sprint próximo mês",
                "module": "M00_home",
                "isHomeOfficeReminder": False,
                "linkedEventId": None,
            },
            {
                "type": "homeoffice",
                "title": "Home Office",
                "user": "Cristina Santos",
                "date": "2025-11-22",
                "startTime": "08:00",
                "endTime": "17:00",
                "location": "Remoto",
                "notes": "Trabalho remoto",
                "module": None,
                "isHomeOfficeReminder": False,
                "linkedEventId": None,
            },
        ]

        for evento_data in sample_eventos:
            evento_id = f"evt-{uuid.uuid4().hex[:8]}-{int(datetime.now().timestamp())}"
            now = datetime.now()

            self._eventos[evento_id] = {
                "id": evento_id,
                "created_at": now,
                "updated_at": now,
                **evento_data,
            }

    def create_evento(self, evento_data: EventoCreate) -> EventoResponse:
        """Cria um novo evento"""
        evento_id = f"evt-{uuid.uuid4().hex[:8]}-{int(datetime.now().timestamp())}"
        now = datetime.now()

        evento_dict = {
            "id": evento_id,
            "created_at": now,
            "updated_at": now,
            **evento_data.model_dump(),
        }

        # Converte date para string para armazenamento
        if isinstance(evento_dict["date"], date):
            evento_dict["date"] = evento_dict["date"].isoformat()

        self._eventos[evento_id] = evento_dict

        # Se for Home Office, cria lembrete automaticamente
        if (
            evento_data.type == EventType.HOMEOFFICE
            and not evento_data.isHomeOfficeReminder
        ):
            self._create_homeoffice_reminder(evento_id, evento_dict)

        return EventoResponse(**evento_dict)

    def _create_homeoffice_reminder(self, ho_event_id: str, ho_event: Dict[str, Any]):
        """Cria lembrete automático de confirmação de Home Office (2 dias antes)"""
        ho_date = (
            datetime.fromisoformat(ho_event["date"])
            if isinstance(ho_event["date"], str)
            else ho_event["date"]
        )
        reminder_date = ho_date - timedelta(days=2)

        # Só cria se a data do lembrete for futura
        if reminder_date.date() >= datetime.now().date():
            reminder_id = (
                f"evt-{uuid.uuid4().hex[:8]}-{int(datetime.now().timestamp())}"
            )
            now = datetime.now()

            reminder_dict = {
                "id": reminder_id,
                "created_at": now,
                "updated_at": now,
                "type": "homeoffice",
                "title": f"Confirmação Home Office - {ho_event['user']}",
                "user": ho_event["user"],
                "date": reminder_date.date().isoformat(),
                "startTime": "09:00",
                "endTime": "09:30",
                "location": "Notificação",
                "notes": f"Confirmação automática do HO marcado para {ho_event['date']}",
                "module": ho_event.get("module"),
                "isHomeOfficeReminder": True,
                "linkedEventId": ho_event_id,
            }

            self._eventos[reminder_id] = reminder_dict

    def get_all_eventos(self) -> List[EventoResponse]:
        """Retorna todos os eventos"""
        eventos_list = [EventoResponse(**evento) for evento in self._eventos.values()]
        # Ordena por data
        eventos_list.sort(key=lambda e: (e.date, e.startTime))
        return eventos_list

    def get_evento_by_id(self, evento_id: str) -> Optional[EventoResponse]:
        """Retorna um evento específico por ID"""
        evento = self._eventos.get(evento_id)
        if evento:
            return EventoResponse(**evento)
        return None

    def update_evento(
        self, evento_id: str, evento_update: EventoUpdate
    ) -> Optional[EventoResponse]:
        """Atualiza um evento existente"""
        if evento_id not in self._eventos:
            return None

        evento = self._eventos[evento_id]
        update_data = evento_update.model_dump(exclude_unset=True)

        # Converte date para string se presente
        if "date" in update_data and isinstance(update_data["date"], date):
            update_data["date"] = update_data["date"].isoformat()

        # Atualiza campos
        for field, value in update_data.items():
            evento[field] = value

        evento["updated_at"] = datetime.now()

        return EventoResponse(**evento)

    def delete_evento(self, evento_id: str) -> bool:
        """Remove um evento"""
        if evento_id not in self._eventos:
            return False

        evento = self._eventos[evento_id]

        # Se for Home Office, remove lembretes vinculados
        if evento.get("type") == "homeoffice" and not evento.get(
            "isHomeOfficeReminder"
        ):
            self._delete_homeoffice_reminders(evento_id)

        # Se for lembrete, remove apenas ele
        del self._eventos[evento_id]
        return True

    def _delete_homeoffice_reminders(self, ho_event_id: str):
        """Remove lembretes vinculados a um evento de Home Office"""
        reminders_to_delete = [
            evt_id
            for evt_id, evt in self._eventos.items()
            if evt.get("isHomeOfficeReminder")
            and evt.get("linkedEventId") == ho_event_id
        ]

        for reminder_id in reminders_to_delete:
            del self._eventos[reminder_id]

    def search_eventos(self, params: EventoSearchParams) -> List[EventoResponse]:
        """Busca eventos com filtros"""
        eventos = list(self._eventos.values())

        # Aplica filtros
        if params.type:
            eventos = [e for e in eventos if e["type"] == params.type]

        if params.user:
            user_lower = params.user.lower()
            eventos = [e for e in eventos if user_lower in e["user"].lower()]

        if params.module:
            if params.module == "all":
                pass  # Não filtra
            else:
                eventos = [e for e in eventos if e.get("module") == params.module]

        if params.date_start:
            date_start_str = params.date_start.isoformat()
            eventos = [e for e in eventos if e["date"] >= date_start_str]

        if params.date_end:
            date_end_str = params.date_end.isoformat()
            eventos = [e for e in eventos if e["date"] <= date_end_str]

        # Ordena
        eventos.sort(key=lambda e: (e["date"], e["startTime"]))

        # Paginação
        start = params.offset
        end = start + params.limit
        eventos_paginated = eventos[start:end]

        return [EventoResponse(**e) for e in eventos_paginated]

    def get_eventos_by_date(self, target_date: date) -> List[EventoResponse]:
        """Retorna eventos de uma data específica"""
        date_str = target_date.isoformat()
        eventos = [
            EventoResponse(**e) for e in self._eventos.values() if e["date"] == date_str
        ]
        eventos.sort(key=lambda e: e.startTime)
        return eventos

    def get_upcoming_eventos(self, days: int = 3) -> List[EventoResponse]:
        """Retorna eventos próximos (nos próximos N dias)"""
        today = datetime.now().date()
        end_date = today + timedelta(days=days)

        eventos = [
            EventoResponse(**e)
            for e in self._eventos.values()
            if today <= datetime.fromisoformat(e["date"]).date() <= end_date
        ]
        eventos.sort(key=lambda e: (e.date, e.startTime))
        return eventos

    def get_statistics(self) -> Dict[str, int]:
        """Retorna estatísticas dos eventos"""
        today = datetime.now().date()
        current_month = today.month
        current_year = today.year

        total = len(self._eventos)
        entregas = sum(1 for e in self._eventos.values() if e["type"] == "entrega")
        reunioes = sum(1 for e in self._eventos.values() if e["type"] == "reuniao")
        homeoffice = sum(
            1
            for e in self._eventos.values()
            if e["type"] == "homeoffice" and not e.get("isHomeOfficeReminder")
        )

        this_month = sum(
            1
            for e in self._eventos.values()
            if datetime.fromisoformat(e["date"]).month == current_month
            and datetime.fromisoformat(e["date"]).year == current_year
        )

        return {
            "total": total,
            "entregas": entregas,
            "reunioes": reunioes,
            "homeOffice": homeoffice,
            "thisMonth": this_month,
        }


# Singleton para compartilhar entre requests
_service_instance = None


def get_calendario_service() -> CalendarioEventosService:
    """Retorna instância singleton do serviço"""
    global _service_instance
    if _service_instance is None:
        _service_instance = CalendarioEventosService()
    return _service_instance
