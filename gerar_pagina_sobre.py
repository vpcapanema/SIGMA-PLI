#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para gerar a página Sobre completa do SIGMA-PLI"""

html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="/static/css/style_global_reset_base.css">
    <link rel="stylesheet" href="/static/css/M02_dashboard/style_dashboard_layout_base.css">
    <link rel="stylesheet" href="/static/css/M00_home/style_home_layout_base.css">
    <link rel="stylesheet" href="/static/css/M00_home/style_home_cards.css">
    <link rel="stylesheet" href="/static/css/M00_home/style_home_navigation.css">
    <style>
        .sobre-hero {
            background: linear-gradient(135deg, #1a1f3a 0%, #2d3561 100%);
            padding: 60px 0 40px;
            text-align: center;
            margin-bottom: 40px;
        }
        .sobre-hero h1 {
            color: #2c8fff;
            font-size: 2.5rem;
            margin-bottom: 15px;
            font-weight: 700;
        }
        .sobre-hero p {
            color: #8b9ab5;
            font-size: 1.2rem;
        }
        .tabs-nav {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin: 30px 0;
            flex-wrap: wrap;
        }
        .tab-btn {
            background: #1e2338;
            color: #8b9ab5;
            border: 2px solid #2d3561;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.95rem;
            font-weight: 600;
        }
        .tab-btn:hover {
            border-color: #2c8fff;
            color: #fff;
            transform: translateY(-2px);
        }
        .tab-btn.active {
            background: linear-gradient(135deg, #2c8fff 0%, #1e5bb8 100%);
            color: #fff;
            border-color: #2c8fff;
        }
        .tab-panel {
            display: none;
            animation: fadeIn 0.3s ease;
        }
        .tab-panel.active {
            display: block;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .content-section {
            background: #1e2338;
            border: 1px solid #2d3561;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
        }
        .content-section h2 {
            color: #2c8fff;
            font-size: 1.8rem;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #2d3561;
        }
        .content-section h3 {
            color: #5a9dff;
            font-size: 1.4rem;
            margin: 25px 0 15px;
        }
        .content-section p {
            color: #8b9ab5;
            line-height: 1.8;
            margin-bottom: 15px;
        }
        .content-section ul {
            color: #8b9ab5;
            line-height: 1.8;
            margin-left: 20px;
            margin-bottom: 15px;
        }
        .content-section li {
            margin-bottom: 10px;
        }
        .content-section strong {
            color: #fff;
        }
        .produtos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .produto-card {
            background: linear-gradient(135deg, #1e2338 0%, #252b4a 100%);
            border: 1px solid #2d3561;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s ease;
        }
        .produto-card:hover {
            border-color: #2c8fff;
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(44, 143, 255, 0.2);
        }
        .produto-card h3 {
            color: #2c8fff;
            font-size: 1.1rem;
            margin-bottom: 10px;
        }
        .produto-card h3 span {
            display: block;
            font-size: 0.9rem;
            color: #5a9dff;
            margin-top: 5px;
        }
        .produto-card p {
            color: #8b9ab5;
            font-size: 0.9rem;
            line-height: 1.6;
        }
    </style>
</head>
<body class="dashboard-body">
    <header class="dashboard-header">
        <nav class="sigma-nav">
            <div class="header-brand">
                <span class="brand-title">SIGMA-PLI</span>
                <span class="brand-subtitle">Sistema Integrado ao PLI/SP</span>
            </div>
            <div class="nav-menu">
                <a href="/" class="nav-link">Home</a>
                <a href="/sobre" class="nav-link active">Sobre o PLI</a>
                <a href="/equipe" class="nav-link">Equipe</a>
                <a href="/ajuda" class="nav-link">Ajuda</a>
                <a href="/contato" class="nav-link">Contato</a>
                <a href="/auth" class="nav-link">Entrar</a>
            </div>
        </nav>
    </header>

    <div class="sobre-hero">
        <h1>Plano de Logística e Investimentos de São Paulo</h1>
        <p>Planejamento Estratégico para Infraestrutura de Transportes até 2050</p>
    </div>

    <div class="container">
        <div class="tabs-nav">
            <button class="tab-btn active" onclick="switchTab('contexto')">Contexto</button>
            <button class="tab-btn" onclick="switchTab('planejamento')">Planejamento</button>
            <button class="tab-btn" onclick="switchTab('escopo')">Escopo</button>
            <button class="tab-btn" onclick="switchTab('objetivo1')">Objetivo 1</button>
            <button class="tab-btn" onclick="switchTab('objetivo2')">Objetivo 2</button>
            <button class="tab-btn" onclick="switchTab('objetivo3')">Objetivo 3</button>
            <button class="tab-btn" onclick="switchTab('objetivo4')">Objetivo 4</button>
            <button class="tab-btn" onclick="switchTab('objetivo5')">Objetivo 5</button>
            <button class="tab-btn" onclick="switchTab('produtos')">Produtos</button>
        </div>

        <div id="contexto" class="tab-panel active">
            <div class="content-section">
                <h2>Contexto e Justificativa</h2>
                <p>O Estado de São Paulo concentra mais de um terço do PIB nacional e possui quase um terço da frota de veículos do país, abrigando cerca de 22% da população brasileira em apenas 3% do território. Essa concentração de pessoas e riqueza gera grande demanda por mobilidade, pressionando a infraestrutura existente e contribuindo para que o setor de transportes responda por 21% das emissões de gases de efeito estufa do Brasil. Para garantir eficiência logística e bem-estar social e ambiental, o governo estadual precisa atuar de forma proativa no planejamento e na execução de investimentos em infraestrutura.</p>
            </div>
        </div>

        <div id="planejamento" class="tab-panel">
            <div class="content-section">
                <h2>Planejamento da Infraestrutura de Transportes Paulista</h2>
                <p>O Plano de Logística e Investimentos (PLI-SP) abrange todo o território paulista e complementa estudos da Macrometrópole. O plano é guiado pela sustentabilidade e busca maximizar o retorno social dos recursos públicos. Suas diretrizes incluem:</p>
                <ul>
                    <li>Atenção especial às regiões fora da Macrometrópole e integração com demais estados;</li>
                    <li>Priorizar projetos que reduzam a dependência do modal rodoviário, aumentando a participação de ferrovias e hidrovias;</li>
                    <li>Promover mudanças na matriz energética com eletrificação e combustíveis <em>verdes</em>;</li>
                    <li>Identificar barreiras institucionais e de infraestrutura para a mudança modal e propor soluções;</li>
                    <li>Organizar carteira de projetos com benefícios sociais e econômicos comprovados.</li>
                </ul>
            </div>
        </div>

        <div id="escopo" class="tab-panel">
            <div class="content-section">
                <h2>Escopo do Estudo</h2>
                <p>O PLI-SP analisa a logística de passageiros e cargas em todo o estado. O estudo conecta as diversas regiões entre si, com a Macrometrópole Paulista, com outros estados e com corredores de importação/exportação. O horizonte de planejamento vai até 2050, com marcos intermediários em 2028, 2033, 2038 e 2043. O ano-base considerado é 2025, pois a maior parte do trabalho será desenvolvida com dados estatísticos completos até 2024.</p>
            </div>
        </div>

        <div id="objetivo1" class="tab-panel">
            <div class="content-section">
                <h2>Objetivo 1 – Plano de Trabalho</h2>
                <p>O primeiro objetivo detalha as questões técnicas e metodológicas do projeto. A meta 1.1, "Plano de Trabalho Detalhado", prevê a organização interna e a estrutura de comunicação do estudo. Entre as principais atividades estão:</p>
                <ul>
                    <li><strong>Organograma do projeto:</strong> definir a equipe, qualificações e responsáveis por cada tarefa;</li>
                    <li><strong>Cronograma de atividades:</strong> estruturar as etapas, produtos e datas de entrega;</li>
                    <li><strong>Matriz de comunicação:</strong> estabelecer a forma e a frequência de comunicação entre as partes;</li>
                    <li><strong>Ações de comunicação social:</strong> desenvolver identidade visual, materiais para imprensa, vídeos institucionais e versões para redes sociais;</li>
                    <li><strong>Metodologia:</strong> descrever a abordagem técnica, os softwares a utilizar e os métodos para hierarquizar investimentos;</li>
                    <li><strong>Fontes de dados:</strong> identificar bases estatísticas e georreferenciadas a serem usadas (sem necessidade de levantamentos de campo, exceto pesquisas específicas);</li>
                    <li><strong>Base de conhecimento:</strong> estruturar um acervo com todos os dados, documentos e produtos gerados ao longo do trabalho.</li>
                </ul>
            </div>
        </div>

        <div id="objetivo2" class="tab-panel">
            <div class="content-section">
                <h2>Objetivo 2 – Diagnóstico</h2>
                <p>Esta etapa estuda o sistema de transportes atual para entender sua dinâmica e gargalos. A análise cobre todos os modais, integrando demanda e oferta por meio de modelagem de transportes e abordagens institucionais e regulatórias.</p>
                
                <h3>Meta 2.1 – Caracterização Socioeconômica</h3>
                <p>Compila dados sobre a evolução histórica, geográfica e econômica do estado, destacando indicadores como PIB, IDH, renda, população e atividades econômicas. Também caracteriza o uso do solo, distinguindo áreas urbanas e rurais.</p>
                
                <h3>Meta 2.2 – Caracterização do Sistema de Transporte</h3>
                <p>Realiza um diagnóstico completo da oferta e demanda, contemplando rodovias, ferrovias, hidrovias, aeroportos, portos e terminais intermodais. A modelagem identifica gargalos, pontos de saturação e questões institucionais, regulatórias e tarifárias.</p>
                
                <h3>Meta 2.3 – Obtenção de Matrizes Multimodais</h3>
                <p>Atualiza ou estima matrizes de viagens (geração e distribuição) para o ano-base. São consideradas matrizes rodoviárias e de cargas existentes, dados auxiliares de uso dos modais e contagens de tráfego. Inclui entrevistas com embarcadores, pesquisas de preferência declarada e pesquisas origem-destino para calibrar modelos de escolha modal.</p>
                
                <h3>Meta 2.4 – Ações Regionais de Divulgação</h3>
                <p>Promove workshops e fóruns nas nove zonas do Zoneamento Ecológico-Econômico, envolvendo órgãos públicos, empresas e sociedade civil. O objetivo é captar sugestões, demandas e soluções locais, além de incentivar a participação nas pesquisas.</p>
                
                <h3>Meta 2.5 – Levantamento da Infraestrutura Existente</h3>
                <p>Levanta e atualiza, de forma georreferenciada, a infraestrutura de transportes: rodovias (incluindo vicinais), ferrovias, hidrovias, portos, terminais intermodais de cargas e passageiros, dutovias, aeroportos e rotas de cabotagem. Registra capacidades, responsáveis pela operação e necessidades de expansão.</p>
                
                <h3>Meta 2.6 – Concepção da Visão do Sistema Logístico Multimodal</h3>
                <p>Define objetivos estratégicos e metas mensuráveis para cada modal e estabelece indicadores para monitorar seu alcance. A visão considera a caracterização socioeconômica, a situação atual do sistema e princípios de sustentabilidade, equidade, inovação e conectividade. Também define a metodologia para construir e analisar cenários de transporte.</p>
                
                <h3>Meta 2.7 – Construção de Modelos de Transporte</h3>
                <p>Baseada nas bases de oferta e demanda levantadas, desenvolve modelos de simulação de rede e modelos de escolha modal usando o software PTV Visum. Esta meta engloba a definição do zoneamento, estimativa de custos logísticos, montagem da rede de simulação, elaboração de matrizes de viagens, calibração da rede e dos modelos de escolha.</p>
            </div>
        </div>

        <div id="objetivo3" class="tab-panel">
            <div class="content-section">
                <h2>Objetivo 3 – Simulação e Análise de Alternativas</h2>
                <p>Visa avaliar o desempenho do sistema diante de diferentes cenários de demanda e oferta. As metas incluem:</p>
                <ul>
                    <li><strong>Meta 3.1 – Projeções de Demanda:</strong> projetar matrizes de viagens de cargas e passageiros para 2028, 2033, 2038, 2043 e 2050 a partir de hipóteses socioeconômicas. Considera cenários base, otimista, pessimista e disruptivos.</li>
                    <li><strong>Meta 3.2 – Caracterização da Oferta Futura:</strong> inventariar projetos em planejamento ou execução e avaliar sua capacidade de atendimento; analisar concorrência portuária e efeitos na acessibilidade regional.</li>
                    <li><strong>Meta 3.3 – Análise de Fatores que Influenciam Cenários Futuros:</strong> examinar evoluções tecnológicas (eletrificação, biocombustíveis, hidrogênio), novos serviços de transporte regional e contribuições recolhidas nas pesquisas e eventos.</li>
                    <li><strong>Meta 3.4 – Simulação de Cenários Futuros:</strong> alocar as matrizes projetadas na rede de transportes para identificar níveis de serviço e necessidades de intervenção; combinar diferentes demandas, ofertas e inovações.</li>
                    <li><strong>Meta 3.5 – Identificação de Pontos de Atenção:</strong> analisar níveis de serviço em cada modal e apontar gargalos e necessidades de investimento à luz dos objetivos e indicadores propostos.</li>
                </ul>
            </div>
        </div>

        <div id="objetivo4" class="tab-panel">
            <div class="content-section">
                <h2>Objetivo 4 – Proposta de Intervenções Logísticas / Plano de Ação</h2>
                <p>Organiza e prioriza projetos e intervenções que atendam às necessidades identificadas no diagnóstico e na simulação.</p>
                <ul>
                    <li><strong>Meta 4.1 – Intervenções e Projetos Selecionados:</strong> listar projetos propostos em estudos prévios e selecionar pelo menos 25 que tratem dos principais gargalos; descrever benefícios sociais, desafios, prazos e envolvidos.</li>
                    <li><strong>Meta 4.2 – Estimativa de CAPEX e OPEX:</strong> estimar custos de implantação (incluindo obras, desapropriações e mitigações ambientais) e de operação e manutenção para cada projeto.</li>
                    <li><strong>Meta 4.3 – Cálculo de Benefício Econômico:</strong> quantificar benefícios em tempo de viagem, custos operacionais, acidentes e emissões para cada intervenção e calcular o índice benefício/custo (B/C) sobre 30 anos.</li>
                    <li><strong>Meta 4.4 – Hierarquização de Projetos:</strong> construir um modelo de priorização baseado no índice B/C e em critérios como redução de desigualdades regionais, complexidade e prazo de implantação; validar e aplicar o modelo em workshops.</li>
                    <li><strong>Meta 4.5 – Exame de Aspectos Jurídicos, Institucionais e Regulatórios:</strong> propor ajustes normativos e arranjos institucionais para viabilizar os serviços logísticos; analisar jurisdições e governança e sugerir soluções baseadas em experiências internacionais.</li>
                </ul>
            </div>
        </div>

        <div id="objetivo5" class="tab-panel">
            <div class="content-section">
                <h2>Objetivo 5 – Sistema de Informação e Assessoria</h2>
                <p>Prevê a organização tecnológica e a disseminação das informações produzidas, além de oferecer apoio técnico ao contratante. Suas metas abrangem:</p>
                <ul>
                    <li><strong>Meta 5.1 – Relatórios Finais:</strong> produzir dois documentos de divulgação – o <em>Relatório Síntese</em>, voltado ao público geral, e o <em>Sumário Executivo</em>, direcionado ao investidor, ambos com linguagem acessível e recursos visuais.</li>
                    <li><strong>Meta 5.2 – Sistema de Informação e Comunicação:</strong> estruturar uma base digital para armazenar dados, relatórios e bancos geográficos; integrar com o site da Secretaria; criar painéis de BI e um portal interativo para divulgação; assegurar formatos adequados (docx, pdf, xlsx/csv, shapefile).</li>
                    <li><strong>Meta 5.3 – Apoio Técnico:</strong> disponibilizar equipe para apoiar o contratante durante o estudo, respondendo dúvidas, preparando apresentações e processando dados.</li>
                </ul>
            </div>
        </div>

        <div id="produtos" class="tab-panel">
            <div class="content-section">
                <h2>Produtos Entregáveis do PLI-SP</h2>
                <p>O Termo de Referência prevê 21 produtos que organizam e documentam todas as etapas do planejamento logístico estadual.</p>
                
                <div class="produtos-grid">
                    <div class="produto-card">
                        <h3>Produto 1<br><span>Plano de Trabalho Detalhado</span></h3>
                        <p>Organiza a estrutura do projeto: organograma, cronograma, matriz de comunicação, ações de comunicação social, metodologia adotada, fontes de dados e plano para organizar a base de conhecimento.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 2<br><span>Caracterização Socioeconômica</span></h3>
                        <p>Reúne indicadores socioeconômicos do Estado de São Paulo (PIB, IDH, renda, população, atividades econômicas) e caracteriza o uso do solo, servindo de base para projeções de demanda.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 3<br><span>Caracterização do Sistema de Transporte</span></h3>
                        <p>Apresenta diagnóstico da oferta e da demanda de transportes em todos os modais, identifica gargalos e aborda questões institucionais, regulatórias e tarifárias.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 4<br><span>Matrizes Multimodais</span></h3>
                        <p>Atualiza ou estima matrizes de viagens de cargas e passageiros para o ano-base, utilizando dados existentes, pesquisas com embarcadores, pesquisas de preferência declarada e pesquisas origem-destino.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 5<br><span>Ações Regionais de Divulgação</span></h3>
                        <p>Realiza workshops e fóruns regionais para colher sugestões, dados e propostas de atores locais, fomentando a participação da sociedade e de empresas.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 6<br><span>Levantamento da Infraestrutura</span></h3>
                        <p>Compila de forma georreferenciada a infraestrutura de transportes existente (rodovias, ferrovias, hidrovias, portos, terminais intermodais, dutovias, aeroportos e cabotagem) e avalia suas capacidades.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 7<br><span>Visão do Sistema Logístico Multimodal</span></h3>
                        <p>Define a visão estratégica do sistema, incluindo objetivos, metas e indicadores para cada modal e a metodologia de construção e análise de cenários futuros.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 8<br><span>Modelos de Transporte</span></h3>
                        <p>Desenvolve modelos de simulação de rede e de escolha modal com base em dados de demanda e oferta, abrangendo zoneamento, custos logísticos, montagem da rede e calibração.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 9<br><span>Projeções de Demanda</span></h3>
                        <p>Projeta matrizes de viagens de cargas e passageiros para 2028, 2033, 2038, 2043 e 2050, considerando cenários base, otimista, pessimista e disruptivo.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 10<br><span>Caracterização da Oferta Futura</span></h3>
                        <p>Avalia projetos em andamento ou planejados e simula cenários de oferta futura, analisando concorrência portuária e impactos na acessibilidade.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 11<br><span>Análise de Fatores Futuristas</span></h3>
                        <p>Analisa evoluções tecnológicas (eletrificação, biocombustíveis, hidrogênio), novos serviços de transporte e sugestões colhidas nas consultas para moldar cenários futuros.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 12<br><span>Simulação de Cenários Futuros</span></h3>
                        <p>Simula a alocação das matrizes projetadas na rede de transporte, avalia níveis de serviço e define combinações de demanda, oferta e inovações.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 13<br><span>Pontos de Atenção</span></h3>
                        <p>Identifica gargalos e saturações atuais ou futuras nos modais e terminais, orientando necessidades de intervenção.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 14<br><span>Intervenções e Projetos Selecionados</span></h3>
                        <p>Relaciona e descreve projetos e intervenções priorizados, destacando benefícios, desafios, prazos e responsáveis.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 15<br><span>Estimativa de CAPEX e OPEX</span></h3>
                        <p>Estima os custos de implantação, operação e manutenção de cada projeto, incluindo obras, desapropriações e medidas ambientais.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 16<br><span>Benefício Econômico</span></h3>
                        <p>Quantifica os ganhos (tempo, custo, acidentes, emissões) de cada intervenção e calcula o índice benefício/custo (B/C).</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 17<br><span>Hierarquização de Projetos</span></h3>
                        <p>Desenvolve e aplica um modelo de priorização com base no índice B/C e critérios como desigualdade regional, complexidade e prazo de implantação.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 18<br><span>Aspectos Jurídicos e Institucionais</span></h3>
                        <p>Analisa jurisdições e regulações, propõe arranjos institucionais e ajustes normativos para viabilizar os serviços logísticos.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 19<br><span>Relatórios Finais</span></h3>
                        <p>Entrega o Relatório Síntese e o Sumário Executivo, documentos ilustrados que resumem o plano para o público geral e potenciais investidores.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 20<br><span>Sistema de Informação e Comunicação</span></h3>
                        <p>Cria uma base de dados digital, integra com o site da Secretaria, desenvolve painéis de BI e prepara uma plataforma de divulgação com projetos georreferenciados.</p>
                    </div>
                    <div class="produto-card">
                        <h3>Produto 21<br><span>Apoio Técnico</span></h3>
                        <p>Disponibiliza suporte técnico contínuo ao contratante, respondendo dúvidas, fornecendo dados intermediários e preparando apresentações e análises.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="dashboard-footer" style="margin-top: 60px;">
        <div class="container">
            <div class="footer-bottom">
                <p>&copy; 2025 SIGMA-PLI. Desenvolvido por VPC-GEOSER</p>
            </div>
        </div>
    </footer>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabId).classList.add('active');
            window.scrollTo({ top: 300, behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""

# Escreve o arquivo
output_path = r"d:\SIGMA-PLI-IMPLEMENTACAO\SIGMA-PRINCIPAL\templates\pages\M00_home\template_sobre_pagina.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Arquivo criado com sucesso: {output_path}")
print(f"📊 Tamanho: {len(html_content)} caracteres")
