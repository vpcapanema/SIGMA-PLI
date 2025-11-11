// SIGMA-PLI - M04: Calendário - Integrações Externas
// Arquivo: script_calendario_integrations.js
// Exportação ICS, CSV, Google Calendar, Microsoft Teams/Outlook

/* ========================================
   EXPORTAÇÃO DE EVENTOS
======================================== */

const CalendarioExport = {
    showExportMenu() {
        const events = CalendarioState.events || [];

        if (events.length === 0) {
            alert('❌ Não há eventos para exportar.');
            return;
        }

        const options = `
            <div class="export-menu-overlay" onclick="this.parentElement.remove()">
                <div class="export-menu-content" onclick="event.stopPropagation()">
                    <h3>Exportar Calendário</h3>
                    <p>${events.length} evento(s) disponível(is)</p>
                    
                    <div class="export-options">
                        <button onclick="CalendarioExport.exportICS()" class="export-btn">
                            📅 Exportar iCalendar (.ics)
                        </button>
                        <button onclick="CalendarioExport.exportCSV()" class="export-btn">
                            📊 Exportar CSV (.csv)
                        </button>
                        <button onclick="CalendarioExport.exportJSON()" class="export-btn">
                            📄 Exportar JSON (.json)
                        </button>
                    </div>
                    
                    <button onclick="this.closest('.export-menu-overlay').remove()" class="export-btn-cancel">
                        Cancelar
                    </button>
                </div>
            </div>
        `;

        // Adicionar ao body
        const div = document.createElement('div');
        div.innerHTML = options;
        document.body.appendChild(div.firstElementChild);
    },

    exportICS() {
        const events = CalendarioState.events || [];
        const ics = this.generateICS(events);
        this.downloadFile(ics, 'calendario-sigma-pli.ics', 'text/calendar');
        document.querySelector('.export-menu-overlay')?.remove();
        alert('✅ Arquivo .ics baixado com sucesso!');
    },

    exportCSV() {
        const events = CalendarioState.events || [];
        const csv = this.generateCSV(events);
        this.downloadFile(csv, 'calendario-sigma-pli.csv', 'text/csv');
        document.querySelector('.export-menu-overlay')?.remove();
        alert('✅ Arquivo .csv baixado com sucesso!');
    },

    exportJSON() {
        const events = CalendarioState.events || [];
        const json = JSON.stringify(events, null, 2);
        this.downloadFile(json, 'calendario-sigma-pli.json', 'application/json');
        document.querySelector('.export-menu-overlay')?.remove();
        alert('✅ Arquivo .json baixado com sucesso!');
    },

    generateICS(events) {
        let ics = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//SIGMA-PLI//Calendario//PT-BR',
            'CALSCALE:GREGORIAN',
            'METHOD:PUBLISH',
            'X-WR-CALNAME:SIGMA-PLI Calendário',
            'X-WR-TIMEZONE:America/Sao_Paulo'
        ].join('\r\n') + '\r\n';

        events.forEach(evt => {
            const dtStart = this.formatICSDate(evt.data_inicio);
            const dtEnd = this.formatICSDate(evt.data_fim || evt.data_inicio);
            const uid = `${evt.id}@sigma-pli`;
            const timestamp = this.formatICSDate(new Date());

            ics += [
                'BEGIN:VEVENT',
                `UID:${uid}`,
                `DTSTAMP:${timestamp}`,
                `DTSTART:${dtStart}`,
                `DTEND:${dtEnd}`,
                `SUMMARY:${this.escapeICS(evt.titulo)}`,
                evt.descricao ? `DESCRIPTION:${this.escapeICS(evt.descricao)}` : '',
                evt.localizacao ? `LOCATION:${this.escapeICS(evt.localizacao)}` : '',
                `CATEGORIES:${evt.tipo}`,
                'STATUS:CONFIRMED',
                'END:VEVENT'
            ].filter(Boolean).join('\r\n') + '\r\n';
        });

        ics += 'END:VCALENDAR\r\n';
        return ics;
    },

    generateCSV(events) {
        const headers = ['ID', 'Título', 'Descrição', 'Data Início', 'Data Fim', 'Tipo', 'Módulo', 'Responsável', 'Localização'];
        const rows = events.map(evt => [
            evt.id,
            this.escapeCSV(evt.titulo),
            this.escapeCSV(evt.descricao || ''),
            evt.data_inicio ? new Date(evt.data_inicio).toLocaleString('pt-BR') : '',
            evt.data_fim ? new Date(evt.data_fim).toLocaleString('pt-BR') : '',
            evt.tipo,
            evt.modulo || '',
            evt.responsavel || '',
            evt.localizacao || ''
        ]);

        return [headers, ...rows].map(row => row.join(',')).join('\n');
    },

    formatICSDate(date) {
        if (!date) return '';
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        return `${year}${month}${day}T${hours}${minutes}${seconds}`;
    },

    escapeICS(text) {
        if (!text) return '';
        return text.replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\n/g, '\\n');
    },

    escapeCSV(text) {
        if (!text) return '';
        text = String(text).replace(/"/g, '""');
        return text.includes(',') || text.includes('"') || text.includes('\n') ? `"${text}"` : text;
    },

    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
};

/* ========================================
   INTEGRAÇÕES COM CALENDÁRIOS EXTERNOS
======================================== */

const CalendarioIntegrations = {
    addToGoogleCalendar() {
        const events = CalendarioState.events || [];

        if (events.length === 0) {
            alert('❌ Não há eventos para adicionar.');
            return;
        }

        // Pegar o primeiro evento ou permitir escolher
        const event = events[0];

        const start = this.formatGoogleDate(event.data_inicio);
        const end = this.formatGoogleDate(event.data_fim || event.data_inicio);

        const params = new URLSearchParams({
            action: 'TEMPLATE',
            text: event.titulo,
            dates: `${start}/${end}`,
            details: event.descricao || '',
            location: event.localizacao || '',
            sf: 'true',
            output: 'xml'
        });

        const url = `https://calendar.google.com/calendar/render?${params.toString()}`;
        window.open(url, '_blank');
    },

    addToOutlook() {
        const events = CalendarioState.events || [];

        if (events.length === 0) {
            alert('❌ Não há eventos para adicionar.');
            return;
        }

        const event = events[0];

        const start = this.formatOutlookDate(event.data_inicio);
        const end = this.formatOutlookDate(event.data_fim || event.data_inicio);

        const params = new URLSearchParams({
            subject: event.titulo,
            body: event.descricao || '',
            startdt: start,
            enddt: end,
            location: event.localizacao || '',
            path: '/calendar/action/compose',
            rru: 'addevent'
        });

        const url = `https://outlook.live.com/calendar/0/deeplink/compose?${params.toString()}`;
        window.open(url, '_blank');
    },

    formatGoogleDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return d.toISOString().replace(/-|:|\.\d+/g, '');
    },

    formatOutlookDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return d.toISOString();
    }
};

/* ========================================
   GERAÇÃO DE ARQUIVOS ICS (iCalendar) - LEGADO
======================================== */

const CalendarioICS = {
    /**
     * Gerar arquivo ICS para um único evento
     */
    generateSingleEventICS(evt) {
        if (!evt || !evt.date) {
            console.error('❌ Evento inválido para export ICS:', evt);
            return null;
        }

        const dtStart = this.buildICSTime(evt.date, evt.startTime || '09:00');
        const dtEnd = this.buildICSTime(evt.date, evt.endTime || this.calculateEndTime(evt.startTime));

        const summary = evt.title || this.getEventLabel(evt);
        const description = this.buildDescription(evt);
        const location = evt.location || '';

        const ics =
            'BEGIN:VCALENDAR\r\n' +
            'VERSION:2.0\r\n' +
            'PRODID:-//SIGMA-PLI//Modulo4-Calendario//PT-BR\r\n' +
            'CALSCALE:GREGORIAN\r\n' +
            'METHOD:PUBLISH\r\n' +
            'X-WR-CALNAME:SIGMA-PLI - Calendário de Eventos\r\n' +
            'X-WR-TIMEZONE:America/Sao_Paulo\r\n' +
            'BEGIN:VEVENT\r\n' +
            `UID:${evt.id}@sigma-pli\r\n` +
            `DTSTAMP:${this.getCurrentICSTime()}\r\n` +
            `DTSTART:${dtStart}\r\n` +
            `DTEND:${dtEnd}\r\n` +
            `SUMMARY:${this.escapeICS(summary)}\r\n` +
            (location ? `LOCATION:${this.escapeICS(location)}\r\n` : '') +
            (description ? `DESCRIPTION:${this.escapeICS(description)}\r\n` : '') +
            `STATUS:CONFIRMED\r\n` +
            `SEQUENCE:0\r\n` +
            `CATEGORIES:${this.getCategoryLabel(evt.type)}\r\n` +
            this.buildAlarms(evt) +
            'END:VEVENT\r\n' +
            'END:VCALENDAR\r\n';

        return ics;
    },

    /**
     * Gerar arquivo ICS com múltiplos eventos
     */
    generateMultipleEventsICS(events) {
        let ics =
            'BEGIN:VCALENDAR\r\n' +
            'VERSION:2.0\r\n' +
            'PRODID:-//SIGMA-PLI//Modulo4-Calendario//PT-BR\r\n' +
            'CALSCALE:GREGORIAN\r\n' +
            'METHOD:PUBLISH\r\n' +
            'X-WR-CALNAME:SIGMA-PLI - Calendário de Eventos\r\n' +
            'X-WR-TIMEZONE:America/Sao_Paulo\r\n';

        events.forEach(evt => {
            const dtStart = this.buildICSTime(evt.date, evt.startTime || '09:00');
            const dtEnd = this.buildICSTime(evt.date, evt.endTime || this.calculateEndTime(evt.startTime));
            const summary = evt.title || this.getEventLabel(evt);
            const description = this.buildDescription(evt);
            const location = evt.location || '';

            ics +=
                'BEGIN:VEVENT\r\n' +
                `UID:${evt.id}@sigma-pli\r\n` +
                `DTSTAMP:${this.getCurrentICSTime()}\r\n` +
                `DTSTART:${dtStart}\r\n` +
                `DTEND:${dtEnd}\r\n` +
                `SUMMARY:${this.escapeICS(summary)}\r\n` +
                (location ? `LOCATION:${this.escapeICS(location)}\r\n` : '') +
                (description ? `DESCRIPTION:${this.escapeICS(description)}\r\n` : '') +
                `STATUS:CONFIRMED\r\n` +
                `CATEGORIES:${this.getCategoryLabel(evt.type)}\r\n` +
                this.buildAlarms(evt) +
                'END:VEVENT\r\n';
        });

        ics += 'END:VCALENDAR\r\n';
        return ics;
    },

    /**
     * Construir timestamp no formato iCalendar (YYYYMMDDTHHMMSS)
     */
    buildICSTime(dateStr, timeStr) {
        const d = CalendarioUtils.parseDate(dateStr);
        const [hh, mm] = (timeStr || '09:00').split(':').map(Number);
        d.setHours(hh, mm || 0, 0, 0);

        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const da = String(d.getDate()).padStart(2, '0');
        const h = String(d.getHours()).padStart(2, '0');
        const mi = String(d.getMinutes()).padStart(2, '0');
        const s = '00';

        return `${y}${m}${da}T${h}${mi}${s}`;
    },

    getCurrentICSTime() {
        const now = new Date();
        return this.buildICSTime(
            CalendarioUtils.formatDateKey(now),
            `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
        );
    },

    calculateEndTime(startTime) {
        if (!startTime) return '10:00';
        const [hh, mm] = startTime.split(':').map(Number);
        const endHour = hh + 1;
        return `${String(endHour).padStart(2, '0')}:${String(mm).padStart(2, '0')}`;
    },

    buildDescription(evt) {
        let desc = evt.notes || '';

        if (evt.isHomeOfficeReminder) {
            desc += '\n\n[Evento gerado automaticamente para confirmação de Home Office]';
        }

        if (evt.user) {
            desc += `\n\nResponsável: ${evt.user}`;
        }

        if (evt.module) {
            desc += `\n\nMódulo: ${evt.module}`;
        }

        desc += '\n\n---\nGerado por SIGMA-PLI - Módulo 4 (Calendário)';

        return desc.trim();
    },

    buildAlarms(evt) {
        // Adicionar alarmes para eventos importantes
        if (evt.type === 'entrega' || evt.type === 'reuniao') {
            return 'BEGIN:VALARM\r\n' +
                'TRIGGER:-PT24H\r\n' +
                'ACTION:DISPLAY\r\n' +
                `DESCRIPTION:Lembrete: ${this.escapeICS(evt.title || 'Evento')}\r\n` +
                'END:VALARM\r\n';
        }
        return '';
    },

    getCategoryLabel(type) {
        switch (type) {
            case 'entrega': return 'Entrega,PLI,Produto';
            case 'reuniao': return 'Reunião,PLI,Agenda';
            case 'homeoffice': return 'Home Office,PLI';
            default: return 'PLI';
        }
    },

    escapeICS(str) {
        return String(str)
            .replace(/\\/g, '\\\\')
            .replace(/;/g, '\\;')
            .replace(/,/g, '\\,')
            .replace(/\r?\n/g, '\\n');
    },

    getEventLabel(evt) {
        if (evt.isHomeOfficeReminder) {
            return `Confirmação HO - ${evt.user || ''}`.trim();
        }
        if (evt.type === 'homeoffice') {
            return `Home Office - ${evt.user || ''}`.trim();
        }
        return evt.title || 'Evento PLI';
    },

    /**
     * Download de arquivo ICS
     */
    downloadICS(evt) {
        if (!evt || !evt.date) {
            console.error('❌ Evento inválido para download ICS:', evt);
            alert('Erro: Evento inválido para exportação');
            return;
        }

        const ics = this.generateSingleEventICS(evt);
        if (!ics) {
            alert('Erro ao gerar arquivo ICS');
            return;
        }

        const blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;

        const safeTitle = (evt.title || 'evento')
            .replace(/[^\w\d\-]+/g, '_')
            .slice(0, 40);
        a.download = `${safeTitle}_${evt.date}.ics`;

        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log('📥 Download ICS:', evt.id);
    },

    /**
     * Download de todos os eventos filtrados
     */
    downloadAllICS() {
        const filtered = CalendarioState.events.filter(CalendarioFilters.eventMatchesFilters);

        if (filtered.length === 0) {
            alert('Nenhum evento para exportar com os filtros atuais.');
            return;
        }

        const ics = this.generateMultipleEventsICS(filtered);
        const blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `calendario_pli_${CalendarioUtils.formatDateKey(new Date())}.ics`;

        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log(`📥 Download ICS completo: ${filtered.length} eventos`);
    }
};

/* ========================================
   INTEGRAÇÃO GOOGLE CALENDAR
======================================== */

const CalendarioGoogle = {
    /**
     * Abrir evento no Google Calendar
     */
    openInGoogleCalendar(evt) {
        if (!evt || !evt.date) {
            console.error('❌ Evento inválido para Google Calendar:', evt);
            alert('Erro: Evento inválido');
            return;
        }

        const title = encodeURIComponent(evt.title || CalendarioICS.getEventLabel(evt));
        const details = encodeURIComponent(CalendarioICS.buildDescription(evt));
        const location = encodeURIComponent(evt.location || '');

        // Datas no formato Google Calendar (YYYYMMDDTHHMMSS)
        const dtStart = CalendarioICS.buildICSTime(evt.date, evt.startTime || '09:00');
        const dtEnd = CalendarioICS.buildICSTime(evt.date, evt.endTime || CalendarioICS.calculateEndTime(evt.startTime));

        const url =
            'https://calendar.google.com/calendar/u/0/r/eventedit?' +
            `text=${title}` +
            `&dates=${dtStart}/${dtEnd}` +
            `&details=${details}` +
            `&location=${location}` +
            `&trp=true`; // Show event as busy

        window.open(url, '_blank', 'noopener,noreferrer');
        console.log('🌐 Aberto no Google Calendar:', evt.id);
    }
};

/* ========================================
   INTEGRAÇÃO MICROSOFT OUTLOOK/TEAMS
======================================== */

const CalendarioOutlook = {
    /**
     * Abrir evento no Outlook Web
     */
    openInOutlookWeb(evt) {
        if (!evt || !evt.date) {
            console.error('❌ Evento inválido para Outlook:', evt);
            alert('Erro: Evento inválido');
            return;
        }

        const title = encodeURIComponent(evt.title || CalendarioICS.getEventLabel(evt));
        const body = encodeURIComponent(CalendarioICS.buildDescription(evt));
        const location = encodeURIComponent(evt.location || '');

        // Formato ISO 8601
        const startDate = this.toISO8601(evt.date, evt.startTime || '09:00');
        const endDate = this.toISO8601(evt.date, evt.endTime || CalendarioICS.calculateEndTime(evt.startTime));

        const url =
            'https://outlook.live.com/calendar/0/deeplink/compose?' +
            `subject=${title}` +
            `&body=${body}` +
            `&location=${location}` +
            `&startdt=${startDate}` +
            `&enddt=${endDate}` +
            `&path=/calendar/action/compose`;

        window.open(url, '_blank', 'noopener,noreferrer');
        console.log('🌐 Aberto no Outlook Web:', evt.id);
    },

    toISO8601(dateStr, timeStr) {
        const d = CalendarioUtils.parseDate(dateStr);
        const [hh, mm] = (timeStr || '09:00').split(':').map(Number);
        d.setHours(hh, mm || 0, 0, 0);
        return d.toISOString();
    },

    /**
     * Criar link do Microsoft Teams
     */
    createTeamsMeetingLink(evt) {
        // TODO: Requer integração com Microsoft Graph API
        // Por enquanto, apenas abre o Teams
        const url = 'msteams://teams.microsoft.com/l/meeting/new';
        window.open(url, '_blank');
        console.log('📞 Teams meeting link (requer integração Graph API)');
    }
};

/* ========================================
   COMPARTILHAMENTO E COLABORAÇÃO
======================================== */

const CalendarioShare = {
    /**
     * Gerar link compartilhável (requer backend)
     */
    async generateShareLink(evt) {
        if (!evt || !evt.id) {
            console.error('❌ Evento inválido para compartilhamento:', evt);
            return null;
        }

        try {
            const response = await fetch(`${CalendarioAPI.baseURL}/eventos/${evt.id}/share`, {
                method: 'POST',
                headers: CalendarioAPI.getHeaders()
            });

            const data = await CalendarioAPI.handleResponse(response);
            return data.shareUrl;
        } catch (error) {
            console.error('❌ Erro ao gerar link:', error);
            return null;
        }
    },

    /**
     * Copiar link para área de transferência
     */
    async copyShareLink(evt) {
        if (!evt || !evt.id) {
            alert('Erro: Evento inválido');
            return;
        }

        const shareUrl = await this.generateShareLink(evt);

        if (shareUrl) {
            try {
                await navigator.clipboard.writeText(shareUrl);
                alert('✅ Link copiado para área de transferência!');
            } catch (error) {
                console.error('❌ Erro ao copiar:', error);
                prompt('Copie este link:', shareUrl);
            }
        }
    },

    /**
     * Compartilhar por e-mail
     */
    shareByEmail(evt) {
        if (!evt || !evt.date) {
            alert('Erro: Evento inválido');
            return;
        }

        const subject = encodeURIComponent(`Evento PLI: ${evt.title || 'Evento'}`);
        const body = encodeURIComponent(
            `Olá,\n\n` +
            `Compartilho com você o seguinte evento do SIGMA-PLI:\n\n` +
            `📅 ${evt.title || 'Evento'}\n` +
            `📆 Data: ${evt.date}\n` +
            (evt.startTime ? `⏰ Horário: ${evt.startTime}\n` : '') +
            (evt.location ? `📍 Local: ${evt.location}\n` : '') +
            (evt.notes ? `\n${evt.notes}\n` : '') +
            `\n\n---\nSIGMA-PLI - Sistema Integrado de Gestão`
        );

        window.location.href = `mailto:?subject=${subject}&body=${body}`;
    }
};

/* ========================================
   UTILITÁRIOS DE EXPORTAÇÃO - LEGADO
======================================== */

// CalendarioExport foi movido para o início do arquivo e substituído por nova implementação

const CalendarioExportLegacy = {
    /**
     * Menu de exportação/integração
     */
    showExportMenu(evt) {
        // Se não foi passado evento específico, exporta todos
        if (!evt) {
            const menu = `
                Exportar calendário:
                
                1. Download todos eventos (.ICS)
                2. Cancelar
            `;

            const choice = prompt(menu, '1');

            if (choice === '1') {
                CalendarioICS.downloadAllICS();
            }
            return;
        }

        const menu = `
            Exportar/Integrar evento:
            
            1. Download .ICS (Outlook, Apple Calendar, etc)
            2. Abrir no Google Calendar
            3. Abrir no Outlook Web
            4. Compartilhar por e-mail
            5. Copiar link compartilhável
        `;

        const choice = prompt(menu, '1');

        switch (choice) {
            case '1':
                CalendarioICS.downloadICS(evt);
                break;
            case '2':
                CalendarioGoogle.openInGoogleCalendar(evt);
                break;
            case '3':
                CalendarioOutlook.openInOutlookWeb(evt);
                break;
            case '4':
                CalendarioShare.shareByEmail(evt);
                break;
            case '5':
                CalendarioShare.copyShareLink(evt);
                break;
            default:
                console.log('Operação cancelada');
        }
    }
};

console.log('✅ Integrações do Calendário carregadas');
