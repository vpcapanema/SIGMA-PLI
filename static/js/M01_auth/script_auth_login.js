// Backwards-compatible login script (keeps legacy name)
// Mirrors behavior from script_login.js: toggle password and submit to /api/v1/auth/login
document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('login-form');
  const pwdToggle = document.querySelector('.btn-password-toggle');

  pwdToggle?.addEventListener('click', function () {
    const icon = this.querySelector('i');
    const pwd = document.getElementById('password');
    if (!pwd) return;
    if (pwd.type === 'password') {
      pwd.type = 'text';
      icon.classList.remove('fa-eye');
      icon.classList.add('fa-eye-slash');
    } else {
      pwd.type = 'password';
      icon.classList.remove('fa-eye-slash');
      icon.classList.add('fa-eye');
    }
  });

  form?.addEventListener('submit', async function (e) {
    e.preventDefault();
    const username = (document.getElementById('username') || document.getElementById('identifier'))?.value;
    const password = document.getElementById('password')?.value;
    const tipo = document.getElementById('tipo-usuario')?.value;

    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, tipo_usuario: tipo })
      });

      if (!res.ok) {
        const text = await res.text();
        console.error('Login falhou', res.status, text);
        alert('Falha no login: ' + (text || res.status));
        return;
      }

      window.location.href = '/app/dashboard';
    } catch (err) {
      console.error('Erro na requisição de login', err);
      alert('Erro de rede ao efetuar login. Veja console para detalhes.');
    }
  });
});
(() => {
    const form = document.getElementById("login-form");
    const feedback = document.getElementById("login-feedback");

    if (!form) {
        return;
    }

    const setFeedback = (message, isError = true) => {
        if (!feedback) {
            return;
        }
        feedback.textContent = message;
        feedback.classList.toggle("error", isError);
        feedback.classList.toggle("success", !isError);
        feedback.hidden = false;
    };

    const clearFeedback = () => {
        if (!feedback) {
            return;
        }
        feedback.hidden = true;
        feedback.textContent = "";
        feedback.classList.remove("error", "success");
    };

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        clearFeedback();

        const submitButton = form.querySelector("button[type='submit']");
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Entrando...";
        }

        const formData = new FormData(form);
        const payload = {
            identifier: String(formData.get("identifier") || "").trim(),
            password: String(formData.get("password") || ""),
        };

        if (!payload.identifier || !payload.password) {
            setFeedback("Informe usuário/e-mail e senha.");
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = "Entrar";
            }
            return;
        }

        try {
            const response = await fetch("/api/v1/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                credentials: "same-origin",
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorPayload = await response.json().catch(() => ({}));
                const errorMessage = errorPayload?.detail ?? "Falha ao autenticar. Verifique as credenciais.";
                setFeedback(errorMessage);
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = "Entrar";
                }
                return;
            }

            const data = await response.json();
            const targetUrl = data?.redirect_url || "/dashboard";
            setFeedback("Autenticado com sucesso! Redirecionando...", false);

            window.setTimeout(() => {
                window.location.assign(targetUrl);
            }, 600);
        } catch (error) {
            console.error("Erro durante o login", error);
            setFeedback("Erro inesperado. Tente novamente mais tarde.");
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = "Entrar";
            }
        }
    });
})();