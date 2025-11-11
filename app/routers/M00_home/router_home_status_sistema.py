"""
SIGMA-PLI - M00: Home/Boas-vindas
Router para página inicial, navegação principal e status do sistema
"""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import time
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# Modelos Pydantic para requests/responses
class ContactForm(BaseModel):
    name: str
    email: str
    message: str


class SystemStatus(BaseModel):
    status: str
    version: str
    uptime: float
    modules: Dict[str, str]
    databases: Dict[str, str]
    last_updated: datetime


class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, Dict[str, Any]]


# Variável global para controlar uptime
start_time = time.time()


@router.get("/")
async def home_page(request: Request):
    """Página inicial do SIGMA-PLI"""
    return templates.TemplateResponse(
        "pages/M00_home/template_home_index_pagina.html",
        {
            "request": request,
            "title": "SIGMA-PLI - Sistema de Gestão de Metadados",
            "description": "Sistema integrado para gestão de metadados, catálogo interativo e repositório de dados geoespaciais",
        },
    )


@router.get("/api/v1/status", response_model=SystemStatus)
async def system_status():
    """Status detalhado do sistema"""
    return SystemStatus(
        status="operational",
        version="1.0.0",
        uptime=time.time() - start_time,
        modules={
            "M00_home": "✅ operational",
            "M01_auth": "✅ operational",
            "M02_dashboard": "� beta",
            "M03_dicionario": "🚧 under_development",
            "M04_minha_area": "🚧 under_development",
            "M05_calendario": "🚧 under_development",
            "M06_institucional": "🚧 under_development",
            "M07_ferramentas": "🚧 under_development",
            "M08_admin": "🚧 under_development",
        },
        databases={"postgresql": "✅ connected", "neo4j": "✅ connected"},
        last_updated=datetime.now(),
    )


@router.get("/api/status", response_model=SystemStatus)
async def system_status_alias():
    """Alias compatível com o front para status do sistema"""
    return await system_status()


@router.get("/api/v1/health", response_model=HealthCheck)
async def health_check():
    """Health check completo do sistema"""
    services_status = await check_services_health()

    overall_status = (
        "healthy"
        if all(service["status"] == "healthy" for service in services_status.values())
        else "degraded"
    )

    return HealthCheck(
        status=overall_status, timestamp=datetime.now(), services=services_status
    )


@router.get("/health")
async def health_check_root():
    """Health check simples"""
    return {"status": "healthy", "service": "SIGMA-PLI Backend", "version": "1.0.0"}


@router.get("/api/v1/keepalive/stats")
async def keepalive_stats():
    """Retorna estatísticas do serviço Keep-Alive"""
    from app.services.service_keepalive import get_keepalive_service

    keepalive = get_keepalive_service()

    if not keepalive:
        return {
            "status": "disabled",
            "message": "Serviço Keep-Alive não está ativo (desenvolvimento local)",
        }

    stats = keepalive.get_stats()
    return {"status": "active", "stats": stats}


@router.post("/api/v1/contact")
async def submit_contact_form(contact: ContactForm, background_tasks: BackgroundTasks):
    """Processa formulário de contato"""
    try:
        # Validação adicional
        if len(contact.name.strip()) < 2:
            raise HTTPException(
                status_code=400, detail="Nome deve ter pelo menos 2 caracteres"
            )

        if len(contact.message.strip()) < 10:
            raise HTTPException(
                status_code=400, detail="Mensagem deve ter pelo menos 10 caracteres"
            )

        # Adiciona tarefa em background para processar o contato
        background_tasks.add_task(process_contact_form, contact)

        return {
            "status": "success",
            "message": "Mensagem enviada com sucesso! Entraremos em contato em breve.",
            "timestamp": datetime.now(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/api/v1/stats")
async def system_stats():
    """Estatísticas gerais do sistema"""
    return {
        "total_users": 0,  # TODO: implementar
        "total_files": 0,  # TODO: implementar
        "total_datasets": 0,  # TODO: implementar
        "system_uptime": time.time() - start_time,
        "active_sessions": 0,  # TODO: implementar
        "last_backup": None,  # TODO: implementar
        "storage_used": "0 GB",  # TODO: implementar
        "storage_available": "100 GB",  # TODO: implementar
    }


@router.get("/api/v1/modules")
async def available_modules():
    """Lista todos os módulos disponíveis"""
    return {
        "modules": [
            {
                "id": "M00",
                "name": "Home",
                "description": "Página inicial e navegação principal",
                "status": "operational",
                "endpoints": ["/", "/api/v1/status", "/api/v1/health"],
            },
            {
                "id": "M01",
                "name": "Autenticação",
                "description": "Login, logout e gerenciamento de sessões",
                "status": "operational",
                "endpoints": [
                    "/auth/login",
                    "/auth/logout",
                    "/api/v1/auth/login",
                    "/api/v1/auth/logout",
                ],
            },
            {
                "id": "M02",
                "name": "Dashboard",
                "description": "Painel inicial com sessão e atalhos",
                "status": "beta",
                "endpoints": ["/dashboard", "/api/v1/dashboard/session"],
            },
            {
                "id": "M03",
                "name": "Dicionário de Dados",
                "description": "Catálogo de metadados e perfis",
                "status": "under_development",
                "endpoints": ["/dicionario"],
            },
            {
                "id": "M04",
                "name": "Minha Área",
                "description": "Área pessoal do usuário",
                "status": "under_development",
                "endpoints": ["/minha-area"],
            },
            {
                "id": "M05",
                "name": "Calendário",
                "description": "Agenda e home office",
                "status": "under_development",
                "endpoints": ["/calendario"],
            },
            {
                "id": "M06",
                "name": "Institucional",
                "description": "Informações institucionais",
                "status": "under_development",
                "endpoints": ["/institucional"],
            },
            {
                "id": "M07",
                "name": "Ferramentas",
                "description": "GeoServer e ETL",
                "status": "under_development",
                "endpoints": ["/ferramentas"],
            },
            {
                "id": "M08",
                "name": "Administração",
                "description": "Painel administrativo",
                "status": "under_development",
                "endpoints": ["/admin"],
            },
        ]
    }


@router.get("/api/v1/test-neo4j")
async def test_neo4j_connection():
    """Testa conexão com Neo4j usando execute_query()"""
    try:
        from app.database import execute_neo4j_query

        # Testa conexão com uma query simples
        records, summary, keys = await execute_neo4j_query(
            "RETURN 'Neo4j OK' as status, timestamp() as ts"
        )

        if records and summary:
            record = records[0]
            return {
                "status": "success",
                "message": "Conexão Neo4j funcionando",
                "data": {
                    "response": record["status"],
                    "timestamp": record["ts"],
                    "query_time_ms": summary.result_available_after,
                },
            }
        else:
            return {
                "status": "error",
                "message": "Neo4j não retornou dados",
                "details": "Query executada mas sem resultados",
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro na conexão Neo4j: {str(e)}",
            "details": str(e),
        }


@router.post("/api/v1/test-neo4j/create-example")
async def create_neo4j_example():
    """Cria um grafo de exemplo no Neo4j"""
    try:
        from app.database import create_neo4j_example_graph

        success = await create_neo4j_example_graph()

        if success:
            return {
                "status": "success",
                "message": "Grafo de exemplo criado com sucesso",
                "data": {"created_nodes": 2, "created_relationships": 1},
            }
        else:
            return {"status": "error", "message": "Falha ao criar grafo de exemplo"}

    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao criar grafo: {str(e)}",
            "details": str(e),
        }


@router.get("/api/v1/test-neo4j/query-example")
async def query_neo4j_example():
    """Executa uma query de exemplo no Neo4j"""
    try:
        from app.database import query_neo4j_example

        records = await query_neo4j_example()

        if records:
            return {
                "status": "success",
                "message": f"Query executada com sucesso, {len(records)} resultados",
                "data": [record.data() for record in records],
            }
        else:
            return {
                "status": "success",
                "message": "Query executada, mas nenhum resultado encontrado",
                "data": [],
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro na query: {str(e)}",
            "details": str(e),
        }


# ============================================
# ROTAS INFORMATIVAS (PÁGINAS PÚBLICAS)
# ============================================


@router.get("/sobre")
async def sobre_page(request: Request):
    """Página 'Sobre' do SIGMA-PLI"""
    return templates.TemplateResponse(
        "pages/M00_home/template_sobre_pagina.html",
        {
            "request": request,
            "page_title": "Sobre | SIGMA-PLI",
            "title": "Sobre o SIGMA-PLI",
        },
    )


@router.get("/ajuda")
async def ajuda_page(request: Request):
    """Página 'Ajuda e Documentação' do SIGMA-PLI"""
    return templates.TemplateResponse(
        "pages/M00_home/template_ajuda_pagina.html",
        {
            "request": request,
            "page_title": "Ajuda | SIGMA-PLI",
            "title": "Ajuda e Documentação",
        },
    )


@router.get("/contato")
async def contato_page(request: Request):
    """Página 'Contato' do SIGMA-PLI"""
    return templates.TemplateResponse(
        "pages/M00_home/template_contato_pagina.html",
        {
            "request": request,
            "page_title": "Contato | SIGMA-PLI",
            "title": "Entre em Contato",
        },
    )


@router.get("/termos")
async def termos_page(request: Request):
    """Página 'Termos de Serviço' do SIGMA-PLI"""
    return templates.TemplateResponse(
        "pages/M00_home/template_termos_pagina.html",
        {
            "request": request,
            "page_title": "Termos de Serviço | SIGMA-PLI",
            "title": "Termos de Serviço",
        },
    )


@router.get("/equipe")
async def equipe_page(request: Request):
    """Página da equipe"""
    return templates.TemplateResponse(
        "pages/M00_home/template_equipe_pagina.html",
        {
            "request": request,
            "page_title": "Nossa Equipe | SIGMA-PLI",
            "title": "Equipe SIGMA-PLI",
        },
    )


# Funções auxiliares
async def check_services_health() -> Dict[str, Dict[str, Any]]:
    """Verifica saúde dos serviços"""
    services = {}

    # PostgreSQL check
    try:
        # TODO: implementar verificação real do PostgreSQL
        services["postgresql"] = {
            "status": "healthy",
            "response_time": 10,
            "last_check": datetime.now(),
        }
    except Exception as e:
        services["postgresql"] = {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.now(),
        }

    # Neo4j check
    try:
        # TODO: implementar verificação real do Neo4j
        services["neo4j"] = {
            "status": "healthy",
            "response_time": 15,
            "last_check": datetime.now(),
        }
    except Exception as e:
        services["neo4j"] = {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.now(),
        }

    # Redis check (se aplicável)
    try:
        # TODO: implementar verificação do Redis se usado
        services["redis"] = {
            "status": "healthy",
            "response_time": 5,
            "last_check": datetime.now(),
        }
    except Exception as e:
        services["redis"] = {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.now(),
        }

    return services


async def process_contact_form(contact: ContactForm):
    """Processa formulário de contato em background"""
    try:
        # Simula processamento (ex: enviar email, salvar no banco, etc.)
        await asyncio.sleep(1)  # Simula delay de processamento

        # TODO: implementar lógica real
        # - Salvar no banco de dados
        # - Enviar email de confirmação
        # - Notificar administradores
        # - Log de auditoria

        print(f"Contato processado: {contact.name} <{contact.email}>")
        print(f"Mensagem: {contact.message[:100]}...")

    except Exception as e:
        print(f"Erro ao processar contato: {e}")
        # TODO: implementar logging adequado
