// Script esquelético para pessoa-juridica (M01_auth)
// Página de visualização pós-login
// Preserva hooks/IDs do original.
// Nota: Endpoints de listagem foram removidos após consolidação de dados

document.addEventListener('DOMContentLoaded', function () {
  console.log('M01_auth: pessoa-juridica script carregado');

  const btnBuscar = document.getElementById('auto_evt_buscar_pj');
  const btnLimpar = document.getElementById('auto_evt_limpar_pj');

  if (btnBuscar) btnBuscar.addEventListener('click', () => console.log('Buscar PJ - integração futura'));
  if (btnLimpar) btnLimpar.addEventListener('click', () => {
    const filtroRazao = document.getElementById('filtroRazao');
    const filtroCnpj = document.getElementById('filtroCnpj');
    if (filtroRazao) filtroRazao.value = '';
    if (filtroCnpj) filtroCnpj.value = '';
    console.log('Filtros limpos (PJ)');
  });
});
