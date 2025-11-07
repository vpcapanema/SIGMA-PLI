"""SIGMA-PLI - Service de Instituição"""

from typing import Optional
from uuid import UUID
import asyncpg
from app.database import get_pg_pool
from app.schemas.schema_cadastro_instituicao import InstituicaoCreate, InstituicaoDetail


class InstituicaoService:
    """Service para gerenciamento de instituições"""

    @staticmethod
    async def create_instituicao(data: InstituicaoCreate) -> InstituicaoDetail:
        """
        Cria uma nova instituição no banco de dados

        Args:
            data: Dados da instituição a ser criada

        Returns:
            InstituicaoDetail: Instituição criada com ID gerado

        Raises:
            ValueError: Se CNPJ já existe
            RuntimeError: Se houver erro ao inserir
        """
        pool = await get_pg_pool()

        async with pool.acquire() as conn:
            # Verifica se CNPJ já existe
            existing = await conn.fetchrow(
                "SELECT id FROM cadastro.instituicao WHERE cnpj = $1", data.cnpj
            )

            if existing:
                raise ValueError(f"CNPJ {data.cnpj} já está cadastrado")

            # Insere a instituição
            query = """
                INSERT INTO cadastro.instituicao (
                    nome, razao_social, nome_fantasia, sigla, cnpj, tipo,
                    porte_empresa, data_abertura, inscricao_estadual, inscricao_municipal,
                    situacao_receita_federal, natureza_juridica, regime_tributario,
                    email, email_secundario, telefone, telefone_secundario, site,
                    cep, logradouro, numero, complemento, bairro, cidade, uf, pais,
                    ativa
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                    $11, $12, $13, $14, $15, $16, $17, $18,
                    $19, $20, $21, $22, $23, $24, $25, $26, $27
                )
                RETURNING 
                    id, nome, razao_social, nome_fantasia, sigla, cnpj, tipo,
                    porte_empresa, data_abertura, inscricao_estadual, inscricao_municipal,
                    situacao_receita_federal, natureza_juridica, regime_tributario,
                    email, email_secundario, telefone, telefone_secundario, site,
                    cep, logradouro, numero, complemento, bairro, cidade, uf, pais,
                    ativa, created_at
            """

            try:
                row = await conn.fetchrow(
                    query,
                    data.nome,
                    data.razao_social,
                    data.nome_fantasia,
                    data.sigla,
                    data.cnpj,
                    data.tipo,
                    data.porte_empresa,
                    data.data_abertura,
                    data.inscricao_estadual,
                    data.inscricao_municipal,
                    data.situacao_receita_federal,
                    data.natureza_juridica,
                    data.regime_tributario,
                    data.email,
                    data.email_secundario,
                    data.telefone,
                    data.telefone_secundario,
                    data.site,
                    data.cep,
                    data.logradouro,
                    data.numero,
                    data.complemento,
                    data.bairro,
                    data.cidade,
                    data.uf,
                    data.pais,
                    data.ativa,
                )

                if not row:
                    raise RuntimeError("Falha ao criar instituição")

                return InstituicaoDetail(**dict(row))

            except asyncpg.UniqueViolationError:
                raise ValueError(f"CNPJ {data.cnpj} já está cadastrado")
            except Exception as e:
                raise RuntimeError(f"Erro ao criar instituição: {str(e)}")

    @staticmethod
    async def get_instituicao_by_id(
        instituicao_id: UUID,
    ) -> Optional[InstituicaoDetail]:
        """
        Busca uma instituição por ID

        Args:
            instituicao_id: UUID da instituição

        Returns:
            InstituicaoDetail ou None se não encontrada
        """
        pool = await get_pg_pool()

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    id, nome, razao_social, nome_fantasia, sigla, cnpj, tipo,
                    porte_empresa, data_abertura, inscricao_estadual, inscricao_municipal,
                    situacao_receita_federal, natureza_juridica, regime_tributario,
                    email, email_secundario, telefone, telefone_secundario, site,
                    cep, logradouro, numero, complemento, bairro, cidade, uf, pais,
                    ativa, created_at
                FROM cadastro.instituicao
                WHERE id = $1
                """,
                instituicao_id,
            )

            if row:
                return InstituicaoDetail(**dict(row))
            return None

    @staticmethod
    async def get_instituicao_by_cnpj(cnpj: str) -> Optional[InstituicaoDetail]:
        """
        Busca uma instituição por CNPJ

        Args:
            cnpj: CNPJ da instituição (apenas números)

        Returns:
            InstituicaoDetail ou None se não encontrada
        """
        pool = await get_pg_pool()

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    id, nome, razao_social, nome_fantasia, sigla, cnpj, tipo,
                    porte_empresa, data_abertura, inscricao_estadual, inscricao_municipal,
                    situacao_receita_federal, natureza_juridica, regime_tributario,
                    email, email_secundario, telefone, telefone_secundario, site,
                    cep, logradouro, numero, complemento, bairro, cidade, uf, pais,
                    ativa, created_at
                FROM cadastro.instituicao
                WHERE cnpj = $1
                """,
                cnpj,
            )

            if row:
                return InstituicaoDetail(**dict(row))
            return None
