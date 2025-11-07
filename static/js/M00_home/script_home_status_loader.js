/**
 * SIGMA-PLI - M00: Home - Status Loader
 * Carrega e exibe o status do sistema
 */

class StatusLoader {
    constructor() {
        this.statusContainer = document.getElementById('system-status');

        // Se não houver container no DOM, não inicializa (evita erros em páginas que não têm o widget)
        if (!this.statusContainer) return;

        this.init();
    }

    async init() {
        try {
            // Usar caminho relativo para evitar hardcode de host/porta
            const response = await fetch('/api/status');

            if (!response.ok) {
                // Log e fallback visual
                const txt = await response.text();
                console.warn('Status endpoint retornou não-ok:', response.status, txt);
                this.renderError();
                return;
            }

            const contentType = response.headers.get('content-type') || '';
            if (!contentType.includes('application/json')) {
                // Resposta não-JSON (provavelmente HTML de erro) — evita SyntaxError ao parsear
                const txt = await response.text();
                console.warn('Resposta de /api/status não é JSON:', contentType, txt.slice(0, 200));
                this.renderError();
                return;
            }

            const data = await response.json();
            this.renderStatus(data || {});
        } catch (error) {
            console.error('Erro ao carregar status:', error);
            this.renderError();
        }
    }

    renderStatus(data) {
    const modules = data.modules || {};
    const databases = data.databases || {};

    const statusCards = Object.entries(modules).map(([module, status]) => {
            const statusClass = this.getStatusClass(status);
            const statusIcon = this.getStatusIcon(status);

            return `
                <div class="status-card ${statusClass}">
                    <h5>${module.replace('_', ' ').toUpperCase()}</h5>
                    <p>${statusIcon} ${this.formatStatus(status)}</p>
                </div>
            `;
        }).join('');

        // Adicionar informações dos bancos
    const dbCards = Object.entries(databases).map(([db, status]) => {
            const statusClass = status === '✅' ? 'success' : 'error';
            const statusIcon = status === '✅' ? '🟢' : '🔴';

            return `
                <div class="status-card ${statusClass}">
                    <h5>${db.toUpperCase()}</h5>
                    <p>${statusIcon} ${status === '✅' ? 'Conectado' : 'Desconectado'}</p>
                </div>
            `;
        }).join('');

        this.statusContainer.innerHTML = statusCards + dbCards;
    }

    renderError() {
        this.statusContainer.innerHTML = `
            <div class="status-card error">
                <h5>Erro de Conexão</h5>
                <p>❌ Não foi possível carregar o status do sistema</p>
            </div>
        `;
    }

    getStatusClass(status) {
        if (status === '✅') return 'success';
        if (status === '🚧') return 'warning';
        return 'error';
    }

    getStatusIcon(status) {
        if (status === '✅') return '✅';
        if (status === '🚧') return '🚧';
        return '❌';
    }

    formatStatus(status) {
        if (status === '✅') return 'Operacional';
        if (status === '🚧') return 'Em Desenvolvimento';
        return 'Indisponível';
    }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    new StatusLoader();
});