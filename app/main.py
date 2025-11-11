"""
SIGMA-PLI - Sistema de Gestão de Metadados e Repositório Interativo
Backend FastAPI - Aplicação Principal (apenas composição e bootstrap)
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn

from app.database import init_db
from app.routers import router
from app.config import settings
from app.services.service_keepalive import init_keepalive_service, get_keepalive_service


app = FastAPI(
    title="SIGMA-PLI API",
    description="Sistema de Gestão de Metadados e Repositório Interativo",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Legacy PLI assets (images) - mount the original PLI-CADASTRO assets so templates
# that reference /static/assets/* continue to work without copying binaries.
# Legacy PLI assets (images) - mount the original PLI-CADASTRO assets so templates
# that reference /static/assets/* continue to work without copying binaries.
# DESABILITADO: caminho hardcoded do Windows não funciona em Docker/Render
# app.mount(
#     "/static/assets",
#     StaticFiles(directory=r"d:/SIGMA-PLI-IMPLEMENTACAO/PLI-CADASTRO/static/assets"),
#     name="pli_assets",
# )

# Static (principais)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Favicon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


# Routers (modular)
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
    except Exception as e:
        print(f"⚠️ Aviso: Falha na inicialização do banco de dados: {e}")
        print("Continuando sem conexões de banco para desenvolvimento...")

    # Inicializar Keep-Alive se habilitado
    if settings.enable_keepalive and settings.keepalive_url:
        print(f"🔄 Inicializando Keep-Alive Service...")
        keepalive = init_keepalive_service(
            base_url=settings.keepalive_url,
            interval_minutes=settings.keepalive_interval_minutes,
        )
        keepalive.start()
        print(f"✅ Keep-Alive ativo - URL: {settings.keepalive_url}")
    else:
        print(f"ℹ️ Keep-Alive desabilitado (desenvolvimento local)")


@app.on_event("shutdown")
async def shutdown_event():
    keepalive = get_keepalive_service()
    if keepalive:
        await keepalive.stop()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
