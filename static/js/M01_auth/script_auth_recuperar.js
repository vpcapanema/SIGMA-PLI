document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('recuperar-form');
  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const data = new FormData(form);
    const payload = Object.fromEntries(data.entries());

    try {
      const res = await fetch(form.action, { method: 'POST', body: JSON.stringify(payload), headers: { 'Content-Type': 'application/json' } });
      const fb = document.getElementById('recuperar-feedback');
      if (!fb) return;
      if (res.ok) {
        fb.hidden = false; fb.textContent = 'Instruções enviadas para seu e-mail.';
      } else {
        const text = await res.text(); fb.hidden = false; fb.textContent = text || 'Erro ao enviar instruções.';
      }
    } catch (err) {
      const fb = document.getElementById('recuperar-feedback'); if (fb) { fb.hidden = false; fb.textContent = 'Erro de rede.'; }
    }
  });
});
