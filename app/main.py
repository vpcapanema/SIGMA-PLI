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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
