"""
SIGMA-PLI - M08: Administração
Router para gestão de usuários, hierarquia e configurações (PROTEGIDO COM PERMISSÕES)
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from app.middleware.auth_middleware import (
    require_admin,
    require_admin_or_gestor,
    require_analista_or_above,
)
from app.schemas.M01_auth.schema_auth import AuthenticatedUser
from app.database import get_pg_pool


router = APIRouter(
    prefix="/api/v1/admin", tags=["Admin - Gestão de Usuários e Hierarquia"]
)


# =====================================================
# SCHEMAS
# =====================================================


class UserHierarchyResponse(BaseModel):
    """Resposta com dados de hierarquia do usuário"""

    id: str
    username: str
    email_institucional: str
    tipo_usuario: str
    nivel_acesso: int
    ativo: bool
    email_verificado: bool
    tipo_usuario_descricao: str


class UserStatsResponse(BaseModel):
    """Estatísticas de usuários por tipo"""

    tipo_usuario: str
    nivel_acesso: int
    total_usuarios: int
    ativos: int
    inativos: int
    emails_verificados: int


class UpdateUserTypeRequest(BaseModel):
    """Request para atualizar tipo de usuário"""

    tipo_usuario: str  # ADMIN, GESTOR, ANALISTA, OPERADOR, VISUALIZADOR


# =====================================================
# ENDPOINTS - LISTAGEM E ESTATÍSTICAS (ANALISTA+)
# =====================================================


@router.get(
    "/usuarios/hierarquia",
    response_model=List[UserHierarchyResponse],
    summary="Listar usuários com hierarquia",
)
async def listar_usuarios_hierarquia(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    tipo_usuario: Optional[str] = Query(None),
    apenas_ativos: bool = Query(True),
    current_user: AuthenticatedUser = Depends(require_analista_or_above),
):
    """
    Lista usuários com informações de hierarquia

    **Permissão requerida:** ANALISTA ou superior (nível 3+)

    **Parâmetros:**
    - limit: Máximo de registros (padrão: 100)
    - offset: Paginação (padrão: 0)
    - tipo_usuario: Filtrar por tipo (ADMIN, GESTOR, etc.)
    - apenas_ativos: Mostrar apenas usuários ativos (padrão: true)
    """
    pool = await get_pg_pool()
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados indisponível",
        )

    # Construir query dinâmica
    where_clauses = []
    params = []
    param_count = 1

    if apenas_ativos:
        where_clauses.append(f"ativo = ${param_count}")
        params.append(True)
        param_count += 1

    if tipo_usuario:
        where_clauses.append(f"tipo_usuario = ${param_count}")
        params.append(tipo_usuario)
        param_count += 1

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            f"""
            SELECT * FROM usuarios.v_usuarios_hierarquia
            {where_sql}
            LIMIT ${param_count} OFFSET ${param_count + 1}
            """,
            *params,
            limit,
            offset,
        )

        return [
            UserHierarchyResponse(
                id=str(row["id"]),
                username=row["username"],
                email_institucional=row["email_institucional"],
                tipo_usuario=row["tipo_usuario"],
                nivel_acesso=row["nivel_acesso"],
                ativo=row["ativo"],
                email_verificado=row["email_verificado"],
                tipo_usuario_descricao=row["tipo_usuario_descricao"],
            )
            for row in rows
        ]


@router.get(
    "/usuarios/estatisticas",
    response_model=List[UserStatsResponse],
    summary="Estatísticas de usuários por tipo",
)
async def estatisticas_usuarios(
    current_user: AuthenticatedUser = Depends(require_analista_or_above),
):
    """
    Retorna estatísticas de usuários agrupadas por tipo_usuario

    **Permissão requerida:** ANALISTA ou superior (nível 3+)
    """
    pool = await get_pg_pool()
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados indisponível",
        )

    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM usuarios.v_estatisticas_tipo_usuario")

        return [
            UserStatsResponse(
                tipo_usuario=row["tipo_usuario"],
                nivel_acesso=row["nivel_acesso"],
                total_usuarios=row["total_usuarios"],
                ativos=row["ativos"],
                inativos=row["inativos"],
                emails_verificados=row["emails_verificados"],
            )
            for row in rows
        ]


# =====================================================
# ENDPOINTS - GESTÃO DE HIERARQUIA (GESTOR+)
# =====================================================


@router.put(
    "/usuarios/{usuario_id}/tipo",
    response_model=UserHierarchyResponse,
    summary="Atualizar tipo/hierarquia de usuário",
)
async def atualizar_tipo_usuario(
    usuario_id: UUID,
    data: UpdateUserTypeRequest,
    current_user: AuthenticatedUser = Depends(require_admin_or_gestor),
):
    """
    Atualiza o tipo_usuario (e automaticamente o nivel_acesso via trigger)

    **Permissão requerida:** GESTOR ou ADMIN (nível 4+)

    **Tipos válidos:**
    - ADMIN (5): Acesso total ao sistema
    - GESTOR (4): Gerenciar usuários e aprovar cadastros
    - ANALISTA (3): Consultar e gerar relatórios
    - OPERADOR (2): Inserir e editar dados
    - VISUALIZADOR (1): Apenas consultar dados
    """
    pool = await get_pg_pool()
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados indisponível",
        )

    # Validar tipo_usuario
    tipos_validos = ["ADMIN", "GESTOR", "ANALISTA", "OPERADOR", "VISUALIZADOR"]
    if data.tipo_usuario not in tipos_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de usuário inválido. Use: {', '.join(tipos_validos)}",
        )

    async with pool.acquire() as conn:
        # Verificar se usuário existe
        usuario_existe = await conn.fetchrow(
            "SELECT id, username FROM usuarios.usuario WHERE id = $1", usuario_id
        )

        if not usuario_existe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )

        # Atualizar tipo (trigger calculará nivel_acesso automaticamente)
        row = await conn.fetchrow(
            """
            UPDATE usuarios.usuario
            SET tipo_usuario = $1
            WHERE id = $2
            RETURNING
                id, username, email_institucional, tipo_usuario,
                nivel_acesso, ativo, email_verificado
            """,
            data.tipo_usuario,
            usuario_id,
        )

        # Buscar descrição
        descricao = {
            "ADMIN": "Administrador",
            "GESTOR": "Gestor",
            "ANALISTA": "Analista",
            "OPERADOR": "Operador",
            "VISUALIZADOR": "Visualizador",
        }[row["tipo_usuario"]]

        return UserHierarchyResponse(
            id=str(row["id"]),
            username=row["username"],
            email_institucional=row["email_institucional"],
            tipo_usuario=row["tipo_usuario"],
            nivel_acesso=row["nivel_acesso"],
            ativo=row["ativo"],
            email_verificado=row["email_verificado"],
            tipo_usuario_descricao=descricao,
        )


# =====================================================
# ENDPOINTS - AÇÕES ADMINISTRATIVAS (ADMIN ONLY)
# =====================================================


@router.delete("/usuarios/{usuario_id}", summary="Deletar usuário (soft delete)")
async def deletar_usuario(
    usuario_id: UUID, current_user: AuthenticatedUser = Depends(require_admin)
):
    """
    Desativa um usuário (soft delete - marca como inativo)

    **Permissão requerida:** ADMIN (nível 5)

    **ATENÇÃO:** Esta ação requer privilégios máximos de administrador
    """
    pool = await get_pg_pool()
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados indisponível",
        )

    async with pool.acquire() as conn:
        # Verificar se usuário existe
        usuario = await conn.fetchrow(
            "SELECT id, username FROM usuarios.usuario WHERE id = $1", usuario_id
        )

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )

        # Soft delete (desativar)
        await conn.execute(
            "UPDATE usuarios.usuario SET ativo = false WHERE id = $1", usuario_id
        )

        return {
            "message": f"Usuário '{usuario['username']}' desativado com sucesso",
            "usuario_id": str(usuario_id),
        }


@router.post("/usuarios/{usuario_id}/reativar", summary="Reativar usuário")
async def reativar_usuario(
    usuario_id: UUID, current_user: AuthenticatedUser = Depends(require_admin)
):
    """
    Reativa um usuário desativado

    **Permissão requerida:** ADMIN (nível 5)
    """
    pool = await get_pg_pool()
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de banco de dados indisponível",
        )

    async with pool.acquire() as conn:
        # Verificar se usuário existe
        usuario = await conn.fetchrow(
            "SELECT id, username FROM usuarios.usuario WHERE id = $1", usuario_id
        )

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )

        # Reativar
        await conn.execute(
            "UPDATE usuarios.usuario SET ativo = true WHERE id = $1", usuario_id
        )

        return {
            "message": f"Usuário '{usuario['username']}' reativado com sucesso",
            "usuario_id": str(usuario_id),
        }


# =====================================================
# ENDPOINT DE STATUS (PÚBLICO PARA TESTES)
# =====================================================


@router.get("/")
async def admin_status():
    """
    Status do módulo administração

    **Público** - Não requer autenticação
    """
    return {
        "module": "M08_admin",
        "status": "active",
        "features": [
            "Hierarquia de 5 níveis (ADMIN, GESTOR, ANALISTA, OPERADOR, VISUALIZADOR)",
            "Gestão de permissões por nível de acesso",
            "Listagem de usuários com hierarquia",
            "Estatísticas por tipo de usuário",
            "Atualização de tipo de usuário (com cálculo automático de nível)",
            "Soft delete de usuários (apenas ADMIN)",
            "Reativação de usuários (apenas ADMIN)",
        ],
        "permissions": {
            "ADMIN": "Nível 5 - Acesso total",
            "GESTOR": "Nível 4 - Gerenciar usuários",
            "ANALISTA": "Nível 3 - Consultar e gerar relatórios",
            "OPERADOR": "Nível 2 - Inserir e editar dados",
            "VISUALIZADOR": "Nível 1 - Apenas consultar",
        },
    }
