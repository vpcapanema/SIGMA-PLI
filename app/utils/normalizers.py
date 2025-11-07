"""
Utilitários de normalização de payloads vindos das páginas (frontend)
para os nomes de campos esperados pelas tabelas do banco.

Regras aplicadas por página/módulo:
- Pessoa Física (cadastro.pessoa)
- Instituição (cadastro.instituicao)
- Usuário (usuarios.usuario)
"""

from __future__ import annotations

from typing import Any, Dict


def normalize_pessoa_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza payload da página de Pessoa Física para colunas de cadastro.pessoa.

    Entrada (possíveis aliases vindos do front):
    - telefone_principal/telefone_secundario -> telefone
    - profissao/ocupacao -> cargo
    - email/email_principal -> email
    - cpf/cpf_pessoa -> cpf

    Saída (modelo esperado pela tabela cadastro.pessoa):
    - nome_completo, cpf, email, telefone, cargo, instituicao_id, departamento_id
    """
    nome_completo = data.get("nome_completo") or data.get("nome")
    cpf = data.get("cpf") or data.get("cpf_pessoa") or ""
    email = data.get("email") or data.get("email_principal") or ""
    telefone = (
        data.get("telefone")
        or data.get("telefone_principal")
        or data.get("telefone_secundario")
    )
    cargo = data.get("cargo") or data.get("profissao") or data.get("ocupacao")

    normalized = {
        "nome_completo": nome_completo,
        "cpf": cpf,
        "email": email,
        "telefone": telefone,
        "cargo": cargo,
        # opcionais/relacionais (mantidos se presentes)
        "instituicao_id": data.get("instituicao_id"),
        "departamento_id": data.get("departamento_id"),
    }
    return normalized


def normalize_instituicao_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza payload da página de Instituição para colunas de cadastro.instituicao.

    Mapeia variações camelCase -> snake_case, quando necessário.
    """
    normalized = {
        "razao_social": data.get("razao_social") or data.get("razaoSocial"),
        "nome_fantasia": data.get("nome_fantasia") or data.get("nomeFantasia"),
        "cnpj": data.get("cnpj"),
        "email": data.get("email"),
        "telefone": data.get("telefone"),
        "telefone_secundario": data.get("telefone_secundario")
        or data.get("telefoneSecundario"),
        "inscricao_estadual": data.get("inscricao_estadual")
        or data.get("inscricaoEstadual"),
        "inscricao_municipal": data.get("inscricao_municipal")
        or data.get("inscricaoMunicipal"),
        "data_fundacao": data.get("data_fundacao") or data.get("dataFundacao"),
        "porte_empresa": data.get("porte_empresa") or data.get("porteEmpresa"),
        "natureza_juridica": data.get("natureza_juridica")
        or data.get("naturezaJuridica"),
        "atividade_principal": data.get("atividade_principal")
        or data.get("atividadePrincipal"),
        "site": data.get("site"),
        # endereço
        "cep": data.get("cep"),
        "logradouro": data.get("logradouro"),
        "numero": data.get("numero"),
        "complemento": data.get("complemento"),
        "bairro": data.get("bairro"),
        "cidade": data.get("cidade"),
        "uf": data.get("uf"),
        "pais": data.get("pais"),
        # classificações opcionais
        "tipo_instituicao": data.get("tipo_instituicao"),
        "esfera_administrativa": data.get("esfera_administrativa"),
    }
    return normalized


def normalize_usuario_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza payload da página de Cadastro de Usuário para colunas de usuarios.usuario.

    Aliases suportados:
    - pessoa_id | pessoa_fisica_id -> pessoa_id
    - password | senha -> senha
    - email | email_institucional -> email_institucional
    - tipo_usuario em qualquer case -> UPPERCASE
    """
    pessoa_id = data.get("pessoa_id") or data.get("pessoa_fisica_id")
    instituicao_id = data.get("instituicao_id")
    username = data.get("username")
    email_institucional = data.get("email_institucional") or data.get("email")
    senha = data.get("senha") or data.get("password")
    telefone_institucional = data.get("telefone_institucional")
    tipo_usuario = (data.get("tipo_usuario") or "").upper()

    normalized = {
        "pessoa_id": pessoa_id,
        "instituicao_id": instituicao_id,
        "username": username,
        "email_institucional": email_institucional,
        "senha": senha,
        "telefone_institucional": telefone_institucional,
        "tipo_usuario": tipo_usuario,
        "termo_privacidade": bool(data.get("termo_privacidade", False)),
        "termo_uso": bool(data.get("termo_uso", False)),
    }
    return normalized
