"""
SIGMA-PLI - Serviço Keep-Alive
Mantém o servidor ativo no Render fazendo auto-ping periódico
"""

import asyncio
import httpx
from datetime import datetime
from typing import Optional


class KeepAliveService:
    """
    Serviço que faz requisições periódicas ao próprio servidor
    para evitar que o Render coloque a aplicação em sleep.
    """

    def __init__(self, base_url: str, interval_minutes: int = 10):
        """
        Args:
            base_url: URL base do servidor (ex: https://sigma-pli.onrender.com)
            interval_minutes: Intervalo entre pings em minutos (padrão: 10)
        """
        self.base_url = base_url.rstrip("/")
        self.interval_seconds = interval_minutes * 60
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self.last_ping_time: Optional[datetime] = None
        self.ping_count = 0
        self.failed_pings = 0

    async def ping(self) -> bool:
        """
        Faz uma requisição GET ao endpoint /health para manter o servidor ativo.

        Returns:
            bool: True se o ping foi bem-sucedido, False caso contrário
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/health")

                if response.status_code == 200:
                    self.last_ping_time = datetime.now()
                    self.ping_count += 1
                    print(
                        f"✅ Keep-Alive ping #{self.ping_count} OK - {self.last_ping_time.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    return True
                else:
                    self.failed_pings += 1
                    print(f"⚠️ Keep-Alive ping falhou com status {response.status_code}")
                    return False

        except Exception as e:
            self.failed_pings += 1
            print(f"❌ Keep-Alive ping erro: {str(e)}")
            return False

    async def _run_loop(self):
        """Loop interno que executa os pings periodicamente."""
        print(
            f"🚀 Keep-Alive iniciado - ping a cada {self.interval_seconds // 60} minutos"
        )
        print(f"🎯 Target URL: {self.base_url}/health")

        # Aguarda 2 minutos antes do primeiro ping (tempo para o servidor subir)
        await asyncio.sleep(120)

        while self.is_running:
            try:
                await self.ping()
                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                print("⏹️ Keep-Alive loop cancelado")
                break
            except Exception as e:
                print(f"❌ Erro no loop Keep-Alive: {str(e)}")
                await asyncio.sleep(60)  # Aguarda 1 minuto em caso de erro

    def start(self):
        """Inicia o serviço de keep-alive em background."""
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._run_loop())
            print(f"✅ Serviço Keep-Alive ativado")

    async def stop(self):
        """Para o serviço de keep-alive."""
        if self.is_running:
            self.is_running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            print(f"⏹️ Serviço Keep-Alive desativado")
            print(
                f"📊 Estatísticas: {self.ping_count} pings OK, {self.failed_pings} falhas"
            )

    def get_stats(self) -> dict:
        """Retorna estatísticas do serviço."""
        return {
            "is_running": self.is_running,
            "base_url": self.base_url,
            "interval_minutes": self.interval_seconds // 60,
            "ping_count": self.ping_count,
            "failed_pings": self.failed_pings,
            "last_ping": (
                self.last_ping_time.isoformat() if self.last_ping_time else None
            ),
        }


# Instância global (será configurada no startup)
keepalive_service: Optional[KeepAliveService] = None


def get_keepalive_service() -> Optional[KeepAliveService]:
    """Retorna a instância global do serviço."""
    return keepalive_service


def init_keepalive_service(
    base_url: str, interval_minutes: int = 10
) -> KeepAliveService:
    """
    Inicializa o serviço global de keep-alive.

    Args:
        base_url: URL base do servidor
        interval_minutes: Intervalo entre pings

    Returns:
        KeepAliveService: Instância configurada
    """
    global keepalive_service
    keepalive_service = KeepAliveService(base_url, interval_minutes)
    return keepalive_service
