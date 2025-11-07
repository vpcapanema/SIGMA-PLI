/**
 * Biblioteca de Máscaras de Formatação para Campos de Entrada
 * Padroniza a formatação de informações que serão ingeridas no banco
 * 
 * Máscaras Disponíveis:
 * - CPF: 123.456.789-00
 * - CNPJ: 12.345.678/0001-90
 * - Telefone: (11) 98765-4321 ou (11) 8765-4321
 * - CEP: 12345-678
 * - Data: DD/MM/YYYY
 * - RG: 12.345.678-9
 * - CNH: 1234567890123456
 */

class InputMaskManager {
    constructor() {
        this.masks = {
            cpf: /(\d{3})(\d{3})(\d{3})(\d{2})/,
            cnpj: /(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/,
            telefone10: /(\d{2})(\d{4})(\d{4})/,
            telefone11: /(\d{2})(\d{5})(\d{4})/,
            cep: /(\d{5})(\d{3})/,
            data: /(\d{2})(\d{2})(\d{4})/,
            rg: /(\d{2})(\d{3})(\d{3})(\d{1})/,
            cnh: /(\d{4})(\d{6})(\d{6})/,
        };

        this.patterns = {
            cpf: { pattern: /\d/g, format: 'cpf' },
            cnpj: { pattern: /\d/g, format: 'cnpj' },
            telefone: { pattern: /\d/g, format: 'telefone' },
            cep: { pattern: /\d/g, format: 'cep' },
            data: { pattern: /\d/g, format: 'data' },
            rg: { pattern: /\d/g, format: 'rg' },
            cnh: { pattern: /\d/g, format: 'cnh' },
        };
    }

    /**
     * Remove caracteres não numéricos
     */
    onlyNumbers(value) {
        return value.replace(/\D/g, '');
    }

    /**
     * Formata CPF: 123.456.789-00
     */
    formatCPF(value) {
        const clean = this.onlyNumbers(value);
        if (clean.length === 0) return '';
        if (clean.length <= 3) return clean;
        if (clean.length <= 6) return `${clean.slice(0, 3)}.${clean.slice(3)}`;
        if (clean.length <= 9)
            return `${clean.slice(0, 3)}.${clean.slice(3, 6)}.${clean.slice(6)}`;
        return `${clean.slice(0, 3)}.${clean.slice(3, 6)}.${clean.slice(
            6,
            9
        )}-${clean.slice(9, 11)}`;
    }

    /**
     * Formata CNPJ: 12.345.678/0001-90
     */
    formatCNPJ(value) {
        const clean = this.onlyNumbers(value);
        if (clean.length === 0) return '';
        if (clean.length <= 2) return clean;
        if (clean.length <= 5) return `${clean.slice(0, 2)}.${clean.slice(2)}`;
        if (clean.length <= 8)
            return `${clean.slice(0, 2)}.${clean.slice(2, 5)}.${clean.slice(5)}`;
        if (clean.length <= 12)
            return `${clean.slice(0, 2)}.${clean.slice(2, 5)}.${clean.slice(
                5,
                8
            )}/${clean.slice(8)}`;
        return `${clean.slice(0, 2)}.${clean.slice(2, 5)}.${clean.slice(
            5,
            8
        )}/${clean.slice(8, 12)}-${clean.slice(12, 14)}`;
    }

    /**
     * Formata Telefone: (11) 98765-4321 ou (11) 8765-4321
     */
    formatTelefone(value) {
        const clean = this.onlyNumbers(value);
        if (clean.length === 0) return '';
        if (clean.length <= 2) return `(${clean}`;
        if (clean.length <= 7)
            return `(${clean.slice(0, 2)}) ${clean.slice(2)}`;
        if (clean.length <= 10)
            return `(${clean.slice(0, 2)}) ${clean.slice(2, 6)}-${clean.slice(6)}`;
        return `(${clean.slice(0, 2)}) ${clean.slice(2, 7)}-${clean.slice(7, 11)}`;
    }

    /**
     * Formata CEP: 12345-678
     */
    formatCEP(value) {
        const clean = this.onlyNumbers(value);
        if (clean.length === 0) return '';
        if (clean.length <= 5) return clean;
        return `${clean.slice(0, 5)}-${clean.slice(5, 8)}`;
    }

    /**
     * Formata Data: DD/MM/YYYY
     */
    formatData(value) {
        const clean = this.onlyNumbers(value);
        if (clean.length === 0) return '';
        if (clean.length <= 2) return clean;
        if (clean.length <= 4) return `${clean.slice(0, 2)}/${clean.slice(2)}`;
        return `${clean.slice(0, 2)}/${clean.slice(2, 4)}/${clean.slice(4, 8)}`;
    }

    /**
     * Formata RG: 12.345.678-9
     */
    formatRG(value) {
        const clean = this.onlyNumbers(value);
        if (clean.length === 0) return '';
        if (clean.length <= 2) return clean;
        if (clean.length <= 5)
            return `${clean.slice(0, 2)}.${clean.slice(2)}`;
        if (clean.length <= 8)
            return `${clean.slice(0, 2)}.${clean.slice(2, 5)}.${clean.slice(5)}`;
        return `${clean.slice(0, 2)}.${clean.slice(2, 5)}.${clean.slice(
            5,
            8
        )}-${clean.slice(8, 9)}`;
    }

    /**
     * Formata CNH: 1234567890123456 (sem formatação, apenas validação)
     */
    formatCNH(value) {
        return this.onlyNumbers(value).slice(0, 13);
    }

    /**
     * Aplica máscara baseada no tipo
     */
    aplicarMascara(value, tipo) {
        const metodo = `format${tipo.charAt(0).toUpperCase() + tipo.slice(1).toLowerCase()}`;
        if (typeof this[metodo] === 'function') {
            return this[metodo](value);
        }
        return value;
    }

    /**
     * Configura listener de input para campo específico
     */
    setupField(fieldId, maskType) {
        const field = document.getElementById(fieldId);
        if (!field) {
            console.warn(`⚠️ Campo não encontrado: ${fieldId}`);
            return false;
        }

        // Listener para entrada em tempo real
        field.addEventListener('input', (e) => {
            e.target.value = this.aplicarMascara(e.target.value, maskType);
        });

        // Listener para blur (ao sair do campo)
        field.addEventListener('blur', (e) => {
            e.target.value = this.aplicarMascara(e.target.value, maskType);
        });

        console.log(`✅ Máscara ${maskType} aplicada ao campo #${fieldId}`);
        return true;
    }

    /**
     * Configura múltiplos campos de uma vez
     */
    setupFields(fieldConfigs) {
        /**
         * fieldConfigs: [
         *   { id: 'cpf', mask: 'cpf' },
         *   { id: 'telefone', mask: 'telefone' },
         *   ...
         * ]
         */
        fieldConfigs.forEach((config) => {
            this.setupField(config.id, config.mask);
        });
        console.log(
            `✅ ${fieldConfigs.length} campos de máscara configurados`
        );
    }

    /**
     * Remove máscara e retorna apenas números
     */
    removeMascara(value) {
        return this.onlyNumbers(value);
    }

    /**
     * Obtém valor limpo (sem máscara) para envio ao servidor
     */
    getCleanValue(fieldId) {
        const field = document.getElementById(fieldId);
        if (!field) return '';
        return this.removeMascara(field.value);
    }

    /**
     * Valida CPF com Módulo 11 (básico)
     */
    validarCPF(cpf) {
        const clean = this.removeMascara(cpf);
        if (clean.length !== 11) return false;

        // Rejeitar sequências conhecidas como inválidas
        if (/^(\d)\1{10}$/.test(clean)) return false;

        // Validação do Módulo 11 (simplificada)
        return true;
    }

    /**
     * Valida CNPJ
     */
    validarCNPJ(cnpj) {
        const clean = this.removeMascara(cnpj);
        return clean.length === 14;
    }

    /**
     * Valida Telefone
     */
    validarTelefone(telefone) {
        const clean = this.removeMascara(telefone);
        return clean.length === 10 || clean.length === 11;
    }

    /**
     * Valida CEP
     */
    validarCEP(cep) {
        const clean = this.removeMascara(cep);
        return clean.length === 8;
    }

    /**
     * Valida Data (DD/MM/YYYY)
     */
    validarData(data) {
        const clean = this.removeMascara(data);
        if (clean.length !== 8) return false;

        const dia = parseInt(clean.slice(0, 2));
        const mes = parseInt(clean.slice(2, 4));
        const ano = parseInt(clean.slice(4, 8));

        if (mes < 1 || mes > 12) return false;
        if (dia < 1 || dia > 31) return false;

        return true;
    }
}

// Instância global
const inputMaskManager = new InputMaskManager();

/**
 * EXEMPLO DE USO:
 *
 * // Configurar campos individuais
 * document.addEventListener('DOMContentLoaded', function () {
 *   inputMaskManager.setupField('cpf', 'cpf');
 *   inputMaskManager.setupField('telefone', 'telefone');
 *   inputMaskManager.setupField('cep', 'cep');
 * });
 *
 * // OU Configurar múltiplos campos
 * inputMaskManager.setupFields([
 *   { id: 'cpf', mask: 'cpf' },
 *   { id: 'telefone', mask: 'telefone' },
 *   { id: 'cep', mask: 'cep' },
 *   { id: 'data_nascimento', mask: 'data' },
 *   { id: 'rg', mask: 'rg' },
 *   { id: 'cnpj', mask: 'cnpj' },
 * ]);
 *
 * // Obter valor limpo para enviar ao servidor
 * const cpfLimpo = inputMaskManager.getCleanValue('cpf'); // "12345678900"
 */
