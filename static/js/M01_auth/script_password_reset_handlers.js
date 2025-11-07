/**
 * Handler do Formulário de Recuperação de Senha
 * Solicitar e confirmar reset de senha
 */

/**
 * Inicializar formulário de solicitação de reset
 */
function initPasswordResetRequest() {
    const form = document.getElementById('passwordResetRequestForm');
    if (!form) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email = document.getElementById('email')?.value.trim();

        if (!email) {
            showError('Por favor, informe seu email');
            return;
        }

        // Validar formato de email
        if (!isValidEmail(email)) {
            showError('Email inválido');
            return;
        }

        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = 'Enviando...';
        }

        try {
            const result = await authManager.requestPasswordReset(email);

            if (result.success) {
                showSuccess(result.message || 'Instruções enviadas para seu email');

                // Limpar formulário
                form.reset();
            } else {
                showError(result.error || 'Erro ao solicitar reset');
            }
        } catch (error) {
            showError('Erro ao processar solicitação');
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = 'Enviar';
            }
        }
    });
}

/**
 * Inicializar formulário de confirmação de reset
 */
function initPasswordResetConfirm() {
    const form = document.getElementById('passwordResetConfirmForm');
    if (!form) return;

    // Obter token da URL
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    if (!token) {
        showError('Token de recuperação não fornecido');
        return;
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const newPassword = document.getElementById('new_password')?.value;
        const confirmPassword = document.getElementById('confirm_password')?.value;

        // Validação
        if (!newPassword || !confirmPassword) {
            showError('Por favor, preencha todos os campos');
            return;
        }

        if (newPassword !== confirmPassword) {
            showError('As senhas não coincidem');
            return;
        }

        if (newPassword.length < 8) {
            showError('A senha deve ter no mínimo 8 caracteres');
            return;
        }

        // Validar força da senha
        if (!validarSenhaForte(newPassword)) {
            showError('A senha deve conter letras maiúsculas, minúsculas, números e caracteres especiais');
            return;
        }

        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = 'Alterando...';
        }

        try {
            const result = await authManager.resetPassword(token, newPassword);

            if (result.success) {
                showSuccess(result.message || 'Senha alterada com sucesso!');

                // Redirecionar para login após 2 segundos
                setTimeout(() => {
                    window.location.href = '/auth/login?password_reset=true';
                }, 2000);
            } else {
                showError(result.error || 'Erro ao alterar senha');
            }
        } catch (error) {
            showError('Erro ao processar alteração');
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = 'Alterar Senha';
            }
        }
    });

    // Validação em tempo real da senha
    const passwordInput = document.getElementById('new_password');
    const passwordStrength = document.getElementById('password_strength');

    if (passwordInput && passwordStrength) {
        passwordInput.addEventListener('input', () => {
            const password = passwordInput.value;
            const strength = calcularForcaSenha(password);

            passwordStrength.textContent = `Força: ${strength.label}`;
            passwordStrength.className = `password-strength ${strength.class}`;
        });
    }

    // Validar confirmação em tempo real
    const confirmInput = document.getElementById('confirm_password');
    const matchIndicator = document.getElementById('password_match');

    if (confirmInput && matchIndicator && passwordInput) {
        confirmInput.addEventListener('input', () => {
            const password = passwordInput.value;
            const confirm = confirmInput.value;

            if (confirm.length > 0) {
                if (password === confirm) {
                    matchIndicator.textContent = '✓ Senhas coincidem';
                    matchIndicator.className = 'password-match match';
                } else {
                    matchIndicator.textContent = '✗ Senhas não coincidem';
                    matchIndicator.className = 'password-match no-match';
                }
            } else {
                matchIndicator.textContent = '';
                matchIndicator.className = 'password-match';
            }
        });
    }
}

/**
 * Validar formato de email
 */
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Validar senha forte
 */
function validarSenhaForte(password) {
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecial = /[^A-Za-z0-9]/.test(password);

    return hasUpper && hasLower && hasNumber && hasSpecial;
}

/**
 * Calcular força da senha
 */
function calcularForcaSenha(password) {
    let score = 0;

    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;

    if (score <= 2) return { label: 'Fraca', class: 'weak' };
    if (score <= 4) return { label: 'Média', class: 'medium' };
    return { label: 'Forte', class: 'strong' };
}

/**
 * Mostrar mensagem de erro
 */
function showError(message) {
    const errorDiv = document.getElementById('formError');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    } else {
        alert(message);
    }

    // Esconder mensagem de sucesso
    const successDiv = document.getElementById('formSuccess');
    if (successDiv) {
        successDiv.style.display = 'none';
    }
}

/**
 * Mostrar mensagem de sucesso
 */
function showSuccess(message) {
    const successDiv = document.getElementById('formSuccess');
    if (successDiv) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
    } else {
        alert(message);
    }

    // Esconder mensagem de erro
    const errorDiv = document.getElementById('formError');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

// Inicializar quando DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    initPasswordResetRequest();
    initPasswordResetConfirm();
});
