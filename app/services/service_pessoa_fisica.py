"""
Serviço de Pessoa Física com Criptografia de Dados Sensíveis (LGPD)

Responsabilidades:
- Encriptar/Descriptografar dados sensíveis (CPF, Telefone)
- Validar dados de entrada
- Gerenciar buscas usando hashes (sem descriptografia)
- Auditar acessos e modificações
- Retornar schemas seguros (sem expor dados sensíveis)

Padrão: Envelope Encryption com buscas por hash SHA256
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.security.crypto import get_crypto_manager
from app.security.validators import validar_cpf, validar_telefone
from app.models.schemas.schema_pessoa_fisica import (
    PessoaFisicaCreate,
    PessoaFisicaUpdate,
    PessoaFisicaResponse,
    PessoaFisicaDetailedResponse,
)


class AuditoriaAcao(str, Enum):
    """Ações auditadas para rastreabilidade LGPD"""

    CRIACAO = "CRIACAO"
    LEITURA = "LEITURA"
    ATUALIZACAO = "ATUALIZACAO"
    DELECAO = "DELECAO"
    DESCRIPTOGRAFIA = "DESCRIPTOGRAFIA"  # Ação sensível!
    BUSCA_CPF = "BUSCA_CPF"
    BUSCA_TELEFONE = "BUSCA_TELEFONE"


class PessoaFisicaService:
    """
    Serviço para gerenciar Pessoa Física com segurança LGPD

    Exemplo de uso:
    ```python
    service = PessoaFisicaService()

    # Criar pessoa com encriptação automática
    pessoa = await service.criar_pessoa(
        sessao_db,
        PessoaFisicaCreate(
            nome="João Silva",
            cpf="123.456.789-00",
            telefone="11987654321",
            email="joao@example.com"
        ),
        usuario_id="admin-uuid"
    )

    # Buscar por CPF (usa hash, não descriptografa)
    resultado = await service.buscar_por_cpf(sessao_db, "123.456.789-00")

    # Retorna schema seguro (CPF mascarado, sem dados sensíveis)
    print(resultado.cpf_display)  # "***.***.***-00"
    ```
    """

    def __init__(self):
        """Inicializa o serviço com o gerenciador de criptografia"""
        self.crypto = get_crypto_manager()
        self.audit_log: List[Dict[str, Any]] = []

    async def criar_pessoa(
        self,
        sessao_db: AsyncSession,
        dados: PessoaFisicaCreate,
        usuario_id: str,
        usuario_ip: str = "127.0.0.1",
    ) -> PessoaFisicaResponse:
        """
        Cria uma nova Pessoa Física com encriptação de dados sensíveis

        Processo:
        1. Valida dados de entrada (Pydantic já faz isso)
        2. Encripta CPF e gera hash para buscas
        3. Encripta Telefone e gera hash
        4. Salva no banco com dados encriptados
        5. Registra auditoria
        6. Retorna schema seguro (sem dados sensíveis)

        Args:
            sessao_db: Sessão do banco de dados (AsyncSession)
            dados: PessoaFisicaCreate com validação Pydantic
            usuario_id: ID do usuário que está criando (auditoria)
            usuario_ip: IP do usuário para auditoria

        Returns:
            PessoaFisicaResponse: Schema seguro com CPF mascarado

        Raises:
            ValueError: Se CPF ou Telefone inválidos (Pydantic valida)
            IntegrityError: Se CPF já existe (unique constraint)
        """
        try:
            # Gerar ID único
            pessoa_id = str(uuid.uuid4())

            # Encriptar e gerar hashes para dados sensíveis
            cpf_criptografado, cpf_hash = self.crypto.encrypt_and_hash(dados.cpf)

            telefone_criptografado, telefone_hash = (
                self.crypto.encrypt_and_hash(dados.telefone)
                if dados.telefone
                else (None, None)
            )

            # TODO: Implementar salvamento no banco
            # pessoa_db = await self._salvar_no_banco(
            #     sessao_db,
            #     pessoa_id=pessoa_id,
            #     nome=dados.nome,
            #     cpf_criptografado=cpf_criptografado,
            #     cpf_hash=cpf_hash,
            #     telefone_criptografado=telefone_criptografado,
            #     telefone_hash=telefone_hash,
            #     email=dados.email,
            #     data_criacao=datetime.utcnow()
            # )

            # Registrar auditoria (LGPD)
            self._registrar_auditoria(
                acao=AuditoriaAcao.CRIACAO,
                entidade_tipo="PessoaFisica",
                entidade_id=pessoa_id,
                usuario_id=usuario_id,
                usuario_ip=usuario_ip,
                descricao=f"Criação de Pessoa Física: {dados.nome}",
                dados_sensíveis={"cpf_hash": cpf_hash},
            )

            # Retornar schema seguro (CPF mascarado)
            return PessoaFisicaResponse(
                id=pessoa_id,
                nome=dados.nome,
                cpf_display=self._mascarar_cpf(dados.cpf),
                email=dados.email,
                telefone_display=(
                    self._mascarar_telefone(dados.telefone) if dados.telefone else None
                ),
                data_criacao=datetime.utcnow(),
                ativo=True,
            )

        except Exception as e:
            # Registrar erro
            self._registrar_auditoria(
                acao=AuditoriaAcao.CRIACAO,
                entidade_tipo="PessoaFisica",
                entidade_id="ERRO",
                usuario_id=usuario_id,
                usuario_ip=usuario_ip,
                descricao=f"Erro ao criar Pessoa Física: {str(e)}",
            )
            raise

    async def buscar_por_cpf(
        self,
        sessao_db: AsyncSession,
        cpf: str,
        usuario_id: Optional[str] = None,
        usuario_ip: str = "127.0.0.1",
    ) -> Optional[PessoaFisicaResponse]:
        """
        Busca Pessoa Física por CPF usando hash (não descriptografa)

        Padrão de Segurança:
        - Calcula hash do CPF buscado
        - Compara com hash armazenado no banco
        - NUNCA descriptografa (não precisa!)
        - Reduz risco de vazamento em logs

        Args:
            sessao_db: Sessão do banco de dados
            cpf: CPF a buscar (será hasheado)
            usuario_id: ID do usuário que faz a busca (auditoria)
            usuario_ip: IP do usuário

        Returns:
            PessoaFisicaResponse ou None se não encontrado
        """
        try:
            # Gerar hash do CPF para comparação
            cpf_hash = self.crypto.hash_data(cpf)

            # TODO: Implementar busca no banco por cpf_hash
            # resultado = await sessao_db.execute(
            #     select(PessoaFisica).where(
            #         PessoaFisica.cpf_hash == cpf_hash
            #     )
            # )
            # pessoa_db = resultado.scalar_one_or_none()

            # Registrar busca (auditoria)
            if usuario_id:
                self._registrar_auditoria(
                    acao=AuditoriaAcao.BUSCA_CPF,
                    entidade_tipo="PessoaFisica",
                    entidade_id="BUSCA",
                    usuario_id=usuario_id,
                    usuario_ip=usuario_ip,
                    descricao="Busca por CPF realizada",
                    dados_sensíveis={"cpf_hash_buscado": cpf_hash},
                )

            # TODO: Retornar schema seguro se encontrado
            # if pessoa_db:
            #     return PessoaFisicaResponse.from_orm(pessoa_db)

            return None

        except Exception as e:
            if usuario_id:
                self._registrar_auditoria(
                    acao=AuditoriaAcao.BUSCA_CPF,
                    entidade_tipo="PessoaFisica",
                    entidade_id="ERRO",
                    usuario_id=usuario_id,
                    usuario_ip=usuario_ip,
                    descricao=f"Erro ao buscar por CPF: {str(e)}",
                )
            raise

    async def atualizar_pessoa(
        self,
        sessao_db: AsyncSession,
        pessoa_id: str,
        dados: PessoaFisicaUpdate,
        usuario_id: str,
        usuario_ip: str = "127.0.0.1",
    ) -> PessoaFisicaResponse:
        """
        Atualiza dados de Pessoa Física com re-encriptação de sensíveis

        Args:
            sessao_db: Sessão do banco de dados
            pessoa_id: ID da pessoa a atualizar
            dados: Dados a atualizar (campos opcionais)
            usuario_id: ID do usuário (auditoria)
            usuario_ip: IP do usuário

        Returns:
            PessoaFisicaResponse atualizada
        """
        try:
            # TODO: Implementar busca da pessoa
            # pessoa_db = await sessao_db.get(PessoaFisica, pessoa_id)
            # if not pessoa_db:
            #     raise ValueError(f"Pessoa {pessoa_id} não encontrada")

            # Atualizar campos não-sensíveis normalmente
            # if dados.nome:
            #     pessoa_db.nome = dados.nome
            # if dados.email:
            #     pessoa_db.email = dados.email

            # Se atualizando CPF, re-encriptar
            # if dados.cpf:
            #     cpf_criptografado, cpf_hash = self.crypto.encrypt_and_hash(dados.cpf)
            #     pessoa_db.cpf_criptografado = cpf_criptografado
            #     pessoa_db.cpf_hash = cpf_hash

            # Se atualizando Telefone, re-encriptar
            # if dados.telefone:
            #     tel_criptografado, tel_hash = self.crypto.encrypt_and_hash(dados.telefone)
            #     pessoa_db.telefone_criptografado = tel_criptografado
            #     pessoa_db.telefone_hash = tel_hash

            # TODO: Salvar no banco
            # await sessao_db.commit()

            # Registrar auditoria
            self._registrar_auditoria(
                acao=AuditoriaAcao.ATUALIZACAO,
                entidade_tipo="PessoaFisica",
                entidade_id=pessoa_id,
                usuario_id=usuario_id,
                usuario_ip=usuario_ip,
                descricao=f"Atualização de Pessoa Física",
                dados_sensíveis={
                    "campos_atualizados": list(dados.dict(exclude_none=True).keys())
                },
            )

            # TODO: Retornar schema seguro
            # return PessoaFisicaResponse.from_orm(pessoa_db)

        except Exception as e:
            self._registrar_auditoria(
                acao=AuditoriaAcao.ATUALIZACAO,
                entidade_tipo="PessoaFisica",
                entidade_id=pessoa_id,
                usuario_id=usuario_id,
                usuario_ip=usuario_ip,
                descricao=f"Erro ao atualizar Pessoa Física: {str(e)}",
            )
            raise

    def _mascarar_cpf(self, cpf: str) -> str:
        """
        Mascara CPF para exibição segura

        Entrada: "12345678900" ou "123.456.789-00"
        Saída: "***.***.***-00" (últimos 2 dígitos visíveis)
        """
        cpf_limpo = cpf.replace(".", "").replace("-", "").replace(" ", "")
        if len(cpf_limpo) < 11:
            return "***.***.***-**"

        ultimo_2 = cpf_limpo[-2:]
        return f"***.***.***-{ultimo_2}"

    def _mascarar_telefone(self, telefone: str) -> str:
        """
        Mascara Telefone para exibição segura

        Entrada: "11987654321" ou "(11) 98765-4321"
        Saída: "(**) 9****-4321" (últimos 4 dígitos visíveis)
        """
        tel_limpo = (
            telefone.replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", "")
            .strip()
        )

        if len(tel_limpo) < 8:
            return "(**) ****-****"

        ultimos_4 = tel_limpo[-4:]
        return f"(**) ****-{ultimos_4}"

    def _registrar_auditoria(
        self,
        acao: AuditoriaAcao,
        entidade_tipo: str,
        entidade_id: str,
        usuario_id: str,
        usuario_ip: str,
        descricao: str,
        dados_sensíveis: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Registra ação para rastreabilidade LGPD

        Importante: Hashes de dados sensíveis são registrados, mas NUNCA
        os valores originais ou descriptografados.

        Args:
            acao: Tipo de ação (CRIACAO, LEITURA, ATUALIZACAO, etc)
            entidade_tipo: Tipo da entidade (PessoaFisica, PessoaJuridica, etc)
            entidade_id: ID da entidade
            usuario_id: ID do usuário que fez a ação
            usuario_ip: IP do usuário
            descricao: Descrição da ação
            dados_sensíveis: Hashes/metadados (NUNCA valores reais!)
        """
        registro = {
            "timestamp": datetime.utcnow().isoformat(),
            "acao": acao.value,
            "entidade_tipo": entidade_tipo,
            "entidade_id": entidade_id,
            "usuario_id": usuario_id,
            "usuario_ip": usuario_ip,
            "descricao": descricao,
            "dados_sensíveis": dados_sensíveis or {},
        }

        self.audit_log.append(registro)

        # TODO: Salvar em tabela de auditoria no banco
        # await salvar_auditoria(registro)

        # Em desenvolvimento, exibir no log
        if acao == AuditoriaAcao.DESCRIPTOGRAFIA:
            print(
                f"⚠️ ALERTA LGPD: {descricao} - Usuário: {usuario_id}, IP: {usuario_ip}"
            )


class PessoaJuridicaService:
    """
    Serviço para gerenciar Pessoa Jurídica com segurança LGPD

    Similar ao PessoaFisicaService mas para CNPJ
    """

    def __init__(self):
        """Inicializa o serviço com o gerenciador de criptografia"""
        self.crypto = get_crypto_manager()
        self.audit_log: List[Dict[str, Any]] = []

    # Implementação similar ao PessoaFisicaService
    # TODO: Implementar métodos para Pessoa Jurídica
    pass


# Factory para obter serviços
_pessoa_fisica_service: Optional[PessoaFisicaService] = None
_pessoa_juridica_service: Optional[PessoaJuridicaService] = None


def get_pessoa_fisica_service() -> PessoaFisicaService:
    """Retorna instância singleton do serviço de Pessoa Física"""
    global _pessoa_fisica_service
    if _pessoa_fisica_service is None:
        _pessoa_fisica_service = PessoaFisicaService()
    return _pessoa_fisica_service


def get_pessoa_juridica_service() -> PessoaJuridicaService:
    """Retorna instância singleton do serviço de Pessoa Jurídica"""
    global _pessoa_juridica_service
    if _pessoa_juridica_service is None:
        _pessoa_juridica_service = PessoaJuridicaService()
    return _pessoa_juridica_service
