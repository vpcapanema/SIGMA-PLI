// SIGMA-PLI - M04: Calendário - API e Persistência
// Arquivo: script_calendario_api.js
// Comunicação com backend FastAPI e gerenciamento de dados

/* ========================================
   CONFIGURAÇÃO DA API
======================================== */

const CalendarioAPI = {
    baseURL: '/api/v1/calendario',

    // Headers padrão para todas as requisições
    getHeaders() {
        return {
            'Content-Type': 'application/json',
            // TODO: Adicionar token de autenticação quando M01 estiver implementado
            // 'Authorization': `Bearer ${getAuthToken()}`
        };
    },

    // Tratamento de erros HTTP
    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Erro desconhecido' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }
        return response.json();
    }
};

/* ========================================
   CRUD DE EVENTOS
======================================== */

const CalendarioEventos = {
    /**
     * Carregar todos os eventos
     * GET /api/v1/calendario/eventos
     */
    async loadAll() {
        try {
            const response = await fetch(`${CalendarioAPI.baseURL}/eventos`, {
                method: 'GET',
                headers: CalendarioAPI.getHeaders()
            });

            const data = await CalendarioAPI.handleResponse(response);

            // A API retorna {eventos: [...], total: N}
            const events = Array.isArray(data) ? data : (data.eventos || []);
            CalendarioState.events = events;

            // Atualizar interface
            CalendarioRenderer.renderCalendar();
            if (typeof CalendarioEventsList !== 'undefined') {
                CalendarioEventsList.render();
            }
            CalendarioNotifications.checkUpcomingEvents();

            console.log(`✅ ${events.length} eventos carregados`);
            return events;
        } catch (error) {
            console.error('❌ Erro ao carregar eventos:', error);
            this.showError('Não foi possível carregar os eventos. Usando dados locais.');
            return CalendarioState.events;
        }
    },

    /**
     * Criar novo evento
     * POST /api/v1/calendario/eventos
     */
    async create(eventData) {
        try {
            const response = await fetch(`${CalendarioAPI.baseURL}/eventos`, {
                method: 'POST',
                headers: CalendarioAPI.getHeaders(),
                body: JSON.stringify(eventData)
            });

            const savedEvent = await CalendarioAPI.handleResponse(response);
            CalendarioState.events.push(savedEvent);

            // Se for Home Office, criar lembrete automático
            if (eventData.type === 'homeoffice') {
                await this.createHomeOfficeReminder(savedEvent);
            }

            // Atualizar interface
            CalendarioRenderer.renderCalendar();
            if (typeof CalendarioEventsList !== 'undefined') {
                CalendarioEventsList.render();
            }

            this.showSuccess('Evento criado com sucesso!');
            console.log('✅ Evento criado:', savedEvent.id);

            return savedEvent;
        } catch (error) {
            console.error('❌ Erro ao criar evento:', error);
            this.showError('Não foi possível criar o evento: ' + error.message);
            return null;
        }
    },

    /**
     * Atualizar evento existente
     * PUT /api/v1/calendario/eventos/{id}
     */
    async update(eventId, eventData) {
        try {
            const response = await fetch(`${CalendarioAPI.baseURL}/eventos/${eventId}`, {
                method: 'PUT',
                headers: CalendarioAPI.getHeaders(),
                body: JSON.stringify(eventData)
            });

            const updatedEvent = await CalendarioAPI.handleResponse(response);

            // Atualizar no state local
            const index = CalendarioState.events.findIndex(e => e.id === eventId);
            if (index !== -1) {
                CalendarioState.events[index] = updatedEvent;
            }

            // Atualizar interface
            CalendarioRenderer.renderCalendar();
            if (typeof CalendarioEventsList !== 'undefined') {
                CalendarioEventsList.render();
            }

            this.showSuccess('Evento atualizado com sucesso!');
            console.log('✅ Evento atualizado:', eventId);

            return updatedEvent;
        } catch (error) {
            console.error('❌ Erro ao atualizar evento:', error);
            this.showError('Não foi possível atualizar o evento: ' + error.message);
            return null;
        }
    },

    /**
     * Deletar evento
     * DELETE /api/v1/calendario/eventos/{id}
     */
    async delete(eventId) {
        try {
            const response = await fetch(`${CalendarioAPI.baseURL}/eventos/${eventId}`, {
                method: 'DELETE',
                headers: CalendarioAPI.getHeaders()
            });

            await CalendarioAPI.handleResponse(response);

            // Remover do state local
            const index = CalendarioState.events.findIndex(e => e.id === eventId);
            if (index !== -1) {
                const event = CalendarioState.events[index];
                CalendarioState.events.splice(index, 1);

                // Se for Home Office, remover lembretes vinculados
                if (event.type === 'homeoffice' && !event.isHomeOfficeReminder) {
                    this.deleteHomeOfficeReminders(event);
                }
            }

            // Atualizar interface
            CalendarioRenderer.renderCalendar();
            if (typeof CalendarioEventsList !== 'undefined') {
                CalendarioEventsList.render();
            }

            this.showSuccess('Evento deletado com sucesso!');
            console.log('✅ Evento deletado:', eventId);

            return true;
        } catch (error) {
            console.error('❌ Erro ao deletar evento:', error);
            this.showError('Não foi possível remover o evento: ' + error.message);
            return false;
        }
    },

    /**
     * Criar lembrete automático para Home Office (2 dias antes)
     */
    async createHomeOfficeReminder(hoEvent) {
        const hoDate = CalendarioUtils.parseDate(hoEvent.date);
        const reminderDate = new Date(hoDate);
        reminderDate.setDate(hoDate.getDate() - 2);

        // Só criar se for pelo menos 2 dias no futuro
        if (reminderDate < new Date()) {
            console.log('ℹ️ Home Office muito próximo, lembrete não criado');
            return;
        }

        const reminderEvent = {
            type: 'homeoffice',
            title: `Confirmação Home Office - ${hoEvent.user || hoEvent.title}`,
            user: hoEvent.user,
            date: CalendarioUtils.formatDateKey(reminderDate),
            startTime: '09:00',
            endTime: '09:30',
            location: '',
            notes: `Confirmação automática do Home Office marcado para ${hoEvent.date}.`,
            isHomeOfficeReminder: true,
            linkedEventId: hoEvent.id
        };

        await this.create(reminderEvent);
        console.log('✅ Lembrete de HO criado para', reminderDate);
    },

    /**
     * Remover lembretes vinculados a um Home Office
     */
    async deleteHomeOfficeReminders(hoEvent) {
        const reminders = CalendarioState.events.filter(e =>
            e.isHomeOfficeReminder &&
            e.linkedEventId === hoEvent.id
        );

        for (const reminder of reminders) {
            await this.delete(reminder.id);
        }
    },

    /**
     * Buscar eventos por filtros
     * GET /api/v1/calendario/eventos?type=...&user=...
     */
    async search(filters) {
        try {
            const params = new URLSearchParams();
            if (filters.type && filters.type !== 'all') params.append('type', filters.type);
            if (filters.user) params.append('user', filters.user);
            if (filters.module && filters.module !== 'all') params.append('module', filters.module);
            if (filters.startDate) params.append('start_date', filters.startDate);
            if (filters.endDate) params.append('end_date', filters.endDate);

            const response = await fetch(`${CalendarioAPI.baseURL}/eventos?${params}`, {
                method: 'GET',
                headers: CalendarioAPI.getHeaders()
            });

            return await CalendarioAPI.handleResponse(response);
        } catch (error) {
            console.error('❌ Erro ao buscar eventos:', error);
            return [];
        }
    },

    /**
     * Notificações de UI
     */
    showSuccess(message) {
        this.showToast(message, 'success');
    },

    showError(message) {
        this.showToast(message, 'error');
    },

    showToast(message, type = 'info') {
        // TODO: Implementar sistema de toast/notificação visual
        console.log(`[${type.toUpperCase()}] ${message}`);

        // Fallback temporário com alert
        if (type === 'error') {
            alert(`⚠️ ${message}`);
        }
    }
};

/* ========================================
   SINCRONIZAÇÃO E CACHE
======================================== */

const CalendarioSync = {
    // Chave para localStorage
    STORAGE_KEY: 'sigma_pli_calendario_cache',

    /**
     * Salvar eventos no cache local
     */
    saveToCache() {
        try {
            const data = {
                events: CalendarioState.events,
                lastSync: new Date().toISOString(),
                version: '1.0'
            };
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
            console.log('✅ Cache salvo localmente');
        } catch (error) {
            console.warn('⚠️ Erro ao salvar cache:', error);
        }
    },

    /**
     * Carregar eventos do cache local
     */
    loadFromCache() {
        try {
            const cached = localStorage.getItem(this.STORAGE_KEY);
            if (!cached) return null;

            const data = JSON.parse(cached);
            console.log(`ℹ️ Cache carregado (última sync: ${data.lastSync})`);
            return data.events || [];
        } catch (error) {
            console.warn('⚠️ Erro ao carregar cache:', error);
            return null;
        }
    },

    /**
     * Limpar cache local
     */
    clearCache() {
        localStorage.removeItem(this.STORAGE_KEY);
        console.log('🗑️ Cache limpo');
    },

    /**
     * Sincronização completa com o servidor
     */
    async sync() {
        console.log('🔄 Sincronizando com servidor...');

        try {
            // Tentar carregar do servidor
            const serverEvents = await CalendarioEventos.loadAll();

            // Salvar no cache local
            this.saveToCache();

            return serverEvents;
        } catch (error) {
            console.warn('⚠️ Erro na sincronização, usando cache local');

            // Fallback para cache local
            const cachedEvents = this.loadFromCache();
            if (cachedEvents) {
                CalendarioState.events = cachedEvents;
                CalendarioRenderer.renderCalendar();
                if (typeof CalendarioEventsList !== 'undefined') {
                    CalendarioEventsList.render();
                }
            }

            return cachedEvents || [];
        }
    }
};

/* ========================================
   API DE FERIADOS
======================================== */

const CalendarioFeriados = {
    feriados: [],

    /**
     * Carregar feriados de um ano
     */
    async loadYear(year) {
        try {
            const response = await fetch(`${CalendarioAPI.baseURL}/feriados/${year}`, {
                method: 'GET',
                headers: CalendarioAPI.getHeaders()
            });

            const data = await CalendarioAPI.handleResponse(response);
            this.feriados = data.feriados || [];

            console.log(`✅ ${this.feriados.length} feriados carregados para ${year}`);
            return this.feriados;
        } catch (error) {
            console.error('❌ Erro ao carregar feriados:', error);
            return [];
        }
    },

    /**
     * Carregar feriados de um mês específico
     */
    async loadMonth(year, month) {
        try {
            const response = await fetch(`${CalendarioAPI.baseURL}/feriados/${year}/${month}`, {
                method: 'GET',
                headers: CalendarioAPI.getHeaders()
            });

            const data = await CalendarioAPI.handleResponse(response);
            return data.feriados || [];
        } catch (error) {
            console.error('❌ Erro ao carregar feriados do mês:', error);
            return [];
        }
    },

    /**
     * Obter próximo feriado
     */
    async getNext() {
        try {
            const response = await fetch(`${CalendarioAPI.baseURL}/feriados/proximo`, {
                method: 'GET',
                headers: CalendarioAPI.getHeaders()
            });

            const data = await CalendarioAPI.handleResponse(response);
            return data.proximo_feriado;
        } catch (error) {
            console.error('❌ Erro ao buscar próximo feriado:', error);
            return null;
        }
    },

    /**
     * Verificar se uma data é feriado
     */
    async checkDate(dateStr) {
        try {
            const response = await fetch(`${CalendarioAPI.baseURL}/feriados/verificar/${dateStr}`, {
                method: 'GET',
                headers: CalendarioAPI.getHeaders()
            });

            const data = await CalendarioAPI.handleResponse(response);
            return data;
        } catch (error) {
            console.error('❌ Erro ao verificar feriado:', error);
            return { eh_feriado: false };
        }
    },

    /**
     * Verifica se uma data está nos feriados carregados
     */
    isFeriado(dateStr) {
        return this.feriados.some(f => f.data === dateStr);
    },

    /**
     * Obter informações do feriado de uma data
     */
    getFeriadoInfo(dateStr) {
        return this.feriados.find(f => f.data === dateStr);
    }
};

/* ========================================
   INICIALIZAÇÃO DA API
======================================== */

async function initCalendarioAPI() {
    console.log('🚀 Inicializando API do Calendário...');

    // Tentar sincronizar com servidor
    await CalendarioSync.sync();

    // Configurar sincronização automática a cada 5 minutos
    setInterval(() => {
        CalendarioSync.sync();
    }, 5 * 60 * 1000);

    // Salvar cache antes de sair da página
    window.addEventListener('beforeunload', () => {
        CalendarioSync.saveToCache();
    });

    console.log('✅ API do Calendário inicializada');
}

// Auto-inicializar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCalendarioAPI);
} else {
    initCalendarioAPI();
}
