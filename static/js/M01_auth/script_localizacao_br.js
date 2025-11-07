/**
 * Script para carregar e gerenciar UFs e Municípios brasileiros
 * Integrando com a API de Localização BR do backend
 * 
 * Endpoints usados:
 * - GET /api/v1/localizacao/ufs
 * - GET /api/v1/localizacao/municipios/{uf}
 */

class LocalizacaoBRManager {
    constructor() {
        this.ufs = [];
        this.municipios = {};
        this.initialized = false;
    }

    /**
     * Carrega lista de UFs do backend
     */
    async carregarUFs() {
        try {
            const response = await fetch('/api/v1/localizacao/ufs');
            const data = await response.json();

            if (!response.ok) {
                console.error('❌ Erro ao carregar UFs:', data);
                return false;
            }

            this.ufs = data.ufs;
            console.log(`✅ ${data.total} UFs carregados`);
            return true;
        } catch (error) {
            console.error('❌ Erro ao conectar backend:', error);
            return false;
        }
    }

    /**
     * Carrega lista de municípios de um UF
     */
    async carregarMunicipios(uf) {
        uf = uf.toUpperCase().trim();

        // Verificar cache
        if (this.municipios[uf]) {
            return this.municipios[uf];
        }

        try {
            const response = await fetch(`/api/v1/localizacao/municipios/${uf}`);
            const data = await response.json();

            if (!response.ok) {
                console.error(`❌ Erro ao carregar municípios de ${uf}:`, data);
                return [];
            }

            this.municipios[uf] = data.municipios;
            console.log(`✅ ${data.total} municípios de ${uf} carregados`);
            return this.municipios[uf];
        } catch (error) {
            console.error(`❌ Erro ao conectar backend:`, error);
            return [];
        }
    }

    /**
     * Popula um select de UFs
     */
    async preencherSelectUFs(selectId) {
        const select = document.getElementById(selectId);
        if (!select) return false;

        // Se UFs não estão carregados, carregar
        if (this.ufs.length === 0) {
            const success = await this.carregarUFs();
            if (!success) return false;
        }

        // Limpar opções existentes (mantendo "Selecione")
        while (select.options.length > 1) {
            select.remove(1);
        }

        // Adicionar UFs
        this.ufs.forEach((uf) => {
            const option = document.createElement('option');
            option.value = uf.sigla;
            option.textContent = `${uf.sigla} - ${uf.nome}`;
            select.appendChild(option);
        });

        console.log(`✅ Select #${selectId} preenchido com ${this.ufs.length} UFs`);
        return true;
    }

    /**
     * Popula um select de Municípios baseado em um UF selecionado
     */
    async preencherSelectMunicipios(ufSelectId, municipioSelectId) {
        const ufSelect = document.getElementById(ufSelectId);
        const municipioSelect = document.getElementById(municipioSelectId);

        if (!ufSelect || !municipioSelect) return false;

        // Listener para mudança de UF
        ufSelect.addEventListener('change', async (e) => {
            const ufSelecionado = e.target.value;

            // Limpar select de municípios
            while (municipioSelect.options.length > 1) {
                municipioSelect.remove(1);
            }

            if (!ufSelecionado) {
                console.log('ℹ️ Nenhum UF selecionado');
                return;
            }

            // Mostrar loading
            municipioSelect.disabled = true;
            municipioSelect.innerHTML = '<option value="">Carregando municípios...</option>';

            // Carregar municípios
            const municipios = await this.carregarMunicipios(ufSelecionado);

            if (municipios.length === 0) {
                municipioSelect.innerHTML =
                    '<option value="">Erro ao carregar municípios</option>';
                municipioSelect.disabled = true;
                return;
            }

            // Preencher select
            municipioSelect.innerHTML = '<option value="">Selecione o município</option>';
            municipios.forEach((mun) => {
                const option = document.createElement('option');
                option.value = mun.id;
                option.textContent = mun.nome;
                municipioSelect.appendChild(option);
            });

            municipioSelect.disabled = false;
            console.log(`✅ Municípios de ${ufSelecionado} carregados`);
        });

        return true;
    }

    /**
     * Inicialização completa - carrega UFs e prepara selects
     */
    async inicializar(ufSelectIds = [], linkMunicipios = []) {
        if (this.initialized) return true;

        // Carregar UFs
        const success = await this.carregarUFs();
        if (!success) {
            console.warn('⚠️ Falha ao carregar UFs');
            return false;
        }

        // Preencher selects de UFs
        for (const selectId of ufSelectIds) {
            await this.preencherSelectUFs(selectId);
        }

        // Vincular UF → Municípios
        for (const link of linkMunicipios) {
            await this.preencherSelectMunicipios(link.ufSelectId, link.municipioSelectId);
        }

        this.initialized = true;
        console.log('✅ LocalizacaoBRManager inicializado');
        return true;
    }
}

// Instância global acessível via window
window.localizacaoBR = new LocalizacaoBRManager();

/**
 * Exemplo de uso:
 * 
 * // Inicializar quando página carrega
 * document.addEventListener('DOMContentLoaded', async () => {
 *   if (window.localizacaoBR) {
 *     await window.localizacaoBR.inicializar(
 *       ['ufNaturalidade', 'ufRg'],  // IDs dos selects de UF
 *       [
 *         { ufSelectId: 'ufNaturalidade', municipioSelectId: 'naturalidade' }
 *       ]  // Vinculações UF → Município
 *     );
 *   }
 * });
 */

// Debug: Log para verificar se foi carregado
console.log('✅ script_localizacao_br.js carregado com sucesso');
if (window.localizacaoBR) {
    console.log('✅ window.localizacaoBR está disponível');
} else {
    console.error('❌ window.localizacaoBR NÃO está disponível!');
}
