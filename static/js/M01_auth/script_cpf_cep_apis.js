/**
 * Script para integração de APIs de CPF e CEP no formulário de cadastro
 * Funcionalidades:
 * - Validação de CPF em tempo real
 * - Consulta automática de CEP
 * - Busca de dados de endereço completo
 */

(function () {
    'use strict';

    // Configurações
    const CONFIG = {
        API_CPF_VALIDAR: '/api/v1/externas/cpf/validar',
        API_CNPJ_VALIDAR: '/api/v1/externas/cnpj/validar',
        API_CEP_CONSULTAR: '/api/v1/externas/cep/consultar',
        DEBOUNCE_DELAY: 500 // ms
    };

    // Estado global
    let debounceTimers = {};

    /**
     * Formata CPF para o padrão XXX.XXX.XXX-XX
     */
    function formatarCPF(cpf) {
        const cleaned = cpf.replace(/\D/g, '');
        if (cleaned.length !== 11) return cleaned;
        return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    }

    /**
     * Remove formatação de CPF
     */
    function limparCPF(cpf) {
        return cpf.replace(/\D/g, '');
    }

    /**
     * Formata CEP para o padrão XXXXX-XXX
     */
    function formatarCEP(cep) {
        const cleaned = cep.replace(/\D/g, '');
        if (cleaned.length !== 8) return cleaned;
        return cleaned.replace(/(\d{5})(\d{3})/, '$1-$2');
    }

    /**
     * Remove formatação de CEP
     */
    function limparCEP(cep) {
        return cep.replace(/\D/g, '');
    }

    /**
     * Exibe mensagem de erro
     */
    function mostrarErro(elementId, mensagem) {
        const elemento = document.getElementById(elementId);
        if (elemento) {
            elemento.classList.add('is-invalid');
            const feedback = elemento.parentElement.querySelector('.invalid-feedback');
            if (feedback) {
                feedback.textContent = mensagem;
                feedback.style.display = 'block';
            }
        }
    }

    /**
     * Remove mensagem de erro
     */
    function limparErro(elementId) {
        const elemento = document.getElementById(elementId);
        if (elemento) {
            elemento.classList.remove('is-invalid');
            const feedback = elemento.parentElement.querySelector('.invalid-feedback');
            if (feedback) {
                feedback.style.display = 'none';
            }
        }
    }

    /**
     * Exibe mensagem de sucesso
     */
    function mostrarSucesso(elementId) {
        const elemento = document.getElementById(elementId);
        if (elemento) {
            elemento.classList.remove('is-invalid');
            elemento.classList.add('is-valid');
        }
    }

    /**
     * Valida CPF via API
     */
    async function validarCPF(cpf) {
        try {
            const cpfLimpo = limparCPF(cpf);

            if (cpfLimpo.length !== 11) {
                mostrarErro('documento', 'CPF deve conter 11 dígitos');
                return false;
            }

            const response = await fetch(CONFIG.API_CPF_VALIDAR, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ cpf: cpfLimpo })
            });

            if (!response.ok) {
                throw new Error('Erro ao validar CPF');
            }

            const data = await response.json();

            if (data.valido) {
                mostrarSucesso('documento');
                limparErro('documento');
                return true;
            } else {
                mostrarErro('documento', data.mensagem || 'CPF inválido');
                return false;
            }

        } catch (error) {
            console.error('Erro ao validar CPF:', error);
            mostrarErro('documento', 'Erro ao validar CPF. Tente novamente.');
            return false;
        }
    }

    /**
     * Consulta dados de endereço pelo CEP
     */
    async function consultarCEP(cep) {
        try {
            const cepLimpo = limparCEP(cep);

            if (cepLimpo.length !== 8) {
                mostrarErro('cep', 'CEP deve conter 8 dígitos');
                return null;
            }

            const response = await fetch(CONFIG.API_CEP_CONSULTAR, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ cep: cepLimpo })
            });

            if (!response.ok) {
                throw new Error('Erro ao consultar CEP');
            }

            const data = await response.json();

            if (data.erro) {
                mostrarErro('cep', data.mensagem || 'CEP não encontrado');
                return null;
            }

            mostrarSucesso('cep');
            limparErro('cep');
            return data;

        } catch (error) {
            console.error('Erro ao consultar CEP:', error);
            mostrarErro('cep', 'Erro ao consultar CEP. Verifique a entrada.');
            return null;
        }
    }

    /**
     * Preenche campos de endereço com dados do CEP
     */
    function preencherEndereco(dados) {
        if (dados.logradouro) {
            const logradouro = document.getElementById('logradouro');
            if (logradouro) logradouro.value = dados.logradouro;
        }

        if (dados.bairro) {
            const bairro = document.getElementById('bairro');
            if (bairro) bairro.value = dados.bairro;
        }

        if (dados.localidade) {
            const cidade = document.getElementById('cidade');
            if (cidade) cidade.value = dados.localidade;
        }

        if (dados.uf) {
            const estado = document.getElementById('estado');
            if (estado) estado.value = dados.uf;
        }

        if (dados.complemento) {
            const complemento = document.getElementById('complemento_endereco');
            if (complemento) complemento.value = dados.complemento;
        }
    }

    /**
     * Preenche campos da empresa com dados do CNPJ
     */
    function preencherEmpresa(dados) {
        if (dados.nome) {
            const nome = document.getElementById('razao_social');
            if (nome) nome.value = dados.nome;
        }

        if (dados.nome_fantasia) {
            const fantasia = document.getElementById('nome_fantasia');
            if (fantasia) fantasia.value = dados.nome_fantasia;
        }

        if (dados.logradouro) {
            const logradouro = document.getElementById('endereco_empresa');
            if (logradouro) logradouro.value = dados.logradouro;
        }

        if (dados.numero) {
            const numero = document.getElementById('numero_empresa');
            if (numero) numero.value = dados.numero;
        }

        if (dados.complemento) {
            const complemento = document.getElementById('complemento_empresa');
            if (complemento) complemento.value = dados.complemento;
        }

        if (dados.bairro) {
            const bairro = document.getElementById('bairro_empresa');
            if (bairro) bairro.value = dados.bairro;
        }

        if (dados.municipio) {
            const cidade = document.getElementById('cidade_empresa');
            if (cidade) cidade.value = dados.municipio;
        }

        if (dados.uf) {
            const estado = document.getElementById('estado_empresa');
            if (estado) estado.value = dados.uf;
        }

        if (dados.cep) {
            const cep = document.getElementById('cep_empresa');
            if (cep) cep.value = dados.cep;
        }

        if (dados.telefone) {
            const telefone = document.getElementById('telefone_empresa');
            if (telefone) telefone.value = dados.telefone;
        }

        if (dados.email) {
            const email = document.getElementById('email_empresa');
            if (email) email.value = dados.email;
        }
    }

    /**
     * Formata CNPJ para o padrão XX.XXX.XXX/XXXX-XX
     */
    function formatarCNPJ(cnpj) {
        const cleaned = cnpj.replace(/\D/g, '');
        if (cleaned.length !== 14) return cleaned;
        return cleaned.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    }

    /**
     * Remove formatação de CNPJ
     */
    function limparCNPJ(cnpj) {
        return cnpj.replace(/\D/g, '');
    }

    /**
     * Valida CNPJ via API
     */
    async function validarCNPJ(cnpj) {
        try {
            const cnpjLimpo = limparCNPJ(cnpj);

            if (cnpjLimpo.length !== 14) {
                mostrarErro('documento_empresa', 'CNPJ deve conter 14 dígitos');
                return false;
            }

            const response = await fetch(CONFIG.API_CNPJ_VALIDAR, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ cnpj: cnpjLimpo })
            });

            if (!response.ok) {
                throw new Error('Erro ao validar CNPJ');
            }

            const data = await response.json();

            if (data.valido) {
                mostrarSucesso('documento_empresa');
                limparErro('documento_empresa');

                // Preencher campos da empresa automaticamente
                preencherEmpresa(data);

                return true;
            } else {
                mostrarErro('documento_empresa', data.mensagem || 'CNPJ inválido');
                return false;
            }

        } catch (error) {
            console.error('Erro ao validar CNPJ:', error);
            mostrarErro('documento_empresa', 'Erro ao validar CNPJ. Tente novamente.');
            return false;
        }
    }

    /**
     * Handler com debounce para validação de CPF
     */
    function setupCPFValidation(elementId = 'cpf') {
        // Compatibilidade: aceitar id 'cpf' ou 'documento'
        const cpfInput = document.getElementById(elementId) || document.getElementById('documento');
        if (!cpfInput) return;

        cpfInput.addEventListener('blur', async (e) => {
            const cpf = e.target.value.trim();
            if (cpf.length > 0) {
                await validarCPF(cpf);
            }
        });

        cpfInput.addEventListener('input', (e) => {
            const cpf = e.target.value;
            // Formatar automaticamente
            if (cpf.length === 11 && limparCPF(cpf).length === 11) {
                e.target.value = formatarCPF(cpf);
            }
        });
    }

    /**
     * Handler com debounce para validação de CNPJ
     */
    function setupCNPJValidation(elementId = 'documento_empresa') {
        const cnpjInput = document.getElementById(elementId);
        if (!cnpjInput) return;

        cnpjInput.addEventListener('blur', async (e) => {
            const cnpj = e.target.value.trim();
            if (cnpj.length > 0) {
                await validarCNPJ(cnpj);
            }
        });

        cnpjInput.addEventListener('input', (e) => {
            const cnpj = e.target.value;
            // Formatar automaticamente
            if (limparCNPJ(cnpj).length === 14) {
                e.target.value = formatarCNPJ(cnpj);
            }
        });
    }

    /**
     * Handler com debounce para consulta de CEP
     */
    function setupCEPConsultation(elementId = 'cep') {
        const cepInput = document.getElementById(elementId) || document.getElementById('cep');
        if (!cepInput) return;

        cepInput.addEventListener('blur', async (e) => {
            const cep = e.target.value.trim();
            if (cep.length === 8 || cep.length === 9) {
                const dados = await consultarCEP(cep);
                if (dados) {
                    preencherEndereco(dados);
                }
            }
        });

        cepInput.addEventListener('input', (e) => {
            const cep = e.target.value;
            // Formatar automaticamente
            if (limparCEP(cep).length === 8) {
                e.target.value = formatarCEP(cep);
            }
        });
    }

    /**
     * Inicializa os handlers
     */
    function inicializar() {
        document.addEventListener('DOMContentLoaded', () => {
            setupCPFValidation();
            setupCNPJValidation();
            setupCEPConsultation();
        });
    }

    // Exportar funções úteis globalmente
    window.CPFCEPApis = {
        formatarCPF,
        limparCPF,
        formatarCEP,
        limparCEP,
        formatarCNPJ,
        limparCNPJ,
        validarCPF,
        validarCNPJ,
        consultarCEP,
        preencherEndereco,
        preencherEmpresa
        ,
        setupCPFValidation,
        setupCNPJValidation,
        setupCEPConsultation,
        setupCEPAutocomplete: setupCEPConsultation
        ,
        // Funções de setup para chamadas por páginas
        setupCPFValidation,
        setupCNPJValidation,
        setupCEPConsultation,
        setupCEPAutocomplete: setupCEPConsultation,
    };

    // Inicializar automaticamente
    inicializar();

})();
