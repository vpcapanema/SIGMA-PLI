"""
SIGMA-PLI - Validadores de Dados Sensíveis
Validação de CPF, CNPJ e Telefone
"""

import re
from typing import Optional


def validar_cpf(cpf: str) -> bool:
    """
    Valida CPF usando algoritmo Módulo 11.

    Args:
        cpf: String de 11 dígitos ou formatada (XXX.XXX.XXX-XX)

    Returns:
        True se CPF válido, False caso contrário
    """
    # Remover formatação
    cpf = re.sub(r"\D", "", cpf)

    # Validações básicas
    if len(cpf) != 11:
        return False

    if not cpf.isdigit():
        return False

    # CPFs conhecidos como inválidos
    cpfs_invalidos = [
        "00000000000",
        "11111111111",
        "22222222222",
        "33333333333",
        "44444444444",
        "55555555555",
        "66666666666",
        "77777777777",
        "88888888888",
        "99999999999",
    ]

    if cpf in cpfs_invalidos:
        return False

    # Validar primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    dv1 = 0 if resto < 2 else 11 - resto

    if int(cpf[9]) != dv1:
        return False

    # Validar segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    dv2 = 0 if resto < 2 else 11 - resto

    if int(cpf[10]) != dv2:
        return False

    return True


def validar_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ usando algoritmo Módulo 11.

    Args:
        cnpj: String de 14 dígitos ou formatada (XX.XXX.XXX/XXXX-XX)

    Returns:
        True se CNPJ válido, False caso contrário
    """
    # Remover formatação
    cnpj = re.sub(r"\D", "", cnpj)

    # Validações básicas
    if len(cnpj) != 14:
        return False

    if not cnpj.isdigit():
        return False

    # CNPJs conhecidos como inválidos
    cnpjs_invalidos = [
        "00000000000000",
        "11111111111111",
        "22222222222222",
        "33333333333333",
        "44444444444444",
        "55555555555555",
        "66666666666666",
        "77777777777777",
        "88888888888888",
        "99999999999999",
    ]

    if cnpj in cnpjs_invalidos:
        return False

    # Validar primeiro dígito verificador
    multiplicador = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * multiplicador[i] for i in range(12))
    resto = soma % 11
    dv1 = 0 if resto < 2 else 11 - resto

    if int(cnpj[12]) != dv1:
        return False

    # Validar segundo dígito verificador
    multiplicador = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3]
    soma = sum(int(cnpj[i]) * multiplicador[i] for i in range(12))
    resto = (soma + dv1 * 2) % 11
    dv2 = 0 if resto < 2 else 11 - resto

    if int(cnpj[13]) != dv2:
        return False

    return True


def validar_telefone(telefone: str) -> bool:
    """
    Valida número de telefone (10 ou 11 dígitos).

    Args:
        telefone: String com 10-11 dígitos ou formatada

    Returns:
        True se telefone válido, False caso contrário
    """
    # Remover formatação
    telefone = re.sub(r"\D", "", telefone)

    # Deve ter 10 ou 11 dígitos
    if len(telefone) not in [10, 11]:
        return False

    # Todos zeros é inválido
    if telefone == "0" * len(telefone):
        return False

    # DDD válido (11-99)
    ddd = int(telefone[:2])
    if not (11 <= ddd <= 99):
        return False

    return True


def limpar_cpf(cpf: str) -> str:
    """Remove formatação do CPF"""
    return re.sub(r"\D", "", cpf)


def limpar_cnpj(cnpj: str) -> str:
    """Remove formatação do CNPJ"""
    return re.sub(r"\D", "", cnpj)


def limpar_telefone(telefone: str) -> str:
    """Remove formatação do telefone"""
    return re.sub(r"\D", "", telefone)


def formatar_cpf(cpf: str) -> str:
    """Formata CPF como XXX.XXX.XXX-XX"""
    cpf = limpar_cpf(cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"
    return cpf


def formatar_cnpj(cnpj: str) -> str:
    """Formata CNPJ como XX.XXX.XXX/XXXX-XX"""
    cnpj = limpar_cnpj(cnpj)
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"
    return cnpj


def formatar_telefone(telefone: str) -> str:
    """Formata telefone como (XX) 9XXXX-XXXX ou (XX) XXXX-XXXX"""
    telefone = limpar_telefone(telefone)
    if len(telefone) == 11:
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:11]}"
    elif len(telefone) == 10:
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:10]}"
    return telefone
