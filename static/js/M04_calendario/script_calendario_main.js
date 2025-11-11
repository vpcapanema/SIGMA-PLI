// SIGMA-PLI - M04: Calendário - Script Principal
// Arquivo: script_calendario_main.js
// Gerenciamento do estado e lógica principal do calendário

/* ========================================
   ESTADO GLOBAL DO CALENDÁRIO
======================================== */

const CalendarioState = {
    current: new Date(),
    events: [],
    filters: {
        type: 'all',
        user: '',
        module: 'all'
    },
    view: 'month' // month, week, list, gantt
};

/* ========================================
   UTILIDADES E FORMATAÇÃO
======================================== */

const CalendarioUtils = {
    formatDateKey(date) {
        const y = date.getFullYear();
        const m = String(date.getMonth() + 1).padStart(2, '0');
        const d = String(date.getDate()).padStart(2, '0');
        return `${y}-${m}-${d}`;
    },

    parseDate(str) {
        const [y, m, d] = str.split('-').map(Number);
        return new Date(y, m - 1, d);
    },

    uuid() {
        return 'evt-' + Math.random().toString(16).slice(2) + Date.now().toString(16);
    },

    formatMonthYear(date) {
        const monthName = date.toLocaleString('pt-BR', { month: 'long' });
        return `${monthName.charAt(0).toUpperCase() + monthName.slice(1)} ${date.getFullYear()}`;
    },

    isToday(dateStr) {
        return dateStr === this.formatDateKey(new Date());
    },

    daysBetween(date1, date2) {
        const d1 = typeof date1 === 'string' ? this.parseDate(date1) : date1;
        const d2 = typeof date2 === 'string' ? this.parseDate(date2) : date2;
        const diffTime = Math.abs(d2 - d1);
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }
};

/* ========================================
   FILTROS E BUSCA
======================================== */

const CalendarioFilters = {
    getFilterType() {
        return document.getElementById('filter-type')?.value || 'all';
    },

    getFilterUser() {
        return document.getElementById('filter-user')?.value.trim().toLowerCase() || '';
    },

    getFilterModule() {
        return document.getElementById('filter-module')?.value || 'all';
    },

    getFilterSearch() {
        return document.getElementById('filter-search')?.value.trim().toLowerCase() || '';
    },

    updateFilters() {
        CalendarioState.filters = {
            type: this.getFilterType(),
            user: this.getFilterUser(),
            module: this.getFilterModule(),
            search: this.getFilterSearch()
        };

        // Atualizar contador de resultados
        this.updateResultsCount();

        // Re-renderizar calendário
        CalendarioRenderer.renderCalendar();
    },

    eventMatchesFilters(evt) {
        const { type, user, module, search } = CalendarioState.filters;

        // Filtro de busca por texto (título, descrição, localização)
        if (search) {
            const searchableText = [
                evt.titulo || evt.title || '',
                evt.descricao || evt.description || '',
                evt.localizacao || evt.location || '',
                evt.responsavel || evt.user || ''
            ].join(' ').toLowerCase();

            if (!searchableText.includes(search)) {
                return false;
            }
        }

        // Filtro de tipo
        if (type !== 'all' && evt.tipo !== type && evt.type !== type) {
            if (!(type === 'homeoffice' && evt.isHomeOfficeReminder)) {
                return false;
            }
        }

        // Filtro de usuário/responsável
        if (user) {
            const eventUser = (evt.responsavel || evt.user || '').toLowerCase();
            if (!eventUser.includes(user)) {
                return false;
            }
        }

        // Filtro de módulo
        if (module !== 'all') {
            const eventModule = evt.modulo || evt.module || '';
            if (eventModule !== module) {
                return false;
            }
        }

        return true;
    },

    updateResultsCount() {
        const container = document.getElementById('filter-results');
        if (!container) return;

        const events = CalendarioState.events || [];
        const filtered = events.filter(evt => this.eventMatchesFilters(evt));

        if (filtered.length === events.length) {
            container.innerHTML = '';
            container.style.display = 'none';
        } else {
            container.style.display = 'block';
            container.innerHTML = `
                <div class="filter-results-content">
                    <span>📊 ${filtered.length} de ${events.length} eventos</span>
                </div>
            `;
        }
    }
};

/* ========================================
   RENDERIZAÇÃO DO CALENDÁRIO (MODO MÊS)
======================================== */

const CalendarioRenderer = {
    renderCalendar() {
        const monthYearLabel = document.getElementById('monthYearLabel');
        const grid = document.getElementById('calendarGrid');

        if (!grid || !monthYearLabel) return;

        grid.innerHTML = '';

        const year = CalendarioState.current.getFullYear();
        const month = CalendarioState.current.getMonth();

        monthYearLabel.textContent = CalendarioUtils.formatMonthYear(CalendarioState.current);

        const firstDayOfMonth = new Date(year, month, 1);
        const lastDayOfMonth = new Date(year, month + 1, 0);
        const startWeekDay = (firstDayOfMonth.getDay() + 6) % 7; // Segunda como primeiro dia
        const daysInMonth = lastDayOfMonth.getDate();

        // Cabeçalho dos dias da semana
        const weekdays = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
        weekdays.forEach(label => {
            const el = document.createElement('div');
            el.className = 'calendar-day-header';
            el.textContent = label;
            grid.appendChild(el);
        });

        // Dias do mês anterior (preencher início)
        const prevMonthLastDay = new Date(year, month, 0).getDate();
        for (let i = 0; i < startWeekDay; i++) {
            const day = prevMonthLastDay - startWeekDay + 1 + i;
            const cell = this.createDayCell(day, true, new Date(year, month - 1, day));
            grid.appendChild(cell);
        }

        // Dias do mês atual
        for (let day = 1; day <= daysInMonth; day++) {
            const cellDate = new Date(year, month, day);
            const cell = this.createDayCell(day, false, cellDate);
            grid.appendChild(cell);
        }

        // Completar última linha com dias do próximo mês
        const totalCells = 7 + startWeekDay + daysInMonth;
        const remaining = totalCells % 7 === 0 ? 0 : 7 - (totalCells % 7);
        for (let i = 1; i <= remaining; i++) {
            const cell = this.createDayCell(i, true, new Date(year, month + 1, i));
            grid.appendChild(cell);
        }
    },

    createDayCell(day, isOutside, date) {
        const dateKey = CalendarioUtils.formatDateKey(date);

        // Garante que events é um array
        const events = Array.isArray(CalendarioState.events) ? CalendarioState.events : [];

        const eventsForDay = events.filter(e =>
            e && e.date === dateKey && CalendarioFilters.eventMatchesFilters(e)
        );

        const cell = document.createElement('div');
        cell.className = 'calendar-day';

        if (isOutside) {
            cell.classList.add('outside');
        }

        if (CalendarioUtils.isToday(dateKey)) {
            cell.classList.add('today');
        }

        if (eventsForDay.length > 0) {
            cell.classList.add('has-events');
        }

        // Verificar se é feriado
        const feriado = CalendarioFeriados.getFeriadoInfo(dateKey);
        if (feriado) {
            cell.classList.add('feriado');
            cell.title = feriado.nome;
        }

        // Número do dia
        const num = document.createElement('div');
        num.className = 'calendar-day-number';
        num.textContent = day;

        // Adiciona ícone de feriado
        if (feriado) {
            const feriadoIcon = document.createElement('span');
            feriadoIcon.className = 'feriado-icon';
            feriadoIcon.textContent = '🎉';
            feriadoIcon.title = feriado.nome;
            num.appendChild(feriadoIcon);
        }

        cell.appendChild(num);

        // Eventos (máximo 3 visíveis)
        eventsForDay.slice(0, 3).forEach(evt => {
            const pill = this.createEventPill(evt);
            cell.appendChild(pill);
        });

        // Indicador "+N" se houver mais eventos
        if (eventsForDay.length > 3) {
            const more = document.createElement('div');
            more.className = 'event-pill event-more';
            more.textContent = `+${eventsForDay.length - 3}`;
            cell.appendChild(more);
        }

        // Click handler para abrir detalhes
        cell.addEventListener('click', () => this.showDayDetails(dateKey, eventsForDay, feriado));

        return cell;
    },

    createEventPill(evt) {
        const pill = document.createElement('div');
        pill.className = 'event-pill ' + this.getEventClass(evt);
        pill.title = evt.title || 'Evento';

        const dot = document.createElement('span');
        dot.className = 'dot';
        pill.appendChild(dot);

        pill.appendChild(document.createTextNode(this.shortEventLabel(evt)));

        return pill;
    },

    getEventClass(evt) {
        if (evt.isHomeOfficeReminder) return 'event-homeoffice';
        switch (evt.type) {
            case 'entrega': return 'event-entrega';
            case 'reuniao': return 'event-reuniao';
            case 'homeoffice': return 'event-homeoffice';
            default: return '';
        }
    },

    shortEventLabel(evt) {
        if (evt.isHomeOfficeReminder) {
            return `Confirma HO - ${evt.user || ''}`.trim();
        }
        if (evt.type === 'homeoffice') {
            return `HO ${evt.user || ''}`.trim();
        }
        return evt.title || 'Evento';
    },

    showDayDetails(dateKey, events, feriado) {
        // Atualizar label da data
        const label = document.getElementById('selected-date-label');
        if (label) {
            const formatted = CalendarioUtils.formatDateDisplay(dateKey);
            label.textContent = formatted;

            // Adicionar informação de feriado se existir
            if (feriado) {
                const feriadoInfo = document.createElement('div');
                feriadoInfo.className = 'feriado-info';
                feriadoInfo.style.cssText = 'background: rgba(243, 156, 18, 0.2); color: #fbbf24; padding: 0.5rem; border-radius: 6px; margin-top: 0.5rem; font-size: 0.85rem;';
                feriadoInfo.innerHTML = `🎉 <strong>${feriado.nome}</strong> (${feriado.tipo.replace('_', ' ')})`;
                label.appendChild(feriadoInfo);
            }
        }

        // Renderizar lista de eventos
        if (typeof CalendarioEventsList !== 'undefined') {
            CalendarioEventsList.renderForDate(dateKey, events);
        }

        console.log('Detalhes do dia:', dateKey, events, feriado);
    },
};

/* ========================================
   NAVEGAÇÃO DO CALENDÁRIO
======================================== */

const CalendarioNavigation = {
    prevMonth() {
        CalendarioState.current.setMonth(CalendarioState.current.getMonth() - 1);
        CalendarioRenderer.renderCalendar();
        this.updateStatistics();
    },

    nextMonth() {
        CalendarioState.current.setMonth(CalendarioState.current.getMonth() + 1);
        CalendarioRenderer.renderCalendar();
        this.updateStatistics();
    },

    goToday() {
        CalendarioState.current = new Date();
        CalendarioRenderer.renderCalendar();
        this.updateStatistics();
    },

    updateStatistics() {
        const stats = this.calculateStats();
        this.renderStats(stats);
    },

    calculateStats() {
        const currentMonth = CalendarioState.current.getMonth();
        const currentYear = CalendarioState.current.getFullYear();

        // Garante que events é um array
        const events = Array.isArray(CalendarioState.events) ? CalendarioState.events : [];

        return {
            total: events.length,
            entregas: events.filter(e => e && e.type === 'entrega').length,
            reunioes: events.filter(e => e && e.type === 'reuniao').length,
            homeOffice: events.filter(e => e && e.type === 'homeoffice').length,
            thisMonth: events.filter(e => {
                if (!e || !e.date) return false;
                const d = CalendarioUtils.parseDate(e.date);
                return d.getMonth() === currentMonth && d.getFullYear() === currentYear;
            }).length
        };
    },

    renderStats(stats) {
        const container = document.getElementById('calendar-stats');
        if (!container) return;

        container.innerHTML = `
            <div class="stat-item">
                <span class="stat-label">Total</span>
                <span class="stat-value">${stats.total}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Entregas</span>
                <span class="stat-value stat-entrega">${stats.entregas}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Reuniões</span>
                <span class="stat-value stat-reuniao">${stats.reunioes}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Este mês</span>
                <span class="stat-value">${stats.thisMonth}</span>
            </div>
        `;
    }
};

/* ========================================
   NOTIFICAÇÕES E ALERTAS
======================================== */

const CalendarioNotifications = {
    checkUpcomingEvents() {
        const today = new Date();
        const in3Days = new Date(today);
        in3Days.setDate(today.getDate() + 3);

        // Garante que events é um array
        const events = Array.isArray(CalendarioState.events) ? CalendarioState.events : [];

        const upcoming = events.filter(evt => {
            if (!evt || !evt.date) return false;
            if (!CalendarioFilters.eventMatchesFilters(evt)) return false;
            const evtDate = CalendarioUtils.parseDate(evt.date);
            return evtDate >= today && evtDate <= in3Days;
        });

        if (upcoming.length > 0) {
            this.showNotificationBadge(upcoming.length);
            return upcoming;
        }

        return [];
    },

    showNotificationBadge(count) {
        const badge = document.getElementById('notification-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = 'inline-flex';
        }
    },

    hideNotificationBadge() {
        const badge = document.getElementById('notification-badge');
        if (badge) {
            badge.style.display = 'none';
        }
    }
};

/* ========================================
   INICIALIZAÇÃO
======================================== */

async function initCalendario() {
    // Carregar feriados do ano atual
    const year = CalendarioState.current.getFullYear();
    await CalendarioFeriados.loadYear(year);

    // Inicializar modal
    CalendarioModal.init();

    // Renderizar calendário inicial
    CalendarioRenderer.renderCalendar();

    // Verificar eventos próximos
    CalendarioNotifications.checkUpcomingEvents();

    // Atualizar estatísticas
    CalendarioNavigation.updateStatistics();

    // Setup de listeners de filtros
    setupFilterListeners();

    console.log('✅ Calendário SIGMA-PLI M04 inicializado com feriados');
}// ========================================
// MODAL DE EVENTOS
// ========================================

const CalendarioEventsList = {
    renderForDate(dateKey, events) {
        const container = document.getElementById('eventos-list-container');
        const dateLabel = document.getElementById('selected-date-label');

        if (!container || !dateLabel) return;

        // Formatar data para exibição
        const [year, month, day] = dateKey.split('-');
        const date = new Date(year, month - 1, day);
        const dateStr = date.toLocaleDateString('pt-BR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        dateLabel.textContent = dateStr.charAt(0).toUpperCase() + dateStr.slice(1);

        if (!events || events.length === 0) {
            container.innerHTML = '<div class="calendario-empty">Nenhum evento para esta data</div>';
            return;
        }

        // Renderizar eventos
        container.innerHTML = events.map(event => this.renderEventCard(event)).join('');

        // Adicionar event listeners nos botões
        container.querySelectorAll('.btn-edit-event').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const eventId = e.target.closest('.btn-edit-event').dataset.eventId;
                const event = events.find(ev => ev.id == eventId);
                if (event) CalendarioModal.open(null, event);
            });
        });

        container.querySelectorAll('.btn-delete-event').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const eventId = e.target.closest('.btn-delete-event').dataset.eventId;
                if (confirm('⚠️ Tem certeza que deseja excluir este evento?')) {
                    await this.deleteEvent(eventId);
                }
            });
        });
    },

    renderEventCard(event) {
        const typeColors = {
            entrega: '#3b82f6',
            reuniao: '#10b981',
            homeoffice: '#8b5cf6'
        };

        const color = typeColors[event.tipo] || '#6b7280';
        const horaInicio = event.data_inicio ? new Date(event.data_inicio).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '';
        const horaFim = event.data_fim ? new Date(event.data_fim).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '';

        return `
            <div class="evento-card" style="border-left: 4px solid ${color}">
                <div class="evento-card-header">
                    <h3>${event.titulo}</h3>
                    <div class="evento-card-actions">
                        <button class="btn-edit-event" data-event-id="${event.id}" title="Editar">
                            ✏️
                        </button>
                        <button class="btn-delete-event" data-event-id="${event.id}" title="Excluir">
                            🗑️
                        </button>
                    </div>
                </div>
                ${event.descricao ? `<p class="evento-descricao">${event.descricao}</p>` : ''}
                <div class="evento-meta">
                    ${horaInicio ? `<span>⏰ ${horaInicio}${horaFim ? ` - ${horaFim}` : ''}</span>` : ''}
                    ${event.responsavel ? `<span>👤 ${event.responsavel}</span>` : ''}
                    ${event.localizacao ? `<span>📍 ${event.localizacao}</span>` : ''}
                </div>
                <div class="evento-tags">
                    <span class="evento-tag" style="background-color: ${color}20; color: ${color}">
                        ${event.tipo}
                    </span>
                    ${event.modulo ? `<span class="evento-tag-secondary">${event.modulo}</span>` : ''}
                </div>
            </div>
        `;
    },

    async deleteEvent(eventId) {
        try {
            await CalendarioAPI.deleteEvento(eventId);
            alert('✅ Evento excluído com sucesso!');

            // Recarregar calendário
            CalendarioRenderer.renderCalendar();
            CalendarioNavigation.updateStatistics();
        } catch (error) {
            console.error('Erro ao excluir evento:', error);
            alert('❌ Erro ao excluir evento. Tente novamente.');
        }
    }
};

const CalendarioModal = {
    modal: null,
    form: null,
    isEditMode: false,

    init() {
        this.modal = document.getElementById('modal-evento');
        this.form = document.getElementById('form-evento');

        if (!this.modal || !this.form) return;

        // Event listeners para fechar modal
        document.getElementById('btn-close-modal')?.addEventListener('click', () => this.close());
        document.getElementById('btn-cancel-modal')?.addEventListener('click', () => this.close());

        // Fechar ao clicar no overlay
        this.modal.querySelector('.calendario-modal-overlay')?.addEventListener('click', () => this.close());

        // Submit do formulário
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));

        // Sincronizar data fim com data início
        document.getElementById('evento-data-inicio')?.addEventListener('change', (e) => {
            const dataFim = document.getElementById('evento-data-fim');
            if (dataFim && !dataFim.value) {
                dataFim.value = e.target.value;
            }
        });
    },

    open(date = null, evento = null) {
        if (!this.modal) return;

        this.isEditMode = !!evento;
        const modalTitle = document.getElementById('modal-title');

        if (this.isEditMode) {
            modalTitle.textContent = 'Editar Evento';
            this.fillForm(evento);
        } else {
            modalTitle.textContent = 'Novo Evento';
            this.form.reset();

            // Preencher com data selecionada
            if (date) {
                document.getElementById('evento-data-inicio').value = date;
                document.getElementById('evento-data-fim').value = date;
            }
        }

        this.modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    },

    close() {
        if (!this.modal) return;

        this.modal.classList.remove('show');
        document.body.style.overflow = '';
        this.form.reset();
        this.isEditMode = false;
    },

    fillForm(evento) {
        document.getElementById('evento-id').value = evento.id || '';
        document.getElementById('evento-titulo').value = evento.titulo || '';
        document.getElementById('evento-descricao').value = evento.descricao || '';
        document.getElementById('evento-tipo').value = evento.tipo || '';
        document.getElementById('evento-modulo').value = evento.modulo || '';
        document.getElementById('evento-responsavel').value = evento.responsavel || '';
        document.getElementById('evento-localizacao').value = evento.localizacao || '';

        if (evento.data_inicio) {
            const dataInicio = new Date(evento.data_inicio);
            document.getElementById('evento-data-inicio').value = dataInicio.toISOString().split('T')[0];
            document.getElementById('evento-hora-inicio').value = dataInicio.toTimeString().slice(0, 5);
        }

        if (evento.data_fim) {
            const dataFim = new Date(evento.data_fim);
            document.getElementById('evento-data-fim').value = dataFim.toISOString().split('T')[0];
            document.getElementById('evento-hora-fim').value = dataFim.toTimeString().slice(0, 5);
        }
    },

    async handleSubmit(e) {
        e.preventDefault();

        const formData = new FormData(this.form);
        const eventoData = {
            titulo: formData.get('titulo'),
            descricao: formData.get('descricao'),
            tipo: formData.get('tipo'),
            modulo: formData.get('modulo'),
            responsavel: formData.get('responsavel'),
            localizacao: formData.get('localizacao'),
            data_inicio: `${formData.get('data_inicio')}T${formData.get('hora_inicio')}:00`,
            data_fim: formData.get('data_fim') ? `${formData.get('data_fim')}T${formData.get('hora_fim')}:00` : null
        };

        try {
            let response;

            if (this.isEditMode) {
                const id = formData.get('id');
                response = await CalendarioAPI.updateEvento(id, eventoData);
            } else {
                response = await CalendarioAPI.createEvento(eventoData);
            }

            if (response && response.id) {
                alert(`✅ Evento ${this.isEditMode ? 'atualizado' : 'criado'} com sucesso!`);
                this.close();

                // Recarregar calendário
                CalendarioRenderer.renderCalendar();
                CalendarioNavigation.updateStatistics();
            }
        } catch (error) {
            console.error('Erro ao salvar evento:', error);
            alert('❌ Erro ao salvar evento. Tente novamente.');
        }
    }
};

function setupFilterListeners() {
    const filterType = document.getElementById('filter-type');
    const filterUser = document.getElementById('filter-user');
    const filterModule = document.getElementById('filter-module');
    const filterSearch = document.getElementById('filter-search');

    if (filterType) {
        filterType.addEventListener('change', () => {
            CalendarioFilters.updateFilters();
        });
    }

    if (filterUser) {
        filterUser.addEventListener('input', () => {
            CalendarioFilters.updateFilters();
        });
    }

    if (filterModule) {
        filterModule.addEventListener('change', () => {
            CalendarioFilters.updateFilters();
        });
    }

    if (filterSearch) {
        filterSearch.addEventListener('input', () => {
            CalendarioFilters.updateFilters();
        });
    }
}

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCalendario);
} else {
    initCalendario();
}
