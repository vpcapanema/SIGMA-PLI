// Skeleton JS para dashboard: mantém hooks e IDs do template original.
(function(){
  'use strict';
  document.addEventListener('DOMContentLoaded', ()=>{
    // Preencher placeholders básicos
    const welcomeUser = document.getElementById('welcomeUser');
    const welcomeDate = document.getElementById('welcomeDate');
    if(welcomeUser) welcomeUser.textContent = 'Usuário SIGMA';
    if(welcomeDate) welcomeDate.textContent = new Date().toLocaleDateString();

    // Carregamento de métricas (skeleton)
    const ids = ['totalPessoasFisicas','totalPessoasJuridicas','totalUsuarios','todosOsCadastros','totalSolicitacoes'];
    ids.forEach(id=>{ const el=document.getElementById(id); if(el) el.textContent='-'; });

    // Charts e tabelas serão preenchidos na fase de integração
    console.log('Dashboard skeleton carregado');
  });
})();
// Dashboard behaviour skeleton
document.addEventListener('DOMContentLoaded', function () {
  console.debug('Dashboard skeleton loaded');
  // TODO: inicializar gráficos e chamadas à API
});
