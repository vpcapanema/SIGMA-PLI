/**
 * Handler do Formulário de Login
 * Conecta formulário HTML ao endpoint /api/v1/auth/login
 */

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const loginButton = document.getElementById('loginButton');
    const errorMessage = document.getElementById('loginError');
    const successMessage = document.getElementById('loginSuccess');

    if (!loginForm) {
        console.warn('Formulário de login não encontrado');
        return;
    }

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Limpar mensagens anteriores
        if (errorMessage) errorMessage.style.display = 'none';
        if (successMessage) successMessage.style.display = 'none';

        // Obter valores do formulário
        const identifier = document.getElementById('identifier')?.value.trim();
        const password = document.getElementById('password')?.value;

        // Validação básica
        if (!identifier || !password) {
            showError('Por favor, preencha todos os campos');
            return;
        }

        // Desabilitar botão durante requisição
        if (loginButton) {
            loginButton.disabled = true;
            loginButton.textContent = 'Entrando...';
        }

        try {
            // Fazer login usando authManager
            const result = await authManager.login(identifier, password);

            if (result.success) {
                showSuccess('Login realizado com sucesso! Redirecionando...');

                // Redirecionar após 1 segundo
                setTimeout(() => {
                    // Verificar se há URL de redirecionamento
                    const urlParams = new URLSearchParams(window.location.search);
                    const redirectUrl = urlParams.get('redirect') || '/dashboard';
                    window.location.href = redirectUrl;
                }, 1000);
            } else {
                showError(result.error || 'Credenciais inválidas');
            }
        } catch (error) {
            console.error('Erro no login:', error);
            showError('Erro ao fazer login. Tente novamente.');
        } finally {
            // Reabilitar botão
            if (loginButton) {
                loginButton.disabled = false;
                loginButton.textContent = 'Entrar';
            }
        }
    });

    /**
     * Mostrar mensagem de erro
     */
    function showError(message) {
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
        } else {
            alert(message);
        }
    }

    /**
     * Mostrar mensagem de sucesso
     */
    function showSuccess(message) {
        if (successMessage) {
            successMessage.textContent = message;
            successMessage.style.display = 'block';
        }
    }

    // Verificar se já está autenticado
    if (authManager.isAuthenticated()) {
        const urlParams = new URLSearchParams(window.location.search);
        const redirectUrl = urlParams.get('redirect') || '/dashboard';
        window.location.href = redirectUrl;
    }
});
