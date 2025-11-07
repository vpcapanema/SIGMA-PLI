document.addEventListener('DOMContentLoaded', function () {
  const toggles = document.querySelectorAll('.password-toggle');
  toggles.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      const targetId = btn.getAttribute('data-target');
      if (!targetId) return;
      const input = document.getElementById(targetId);
      if (!input) return;
      if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = 'Ocultar';
      } else {
        input.type = 'password';
        btn.textContent = 'Mostrar';
      }
    });
  });
});
