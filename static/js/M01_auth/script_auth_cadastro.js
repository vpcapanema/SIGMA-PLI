document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('cadastro-form');
  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const data = new FormData(form);
    const payload = Object.fromEntries(data.entries());

    if (payload.password !== payload.password_confirm) {
      const fb = document.getElementById('cadastro-feedback');
      if (fb) { fb.hidden = false; fb.textContent = 'As senhas não coincidem.'; }
      return;
    }

    try {
      const res = await fetch(form.action, { method: 'POST', body: JSON.stringify(payload), headers: { 'Content-Type': 'application/json' } });
      if (res.ok) {
        const fb = document.getElementById('cadastro-feedback');
        if (fb) { fb.hidden = false; fb.textContent = 'Conta criada com sucesso. Verifique seu e-mail.'; }
      } else {
        const text = await res.text();
        const fb = document.getElementById('cadastro-feedback');
        if (fb) { fb.hidden = false; fb.textContent = text || 'Erro ao criar conta.'; }
      }
    } catch (err) {
      const fb = document.getElementById('cadastro-feedback');
      if (fb) { fb.hidden = false; fb.textContent = 'Erro de rede.'; }
    }
  });
});
