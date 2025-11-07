// Skeleton JS para recuperar-senha: preserva IDs e hooks usados pelo PLI original.
(function(){
  'use strict';

  function qs(id){ return document.getElementById(id); }

  // Forms
  const emailForm = qs('emailForm');
  const tokenForm = qs('tokenForm');
  const passwordForm = qs('passwordForm');

  // Buttons
  const resendLink = qs('resendLink');
  const resendTimer = qs('resendTimer');

  // Password toggles
  function togglePassword(inputId, toggleId){
    const input = qs(inputId);
    const toggle = qs(toggleId);
    if(!input || !toggle) return;
    toggle.addEventListener('click', ()=>{
      input.type = input.type === 'password' ? 'text' : 'password';
      toggle.querySelector('i').classList.toggle('fa-eye-slash');
    });
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    if(emailForm){
      emailForm.addEventListener('submit', (e)=>{
        e.preventDefault();
        console.log('Enviar instruções (skeleton) ->', qs('email')?.value);
        // TODO: implementar chamada para backend (/api/v1/auth/recover) na onda de integração
      });
    }

    if(tokenForm){
      tokenForm.addEventListener('submit', (e)=>{
        e.preventDefault();
        console.log('Verificar token (skeleton) ->', qs('token')?.value);
      });
    }

    if(passwordForm){
      passwordForm.addEventListener('submit', (e)=>{
        e.preventDefault();
        console.log('Resetar senha (skeleton) ->', qs('newPassword')?.value);
      });
    }

    // toggles
    togglePassword('newPassword','toggleNewPassword');
    togglePassword('confirmPassword','toggleConfirmPassword');

    // resend link placeholder
    if(resendLink){
      resendLink.addEventListener('click', (e)=>{
        e.preventDefault();
        console.log('Reenviar código - ação skeleton');
        if(resendTimer) resendTimer.textContent = 'Código reenviado';
      });
    }
  });

})();
// Skeleton for recuperar senha
document.getElementById('recuperar-form')?.addEventListener('submit', function (e) {
  e.preventDefault();
  const email = document.getElementById('email').value;
  console.debug('Solicitar recuperação para', email);
  // TODO: POST to /api/v1/auth/recover
});
