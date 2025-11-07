// Script esquelético para pessoa-fisica (M01_auth)
// Página de visualização pós-login
// Preserva hooks/IDs do original.
// Nota: Endpoints de listagem foram removidos após consolidação de dados

document.addEventListener('DOMContentLoaded', function () {
  console.log('M01_auth: pessoa-fisica script carregado');

  // Placeholders para botões de filtro
  const btnBuscar = document.getElementById('auto_evt_buscar_pf');
  const btnLimpar = document.getElementById('auto_evt_limpar_pf');

  if (btnBuscar) btnBuscar.addEventListener('click', () => console.log('Buscar PF - integração futura'));
  if (btnLimpar) btnLimpar.addEventListener('click', () => {
    const filtroNome = document.getElementById('filtroNome');
    const filtroCpf = document.getElementById('filtroCpf');
    if (filtroNome) filtroNome.value = '';
    if (filtroCpf) filtroCpf.value = '';
    console.log('Filtros limpos (PF)');
  });
});
