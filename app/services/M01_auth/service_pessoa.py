"""
Serviço de gerenciamento de pessoas (Física e Jurídica)
Interage com PostgreSQL para CRUD de pessoas
"""

from typing import Optional
from datetime import date
import uuid

from app.database import get_postgres_connection
from app.services.M01_auth.service_cadastro_pessoa import (
    CadastroPessoaService,
)


class PessoaService:
    """Serviço para operações de pessoa no banco de dados"""

    @staticmethod
    async def create_pessoa_fisica(
        nome_completo: str,
        cpf: str,
        email: str,
        data_nascimento: Optional[date] = None,
        nome_social: Optional[str] = None,
        sexo: Optional[str] = None,
        estado_civil: Optional[str] = None,
        nacionalidade: Optional[str] = "BRASILEIRA",
        naturalidade: Optional[str] = None,
        nome_pai: Optional[str] = None,
        nome_mae: Optional[str] = None,
        rg: Optional[str] = None,
        orgao_expeditor: Optional[str] = None,
        uf_rg: Optional[str] = None,
        data_expedicao_rg: Optional[date] = None,
        titulo_eleitor: Optional[str] = None,
        zona_eleitoral: Optional[str] = None,
        secao_eleitoral: Optional[str] = None,
        pis_pasep: Optional[str] = None,
        telefone_principal: Optional[str] = None,
        telefone_secundario: Optional[str] = None,
        email_secundario: Optional[str] = None,
        profissao: Optional[str] = None,
        escolaridade: Optional[str] = None,
        renda_mensal: Optional[float] = None,
        cep: Optional[str] = None,
        logradouro: Optional[str] = None,
        numero: Optional[str] = None,
        complemento: Optional[str] = None,
        bairro: Optional[str] = None,
        cidade: Optional[str] = None,
        uf: Optional[str] = None,
        pais: Optional[str] = "Brasil",
    ) -> uuid.UUID:
        """
        Criar pessoa física na tabela definitiva de cadastro (cadastro.pessoa).

        Observação: campos extras recebidos são ignorados no armazenamento simplificado
        e poderão ser tratados em módulos específicos posteriormente.

        Returns:
            UUID da pessoa criada
        """
        # Redireciona para o serviço de cadastro público (cadastro.pessoa)
        pessoa_id = await CadastroPessoaService.create_pessoa(
            nome_completo=nome_completo,
            cpf=cpf,
            email=email,
            telefone=telefone_principal or None,
            cargo=profissao or None,
        )
        return pessoa_id

    @staticmethod
    async def create_instituicao(
        razao_social: str,
        cnpj: str,
        email: str,
        nome_fantasia: Optional[str] = None,
        tipo_instituicao: Optional[str] = None,
        esfera_administrativa: Optional[str] = None,
        inscricao_estadual: Optional[str] = None,
        inscricao_municipal: Optional[str] = None,
        data_fundacao: Optional[date] = None,
        porte_empresa: Optional[str] = None,
        natureza_juridica: Optional[str] = None,
        atividade_principal: Optional[str] = None,
        telefone: Optional[str] = None,
        telefone_secundario: Optional[str] = None,
        email_secundario: Optional[str] = None,
        site: Optional[str] = None,
        cep: Optional[str] = None,
        logradouro: Optional[str] = None,
        numero: Optional[str] = None,
        complemento: Optional[str] = None,
        bairro: Optional[str] = None,
        cidade: Optional[str] = None,
        uf: Optional[str] = None,
        pais: Optional[str] = "Brasil",
    ) -> uuid.UUID:
        """
        Criar instituição (pessoa jurídica, empresa, órgão público, autarquia, fundação, etc.)

        Returns:
            UUID da instituição criada
        """
        conn = await get_postgres_connection()
        try:
            pessoa_id = uuid.uuid4()

            # Inserção mínima e compatível com o DDL atual de cadastro.instituicao
            # Campos disponíveis: id, nome, sigla, cnpj, tipo, endereco, telefone, email, site, ativa, created_at
            # Mapeamentos: razao_social -> nome, tipo_instituicao -> tipo. Demais campos ficam como NULL/ignorados.
            query = """
                INSERT INTO cadastro.instituicao (
                    id, nome, cnpj, email, telefone, site, tipo
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7
                )
                RETURNING id
            """

            await conn.execute(
                query,
                pessoa_id,
                razao_social,
                cnpj,
                email,
                telefone,
                site,
                tipo_instituicao,
            )

            return pessoa_id
        finally:
            await conn.close()

    @staticmethod
    async def get_pessoa_by_cpf(cpf: str) -> Optional[dict]:
        """Buscar pessoa física por CPF"""
        conn = await get_postgres_connection()
        try:
            query = """
                SELECT * FROM cadastro.pessoa
                WHERE cpf = $1
            """
            row = await conn.fetchrow(query, cpf)
            return dict(row) if row else None
        finally:
            await conn.close()

    @staticmethod
    async def get_pessoa_by_cnpj(cnpj: str) -> Optional[dict]:
        """Buscar instituição por CNPJ"""
        conn = await get_postgres_connection()
        try:
            query = """
                SELECT * FROM cadastro.instituicao
                WHERE cnpj = $1
            """
            row = await conn.fetchrow(query, cnpj)
            return dict(row) if row else None
        finally:
            await conn.close()

    @staticmethod
    async def get_instituicao_by_cnpj(cnpj: str) -> Optional[dict]:
        """Buscar instituição por CNPJ (alias para get_pessoa_by_cnpj)"""
        return await PessoaService.get_pessoa_by_cnpj(cnpj)

    @staticmethod
    async def get_pessoa_by_email(email: str) -> Optional[dict]:
        """Buscar pessoa por email"""
        conn = await get_postgres_connection()
        try:
            # Primeiro procura em cadastro.pessoa (PF)
            row = await conn.fetchrow(
                "SELECT * FROM cadastro.pessoa WHERE email = $1",
                email,
            )
            if row:
                return dict(row)
            # Depois procura em cadastro.instituicao (PJ)
            row = await conn.fetchrow(
                "SELECT * FROM cadastro.instituicao WHERE email = $1",
                email,
            )
            return dict(row) if row else None
        finally:
            await conn.close()
