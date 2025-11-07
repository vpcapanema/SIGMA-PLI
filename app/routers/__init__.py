"""
SIGMA-PLI - Routers Principais (composição)
"""

from fastapi import APIRouter

from app.routers.M00_home.router_home_status_sistema import (
    router as home_router,
)
from app.routers.M02_dashboard.router_dashboard_home import (
    router as dashboard_router,
)
from app.routers.M01_auth.router_auth_pages import (
    router as auth_pages_router,
)
from app.routers.M01_auth.router_auth_api import (
    router as auth_api_router,
)
from app.routers.M08_admin.router_admin_usuarios_config import (
    router as admin_router,
)
from app.routers.M08_admin.router_admin_pages import (
    router as admin_pages_router,
)
from app.routers.M01_auth.router_externas_cpf_cep import (
    router as externas_router,
)
from app.routers.M01_auth.router_localizacao_br import (
    router as localizacao_br_router,
)

# Novos routers modularizados (páginas públicas e restritas)
from app.routers.M01_auth.public.router_pages_cadastro_pessoa_fisica import (
    router as public_pf_pages_router,
)
from app.routers.M01_auth.public.router_pages_cadastro_instituicao import (
    router as public_pj_pages_router,
)
from app.routers.M01_auth.public.router_pages_cadastro_usuario import (
    router as public_user_pages_router,
)
from app.routers.M01_auth.restrito.router_pages_pessoa_fisica import (
    router as restrito_pf_pages_router,
)
from app.routers.M01_auth.restrito.router_pages_instituicao import (
    router as restrito_pj_pages_router,
)
from app.routers.M01_auth.restrito.router_pages_usuarios import (
    router as restrito_user_pages_router,
)

# M07 - Ferramentas
from app.routers.M07_ferramentas.router_ferramentas_geoserver_etl import (
    router as ferramentas_router,
)

router = APIRouter()

# Home define a rota "/" e também "/api/v1/..." específicas do módulo
router.include_router(home_router)

router.include_router(dashboard_router)
router.include_router(auth_pages_router)
router.include_router(auth_api_router)

router.include_router(admin_router)
router.include_router(admin_pages_router)
router.include_router(externas_router)
router.include_router(localizacao_br_router)

# Registro dos novos routers modularizados
router.include_router(public_pf_pages_router)
router.include_router(public_pj_pages_router)
router.include_router(public_user_pages_router)

router.include_router(restrito_pf_pages_router)
router.include_router(restrito_pj_pages_router)
router.include_router(restrito_user_pages_router)

# M07 - Ferramentas
router.include_router(
    ferramentas_router, prefix="/ferramentas", tags=["M07 - Ferramentas"]
)

# TODO: Incluir outros módulos quando implementados
# router.include_router(
#     auth_router,
#     prefix="/api/v1/auth",
#     tags=["M01 - Autenticação"]
# )
# ... outros módulos
