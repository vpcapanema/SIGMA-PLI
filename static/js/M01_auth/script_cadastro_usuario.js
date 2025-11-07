// Script para cadastro de usuário - formulário público simplificado
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('usuarioPublicForm');
    const toggleSenha = document.getElementById('toggleSenha');
    const toggleConfirm = document.getElementById('toggleConfirmarSenha');
    const senhaInput = document.getElementById('senha');
    const confirmarSenhaInput = document.getElementById('confirmarSenha');
    const passwordStrengthBar = document.getElementById('passwordStrength');
    const passwordStrengthText = document.getElementById('passwordStrengthText');

    // Toggle visualização de senha
    function toggle(inputId, button) {
      const input = document.getElementById(inputId);
      if (!input) return;
      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';
      const icon = button.querySelector('i');
      if (icon) {
        icon.className = isPassword ? 'fa fa-eye-slash' : 'fa fa-eye';
      }
    }

    if (toggleSenha) {
      toggleSenha.addEventListener('click', () => toggle('senha', toggleSenha));
    }
    if (toggleConfirm) {
      toggleConfirm.addEventListener('click', () => toggle('confirmarSenha', toggleConfirm));
    }

    // Validação de força da senha
    function checkPasswordStrength(password) {
      let strength = 0;
      if (password.length >= 8) strength++;
      if (password.length >= 12) strength++;
      if (/[a-z]/.test(password)) strength++;
      if (/[A-Z]/.test(password)) strength++;
      if (/[0-9]/.test(password)) strength++;
      if (/[^a-zA-Z0-9]/.test(password)) strength++;

      return strength;
    }

    function updatePasswordStrength() {
      if (!senhaInput || !passwordStrengthBar || !passwordStrengthText) return;

      const password = senhaInput.value;
      const strength = checkPasswordStrength(password);

      const strengthLevels = [
        { level: 0, text: '', width: '0%', color: '' },
        { level: 1, text: 'Muito fraca', width: '20%', color: 'bg-danger' },
        { level: 2, text: 'Fraca', width: '40%', color: 'bg-warning' },
        { level: 3, text: 'Média', width: '60%', color: 'bg-info' },
        { level: 4, text: 'Boa', width: '80%', color: 'bg-primary' },
        { level: 5, text: 'Forte', width: '100%', color: 'bg-success' },
        { level: 6, text: 'Muito forte', width: '100%', color: 'bg-success' }
      ];

      const current = strengthLevels[Math.min(strength, 6)];

      passwordStrengthBar.style.width = current.width;
      passwordStrengthBar.className = 'password-strength-bar ' + current.color;
      passwordStrengthText.textContent = current.text;
    }

    if (senhaInput) {
      senhaInput.addEventListener('input', updatePasswordStrength);
    }

    // Validação do formulário
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Validação básica
        if (!form.checkValidity()) {
          e.stopPropagation();
          form.classList.add('was-validated');
          return;
        }

        // Verificar se as senhas coincidem
        const senha = senhaInput?.value;
        const confirmarSenha = confirmarSenhaInput?.value;

        if (senha !== confirmarSenha) {
          const feedback = document.getElementById('confirmarSenhaFeedback');
          if (feedback) feedback.textContent = 'As senhas não coincidem.';
          if (confirmarSenhaInput) {
            confirmarSenhaInput.classList.add('is-invalid');
          }
          return;
        }

        // Verificar força da senha
        const strength = checkPasswordStrength(senha);
        if (strength < 4) {
          const feedback = document.getElementById('senhaFeedback');
          if (feedback) feedback.textContent = 'A senha não é forte o suficiente. Use pelo menos 8 caracteres com letras maiúsculas, minúsculas, números e caracteres especiais.';
          if (senhaInput) {
            senhaInput.classList.add('is-invalid');
          }
          return;
        }

        // Coletar dados do formulário
        const formData = {
          nome: form.nome.value,
          email: form.email.value,
          documento: form.documento.value,
          telefone: form.telefone.value,
          data_nascimento: form.data_nascimento?.value || null,
          instituicao_nome: form.instituicao_nome?.value || null,
          departamento: form.departamento?.value || null,
          cargo: form.cargo?.value || null,
          email_institucional: form.email_institucional?.value || null,
          telefone_institucional: form.telefone_institucional?.value || null,
          ramal_institucional: form.ramal_institucional?.value || null,
          tipo_usuario: form.tipo_usuario.value,
          username: form.username.value,
          senha: senha,
          termo_privacidade: form.termo_privacidade.checked,
          termo_uso: form.termo_uso.checked
        };

        console.log('Dados do cadastro:', formData);

        // Enviar para API /api/cadastro/usuario
        try {
          const response = await fetch('/api/cadastro/usuario', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
          });

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao criar usuário');
          }

          const result = await response.json();
          alert('Usuário cadastrado com sucesso!');

          // Redirecionar para login
          setTimeout(() => {
            window.location.href = '/auth/login';
          }, 2000);

        } catch (error) {
          console.error('Erro ao cadastrar:', error);
          alert(error.message || 'Erro ao cadastrar usuário');
        }
      });
    }
  });
})();
