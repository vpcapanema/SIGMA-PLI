// Login page behaviour (skeleton)
document.getElementById('login-form')?.addEventListener('submit', async function (e) {
  e.preventDefault();
  const email = document.getElementById('email')?.value || document.getElementById('identifier')?.value;
  const password = document.getElementById('password')?.value;
  console.debug('Submeter login', { email });
  // TODO: chamar endpoint /api/v1/auth/login e tratar resposta
});
