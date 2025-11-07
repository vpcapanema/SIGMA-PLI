/**
 * SIGMA-PLI - M00: Home - State Management
 * Gerencia estado da aplicação e comunicação com APIs
 */

class StateManager {
    constructor() {
        this.state = {
            user: null,
            systemStatus: null,
            notifications: [],
            loading: false,
            error: null
        };
        this.listeners = {};
        this.init();
    }

    init() {
        this.loadPersistedState();
        this.setupEventListeners();
    }

    // Gerenciamento de estado
    setState(updates) {
        const oldState = { ...this.state };
        this.state = { ...this.state, ...updates };
        this.persistState();
        this.notifyListeners(oldState);
    }

    getState() {
        return { ...this.state };
    }

    subscribe(key, callback) {
        if (!this.listeners[key]) {
            this.listeners[key] = [];
        }
        this.listeners[key].push(callback);

        // Retornar função para remover listener
        return () => {
            this.listeners[key] = this.listeners[key].filter(cb => cb !== callback);
        };
    }

    notifyListeners(oldState) {
        Object.keys(this.listeners).forEach(key => {
            if (oldState[key] !== this.state[key]) {
                this.listeners[key].forEach(callback => callback(this.state[key], oldState[key]));
            }
        });
    }

    // Persistência de estado
    persistState() {
        try {
            const stateToPersist = {
                user: this.state.user,
                notifications: this.state.notifications
            };
            localStorage.setItem('sigma_pli_state', JSON.stringify(stateToPersist));
        } catch (error) {
            console.warn('Erro ao persistir estado:', error);
        }
    }

    loadPersistedState() {
        try {
            const persisted = localStorage.getItem('sigma_pli_state');
            if (persisted) {
                const parsed = JSON.parse(persisted);
                this.state = { ...this.state, ...parsed };
            }
        } catch (error) {
            console.warn('Erro ao carregar estado persistido:', error);
        }
    }

    setupEventListeners() {
        // Listener para mudanças de visibilidade da página
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.refreshSystemStatus();
            }
        });

        // Listener para online/offline
        window.addEventListener('online', () => {
            this.setState({ error: null });
            this.refreshSystemStatus();
        });

        window.addEventListener('offline', () => {
            this.setState({
                error: 'Conexão com a internet perdida',
                systemStatus: { ...this.state.systemStatus, online: false }
            });
        });
    }

    // Métodos específicos de estado
    async login(credentials) {
        this.setState({ loading: true, error: null });

        try {
            const response = await ApiService.login(credentials);

            if (response.success) {
                this.setState({
                    user: response.user,
                    loading: false
                });
                return { success: true };
            } else {
                this.setState({
                    error: response.message,
                    loading: false
                });
                return { success: false, message: response.message };
            }
        } catch (error) {
            this.setState({
                error: 'Erro ao fazer login',
                loading: false
            });
            return { success: false, message: 'Erro de conexão' };
        }
    }

    async logout() {
        this.setState({ loading: true });

        try {
            await ApiService.logout();
            this.setState({
                user: null,
                loading: false
            });
        } catch (error) {
            console.warn('Erro ao fazer logout:', error);
            // Mesmo com erro, limpar estado local
            this.setState({
                user: null,
                loading: false
            });
        }
    }

    async refreshSystemStatus() {
        try {
            const status = await ApiService.getSystemStatus();
            this.setState({
                systemStatus: status,
                error: null
            });
        } catch (error) {
            this.setState({
                error: 'Erro ao atualizar status do sistema'
            });
        }
    }

    addNotification(notification) {
        const newNotification = {
            id: Date.now(),
            timestamp: new Date(),
            ...notification
        };

        this.setState({
            notifications: [...this.state.notifications, newNotification]
        });

        // Auto-remover notificações após 5 segundos
        setTimeout(() => {
            this.removeNotification(newNotification.id);
        }, 5000);
    }

    removeNotification(id) {
        this.setState({
            notifications: this.state.notifications.filter(n => n.id !== id)
        });
    }

    clearError() {
        this.setState({ error: null });
    }
}

// Serviço de API
class ApiService {
    static baseURL = '/api/v1';

    static async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Adicionar token de autenticação se existir
        const token = localStorage.getItem('sigma_pli_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    }

    static async login(credentials) {
        const response = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
        return response;
    }

    static async logout() {
        const response = await this.request('/auth/logout', {
            method: 'POST'
        });
        return response;
    }

    static async getSystemStatus() {
        const response = await this.request('/status');
        return response;
    }

    static async getUserProfile() {
        const response = await this.request('/user/profile');
        return response;
    }

    static async updateUserProfile(data) {
        const response = await this.request('/user/profile', {
            method: 'PUT',
            body: JSON.stringify(data)
        });
        return response;
    }
}

// Cache de dados
class DataCache {
    constructor(maxAge = 5 * 60 * 1000) { // 5 minutos por padrão
        this.cache = new Map();
        this.maxAge = maxAge;
    }

    set(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    get(key) {
        const item = this.cache.get(key);

        if (!item) return null;

        if (Date.now() - item.timestamp > this.maxAge) {
            this.cache.delete(key);
            return null;
        }

        return item.data;
    }

    clear() {
        this.cache.clear();
    }

    delete(key) {
        return this.cache.delete(key);
    }

    // Limpar cache expirado
    cleanup() {
        const now = Date.now();
        for (const [key, item] of this.cache.entries()) {
            if (now - item.timestamp > this.maxAge) {
                this.cache.delete(key);
            }
        }
    }
}

// Utilitários de estado
class StateUtils {
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    static throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    static deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (typeof obj === 'object') {
            const cloned = {};
            Object.keys(obj).forEach(key => {
                cloned[key] = this.deepClone(obj[key]);
            });
            return cloned;
        }
    }

    static diff(obj1, obj2) {
        const differences = {};

        const keys1 = Object.keys(obj1);
        const keys2 = Object.keys(obj2);

        // Verificar propriedades adicionadas ou modificadas
        keys1.forEach(key => {
            if (!(key in obj2)) {
                differences[key] = { type: 'removed', oldValue: obj1[key] };
            } else if (obj1[key] !== obj2[key]) {
                differences[key] = { type: 'modified', oldValue: obj1[key], newValue: obj2[key] };
            }
        });

        // Verificar propriedades removidas
        keys2.forEach(key => {
            if (!(key in obj1)) {
                differences[key] = { type: 'added', newValue: obj2[key] };
            }
        });

        return differences;
    }
}

// Instância global do gerenciador de estado
const stateManager = new StateManager();
const dataCache = new DataCache();

// Limpar cache periodicamente
setInterval(() => {
    dataCache.cleanup();
}, 60 * 1000); // A cada minuto

// Exportar para uso global
window.StateManager = StateManager;
window.ApiService = ApiService;
window.DataCache = DataCache;
window.StateUtils = StateUtils;
window.stateManager = stateManager;
window.dataCache = dataCache;