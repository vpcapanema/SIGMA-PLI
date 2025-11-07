// Skeleton JS para Meus Dados: preserva IDs e permite ativar modo edição localmente.
(function(){
  'use strict';
  document.addEventListener('DOMContentLoaded', ()=>{
    const editBtn = document.getElementById('auto_evt_6bcf612e');
    const editButtons = document.getElementById('editButtons');
    const userDataForm = document.getElementById('userDataForm');

    if(editBtn){
      editBtn.addEventListener('click', ()=>{
        const inputs = userDataForm.querySelectorAll('input');
        const hidden = editButtons.classList.contains('d-none');
        inputs.forEach(i=> i.disabled = !hidden);
        editButtons.classList.toggle('d-none');
        document.getElementById('editModeText').textContent = hidden ? 'Cancelar' : 'Editar';
      });
    }

    if(userDataForm){
      userDataForm.addEventListener('submit', (e)=>{
        e.preventDefault();
        console.log('Salvar dados do usuário (skeleton)');
      });
    }

    const passwordForm = document.getElementById('passwordForm');
    if(passwordForm){
      passwordForm.addEventListener('submit', (e)=>{
        e.preventDefault();
        console.log('Alterar senha (skeleton)');
      });
    }
  });
})();
// Meus dados page skeleton
document.addEventListener('DOMContentLoaded', function () {
  console.debug('Meus dados script loaded');
});
