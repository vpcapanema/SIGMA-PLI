// Script para cadastro de usuário - formulário com lógica completa
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', () => {
        const form = document.getElementById('usuarioPublicForm');
        const nomeSelect = document.getElementById('nome');
        const instituicaoSelect = document.getElementById('instituicao_nome');
        const tipoUsuarioSelect = document.getElementById('tipo_usuario');
        const usernameInput = document.getElementById('username');
        const toggleSenha = document.getElementById('toggleSenha');
        const toggleConfirm = document.getElementById('toggleConfirmarSenha');
        const senhaInput = document.getElementById('senha');
        const confirmarSenhaInput = document.getElementById('confirmarSenha');
        const passwordStrengthBar = document.getElementById('passwordStrength');
        const passwordStrengthText = document.getElementById('passwordStrengthText');

        let pessoasFisicas = [];
        let instituicoes = [];
        let pessoaSelecionada = null;

        // Nota: Endpoints /api/v1/pessoas/fisicas e /api/v1/pessoas/juridicas foram removidos
        // O formulário de cadastro de usuário agora recebe pessoa_fisica_id e instituicao_id diretamente
        // Esses selects são opcionais e podem ser preenchidos manualmente ou via integração posterior

        // Gerar username automaticamente
        function gerarUsername() {
            if (!pessoaSelecionada || !tipoUsuarioSelect.value) {
                usernameInput.value = '';
                return;
            }

            const nomeCompleto = pessoaSelecionada.nome.trim();
            const partes = nomeCompleto.split(' ').filter(p => p.length > 0);

            if (partes.length === 0) {
                usernameInput.value = '';
                return;
            }

            const primeiroNome = partes[0].toLowerCase();
            const ultimoSobrenome = partes.length > 1 ? partes[partes.length - 1].toLowerCase() : '';
            const tipoUsuario = tipoUsuarioSelect.value;

            const username = ultimoSobrenome
                ? `${primeiroNome}.${ultimoSobrenome}_${tipoUsuario}`
                : `${primeiroNome}_${tipoUsuario}`;

            // Remover acentos e caracteres especiais
            usernameInput.value = username
                .normalize('NFD')
                .replace(/[\u0300-\u036f]/g, '')
                .replace(/[^a-z0-9_.]/g, '');
        }

        // Handler para seleção de pessoa física
        nomeSelect.addEventListener('change', (e) => {
            const selectedOption = e.target.selectedOptions[0];

            if (!selectedOption || !selectedOption.value) {
                // Limpar campos
                document.getElementById('pessoa_fisica_id').value = '';
                document.getElementById('email').value = '';
                document.getElementById('documento').value = '';
                document.getElementById('telefone').value = '';
                document.getElementById('data_nascimento').value = '';
                pessoaSelecionada = null;
                gerarUsername();
                return;
            }

            pessoaSelecionada = JSON.parse(selectedOption.dataset.pessoa);

            // Preencher campos
            document.getElementById('pessoa_fisica_id').value = pessoaSelecionada.id;
            document.getElementById('email').value = pessoaSelecionada.email || '';
            document.getElementById('documento').value = pessoaSelecionada.cpf || '';
            document.getElementById('telefone').value = pessoaSelecionada.telefone || '';
            document.getElementById('data_nascimento').value = pessoaSelecionada.data_nascimento || '';

            gerarUsername();
        });

        // Handler para seleção de instituição
        instituicaoSelect.addEventListener('change', (e) => {
            const selectedOption = e.target.selectedOptions[0];

            if (!selectedOption || !selectedOption.value) {
                document.getElementById('instituicao_id').value = '';
                return;
            }

            const instituicao = JSON.parse(selectedOption.dataset.instituicao);
            document.getElementById('instituicao_id').value = instituicao.id;
        });

        // Handler para mudança no tipo de usuário
        tipoUsuarioSelect.addEventListener('change', gerarUsername);

        // Toggle visualização de senha
        function toggle(inputId, button) {
            const input = document.getElementById(inputId);
            if (!input) return;
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            const icon = button.querySelector('i');
            if (icon) {
                icon.className = isPassword ? 'fa fa-eye-slash' : 'fa fa-eye';
            }
        }

        if (toggleSenha) {
            toggleSenha.addEventListener('click', () => toggle('senha', toggleSenha));
        }
        if (toggleConfirm) {
            toggleConfirm.addEventListener('click', () => toggle('confirmarSenha', toggleConfirm));
        }

        // Validação de força da senha
        function checkPasswordStrength(password) {
            let strength = 0;
            if (password.length >= 8) strength++;
            if (password.length >= 12) strength++;
            if (/[a-z]/.test(password)) strength++;
            if (/[A-Z]/.test(password)) strength++;
            if (/[0-9]/.test(password)) strength++;
            if (/[^a-zA-Z0-9]/.test(password)) strength++;

            return strength;
        }

        function updatePasswordStrength() {
            if (!senhaInput || !passwordStrengthBar || !passwordStrengthText) return;

            const password = senhaInput.value;
            const strength = checkPasswordStrength(password);

            const strengthLevels = [
                { level: 0, text: '', width: '0%', color: '' },
                { level: 1, text: 'Muito fraca', width: '20%', color: 'bg-danger' },
                { level: 2, text: 'Fraca', width: '40%', color: 'bg-warning' },
                { level: 3, text: 'Média', width: '60%', color: 'bg-info' },
                { level: 4, text: 'Boa', width: '80%', color: 'bg-primary' },
                { level: 5, text: 'Forte', width: '100%', color: 'bg-success' },
                { level: 6, text: 'Muito forte', width: '100%', color: 'bg-success' }
            ];

            const current = strengthLevels[Math.min(strength, 6)];

            passwordStrengthBar.style.width = current.width;
            passwordStrengthBar.className = 'password-strength-bar ' + current.color;
            passwordStrengthText.textContent = current.text;
        }

        if (senhaInput) {
            senhaInput.addEventListener('input', updatePasswordStrength);
        }

        function showError(message) {
            alert(message); // Substituir por toast notification se necessário
        }

        function showSuccess(message) {
            alert(message); // Substituir por toast notification se necessário
        }

        // Validação do formulário
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                // Validação básica
                if (!form.checkValidity()) {
                    e.stopPropagation();
                    form.classList.add('was-validated');
                    return;
                }

                // Verificar se as senhas coincidem
                const senha = senhaInput?.value;
                const confirmarSenha = confirmarSenhaInput?.value;

                if (senha !== confirmarSenha) {
                    const feedback = document.getElementById('confirmarSenhaFeedback');
                    if (feedback) feedback.textContent = 'As senhas não coincidem.';
                    if (confirmarSenhaInput) {
                        confirmarSenhaInput.classList.add('is-invalid');
                    }
                    return;
                }

                // Verificar força da senha
                const strength = checkPasswordStrength(senha);
                if (strength < 4) {
                    const feedback = document.getElementById('senhaFeedback');
                    if (feedback) feedback.textContent = 'A senha não é forte o suficiente. Use pelo menos 8 caracteres com letras maiúsculas, minúsculas, números e caracteres especiais.';
                    if (senhaInput) {
                        senhaInput.classList.add('is-invalid');
                    }
                    return;
                }

                // Coletar dados do formulário
                const formData = {
                    pessoa_fisica_id: document.getElementById('pessoa_fisica_id').value,
                    instituicao_id: document.getElementById('instituicao_id').value,
                    email_institucional: form.email_institucional.value,
                    telefone_institucional: form.telefone_institucional?.value || null,
                    tipo_usuario: form.tipo_usuario.value,
                    username: form.username.value,
                    senha: senha,
                    termo_privacidade: form.termo_privacidade.checked,
                    termo_uso: form.termo_uso.checked
                };

                console.log('Dados do cadastro:', formData);

                // Enviar para API /api/cadastro/usuario
                try {
                    const response = await fetch('/api/cadastro/usuario', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(formData)
                    });

                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Erro ao criar usuário');
                    }

                    const result = await response.json();
                    showSuccess('Usuário cadastrado com sucesso!');

                    // Redirecionar ou mostrar modal de sucesso
                    setTimeout(() => {
                        window.location.href = '/auth/login';
                    }, 2000);

                } catch (error) {
                    console.error('Erro ao cadastrar:', error);
                    showError(error.message || 'Erro ao cadastrar usuário');
                }
            });
        }
    });
})();
