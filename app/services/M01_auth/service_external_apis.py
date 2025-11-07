"""
Serviço para integração com APIs externas de CPF e CEP.
Responsável por validar CPF e buscar dados de endereço.
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any
import re

logger = logging.getLogger(__name__)


class CPFService:
    """Serviço para validação e consulta de CPF"""

    @staticmethod
    def validar_cpf_formato(cpf: str) -> bool:
        """Valida o formato básico do CPF"""
        # Remove caracteres não numéricos
        cpf_limpo = re.sub(r"\D", "", cpf)

        # Verifica se tem 11 dígitos
        if len(cpf_limpo) != 11:
            return False

        # Verifica se todos os dígitos são iguais
        if cpf_limpo == cpf_limpo[0] * 11:
            return False

        # Validação do primeiro dígito verificador
        soma = sum(int(d) * (10 - i) for i, d in enumerate(cpf_limpo[:9]))
        primeiro_verificador = 11 - (soma % 11)
        if primeiro_verificador >= 10:
            primeiro_verificador = 0

        if int(cpf_limpo[9]) != primeiro_verificador:
            return False

        # Validação do segundo dígito verificador
        soma = sum(int(d) * (11 - i) for i, d in enumerate(cpf_limpo[:10]))
        segundo_verificador = 11 - (soma % 11)
        if segundo_verificador >= 10:
            segundo_verificador = 0

        if int(cpf_limpo[10]) != segundo_verificador:
            return False

        return True

    @staticmethod
    async def consultar_cpf(cpf: str) -> Optional[Dict[str, Any]]:
        """
        Consulta dados de CPF usando API pública.
        Retorna dados básicos como nome, data de nascimento, etc.

        APIs disponíveis (free tier):
        - https://www.receitafederal.gov.br/ (oficial, mas restrições)
        - https://api.carroapi.com.br/cpf (necessita documentação)
        """
        try:
            cpf_limpo = re.sub(r"\D", "", cpf)

            if not CPFService.validar_cpf_formato(cpf_limpo):
                logger.warning(f"CPF inválido: {cpf}")
                return {"valido": False, "mensagem": "CPF inválido"}

            # Aqui você pode integrar com uma API real de CPF
            # Exemplo: https://api.carroapi.com.br/cpf/{cpf}
            # Por enquanto, retornamos apenas validação básica

            logger.info(f"CPF validado com sucesso: {cpf_limpo}")
            return {"valido": True, "cpf": cpf_limpo, "mensagem": "CPF válido"}

        except Exception as e:
            logger.error(f"Erro ao consultar CPF: {str(e)}")
            return None


class CEPService:
    """Serviço para consulta de CEP e dados de endereço"""

    # API ViaCEP - gratuita e confiável
    VIACEP_BASE_URL = "https://viacep.com.br/ws"

    @staticmethod
    def validar_cep_formato(cep: str) -> bool:
        """Valida o formato básico do CEP"""
        cep_limpo = re.sub(r"\D", "", cep)
        return len(cep_limpo) == 8

    @staticmethod
    async def consultar_cep(cep: str) -> Optional[Dict[str, Any]]:
        """
        Consulta dados de endereço pelo CEP usando a API ViaCEP.

        Retorna:
        {
            "cep": "01310100",
            "logradouro": "Avenida Paulista",
            "bairro": "Bela Vista",
            "localidade": "São Paulo",
            "uf": "SP",
            "complemento": "lado par",
            "erro": False
        }
        """
        try:
            cep_limpo = re.sub(r"\D", "", cep)

            if not CEPService.validar_cep_formato(cep):
                logger.warning(f"CEP inválido: {cep}")
                return {"erro": True, "mensagem": "CEP inválido"}

            url = f"{CEPService.VIACEP_BASE_URL}/{cep_limpo}/json/"

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        if data.get("erro"):
                            logger.warning(f"CEP não encontrado: {cep_limpo}")
                            return {"erro": True, "mensagem": "CEP não encontrado"}

                        logger.info(f"CEP consultado com sucesso: {cep_limpo}")
                        return data
                    else:
                        logger.error(f"Erro na API ViaCEP: {response.status}")
                        return {
                            "erro": True,
                            "mensagem": f"Erro na consulta: {response.status}",
                        }

        except asyncio.TimeoutError:
            logger.error(f"Timeout ao consultar CEP: {cep}")
            return {"erro": True, "mensagem": "Timeout na consulta"}
        except Exception as e:
            logger.error(f"Erro ao consultar CEP: {str(e)}")
            return {"erro": True, "mensagem": f"Erro: {str(e)}"}


class AddressService:
    """Serviço consolidado para operações de endereço"""

    @staticmethod
    async def validar_e_consultar_endereco(
        cep: str, endereco_manual: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Valida e consulta endereço pelo CEP.
        Se não encontrar, permite entrada manual.
        """
        resultado = await CEPService.consultar_cep(cep)

        if resultado and not resultado.get("erro"):
            return {"sucesso": True, "origem": "cep", "dados": resultado}
        else:
            return {
                "sucesso": False,
                "origem": "manual",
                "mensagem": (
                    resultado.get("mensagem") if resultado else "Erro desconhecido"
                ),
            }


class CNPJService:
    """Serviço para validação de CNPJ"""

    @staticmethod
    def validar_cnpj_formato(cnpj: str) -> bool:
        """Valida o formato básico do CNPJ"""
        # Remove caracteres não numéricos
        cnpj_limpo = re.sub(r"\D", "", cnpj)

        # Verifica se tem 14 dígitos
        if len(cnpj_limpo) != 14:
            return False

        # Verifica se todos os dígitos são iguais
        if cnpj_limpo == cnpj_limpo[0] * 14:
            return False

        # Validação do primeiro dígito verificador
        soma = sum(int(d) * (5 - i % 8) for i, d in enumerate(cnpj_limpo[:8]))
        soma += sum(int(d) * (10 - i % 8) for i, d in enumerate(cnpj_limpo[8:12]))
        primeiro_verificador = 11 - (soma % 11)
        if primeiro_verificador >= 10:
            primeiro_verificador = 0

        if int(cnpj_limpo[12]) != primeiro_verificador:
            return False

        # Validação do segundo dígito verificador
        soma = sum(int(d) * (6 - i % 8) for i, d in enumerate(cnpj_limpo[:9]))
        soma += sum(int(d) * (10 - i % 8) for i, d in enumerate(cnpj_limpo[9:13]))
        segundo_verificador = 11 - (soma % 11)
        if segundo_verificador >= 10:
            segundo_verificador = 0

        if int(cnpj_limpo[13]) != segundo_verificador:
            return False

        return True

    @staticmethod
    async def consultar_cnpj(cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Consulta dados de CNPJ usando a API ReceitaWS.

        Retorna:
        {
            "valido": true,
            "cnpj": "11222333000181",
            "nome": "Empresa LTDA",
            "logradouro": "Rua Tal",
            "numero": "123",
            "complemento": "Sala 10",
            "bairro": "Centro",
            "municipio": "São Paulo",
            "uf": "SP",
            "cep": "01310100",
            "telefone": "1133334444",
            "email": "contato@empresa.com.br",
            "atividade_principal": "Atividade Econômica"
        }
        """
        try:
            cnpj_limpo = re.sub(r"\D", "", cnpj)

            if not CNPJService.validar_cnpj_formato(cnpj_limpo):
                logger.warning(f"CNPJ inválido: {cnpj}")
                return {
                    "valido": False,
                    "mensagem": "CNPJ inválido",
                }

            # Usar API ReceitaWS (gratuita e sem autenticação)
            url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj_limpo}"

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        if data.get("status") == "ERROR":
                            logger.warning(f"CNPJ não encontrado na RF: {cnpj_limpo}")
                            return {
                                "valido": True,
                                "cnpj": cnpj_limpo,
                                "mensagem": "Formato válido, mas não encontrado. Preencha os dados manualmente.",
                            }

                        logger.info(f"CNPJ consultado com sucesso: {cnpj_limpo}")
                        return {
                            "valido": True,
                            "cnpj": cnpj_limpo,
                            "nome": data.get("nome", ""),
                            "nome_fantasia": data.get("fantasia", ""),
                            "logradouro": data.get("logradouro", ""),
                            "numero": data.get("numero", ""),
                            "complemento": data.get("complemento", ""),
                            "bairro": data.get("bairro", ""),
                            "municipio": data.get("municipio", ""),
                            "uf": data.get("uf", ""),
                            "cep": data.get("cep", ""),
                            "telefone": data.get("telefone", ""),
                            "email": data.get("email", ""),
                            "mensagem": "Dados carregados com sucesso",
                        }
                    else:
                        logger.error(f"Erro na API ReceitaWS: {response.status}")
                        return {
                            "valido": True,
                            "cnpj": cnpj_limpo,
                            "mensagem": "Não foi possível consultar dados. Preencha manualmente.",
                        }

        except asyncio.TimeoutError:
            logger.error(f"Timeout ao consultar CNPJ: {cnpj}")
            return {
                "valido": True,
                "cnpj": cnpj_limpo,
                "mensagem": "Timeout na consulta. Tente novamente.",
            }
        except Exception as e:
            logger.error(f"Erro ao consultar CNPJ: {str(e)}")
            return {
                "valido": True,
                "cnpj": cnpj_limpo,
                "mensagem": f"Erro na consulta: {str(e)}",
            }
