"""
Exemplos Práticos de Uso do Sistema de Hierarquia e Permissões
SIGMA-PLI - Migration 006

NOTA: Este arquivo contém múltiplos exemplos independentes.
Os imports estão dentro de cada exemplo para clareza didática.
"""

# =====================================================
# EXEMPLO 1: Proteger um endpoint DELETE (ADMIN apenas)
# =====================================================

from fastapi import APIRouter, Depends, HTTPException  # noqa: E402  # noqa: E402
from uuid import UUID  # noqa: E402  # noqa: E402
from app.middleware.auth_middleware import require_admin  # noqa: E402  # noqa: E402
from app.schemas.M01_auth.schema_auth import (  # noqa: E402  # noqa: E402
    AuthenticatedUser,
)
from app.database import get_postgres_pool  # noqa: E402  # noqa: E402

router = APIRouter(prefix="/api/v1/projetos", tags=["Projetos"])


@router.delete("/{projeto_id}")
async def deletar_projeto(
    projeto_id: UUID,
    current_user: AuthenticatedUser = Depends(require_admin),  # ← PROTEGE COM ADMIN
):
    """
    Deletar um projeto (soft delete)

    PERMISSÃO: Apenas ADMIN (nível 5)
    """
    pool = await get_postgres_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE projetos SET ativo = false WHERE id = $1", projeto_id
        )

    return {
        "message": "Projeto deletado com sucesso",
        "deleted_by": current_user.username,
    }


# =====================================================
# EXEMPLO 2: Aprovar cadastros (GESTOR ou ADMIN)
# =====================================================

# noqa: E402
from app.middleware.auth_middleware import (  # noqa: E402  # noqa: E402
    require_admin_or_gestor,
)


@router.post("/solicitacoes/{solicitacao_id}/aprovar")
async def aprovar_solicitacao(
    solicitacao_id: UUID,
    current_user: AuthenticatedUser = Depends(require_admin_or_gestor),  # ← GESTOR+
):
    """
    Aprovar solicitação de cadastro

    PERMISSÃO: GESTOR ou ADMIN (nível 4+)
    """
    pool = await get_postgres_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE solicitacoes
            SET status = 'APROVADO', aprovado_por = $1, aprovado_em = NOW()
            WHERE id = $2
        """,
            UUID(current_user.conta_id),
            solicitacao_id,
        )

    return {"message": "Solicitação aprovada", "approved_by": current_user.username}


# =====================================================
# EXEMPLO 3: Gerar relatório (ANALISTA ou superior)
# =====================================================

from app.middleware.auth_middleware import require_analista_or_above  # noqa: E402


@router.get("/relatorios/mensal")
async def gerar_relatorio_mensal(
    mes: int,
    ano: int,
    current_user: AuthenticatedUser = Depends(require_analista_or_above),  # ← ANALISTA+
):
    """
    Gerar relatório mensal

    PERMISSÃO: ANALISTA, GESTOR ou ADMIN (nível 3+)
    """
    pool = await get_postgres_pool()
    async with pool.acquire() as conn:
        dados = await conn.fetch(
            """
            SELECT * FROM projetos
            WHERE EXTRACT(MONTH FROM criado_em) = $1
                AND EXTRACT(YEAR FROM criado_em) = $2
        """,
            mes,
            ano,
        )

    return {
        "mes": mes,
        "ano": ano,
        "total_projetos": len(dados),
        "generated_by": current_user.username,
    }


# =====================================================
# EXEMPLO 4: Criar registro (OPERADOR ou superior)
# =====================================================

from app.middleware.auth_middleware import require_operador_or_above  # noqa: E402
from pydantic import BaseModel  # noqa: E402


class ProjetoCreate(BaseModel):
    nome: str
    descricao: str


@router.post("/")
async def criar_projeto(
    projeto: ProjetoCreate,
    current_user: AuthenticatedUser = Depends(require_operador_or_above),  # ← OPERADOR+
):
    """
    Criar novo projeto

    PERMISSÃO: OPERADOR ou superior (nível 2+)
    """
    pool = await get_postgres_pool()
    async with pool.acquire() as conn:
        projeto_id = await conn.fetchval(
            """
            INSERT INTO projetos (nome, descricao, criado_por)
            VALUES ($1, $2, $3)
            RETURNING id
        """,
            projeto.nome,
            projeto.descricao,
            UUID(current_user.conta_id),
        )

    return {
        "message": "Projeto criado",
        "id": str(projeto_id),
        "created_by": current_user.username,
    }


# =====================================================
# EXEMPLO 5: Listar dados (todos os usuários autenticados)
# =====================================================

from app.dependencies import get_current_user  # noqa: E402


@router.get("/")
async def listar_projetos(
    limit: int = 50,
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),  # ← Qualquer autenticado
):
    """
    Listar projetos

    PERMISSÃO: Qualquer usuário autenticado (todos os níveis)
    """
    pool = await get_postgres_pool()
    async with pool.acquire() as conn:
        projetos = await conn.fetch(
            "SELECT * FROM projetos WHERE ativo = true LIMIT $1", limit
        )

    return {"total": len(projetos), "projetos": [dict(p) for p in projetos]}


# =====================================================
# EXEMPLO 6: Nível customizado (ex: nível 3 exato)
# =====================================================

from functools import partial  # noqa: E402
from app.middleware.auth_middleware import verify_permission_level  # noqa: E402

# Criar dependency para nível 3 ou superior
require_nivel_3 = partial(verify_permission_level, 3)


@router.get("/dados-sensiveis")
async def listar_dados_sensiveis(
    current_user: AuthenticatedUser = Depends(require_nivel_3),  # ← Nível 3+
):
    """
    Listar dados sensíveis

    PERMISSÃO: Nível 3 ou superior (ANALISTA, GESTOR, ADMIN)
    """
    return {"dados": "sensíveis"}


# =====================================================
# EXEMPLO 7: Verificação manual de permissão
# =====================================================

from app.middleware.auth_middleware import PermissionChecker  # noqa: E402


@router.put("/{projeto_id}")
async def atualizar_projeto(
    projeto_id: UUID,
    projeto: ProjetoCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Atualizar projeto

    PERMISSÃO:
    - OPERADOR+ pode atualizar próprios projetos
    - GESTOR+ pode atualizar qualquer projeto
    """
    pool = await get_postgres_pool()
    async with pool.acquire() as conn:
        # Buscar projeto
        projeto_db = await conn.fetchrow(
            "SELECT criado_por FROM projetos WHERE id = $1", projeto_id
        )

        if not projeto_db:
            raise HTTPException(404, "Projeto não encontrado")

        # Verificar se é GESTOR ou superior
        is_gestor_plus = await PermissionChecker.verify_permission(
            UUID(current_user.conta_id), 4  # Nível GESTOR
        )

        # Verificar se é o criador
        is_owner = str(projeto_db["criado_por"]) == current_user.conta_id

        # Apenas GESTOR+ ou criador pode atualizar
        if not (is_gestor_plus or is_owner):
            raise HTTPException(
                403, "Apenas GESTORs ou o criador podem atualizar este projeto"
            )

        # Atualizar
        await conn.execute(
            """
            UPDATE projetos
            SET nome = $1, descricao = $2, atualizado_em = NOW()
            WHERE id = $3
        """,
            projeto.nome,
            projeto.descricao,
            projeto_id,
        )

    return {"message": "Projeto atualizado"}


# =====================================================
# EXEMPLO 8: Endpoint público (sem autenticação)
# =====================================================


@router.get("/public/estatisticas")
async def estatisticas_publicas():
    """
    Estatísticas públicas

    PERMISSÃO: Nenhuma (endpoint público)
    """
    pool = await get_postgres_pool()
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM projetos WHERE ativo = true")

    return {"total_projetos": total}


# =====================================================
# EXEMPLO 9: Middleware em router inteiro
# =====================================================

# Aplicar permissão a TODOS os endpoints do router
router_admin = APIRouter(
    prefix="/api/v1/admin-restricted",
    tags=["Admin - Área Restrita"],
    dependencies=[Depends(require_admin)],  # ← Todos os endpoints exigem ADMIN
)


@router_admin.get("/logs")
async def listar_logs():
    """Todos os endpoints deste router exigem ADMIN"""
    return {"logs": [...]}


@router_admin.delete("/clear-cache")
async def limpar_cache():
    """Também exige ADMIN (herdado do router)"""
    return {"message": "Cache limpo"}


# =====================================================
# EXEMPLO 10: Retornar dados diferentes por nível
# =====================================================


@router.get("/{projeto_id}")
async def obter_projeto(
    projeto_id: UUID, current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Obter projeto (com dados diferentes por nível)

    PERMISSÃO: Qualquer autenticado
    - VISUALIZADOR: Dados básicos
    - OPERADOR+: Dados completos
    - GESTOR+: Dados completos + auditoria
    """
    pool = await get_postgres_pool()

    # Verificar nível do usuário
    nivel_usuario = await PermissionChecker.get_user_permission_level(
        UUID(current_user.conta_id)
    )

    async with pool.acquire() as conn:
        # Query base
        projeto = await conn.fetchrow(
            "SELECT * FROM projetos WHERE id = $1", projeto_id
        )

        if not projeto:
            raise HTTPException(404, "Projeto não encontrado")

        # Dados básicos (todos)
        resultado = {
            "id": str(projeto["id"]),
            "nome": projeto["nome"],
            "descricao": projeto["descricao"],
        }

        # OPERADOR+ vê mais dados
        if nivel_usuario >= 2:
            resultado["criado_em"] = projeto["criado_em"]
            resultado["atualizado_em"] = projeto["atualizado_em"]

        # GESTOR+ vê dados de auditoria
        if nivel_usuario >= 4:
            resultado["criado_por"] = str(projeto["criado_por"])
            resultado["ativo"] = projeto["ativo"]

        return resultado


# =====================================================
# EXEMPLO 11: Atualizar próprio tipo de usuário (SQL)
# =====================================================

"""
-- SQL direto no banco (para testes)

-- Promover usuário para ADMIN
UPDATE usuarios.usuario
SET tipo_usuario = 'ADMIN'
WHERE username = 'joao.silva';
-- nivel_acesso será automaticamente definido como 5

-- Rebaixar para OPERADOR
UPDATE usuarios.usuario
SET tipo_usuario = 'OPERADOR'
WHERE username = 'joao.silva';
-- nivel_acesso será automaticamente definido como 2

-- Verificar resultado
SELECT username, tipo_usuario, nivel_acesso
FROM usuarios.usuario
WHERE username = 'joao.silva';
"""


# =====================================================
# EXEMPLO 12: Usar a API para atualizar tipo
# =====================================================

"""
# Via API (requer GESTOR ou ADMIN)

PUT /api/v1/admin/usuarios/{usuario_id}/tipo

Body:
{
    "tipo_usuario": "ADMIN"
}

Response:
{
    "id": "uuid",
    "username": "joao.silva",
    "email_institucional": "joao.silva@sigma.gov.br",
    "tipo_usuario": "ADMIN",
    "nivel_acesso": 5,
    "ativo": true,
    "email_verificado": true,
    "tipo_usuario_descricao": "Administrador"
}
"""


# =====================================================
# EXEMPLO 13: Tratamento de erros customizado
# =====================================================

from fastapi import status  # noqa: E402


@router.post("/acao-critica")
async def acao_critica(current_user: AuthenticatedUser = Depends(get_current_user)):
    """
    Ação crítica com verificação customizada
    """
    # Verificar se é ADMIN
    nivel = await PermissionChecker.get_user_permission_level(
        UUID(current_user.conta_id)
    )

    if nivel < 5:
        # Mensagem customizada
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Acesso Negado",
                "message": "Esta ação requer privilégios de ADMINISTRADOR.",
                "your_level": nivel,
                "required_level": 5,
                "contact": "Entre em contato com o administrador do sistema.",
            },
        )

    # Executar ação crítica
    return {"message": "Ação executada com sucesso"}


# =====================================================
# RESULTADO DOS EXEMPLOS
# =====================================================

"""
✅ EXEMPLO 1: DELETE protegido (ADMIN)
✅ EXEMPLO 2: Aprovação (GESTOR+)
✅ EXEMPLO 3: Relatórios (ANALISTA+)
✅ EXEMPLO 4: Criar dados (OPERADOR+)
✅ EXEMPLO 5: Listar dados (todos autenticados)
✅ EXEMPLO 6: Nível customizado
✅ EXEMPLO 7: Verificação manual
✅ EXEMPLO 8: Endpoint público
✅ EXEMPLO 9: Middleware em router inteiro
✅ EXEMPLO 10: Dados diferentes por nível
✅ EXEMPLO 11: SQL direto
✅ EXEMPLO 12: API para atualizar tipo
✅ EXEMPLO 13: Erros customizados

🚀 Sistema pronto para uso em produção!
"""
