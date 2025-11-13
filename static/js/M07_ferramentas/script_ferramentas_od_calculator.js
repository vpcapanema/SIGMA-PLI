/*
 * Calculadora OD (Origem-Destino) - Script
 * - Suporta seleção de fonte CSV vs Camada
 * - Lê cabeçalho CSV e popula selects de campo (origin/destination)
 * - Permite selecionar camada e simula campos (mocked)
 */

document.addEventListener('DOMContentLoaded', () => {
    initOdCalculator();
});

function initOdCalculator() {
    const odSourceCsv = document.getElementById('odSourceCsv');
    const odSourceLayer = document.getElementById('odSourceLayer');
    const csvInput = document.getElementById('csvInput');
    const layerInput = document.getElementById('layerInput');
    const csvFileInput = document.getElementById('csvFile');
    const layerSelect = document.getElementById('layerSelect');
    const fieldOrigin = document.getElementById('fieldOrigin');
    const fieldDest = document.getElementById('fieldDest');
    const parseCsvBtn = document.getElementById('parseCsvBtn');
    const calcOdBtn = document.getElementById('calcOdBtn');
    const resetBtn = document.getElementById('resetBtn');
    const odResult = document.getElementById('odResult');

    function toggleSource() {
        if (odSourceCsv.checked) {
            csvInput.classList.remove('d-none');
            layerInput.classList.add('d-none');
            fieldOrigin.innerHTML = '';
            fieldDest.innerHTML = '';
        } else {
            csvInput.classList.add('d-none');
            layerInput.classList.remove('d-none');
            // Load mock fields for layer
            populateFieldOptions(['id', 'nome', 'geocodigo']);
        }
    }

    function populateFieldOptions(fields) {
        fieldOrigin.innerHTML = '';
        fieldDest.innerHTML = '';
        fields.forEach((f) => {
            const o1 = document.createElement('option');
            o1.value = f; o1.textContent = f; fieldOrigin.appendChild(o1);
            const o2 = document.createElement('option');
            o2.value = f; o2.textContent = f; fieldDest.appendChild(o2);
        });
    }

    function parseCSV(file) {
        // Simple parsing, only headers
        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            const lines = content.split(/\r?\n/);
            if (!lines.length) return;
            const header = lines[0].split(',').map(h => h.trim());
            populateFieldOptions(header);
            odResult.innerHTML = `<div class="alert alert-success">Cabeçalho lido: ${header.join(', ')}</div>`;
        };
        reader.readAsText(file);
    }

    // Event listeners
    odSourceCsv.addEventListener('change', toggleSource);
    odSourceLayer.addEventListener('change', toggleSource);

    parseCsvBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if (!csvFileInput.files || !csvFileInput.files.length) {
            odResult.innerHTML = '<div class="alert alert-warning">Selecione um arquivo CSV primeiro.</div>';
            return;
        }
        parseCSV(csvFileInput.files[0]);
    });

    layerSelect.addEventListener('change', () => {
        // Mock fetching fields from layer
        const layer = layerSelect.value;
        if (!layer) {
            populateFieldOptions([]);
            odResult.innerHTML = '';
            return;
        }
        // Simple mocked mapping
        const mockedFields = {
            'layer_roads': ['road_id', 'nome', 'tipo', 'geometry'],
            'layer_municipios': ['mun_id', 'nome_munic', 'populacao', 'geometry']
        };
        populateFieldOptions(mockedFields[layer] || []);
        odResult.innerHTML = `<div class="alert alert-info">Campos da camada carregados: ${(mockedFields[layer] || []).join(', ')}</div>`;
    });

    calcOdBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        const originField = fieldOrigin.value;
        const destField = fieldDest.value;
        if (!originField || !destField) {
            odResult.innerHTML = '<div class="alert alert-warning">Escolha os campos de origem e destino.</div>';
            return;
        }
        odResult.innerHTML = '<div class="alert alert-secondary">Calculando OD - enviando para API...</div>';
        try {
            const body = {
                source: odSourceCsv.checked ? 'csv' : 'layer',
                origin_field: originField,
                dest_field: destField,
                layer: layerSelect.value || null,
            };
            const res = await fetch('/ferramentas/api/v1/ferramentas/od/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            if (!res.ok) throw new Error('API error: ' + res.status);
            const data = await res.json();
            odResult.innerHTML = `<div class="alert alert-success">Resultado: ${data.message} <pre>${JSON.stringify(data.result, null, 2)}</pre></div>`;
        } catch (err) {
            odResult.innerHTML = `<div class="alert alert-danger">Erro ao calcular OD: ${err.message}</div>`;
        }
    });

    resetBtn.addEventListener('click', () => {
        csvFileInput.value = '';
        layerSelect.value = '';
        fieldOrigin.innerHTML = '';
        fieldDest.innerHTML = '';
        odResult.innerHTML = '';
    });

    // initial toggle
    toggleSource();
}
