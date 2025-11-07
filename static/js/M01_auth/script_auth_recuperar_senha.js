/**
 * SIGMA-PLI - Recuperar Senha - Interface Hierárquica
 * Script completo para fluxo de 3 etapas com validações visuais avançadas
 */

// === Elementos do DOM ===
const passwordInput = document.getElementById('newPassword');
const confirmPasswordInput = document.getElementById('confirmPassword');
const progressFill = document.getElementById('progressFill');
const strengthFill = document.getElementById('strengthFill');
const strengthText = document.getElementById('strengthText');

const checklist = {
  length: document.getElementById('chk-length'),
  upper: document.getElementById('chk-upper'),
  lower: document.getElementById('chk-lower'),
  number: document.getElementById('chk-number'),
  special: document.getElementById('chk-special'),
};

// === Estado Global ===
let currentStep = 1;
let userEmail = '';
let userToken = '';

// === Função: Ir para Step ===
function goToStep(step) {
  currentStep = step;
  
  // Oculta todos os cards
  const allCards = ['cardEmail', 'cardToken', 'cardPassword'];
  allCards.forEach(cardId => {
    const card = document.getElementById(cardId);
    if (card) {
      card.style.display = 'none';
      card.classList.remove('recuperar-senha__active--div');
    }
  });
  
  // Mostra apenas o card atual
  const currentCards = {
    1: 'cardEmail',
    2: 'cardToken',
    3: 'cardPassword'
  };
  
  const currentCard = document.getElementById(currentCards[step]);
  if (currentCard) {
    currentCard.style.display = 'block';
    currentCard.classList.add('recuperar-senha__active--div');
    
    // Animação de entrada
    currentCard.style.animation = 'fadeIn 0.5s ease';
  }
  
  // Atualiza progresso visual
  updateProgress(step);
  
  // Limpa alertas
  const alertContainer = document.getElementById('alertContainer');
  if (alertContainer) alertContainer.innerHTML = '';
}

// === Função: Atualizar Progresso ===
function updateProgress(step) {
  const progress = ((step - 1) / 2) * 100; // 0%, 50%, 100% para 3 steps
  if (progressFill) {
    progressFill.style.width = `${progress}%`;
  }
  
  // Atualiza indicadores de step
  for (let i = 1; i <= 3; i++) {
    const stepEl = document.getElementById(`progressStep${i}`);
    if (!stepEl) continue;
    
    stepEl.classList.remove('recuperar-senha__active--div', 'recuperar-senha__completed--div');
    
    if (i < step) {
      stepEl.classList.add('recuperar-senha__completed--div');
    } else if (i === step) {
      stepEl.classList.add('recuperar-senha__active--div');
    }
  }
}

// === Função: Validar Senha ===
function validatePassword(password) {
  return {
    length: password.length >= 8,
    upper: /[A-Z]/.test(password),
    lower: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[^A-Za-z0-9]/.test(password),
  };
}

// === Função: Calcular Força da Senha ===
function calculateStrength(password) {
  const result = validatePassword(password);
  const score = Object.values(result).filter(Boolean).length;
  
  if (score <= 2) return 'weak';
  if (score <= 4) return 'medium';
  return 'strong';
}

// === Função: Atualizar Checklist ===
function updateChecklist(password) {
  const result = validatePassword(password);
  
  Object.keys(checklist).forEach((key) => {
    const item = checklist[key];
    if (!item) return;
    
    if (result[key]) {
      item.classList.remove('recuperar-senha__unchecked--li');
      item.classList.add('recuperar-senha__checked--li');
      const span = item.querySelector('span');
      if (span) {
        span.className = 'recuperar-senha__check--span';
        span.innerHTML = '<i class="fas fa-check-circle"></i>';
      }
    } else {
      item.classList.remove('recuperar-senha__checked--li');
      item.classList.add('recuperar-senha__unchecked--li');
      const span = item.querySelector('span');
      if (span) {
        span.className = 'recuperar-senha__uncheck--span';
        span.innerHTML = '<i class="fas fa-times-circle"></i>';
      }
    }
  });
  
  // Atualiza barra de força
  const strength = calculateStrength(password);
  if (strengthFill) {
    strengthFill.setAttribute('data-strength', strength);
    
    const strengthLabels = {
      weak: 'Fraca',
      medium: 'Média',
      strong: 'Forte'
    };
    
    if (strengthText) {
      strengthText.textContent = `Força da senha: ${strengthLabels[strength]}`;
    }
  }
  
  return Object.values(result).every(Boolean);
}

// === Função: Atualizar Match de Senha ===
function updatePasswordMatch() {
  const matchIndicator = document.getElementById('passwordMatchIndicator');
  const successEl = document.getElementById('passwordMatchSuccess');
  const errorEl = document.getElementById('passwordMatchError');
  
  if (!matchIndicator || !passwordInput || !confirmPasswordInput) return;
  
  const password = passwordInput.value;
  const confirm = confirmPasswordInput.value;
  
  if (confirm === '') {
    matchIndicator.classList.add('recuperar-senha__hidden--div');
    return;
  }
  
  matchIndicator.classList.remove('recuperar-senha__hidden--div');
  
  if (password === confirm && password !== '') {
    successEl.classList.remove('recuperar-senha__hidden--div');
    errorEl.classList.add('recuperar-senha__hidden--div');
  } else {
    successEl.classList.add('recuperar-senha__hidden--div');
    errorEl.classList.remove('recuperar-senha__hidden--div');
  }
}

// === Função: Toggle Password ===
function togglePasswordVisibility(inputId, toggleId) {
  const input = document.getElementById(inputId);
  const toggle = document.getElementById(toggleId);
  if (!input || !toggle) return;
  
  toggle.addEventListener('click', () => {
    if (input.type === 'password') {
      input.type = 'text';
      toggle.innerHTML = '<i class="fas fa-eye-slash"></i>';
    } else {
      input.type = 'password';
      toggle.innerHTML = '<i class="fas fa-eye"></i>';
    }
  });
}

// === Função: Timer de Reenvio ===
function startResendTimer() {
  const resendLink = document.getElementById('resendLink');
  const resendTimer = document.getElementById('resendTimer');
  
  if (!resendLink || !resendTimer) return;
  
  resendLink.classList.add('disabled');
  
  let timeLeft = 60;
  resendTimer.textContent = `Aguarde ${timeLeft}s para reenviar`;
  
  const interval = setInterval(() => {
    timeLeft--;
    
    if (timeLeft <= 0) {
      clearInterval(interval);
      resendLink.classList.remove('disabled');
      resendTimer.textContent = '';
    } else {
      resendTimer.textContent = `Aguarde ${timeLeft}s para reenviar`;
    }
  }, 1000);
}

// === Função: Mostrar Feedback ===
function showFeedback(id, message, type = 'danger') {
  const el = document.getElementById(id);
  if (el) {
    el.innerHTML = `<div class="alert alert-${type} py-2 px-3 mb-3">${message}</div>`;
  }
}

function clearFeedback(id) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = '';
}

// === Função: Mostrar Alerta ===
function showAlert(type, message) {
  const alertContainer = document.getElementById('alertContainer');
  if (!alertContainer) return;
  
  alertContainer.innerHTML = '';
  
  const alert = document.createElement('div');
  alert.className = `alert alert-${type} alert-dismissible fade show`;
  alert.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
  `;
  
  alertContainer.appendChild(alert);
  
  setTimeout(() => {
    if (alert && alert.parentNode) {
      alert.remove();
    }
  }, 5000);
}

// === API Helper ===
const API = {
  async post(url, data) {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro na requisição');
    }
    
    return await response.json();
  }
};

// === INICIALIZAÇÃO ===
document.addEventListener('DOMContentLoaded', () => {
  // Inicia no step 1
  goToStep(1);
  
  // Configura toggle de senha
  togglePasswordVisibility('newPassword', 'toggleNewPassword');
  togglePasswordVisibility('confirmPassword', 'toggleConfirmPassword');
  
  // Configura eventos de senha
  if (passwordInput) {
    passwordInput.addEventListener('input', (e) => {
      updateChecklist(e.target.value);
      updatePasswordMatch();
      clearFeedback('feedbackPassword');
    });
  }
  
  if (confirmPasswordInput) {
    confirmPasswordInput.addEventListener('input', () => {
      updatePasswordMatch();
      clearFeedback('feedbackPassword');
    });
  }
  
  // === FORM 1: Email ===
  const emailForm = document.getElementById('emailForm');
  if (emailForm) {
    emailForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      if (!emailForm.checkValidity()) {
        emailForm.classList.add('was-validated');
        return;
      }
      
      const email = document.getElementById('email').value;
      const btnSendEmail = document.getElementById('btnSendEmail');
      
      userEmail = email;
      
      try {
        btnSendEmail.disabled = true;
        btnSendEmail.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...';
        
        // Envia solicitação
        await API.post('/api/v1/auth/forgot-password', { email });
        
        // Exibe email no step 2
        const emailDisplay = document.getElementById('emailDisplay');
        if (emailDisplay) emailDisplay.textContent = email;
        
        // Inicia timer
        startResendTimer();
        
        // Avança para step 2
        goToStep(2);
        
        showAlert('success', '<i class="fas fa-check-circle me-2"></i>Código enviado para seu email!');
        
      } catch (error) {
        showAlert('danger', `<i class="fas fa-exclamation-circle me-2"></i>${error.message}`);
      } finally {
        btnSendEmail.disabled = false;
        btnSendEmail.innerHTML = '<span class="btn-text"><i class="fas fa-paper-plane me-2"></i>Enviar Código</span>';
      }
    });
  }
  
  // === LINK: Reenviar ===
  const resendLink = document.getElementById('resendLink');
  if (resendLink) {
    resendLink.addEventListener('click', async (e) => {
      e.preventDefault();
      
      if (resendLink.classList.contains('disabled')) return;
      
      try {
        await API.post('/api/v1/auth/forgot-password', { email: userEmail });
        showAlert('success', '<i class="fas fa-check-circle me-2"></i>Código reenviado!');
        startResendTimer();
      } catch (error) {
        showAlert('danger', `<i class="fas fa-exclamation-circle me-2"></i>${error.message}`);
      }
    });
  }
  
  // === FORM 2: Token ===
  const tokenForm = document.getElementById('tokenForm');
  if (tokenForm) {
    tokenForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      if (!tokenForm.checkValidity()) {
        tokenForm.classList.add('was-validated');
        return;
      }
      
      const token = document.getElementById('token').value;
      const btnVerifyToken = document.getElementById('btnVerifyToken');
      
      userToken = token;
      
      try {
        btnVerifyToken.disabled = true;
        btnVerifyToken.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Verificando...';
        
        // Avança para step 3
        goToStep(3);
        
        showAlert('success', '<i class="fas fa-check-circle me-2"></i>Código verificado com sucesso!');
        
      } catch (error) {
        showAlert('danger', `<i class="fas fa-exclamation-circle me-2"></i>${error.message}`);
      } finally {
        btnVerifyToken.disabled = false;
        btnVerifyToken.innerHTML = '<span class="btn-text"><i class="fas fa-check me-2"></i>Verificar Código</span>';
      }
    });
  }
  
  // === FORM 3: Nova Senha ===
  const passwordForm = document.getElementById('passwordForm');
  if (passwordForm) {
    passwordForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearFeedback('feedbackPassword');
      
      if (!passwordForm.checkValidity()) {
        passwordForm.classList.add('was-validated');
        return;
      }
      
      const password = passwordInput.value;
      const confirm = confirmPasswordInput.value;
      
      // Valida força da senha
      const isValid = updateChecklist(password);
      if (!isValid) {
        showFeedback('feedbackPassword', '<i class="fas fa-exclamation-triangle me-2"></i>A senha não atende todos os requisitos.', 'danger');
        return;
      }
      
      // Valida match
      if (password !== confirm) {
        showFeedback('feedbackPassword', '<i class="fas fa-times-circle me-2"></i>As senhas não coincidem.', 'danger');
        return;
      }
      
      const btnResetPassword = document.getElementById('btnResetPassword');
      
      try {
        btnResetPassword.disabled = true;
        btnResetPassword.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Alterando...';
        
        // Envia nova senha
        await API.post('/api/v1/auth/reset-password', { 
          token: userToken,
          new_password: password 
        });
        
        // Oculta cards e mostra sucesso
        document.getElementById('cardEmail').classList.add('recuperar-senha__hidden--div');
        document.getElementById('cardToken').classList.add('recuperar-senha__hidden--div');
        document.getElementById('cardPassword').classList.add('recuperar-senha__hidden--div');
        
        const successCard = document.getElementById('stepSuccess');
        if (successCard) {
          successCard.classList.remove('recuperar-senha__hidden--div');
        }
        
        const progressContainer = document.getElementById('progressContainer');
        if (progressContainer) {
          progressContainer.classList.add('recuperar-senha__hidden--div');
        }
        
        showAlert('success', '<i class="fas fa-check-circle me-2"></i>Senha alterada com sucesso!');
        
      } catch (error) {
        showFeedback('feedbackPassword', `<i class="fas fa-exclamation-circle me-2"></i>${error.message}`, 'danger');
      } finally {
        btnResetPassword.disabled = false;
        btnResetPassword.innerHTML = '<span class="btn-text"><i class="fas fa-save me-2"></i>Alterar Senha</span>';
      }
    });
  }
});

// Exporta função goToStep para uso global (botões Voltar)
window.goToStep = goToStep;
