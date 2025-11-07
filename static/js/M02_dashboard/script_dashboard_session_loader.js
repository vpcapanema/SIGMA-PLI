const formatDateTime = (isoString) => {
    if (!isoString) {
        return "Não disponível";
    }

    try {
        const date = new Date(isoString);
        return date.toLocaleString("pt-BR", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    } catch (error) {
        console.error("Falha ao formatar data", error);
        return isoString;
    }
};

const updateSessionInfo = async () => {
    const idElement = document.getElementById("session-id");
    const expiresElement = document.getElementById("session-expires");

    if (!idElement || !expiresElement) {
        return;
    }

    try {
        const response = await fetch("/api/v1/dashboard/session", {
            headers: {
                "Accept": "application/json",
            },
            credentials: "same-origin",
        });

        if (!response.ok) {
            throw new Error(`Erro ao recuperar sessão (status ${response.status})`);
        }

        const payload = await response.json();
        idElement.textContent = payload.session_id || "Indisponível";
        expiresElement.textContent = formatDateTime(payload.expires_at);
    } catch (error) {
        console.error("Não foi possível carregar detalhes da sessão", error);
        idElement.textContent = "Erro ao carregar";
        expiresElement.textContent = "Erro ao carregar";
    }
};

const configureLogout = () => {
    const button = document.getElementById("logout-button");
    if (!button) {
        return;
    }

    button.addEventListener("click", async () => {
        button.disabled = true;
        button.textContent = "Saindo...";

        try {
            const response = await fetch("/api/v1/auth/logout", {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                },
                credentials: "same-origin",
            });

            if (!response.ok) {
                throw new Error("Falha ao encerrar sessão");
            }

            window.location.assign("/auth/login");
        } catch (error) {
            console.error("Erro durante logout", error);
            button.disabled = false;
            button.textContent = "Sair";
            alert("Não foi possível encerrar a sessão. Tente novamente.");
        }
    });
};

updateSessionInfo();
configureLogout();