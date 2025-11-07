"""
Middleware de Autenticação e Permissões
Sistema de hierarquia de 5 níveis: ADMIN(5), GESTOR(4), ANALISTA(3), OPERADOR(2), VISUALIZADOR(1)
"""

from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status

from app.dependencies import get_current_user
from app.schemas.M01_auth.schema_auth import AuthenticatedUser
from app.database import get_pg_pool


class PermissionChecker:
    """Classe para verificação de permissões baseada em hierarquia"""

    @staticmethod
    async def get_user_permission_level(usuario_id: UUID) -> Optional[int]:
        """
        Busca o nivel_acesso do usuário no banco de dados

        Args:
            usuario_id: UUID do usuário

        Returns:
            nivel_acesso (1-5) ou None se não encontrado
        """
        pool = await get_pg_pool()
        if not pool:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de banco de dados indisponível",
            )

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT nivel_acesso, tipo_usuario, ativo
                FROM usuarios.usuario
                WHERE id = $1
                """,
                usuario_id,
            )

            if not row:
                return None

            if not row["ativo"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo"
                )

            return row["nivel_acesso"]

    @staticmethod
    async def verify_permission(usuario_id: UUID, nivel_minimo: int) -> bool:
        """
        Verifica se usuário tem permissão baseado no nível mínimo

        Args:
            usuario_id: UUID do usuário
            nivel_minimo: Nível mínimo requerido (1-5)

        Returns:
            True se tem permissão, False caso contrário
        """
        nivel_usuario = await PermissionChecker.get_user_permission_level(usuario_id)

        if nivel_usuario is None:
            return False

        return nivel_usuario >= nivel_minimo

    @staticmethod
    async def require_permission(
        usuario_id: UUID, nivel_minimo: int, tipo_descricao: str
    ) -> None:
        """
        Exige que usuário tenha permissão mínima, caso contrário levanta exceção

        Args:
            usuario_id: UUID do usuário
            nivel_minimo: Nível mínimo requerido (1-5)
            tipo_descricao: Descrição do tipo de usuário para mensagem de erro

        Raises:
            HTTPException 403 se não tem permissão
        """
        tem_permissao = await PermissionChecker.verify_permission(
            usuario_id, nivel_minimo
        )

        if not tem_permissao:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Apenas usuários do tipo {tipo_descricao} podem realizar esta ação.",
            )


# =====================================================
# DEPENDENCIES PARA USAR NOS ROUTERS
# =====================================================


async def require_admin(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """
    Dependency que exige nível ADMIN (5)

    Usage:
        @router.delete("/usuarios/{id}")
        async def deletar_usuario(
            id: UUID,
            user: AuthenticatedUser = Depends(require_admin)
        ):
            ...
    """
    await PermissionChecker.require_permission(UUID(current_user.conta_id), 5, "ADMIN")
    return current_user


async def require_admin_or_gestor(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """
    Dependency que exige nível GESTOR ou superior (4+)

    Usage:
        @router.post("/usuarios/aprovar/{id}")
        async def aprovar_usuario(
            id: UUID,
            user: AuthenticatedUser = Depends(require_admin_or_gestor)
        ):
            ...
    """
    await PermissionChecker.require_permission(
        UUID(current_user.conta_id), 4, "GESTOR ou ADMIN"
    )
    return current_user


async def require_analista_or_above(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """
    Dependency que exige nível ANALISTA ou superior (3+)

    Usage:
        @router.put("/dados/{id}")
        async def atualizar_dados(
            id: UUID,
            user: AuthenticatedUser = Depends(require_analista_or_above)
        ):
            ...
    """
    await PermissionChecker.require_permission(
        UUID(current_user.conta_id), 3, "ANALISTA, GESTOR ou ADMIN"
    )
    return current_user


async def require_operador_or_above(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """
    Dependency que exige nível OPERADOR ou superior (2+)

    Usage:
        @router.post("/registros")
        async def criar_registro(
            user: AuthenticatedUser = Depends(require_operador_or_above)
        ):
            ...
    """
    await PermissionChecker.require_permission(
        UUID(current_user.conta_id), 2, "OPERADOR ou superior"
    )
    return current_user


async def verify_permission_level(
    nivel_minimo: int, current_user: AuthenticatedUser = Depends(get_current_user)
) -> AuthenticatedUser:
    """
    Dependency genérica para verificar qualquer nível de permissão

    Args:
        nivel_minimo: Nível mínimo requerido (1-5)

    Usage:
        from functools import partial
        require_nivel_3 = partial(verify_permission_level, 3)

        @router.get("/dados")
        async def listar_dados(
            user: AuthenticatedUser = Depends(require_nivel_3)
        ):
            ...
    """
    await PermissionChecker.require_permission(
        UUID(current_user.conta_id), nivel_minimo, f"nível {nivel_minimo} ou superior"
    )
    return current_user
