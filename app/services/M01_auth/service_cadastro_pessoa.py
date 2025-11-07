"""
SIGMA-PLI - Serviço de Cadastro de Pessoa (tabela cadastro.pessoa)

Este serviço grava cadastros públicos de Pessoa Física na tabela
cadastro.pessoa (modelo simples de cadastro).
"""

from typing import Optional
import uuid

from app.database import get_postgres_connection


class CadastroPessoaService:
    """Operações de cadastro para tabela cadastro.pessoa"""

    @staticmethod
    async def create_pessoa(
        nome_completo: str,
        cpf: str,
        email: str,
        telefone: Optional[str] = None,
        cargo: Optional[str] = None,
        instituicao_id: Optional[uuid.UUID] = None,
        departamento_id: Optional[uuid.UUID] = None,
    ) -> uuid.UUID:
        """
        Insere uma pessoa na tabela cadastro.pessoa e retorna o UUID gerado.
                        Campos presentes em cadastro.pessoa (DDL simplificada):
                            id, nome_completo, cpf, email, telefone, cargo,
                            instituicao_id, departamento_id, ativa, created_at
        """
        conn = await get_postgres_connection()
        try:
            pessoa_id = uuid.uuid4()

            # Garantir CPF apenas dígitos
            import re

            cpf_limpo = re.sub(r"[^\d]", "", cpf or "")

            # Verificar duplicidade por CPF ou Email
            exists = await conn.fetchrow(
                """
                SELECT id FROM cadastro.pessoa
                WHERE (cpf = $1 AND cpf IS NOT NULL) OR (email = $2 AND email IS NOT NULL)
                """,
                cpf_limpo or None,
                email or None,
            )
            if exists:
                # Retornar o id existente para manter idempotência do cadastro público
                return exists["id"]

            await conn.execute(
                """
                INSERT INTO cadastro.pessoa (
                    id, nome_completo, cpf, email, telefone, cargo,
                    instituicao_id, departamento_id, ativa, created_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6,
                    $7, $8, TRUE, NOW()
                )
                """,
                pessoa_id,
                nome_completo,
                cpf_limpo or None,
                email,
                telefone,
                cargo,
                instituicao_id,
                departamento_id,
            )

            return pessoa_id
        finally:
            await conn.close()

    @staticmethod
    async def get_by_cpf(cpf: str) -> Optional[dict]:
        """Busca pessoa em cadastro.pessoa por CPF"""
        conn = await get_postgres_connection()
        try:
            import re

            cpf_limpo = re.sub(r"[^\d]", "", cpf or "")
            row = await conn.fetchrow(
                "SELECT * FROM cadastro.pessoa WHERE cpf = $1",
                cpf_limpo or None,
            )
            return dict(row) if row else None
        finally:
            await conn.close()

    @staticmethod
    async def get_by_email(email: str) -> Optional[dict]:
        """Busca pessoa em cadastro.pessoa por Email"""
        conn = await get_postgres_connection()
        try:
            row = await conn.fetchrow(
                "SELECT * FROM cadastro.pessoa WHERE email = $1",
                email,
            )
            return dict(row) if row else None
        finally:
            await conn.close()
