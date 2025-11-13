/**
 * Gerenciador de Tokens de Autenticação
 * Gerencia localStorage, auto-refresh e interceptors
 */

class AuthTokenManager {
    constructor() {
        this.sessionToken = null;
        this.refreshToken = null;
        this.user = null;
        this.refreshTimer = null;

        // Carregar do localStorage na inicialização
        this.loadFromStorage();
    }

    // Helper para acesso seguro a localStorage (evita erros quando bloqueado por Tracking Prevention)
    safeSetItem(key, value) {
        try {
            localStorage.setItem(key, value);
        } catch (e) {
            // Falha ao acessar localStorage (ex.: Tracking Prevention) -> silencioso
            console.warn('localStorage inacessível:', e.message);
        }
    }

    safeGetItem(key) {
        try {
            return localStorage.getItem(key);
        } catch (e) {
            console.warn('localStorage inacessível:', e.message);
            return null;
        }
    }

    safeRemoveItem(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('localStorage inacessível:', e.message);
        }
    }

    /**
     * Salvar tokens no localStorage
     */
    saveToStorage() {
        if (this.sessionToken) {
            this.safeSetItem('session_token', this.sessionToken);
        }
        if (this.refreshToken) {
            this.safeSetItem('refresh_token', this.refreshToken);
        }
        if (this.user) {
            this.safeSetItem('user', JSON.stringify(this.user));
        }
    }

    /**
     * Carregar tokens do localStorage
     */
    loadFromStorage() {
        this.sessionToken = this.safeGetItem('session_token');
        this.refreshToken = this.safeGetItem('refresh_token');
        const userStr = this.safeGetItem('user');
        if (userStr) {
            try {
                this.user = JSON.parse(userStr);
            } catch (e) {
                console.error('Erro ao parsear dados do usuário:', e);
            }
        }
    }

    /**
     * Limpar tokens e dados do usuário
     */
    clearStorage() {
        this.sessionToken = null;
        this.refreshToken = null;
        this.user = null;
        this.safeRemoveItem('session_token');
        this.safeRemoveItem('refresh_token');
        this.safeRemoveItem('user');
        this.stopAutoRefresh();
    }

    /**
     * Verificar se usuário está autenticado
     */
    isAuthenticated() {
        return !!this.sessionToken;
    }

    /**
     * Obter usuário atual
     */
    getUser() {
        return this.user;
    }

    /**
     * Definir tokens após login
     */
    setTokens(sessionToken, refreshToken, userData) {
        this.sessionToken = sessionToken;
        this.refreshToken = refreshToken;
        this.user = userData;
        this.saveToStorage();
        this.startAutoRefresh();
    }

    /**
     * Obter header Authorization
     */
    getAuthHeader() {
        if (!this.sessionToken) {
            return null;
        }
        return `Bearer ${this.sessionToken}`;
    }

    /**
     * Fazer requisição autenticada
     */
    async fetch(url, options = {}) {
        // Adicionar header de autenticação
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.sessionToken) {
            headers['Authorization'] = this.getAuthHeader();
        }

        const response = await fetch(url, {
            ...options,
            headers,
        });

        // Se 401, tentar refresh
        if (response.status === 401 && this.refreshToken) {
            const refreshed = await this.refreshSession();
            if (refreshed) {
                // Tentar novamente com novo token
                headers['Authorization'] = this.getAuthHeader();
                return fetch(url, {
                    ...options,
                    headers,
                });
            } else {
                // Refresh falhou, fazer logout
                this.clearStorage();
                window.location.href = '/auth/login';
            }
        }

        return response;
    }

    /**
     * Renovar sessão usando refresh token
     */
    async refreshSession() {
        if (!this.refreshToken) {
            return false;
        }

        try {
            const response = await fetch('/api/v1/auth/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    refresh_token: this.refreshToken,
                }),
            });

            if (!response.ok) {
                return false;
            }

            const data = await response.json();

            this.sessionToken = data.session_token;
            this.refreshToken = data.refresh_token;
            this.saveToStorage();

            return true;
        } catch (error) {
            console.error('Erro ao renovar sessão:', error);
            return false;
        }
    }

    /**
     * Iniciar auto-refresh (renova 5 minutos antes de expirar)
     * Sessão padrão: 24h, refresh a cada 23h55min
     */
    startAutoRefresh() {
        this.stopAutoRefresh();

        // Renovar a cada 23 horas e 55 minutos
        const intervalMs = (24 * 60 - 5) * 60 * 1000;

        this.refreshTimer = setInterval(async () => {
            const refreshed = await this.refreshSession();
            if (!refreshed) {
                this.clearStorage();
                window.location.href = '/auth/login';
            }
        }, intervalMs);
    }

    /**
     * Parar auto-refresh
     */
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    /**
     * Fazer login
     */
    async login(identifier, password) {
        try {
            const response = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    identifier,
                    password,
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao fazer login');
            }

            const data = await response.json();

            this.setTokens(data.session_token, data.refresh_token, data.user);

            return {
                success: true,
                user: data.user,
            };
        } catch (error) {
            console.error('Erro no login:', error);
            return {
                success: false,
                error: error.message,
            };
        }
    }

    /**
     * Fazer logout
     */
    async logout() {
        try {
            if (this.sessionToken) {
                await this.fetch('/api/v1/auth/logout', {
                    method: 'POST',
                });
            }
        } catch (error) {
            console.error('Erro ao fazer logout:', error);
        } finally {
            this.clearStorage();
            window.location.href = '/auth/login';
        }
    }

    /**
     * Registrar novo usuário
     */
    async register(username, email, password, pessoaId = null) {
        try {
            const response = await fetch('/api/v1/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                    email,
                    password,
                    pessoa_id: pessoaId,
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao registrar');
            }

            const data = await response.json();

            return {
                success: true,
                message: data.message,
            };
        } catch (error) {
            console.error('Erro no registro:', error);
            return {
                success: false,
                error: error.message,
            };
        }
    }

    /**
     * Obter dados do usuário atual
     */
    async getCurrentUser() {
        try {
            const response = await this.fetch('/api/v1/auth/me');

            if (!response.ok) {
                return null;
            }

            const user = await response.json();
            this.user = user;
            this.saveToStorage();

            return user;
        } catch (error) {
            console.error('Erro ao obter usuário:', error);
            return null;
        }
    }

    /**
     * Solicitar reset de senha
     */
    async requestPasswordReset(email) {
        try {
            const response = await fetch('/api/v1/auth/request-password-reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            const data = await response.json();

            return {
                success: data.success,
                message: data.message,
            };
        } catch (error) {
            console.error('Erro ao solicitar reset:', error);
            return {
                success: false,
                error: error.message,
            };
        }
    }

    /**
     * Confirmar reset de senha
     */
    async resetPassword(token, newPassword) {
        try {
            const response = await fetch('/api/v1/auth/reset-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    token,
                    new_password: newPassword,
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao resetar senha');
            }

            const data = await response.json();

            return {
                success: true,
                message: data.message,
            };
        } catch (error) {
            console.error('Erro ao resetar senha:', error);
            return {
                success: false,
                error: error.message,
            };
        }
    }

    /**
     * Verificar email
     */
    async verifyEmail(token) {
        try {
            const response = await fetch(`/api/v1/auth/verify-email?token=${token}`);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao verificar email');
            }

            const data = await response.json();

            return {
                success: true,
                message: data.message,
            };
        } catch (error) {
            console.error('Erro ao verificar email:', error);
            return {
                success: false,
                error: error.message,
            };
        }
    }
}

// Instância global
const authManager = new AuthTokenManager();

// Expor globalmente
window.authManager = authManager;
