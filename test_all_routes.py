"""
Script de teste de TODAS as rotas do SIGMA-PLI
Verifica se as páginas estão acessíveis e retornam 200 OK
"""

import asyncio
import httpx
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

# Base URL do servidor
BASE_URL = "http://127.0.0.1:8010"

# Definição de todas as rotas do sistema
ROUTES = {
    "🏠 HOME (M00)": [
        "/",
        "/health",
        "/api/v1/status",
        "/api/status",
    ],
    "🔐 AUTENTICAÇÃO - Páginas Públicas": [
        "/login",
        "/auth/login",
        "/auth/index",
        "/auth/recuperar-senha",
        "/auth/cadastro-pessoa-fisica",
        "/auth/cadastro-pessoa-juridica",
        "/auth/cadastro-usuario",
        "/auth/admin-login",
        "/auth/sobre",
    ],
    "📄 PÁGINAS PÚBLICAS STANDALONE": [
        "/acesso-negado",
        "/email-verificado",
        "/selecionar-perfil",
        "/recursos",
    ],
    "🔒 PÁGINAS COM AUTENTICAÇÃO (retornarão 403 se não logado)": [
        "/dashboard",
        "/admin/panel",
        "/meus-dados",
        "/pessoa-fisica",
        "/pessoa-juridica",
        "/usuarios",
        "/solicitacoes-cadastro",
        "/sessions-manager",
    ],
    "🧪 ROTAS DE TESTE (sem autenticação)": [
        "/teste/pessoa-fisica",
        "/teste/pessoa-juridica",
        "/teste/usuarios",
        "/teste/solicitacoes",
        "/teste/dashboard",
    ],
}


async def test_route(client: httpx.AsyncClient, route: str) -> tuple[str, int, str]:
    """
    Testa uma rota e retorna (rota, status_code, mensagem).
    """
    try:
        response = await client.get(route, follow_redirects=True, timeout=10.0)

        if response.status_code == 200:
            return (route, response.status_code, "✅ OK")
        elif response.status_code == 403:
            return (route, response.status_code, "🔒 Autenticação necessária")
        elif response.status_code == 404:
            return (route, response.status_code, "❌ Não encontrada")
        elif response.status_code == 500:
            return (route, response.status_code, "❌ Erro interno")
        else:
            return (route, response.status_code, f"⚠️ Status {response.status_code}")

    except httpx.ConnectError:
        return (route, 0, "❌ Servidor não está rodando")
    except httpx.TimeoutException:
        return (route, 0, "⏱️ Timeout")
    except Exception as e:
        return (route, 0, f"❌ Erro: {str(e)[:50]}")


async def test_all_routes():
    """
    Testa todas as rotas definidas.
    """
    console.print("\n[bold cyan]🚀 SIGMA-PLI - Teste de Rotas[/bold cyan]")
    console.print(f"[dim]Servidor: {BASE_URL}[/dim]\n")

    # Verificar se o servidor está rodando
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            if response.status_code != 200:
                console.print(
                    "[bold red]❌ Servidor não está respondendo corretamente![/bold red]"
                )
                console.print(
                    "[yellow]Execute: uvicorn app.main:app --host 127.0.0.1 --port 8010[/yellow]\n"
                )
                return
    except Exception as e:
        console.print("[bold red]❌ Não foi possível conectar ao servidor![/bold red]")
        console.print(f"[dim]Erro: {e}[/dim]")
        console.print(
            "[yellow]Execute: uvicorn app.main:app --host 127.0.0.1 --port 8010[/yellow]\n"
        )
        return

    console.print("[bold green]✅ Servidor está rodando![/bold green]\n")

    # Testar todas as rotas
    total_routes = sum(len(routes) for routes in ROUTES.values())
    successful = 0
    auth_required = 0
    errors = 0

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        for category, routes in ROUTES.items():
            console.print(f"\n[bold magenta]{category}[/bold magenta]")

            # Criar tabela para esta categoria
            table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
            table.add_column("Rota", style="white", no_wrap=False)
            table.add_column("Status", justify="center", width=10)
            table.add_column("Resultado", style="dim")

            for route in routes:
                route_path, status_code, message = await test_route(client, route)

                # Colorir status
                if status_code == 200:
                    status_color = "[bold green]200[/bold green]"
                    successful += 1
                elif status_code == 403:
                    status_color = "[bold yellow]403[/bold yellow]"
                    auth_required += 1
                elif status_code == 0:
                    status_color = "[bold red]ERR[/bold red]"
                    errors += 1
                else:
                    status_color = f"[bold red]{status_code}[/bold red]"
                    errors += 1

                table.add_row(route_path, status_color, message)

            console.print(table)

    # Resumo final
    console.print("\n[bold cyan]📊 RESUMO[/bold cyan]")
    summary_table = Table(box=box.ROUNDED)
    summary_table.add_column("Métrica", style="bold")
    summary_table.add_column("Valor", justify="right")

    summary_table.add_row("Total de rotas testadas", f"[bold]{total_routes}[/bold]")
    summary_table.add_row("✅ Sucesso (200)", f"[bold green]{successful}[/bold green]")
    summary_table.add_row(
        "🔒 Autenticação necessária (403)",
        f"[bold yellow]{auth_required}[/bold yellow]",
    )
    summary_table.add_row("❌ Erros", f"[bold red]{errors}[/bold red]")

    # Calcular percentual de sucesso (considerando 403 como sucesso esperado)
    success_rate = ((successful + auth_required) / total_routes) * 100
    summary_table.add_row(
        "Taxa de sucesso", f"[bold cyan]{success_rate:.1f}%[/bold cyan]"
    )

    console.print(summary_table)

    # Mensagem final
    if errors == 0:
        console.print(
            "\n[bold green]🎉 Todos os endpoints estão funcionando corretamente![/bold green]"
        )
    else:
        console.print(
            f"\n[bold yellow]⚠️ {errors} endpoint(s) com problemas. Verifique os erros acima.[/bold yellow]"
        )

    console.print()


async def test_navigation_flow():
    """
    Testa o fluxo de navegação entre páginas.
    """
    console.print("\n[bold cyan]🔗 Teste de Fluxo de Navegação[/bold cyan]\n")

    flows = [
        {
            "name": "Fluxo de Login",
            "steps": [
                ("Home", "/"),
                ("Login", "/auth/login"),
                ("Dashboard (teste)", "/teste/dashboard"),
            ],
        },
        {
            "name": "Fluxo de Cadastro PF",
            "steps": [
                ("Home", "/"),
                ("Cadastro PF", "/auth/cadastro-pessoa-fisica"),
                ("Email Verificado", "/email-verificado"),
                ("Login", "/auth/login"),
            ],
        },
        {
            "name": "Fluxo de Recursos",
            "steps": [
                ("Recursos", "/recursos"),
                ("Login", "/auth/login"),
                ("Dashboard (teste)", "/teste/dashboard"),
            ],
        },
        {
            "name": "Fluxo de Perfil",
            "steps": [
                ("Login", "/auth/login"),
                ("Selecionar Perfil", "/selecionar-perfil"),
                ("Dashboard (teste)", "/teste/dashboard"),
            ],
        },
    ]

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        for flow in flows:
            console.print(f"[bold magenta]{flow['name']}[/bold magenta]")

            table = Table(box=box.ROUNDED)
            table.add_column("Passo", style="cyan", width=8)
            table.add_column("Página", style="white")
            table.add_column("Status", justify="center")

            all_ok = True
            for i, (page_name, route) in enumerate(flow["steps"], 1):
                _, status_code, _ = await test_route(client, route)

                if status_code == 200:
                    status = "[bold green]✅ OK[/bold green]"
                elif status_code == 403:
                    status = "[bold yellow]🔒 Auth[/bold yellow]"
                else:
                    status = f"[bold red]❌ {status_code}[/bold red]"
                    all_ok = False

                table.add_row(f"Passo {i}", f"{page_name} ({route})", status)

            console.print(table)

            if all_ok:
                console.print("[bold green]✅ Fluxo funcional![/bold green]\n")
            else:
                console.print("[bold red]❌ Fluxo com problemas![/bold red]\n")


async def main():
    """
    Função principal.
    """
    await test_all_routes()
    await test_navigation_flow()

    console.print("\n[bold cyan]💡 Dicas:[/bold cyan]")
    console.print("1. Rotas públicas devem retornar [bold green]200 OK[/bold green]")
    console.print(
        "2. Rotas protegidas retornam [bold yellow]403 Forbidden[/bold yellow] sem autenticação"
    )
    console.print(
        "3. Use as rotas [bold cyan]/teste/*[/bold cyan] para testar sem login"
    )
    console.print("4. Acesse [bold cyan]http://127.0.0.1:8010/[/bold cyan] para a home")
    console.print(
        "5. Acesse [bold cyan]http://127.0.0.1:8010/recursos[/bold cyan] para ver funcionalidades\n"
    )


if __name__ == "__main__":
    asyncio.run(main())
