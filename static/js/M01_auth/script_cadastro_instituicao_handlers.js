/**
 * SIGMA-PLI - Handler de Cadastro de Instituição
 * Gerencia o formulário de cadastro de instituição (pessoa jurídica)
 */

(function () {
    'use strict';

    /**
     * Inicializa o formulário de cadastro de instituição
     */
    function initCadastroInstituicao() {
        const form = document.getElementById('instituicaoForm');

        if (!form) {
            console.warn('Formulário de instituição não encontrado');
            return;
        }

        // Máscaras de input
        setupInputMasks();

        // Busca de CEP
        setupCepLookup();

        // Validação e submissão
        form.addEventListener('submit', handleSubmit);

        console.log('✅ Handler de cadastro de instituição inicializado');
    }

    /**
     * Configura máscaras de input
     */
    function setupInputMasks() {
        // Máscara de CNPJ
        const cnpjInput = document.getElementById('cnpj');
        if (cnpjInput) {
            cnpjInput.addEventListener('input', function (e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 14) value = value.substr(0, 14);

                // Formata: 00.000.000/0000-00
                if (value.length > 12) {
                    value = value.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
                } else if (value.length > 8) {
                    value = value.replace(/^(\d{2})(\d{3})(\d{3})(\d{1,4})/, '$1.$2.$3/$4');
                } else if (value.length > 5) {
                    value = value.replace(/^(\d{2})(\d{3})(\d{1,3})/, '$1.$2.$3');
                } else if (value.length > 2) {
                    value = value.replace(/^(\d{2})(\d{1,3})/, '$1.$2');
                }

                e.target.value = value;
            });
        }

        // Máscara de CEP
        const cepInput = document.getElementById('cep');
        if (cepInput) {
            cepInput.addEventListener('input', function (e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 8) value = value.substr(0, 8);

                // Formata: 00000-000
                if (value.length > 5) {
                    value = value.replace(/^(\d{5})(\d{1,3})/, '$1-$2');
                }

                e.target.value = value;
            });
        }

        // Máscara de telefone
        const telefoneInputs = document.querySelectorAll('#telefone, #telefoneSecundario');
        telefoneInputs.forEach(input => {
            input.addEventListener('input', function (e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 11) value = value.substr(0, 11);

                // Formata: (00) 0000-0000 ou (00) 00000-0000
                if (value.length > 10) {
                    value = value.replace(/^(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
                } else if (value.length > 6) {
                    value = value.replace(/^(\d{2})(\d{4})(\d{1,4})/, '($1) $2-$3');
                } else if (value.length > 2) {
                    value = value.replace(/^(\d{2})(\d{1,5})/, '($1) $2');
                }

                e.target.value = value;
            });
        });
    }

    /**
     * Configura busca de CEP via ViaCEP
     */
    function setupCepLookup() {
        const cepInput = document.getElementById('cep');

        if (!cepInput) return;

        cepInput.addEventListener('blur', async function () {
            const cep = this.value.replace(/\D/g, '');

            if (cep.length !== 8) return;

            try {
                const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);

                if (!response.ok) {
                    console.warn('Erro ao buscar CEP');
                    return;
                }

                const data = await response.json();

                if (data.erro) {
                    showToast('CEP não encontrado', 'warning');
                    return;
                }

                // Preenche campos
                document.getElementById('logradouro').value = data.logradouro || '';
                document.getElementById('bairro').value = data.bairro || '';
                document.getElementById('cidade').value = data.localidade || '';
                document.getElementById('uf').value = data.uf || '';
                document.getElementById('complemento').value = data.complemento || '';

                // Foca no número
                document.getElementById('numero').focus();

            } catch (error) {
                console.error('Erro ao buscar CEP:', error);
            }
        });
    }

    /**
     * Processa o submit do formulário
     */
    async function handleSubmit(e) {
        e.preventDefault();
        e.stopPropagation();

        const form = e.target;

        // Validação HTML5
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            showToast('Por favor, preencha todos os campos obrigatórios', 'error');
            return;
        }

        // Verifica termos
        const termoPrivacidade = document.getElementById('termoPrivacidade');
        const termoUso = document.getElementById('termoUso');

        if (!termoPrivacidade.checked || !termoUso.checked) {
            showToast('Você deve aceitar os termos de uso e política de privacidade', 'error');
            return;
        }

        // Coleta dados do formulário
        const formData = new FormData(form);
        const data = {};

        formData.forEach((value, key) => {
            // Ignora checkboxes de termos
            if (key === 'termo_privacidade' || key === 'termo_uso') return;

            // Converte data_abertura para formato ISO
            if (key === 'data_abertura' && value) {
                data[key] = value; // FastAPI aceita YYYY-MM-DD
            } else if (value !== '') {
                data[key] = value;
            }
        });

        // Adiciona campo 'nome' (usa razão social ou nome fantasia)
        data.nome = data.razao_social || data.nome_fantasia || 'Instituição sem nome';

        console.log('📤 Enviando dados:', data);

        // Mostra progresso
        showProgress('validation');

        try {
            showProgress('sending');

            const response = await fetch('/api/cadastro/instituicao', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                // Erro de validação ou duplicação
                showProgress('complete', false);

                let errorMessage = 'Erro ao cadastrar instituição';

                if (response.status === 400) {
                    errorMessage = result.detail || 'Dados inválidos';
                } else if (response.status === 422) {
                    errorMessage = 'Dados inválidos: ' + JSON.stringify(result.detail);
                }

                showToast(errorMessage, 'error');
                return;
            }

            // Sucesso
            showProgress('complete', true);
            console.log('✅ Instituição cadastrada:', result);

            // Mostra modal de sucesso
            const successModal = new bootstrap.Modal(document.getElementById('successModal'));
            successModal.show();

            // Limpa formulário
            form.reset();
            form.classList.remove('was-validated');

        } catch (error) {
            console.error('❌ Erro ao cadastrar instituição:', error);
            showProgress('complete', false);
            showToast('Erro ao conectar com o servidor. Tente novamente.', 'error');
        }
    }

    /**
     * Mostra progresso do envio
     */
    function showProgress(step, success = true) {
        const container = document.getElementById('progressContainer');
        const steps = {
            'validation': 0,
            'processing': 1,
            'sending': 2,
            'complete': 3
        };

        if (!container) return;

        const stepElements = container.querySelectorAll('.cadastro-pessoa-juridica__progress-step--div');
        const messageElement = document.getElementById('progressMessage');

        // Remove classes anteriores
        stepElements.forEach(el => {
            el.classList.remove('active', 'complete', 'error');
        });

        // Adiciona classe ao step atual
        const currentStep = steps[step];

        for (let i = 0; i <= currentStep; i++) {
            if (i < currentStep) {
                stepElements[i].classList.add('complete');
            } else if (i === currentStep) {
                if (step === 'complete' && !success) {
                    stepElements[i].classList.add('error');
                } else {
                    stepElements[i].classList.add('active');
                    if (step === 'complete') {
                        stepElements[i].classList.add('complete');
                    }
                }
            }
        }

        // Atualiza mensagem
        const messages = {
            'validation': 'Validando dados...',
            'processing': 'Processando informações...',
            'sending': 'Enviando para o servidor...',
            'complete': success ? 'Cadastro concluído com sucesso!' : 'Erro ao processar cadastro'
        };

        if (messageElement) {
            messageElement.textContent = messages[step] || '';
        }

        // Mostra/oculta container
        container.style.display = step !== 'complete' || !success ? 'block' : 'none';
    }

    /**
     * Mostra toast de notificação
     */
    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');

        if (!container) {
            alert(message);
            return;
        }

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'warning' ? 'warning' : 'success'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        container.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remove após fechar
        toast.addEventListener('hidden.bs.toast', function () {
            toast.remove();
        });
    }

    // Exporta para uso global
    window.initCadastroInstituicao = initCadastroInstituicao;

    // Auto-init se DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCadastroInstituicao);
    } else {
        initCadastroInstituicao();
    }

})();
