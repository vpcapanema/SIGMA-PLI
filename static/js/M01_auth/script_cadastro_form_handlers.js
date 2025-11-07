/**
 * Handler dos Formulários de Cadastro
 * Pessoa Física, Pessoa Jurídica e Usuário
 */

/**
 * Handler para Cadastro de Pessoa Física
 */
function initCadastroPessoaFisica() {
    const form = document.getElementById('pessoaFisicaPublicForm');
    if (!form) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Validar formulário
        if (!form.checkValidity()) {
            event.stopPropagation();
            form.classList.add('was-validated');
            return;
        }

        const formData = {
            // Dados Pessoais
            nome_completo: document.getElementById('nomeCompleto')?.value.trim(),
            nome_social: document.getElementById('nomeSocial')?.value.trim() || null,
            cpf: document.getElementById('cpf')?.value.replace(/\D/g, ''),
            data_nascimento: document.getElementById('dataNascimento')?.value || null,
            sexo: document.getElementById('sexo')?.value || null,
            estado_civil: document.getElementById('estado_civil')?.value || null,
            nacionalidade: document.getElementById('nacionalidade')?.value.trim() || "BRASILEIRA",
            naturalidade: document.getElementById('naturalidade')?.value.trim() || null,

            // Informações Familiares
            nome_pai: document.getElementById('nomePai')?.value.trim() || null,
            nome_mae: document.getElementById('nomeMae')?.value.trim() || null,

            // Documentos
            rg: document.getElementById('rg')?.value.trim() || null,
            orgao_expeditor: document.getElementById('orgaoExpeditor')?.value.trim() || null,
            uf_rg: document.getElementById('ufRg')?.value || null,
            data_expedicao_rg: document.getElementById('dataExpedicaoRg')?.value || null,
            titulo_eleitor: document.getElementById('tituloEleitor')?.value.trim() || null,
            zona_eleitoral: document.getElementById('zonaEleitoral')?.value.trim() || null,
            secao_eleitoral: document.getElementById('secaoEleitoral')?.value.trim() || null,
            pis_pasep: document.getElementById('pisPasep')?.value.trim() || null,

            // Contato
            email: document.getElementById('email')?.value.trim(),
            email_secundario: document.getElementById('emailSecundario')?.value.trim() || null,
            telefone_principal: document.getElementById('telefonePrincipal')?.value.trim() || null,
            telefone_secundario: document.getElementById('telefoneSecundario')?.value.trim() || null,

            // Profissionais
            profissao: document.getElementById('profissao')?.value.trim() || null,
            escolaridade: document.getElementById('escolaridade')?.value || null,
            renda_mensal: document.getElementById('rendaMensal')?.value ? parseFloat(document.getElementById('rendaMensal').value) : null,

            // Endereço
            cep: document.getElementById('cep')?.value.replace(/\D/g, '') || null,
            logradouro: document.getElementById('logradouro')?.value.trim() || null,
            numero: document.getElementById('numero')?.value.trim() || null,
            complemento: document.getElementById('complemento')?.value.trim() || null,
            bairro: document.getElementById('bairro')?.value.trim() || null,
            cidade: document.getElementById('cidade')?.value.trim() || null,
            uf: document.getElementById('uf')?.value || null,
            pais: document.getElementById('pais')?.value.trim() || "Brasil"
        };

        // Validação
        if (!formData.nome_completo || !formData.cpf || !formData.email) {
            showError('Por favor, preencha todos os campos obrigatórios');
            return;
        }

        // Validar CPF
        if (!validarCPF(formData.cpf)) {
            showError('CPF inválido');
            return;
        }

        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
        }

        try {
            // Gravar no cadastro.pessoa (rota pública de cadastro)
            const response = await fetch('/api/cadastro/pessoa-fisica', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // Payload mínimo esperado pelo endpoint público
                body: JSON.stringify({
                    nome_completo: formData.nome_completo,
                    cpf: formData.cpf,
                    email: formData.email,
                    telefone_principal: formData.telefone_principal || formData.telefone_secundario || null,
                    profissao: formData.profissao || null
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao cadastrar');
            }

            const data = await response.json();

            showSuccess('Cadastro realizado com sucesso!');

            // Mostrar modal de sucesso se existir
            const successModal = document.getElementById('successModal');
            if (successModal) {
                const modal = new bootstrap.Modal(successModal);
                modal.show();
            }

            // Redirecionar ou limpar formulário
            setTimeout(() => {
                window.location.href = '/auth/cadastro-usuario?pessoa_id=' + data.pessoa_id;
            }, 2000);
        } catch (error) {
            showError(error.message);
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar Cadastro';
            }
        }
    });
}

/**
 * Handler para Cadastro de Pessoa Jurídica
 */
function initCadastroPessoaJuridica() {
    const form = document.getElementById('pessoaJuridicaPublicForm');
    if (!form) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Validar formulário
        if (!form.checkValidity()) {
            event.stopPropagation();
            form.classList.add('was-validated');
            return;
        }

        const formData = {
            // Dados da Empresa
            razao_social: document.getElementById('razaoSocial')?.value.trim(),
            nome_fantasia: document.getElementById('nomeFantasia')?.value.trim() || null,
            cnpj: document.getElementById('cnpj')?.value.replace(/\D/g, ''),
            inscricao_estadual: document.getElementById('inscricaoEstadual')?.value.trim() || null,
            inscricao_municipal: document.getElementById('inscricaoMunicipal')?.value.trim() || null,
            data_fundacao: document.getElementById('dataFundacao')?.value || null,
            porte_empresa: document.getElementById('porteEmpresa')?.value || null,
            natureza_juridica: document.getElementById('naturezaJuridica')?.value.trim() || null,
            atividade_principal: document.getElementById('atividadePrincipal')?.value.trim() || null,

            // Contato
            email: document.getElementById('email')?.value.trim(),
            email_secundario: document.getElementById('emailSecundario')?.value.trim() || null,
            telefone: document.getElementById('telefone')?.value.trim() || null,
            telefone_secundario: document.getElementById('telefoneSecundario')?.value.trim() || null,
            site: document.getElementById('site')?.value.trim() || null,

            // Endereço
            cep: document.getElementById('cep')?.value.replace(/\D/g, '') || null,
            logradouro: document.getElementById('logradouro')?.value.trim() || null,
            numero: document.getElementById('numero')?.value.trim() || null,
            complemento: document.getElementById('complemento')?.value.trim() || null,
            bairro: document.getElementById('bairro')?.value.trim() || null,
            cidade: document.getElementById('cidade')?.value.trim() || null,
            uf: document.getElementById('uf')?.value || null,
            pais: document.getElementById('pais')?.value.trim() || "Brasil"
        };

        // Validação
        if (!formData.razao_social || !formData.cnpj || !formData.email) {
            showError('Por favor, preencha todos os campos obrigatórios');
            return;
        }

        // Validar CNPJ
        if (!validarCNPJ(formData.cnpj)) {
            showError('CNPJ inválido');
            return;
        }

        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
        }

        try {
            const response = await fetch('/api/cadastro/instituicao', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao cadastrar');
            }

            const data = await response.json();

            showSuccess('Cadastro realizado com sucesso!');

            // Mostrar modal de sucesso se existir
            const successModal = document.getElementById('successModal');
            if (successModal) {
                const modal = new bootstrap.Modal(successModal);
                modal.show();
            }

            setTimeout(() => {
                window.location.href = '/auth/cadastro-usuario?pessoa_id=' + data.pessoa_id;
            }, 2000);
        } catch (error) {
            showError(error.message);
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar Cadastro';
            }
        }
    });
}

/**
 * Handler para Cadastro de Usuário
 */
function initCadastroUsuario() {
    const form = document.getElementById('usuarioPublicForm');
    if (!form) {
        console.error('Formulário usuarioPublicForm não encontrado');
        return;
    }

    // Obter pessoa_id da URL
    const urlParams = new URLSearchParams(window.location.search);
    const pessoaId = urlParams.get('pessoa_id');

    // Validar se pessoa_id existe
    if (!pessoaId) {
        showError('ID da pessoa não encontrado. Por favor, faça o cadastro de pessoa primeiro.');
        setTimeout(() => {
            window.location.href = '/auth/cadastro-pessoa-fisica';
        }, 2000);
        return;
    }

    // Preencher campo hidden se existir
    const pessoaIdField = document.getElementById('pessoaId');
    if (pessoaIdField) {
        pessoaIdField.value = pessoaId;
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Validar formulário
        if (!form.checkValidity()) {
            event.stopPropagation();
            form.classList.add('was-validated');
            return;
        }

        const username = document.getElementById('username')?.value.trim();
        const email = document.getElementById('email')?.value.trim();
        const password = document.getElementById('senha')?.value;
        const confirmPassword = document.getElementById('confirmarSenha')?.value;

        // Validação
        if (!username || !email || !password || !confirmPassword) {
            showError('Por favor, preencha todos os campos');
            return;
        }

        if (password !== confirmPassword) {
            showError('As senhas não coincidem');
            return;
        }

        if (password.length < 8) {
            showError('A senha deve ter no mínimo 8 caracteres');
            return;
        }

        // Validar força da senha
        if (!validarSenhaForte(password)) {
            showError('A senha deve conter letras maiúsculas, minúsculas, números e caracteres especiais');
            return;
        }

        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Criando conta...';
        }

        try {
            const formData = {
                pessoa_id: pessoaId,
                username: username,
                email: email,
                password: password
            };

            const response = await fetch('/api/v1/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao criar conta');
            }

            const data = await response.json();

            showSuccess('Conta criada com sucesso! Redirecionando para login...');

            // Mostrar modal de sucesso se existir
            const successModal = document.getElementById('successModal');
            if (successModal) {
                const modal = new bootstrap.Modal(successModal);
                modal.show();
            }

            // Redirecionar para login
            setTimeout(() => {
                window.location.href = '/auth/login?registered=true';
            }, 2000);
        } catch (error) {
            showError(error.message);
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-user-plus me-2"></i>Criar Conta';
            }
        }
    });

    // Validação em tempo real da senha
    const passwordInput = document.getElementById('senha');
    const passwordStrength = document.getElementById('password_strength');

    if (passwordInput && passwordStrength) {
        passwordInput.addEventListener('input', () => {
            const password = passwordInput.value;
            const strength = calcularForcaSenha(password);

            passwordStrength.textContent = `Força: ${strength.label}`;
            passwordStrength.className = `password-strength ${strength.class}`;
        });
    }
}

/**
 * Validar CPF
 */
function validarCPF(cpf) {
    cpf = cpf.replace(/[^\d]/g, '');

    if (cpf.length !== 11) return false;
    if (/^(\d)\1+$/.test(cpf)) return false;

    let soma = 0;
    for (let i = 0; i < 9; i++) {
        soma += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let resto = 11 - (soma % 11);
    let digitoVerificador1 = resto >= 10 ? 0 : resto;

    soma = 0;
    for (let i = 0; i < 10; i++) {
        soma += parseInt(cpf.charAt(i)) * (11 - i);
    }
    resto = 11 - (soma % 11);
    let digitoVerificador2 = resto >= 10 ? 0 : resto;

    return (
        parseInt(cpf.charAt(9)) === digitoVerificador1 &&
        parseInt(cpf.charAt(10)) === digitoVerificador2
    );
}

/**
 * Validar CNPJ
 */
function validarCNPJ(cnpj) {
    cnpj = cnpj.replace(/[^\d]/g, '');

    if (cnpj.length !== 14) return false;
    if (/^(\d)\1+$/.test(cnpj)) return false;

    let tamanho = cnpj.length - 2;
    let numeros = cnpj.substring(0, tamanho);
    let digitos = cnpj.substring(tamanho);
    let soma = 0;
    let pos = tamanho - 7;

    for (let i = tamanho; i >= 1; i--) {
        soma += numeros.charAt(tamanho - i) * pos--;
        if (pos < 2) pos = 9;
    }

    let resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11);
    if (resultado !== parseInt(digitos.charAt(0))) return false;

    tamanho = tamanho + 1;
    numeros = cnpj.substring(0, tamanho);
    soma = 0;
    pos = tamanho - 7;

    for (let i = tamanho; i >= 1; i--) {
        soma += numeros.charAt(tamanho - i) * pos--;
        if (pos < 2) pos = 9;
    }

    resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11);
    return resultado === parseInt(digitos.charAt(1));
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
}

// Inicializar handlers quando DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    initCadastroPessoaFisica();
    initCadastroPessoaJuridica();
    initCadastroUsuario();
});
