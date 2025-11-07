/**
 * SIGMA-PLI - M00: Home - Form Validation
 * Gerencia validação de formulários e interações
 */

class FormValidator {
    constructor(formElement) {
        this.form = formElement;
        this.errors = {};
        this.init();
    }

    init() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.setupRealTimeValidation();
        this.setupInputMasks();
    }

    setupRealTimeValidation() {
        const inputs = this.form.querySelectorAll('input, textarea, select');

        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    }

    setupInputMasks() {
        // Máscara para CPF
        const cpfInputs = this.form.querySelectorAll('input[data-mask="cpf"]');
        cpfInputs.forEach(input => {
            input.addEventListener('input', (e) => this.applyCpfMask(e.target));
        });

        // Máscara para telefone
        const phoneInputs = this.form.querySelectorAll('input[data-mask="phone"]');
        phoneInputs.forEach(input => {
            input.addEventListener('input', (e) => this.applyPhoneMask(e.target));
        });

        // Máscara para data
        const dateInputs = this.form.querySelectorAll('input[data-mask="date"]');
        dateInputs.forEach(input => {
            input.addEventListener('input', (e) => this.applyDateMask(e.target));
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;
        let error = null;

        // Regras de validação baseadas no tipo de campo
        switch (fieldName) {
            case 'email':
                error = this.validateEmail(value);
                break;
            case 'password':
                error = this.validatePassword(value);
                break;
            case 'cpf':
                error = this.validateCpf(value);
                break;
            case 'phone':
                error = this.validatePhone(value);
                break;
            case 'name':
                error = this.validateName(value);
                break;
            default:
                if (field.hasAttribute('required') && !value) {
                    error = 'Este campo é obrigatório';
                }
                break;
        }

        if (error) {
            this.showFieldError(field, error);
            return false;
        } else {
            this.clearFieldError(field);
            return true;
        }
    }

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email) return 'E-mail é obrigatório';
        if (!emailRegex.test(email)) return 'E-mail inválido';
        return null;
    }

    validatePassword(password) {
        if (!password) return 'Senha é obrigatória';
        if (password.length < 8) return 'Senha deve ter pelo menos 8 caracteres';
        if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
            return 'Senha deve conter letras maiúsculas, minúsculas e números';
        }
        return null;
    }

    validateCpf(cpf) {
        if (!cpf) return 'CPF é obrigatório';

        // Remover caracteres não numéricos
        cpf = cpf.replace(/\D/g, '');

        if (cpf.length !== 11) return 'CPF deve ter 11 dígitos';

        // Verificar se todos os dígitos são iguais
        if (/^(\d)\1+$/.test(cpf)) return 'CPF inválido';

        // Calcular dígitos verificadores
        let sum = 0;
        for (let i = 0; i < 9; i++) {
            sum += parseInt(cpf.charAt(i)) * (10 - i);
        }
        let remainder = sum % 11;
        let digit1 = remainder < 2 ? 0 : 11 - remainder;

        sum = 0;
        for (let i = 0; i < 10; i++) {
            sum += parseInt(cpf.charAt(i)) * (11 - i);
        }
        remainder = sum % 11;
        let digit2 = remainder < 2 ? 0 : 11 - remainder;

        if (parseInt(cpf.charAt(9)) !== digit1 || parseInt(cpf.charAt(10)) !== digit2) {
            return 'CPF inválido';
        }

        return null;
    }

    validatePhone(phone) {
        const phoneRegex = /^\(\d{2}\)\s\d{4,5}-\d{4}$/;
        if (!phone) return 'Telefone é obrigatório';
        if (!phoneRegex.test(phone)) return 'Telefone inválido';
        return null;
    }

    validateName(name) {
        if (!name) return 'Nome é obrigatório';
        if (name.length < 2) return 'Nome deve ter pelo menos 2 caracteres';
        if (!/^[a-zA-ZÀ-ÿ\s]+$/.test(name)) return 'Nome deve conter apenas letras';
        return null;
    }

    showFieldError(field, message) {
        this.clearFieldError(field);

        field.classList.add('error');

        const errorElement = document.createElement('span');
        errorElement.className = 'field-error';
        errorElement.textContent = message;

        field.parentNode.appendChild(errorElement);
        this.errors[field.name] = message;
    }

    clearFieldError(field) {
        field.classList.remove('error');

        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }

        delete this.errors[field.name];
    }

    handleSubmit(e) {
        e.preventDefault();

        const inputs = this.form.querySelectorAll('input, textarea, select');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        if (isValid) {
            this.submitForm();
        } else {
            this.showFormErrors();
        }
    }

    async submitForm() {
        const formData = new FormData(this.form);
        const data = Object.fromEntries(formData.entries());

        try {
            // Mostrar loading
            this.showLoading(true);

            // Simular envio (substituir pela chamada real da API)
            const response = await this.mockApiCall(data);

            if (response.success) {
                this.showSuccess('Formulário enviado com sucesso!');
                this.form.reset();
            } else {
                this.showError('Erro ao enviar formulário: ' + response.message);
            }
        } catch (error) {
            this.showError('Erro de conexão. Tente novamente.');
        } finally {
            this.showLoading(false);
        }
    }

    async mockApiCall(data) {
        // Simulação de chamada API
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({ success: true, message: 'OK' });
            }, 2000);
        });
    }

    showFormErrors() {
        const firstErrorField = this.form.querySelector('.error');
        if (firstErrorField) {
            firstErrorField.focus();
            firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    showLoading(show) {
        let loader = this.form.querySelector('.form-loader');

        if (show) {
            if (!loader) {
                loader = document.createElement('div');
                loader.className = 'form-loader';
                loader.innerHTML = '<div class="spinner"></div><span>Enviando...</span>';
                this.form.appendChild(loader);
            }
            loader.style.display = 'flex';
        } else if (loader) {
            loader.style.display = 'none';
        }
    }

    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    showError(message) {
        this.showMessage(message, 'error');
    }

    showMessage(message, type) {
        const messageElement = document.createElement('div');
        messageElement.className = `form-message ${type}`;
        messageElement.textContent = message;

        this.form.insertBefore(messageElement, this.form.firstChild);

        setTimeout(() => {
            messageElement.remove();
        }, 5000);
    }

    // Máscaras de entrada
    applyCpfMask(input) {
        let value = input.value.replace(/\D/g, '');
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
        input.value = value;
    }

    applyPhoneMask(input) {
        let value = input.value.replace(/\D/g, '');
        if (value.length <= 11) {
            value = value.replace(/(\d{2})(\d)/, '($1) $2');
            value = value.replace(/(\d{4,5})(\d{4})$/, '$1-$2');
        }
        input.value = value;
    }

    applyDateMask(input) {
        let value = input.value.replace(/\D/g, '');
        value = value.replace(/(\d{2})(\d)/, '$1/$2');
        value = value.replace(/(\d{2})(\d)/, '$1/$2');
        input.value = value;
    }
}

// Utilitários de validação
class ValidationUtils {
    static isValidCpf(cpf) {
        return !new FormValidator(document.createElement('form')).validateCpf(cpf);
    }

    static isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    static isValidPhone(phone) {
        const phoneRegex = /^\(\d{2}\)\s\d{4,5}-\d{4}$/;
        return phoneRegex.test(phone);
    }

    static formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    }

    static formatDate(date) {
        return new Intl.DateTimeFormat('pt-BR').format(new Date(date));
    }

    static formatCpf(cpf) {
        cpf = cpf.replace(/\D/g, '');
        return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    }
}

// Inicializar validação para todos os formulários
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('form').forEach(form => {
        new FormValidator(form);
    });
});