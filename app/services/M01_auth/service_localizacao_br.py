"""
Service para consultar dados de localização brasileira
via API pública do IBGE (Instituto Brasileiro de Geografia e Estatística)

APIs utilizadas:
- UFs: https://servicodados.ibge.gov.br/api/v1/localidades/estados
- Municípios por UF: https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios
"""

import aiohttp
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class LocalizacaoBRService:
    """Serviço para consultar UFs e Municípios brasileiros"""

    # URLs da API IBGE (pública, sem autenticação)
    IBGE_BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"
    IBGE_UFS_URL = f"{IBGE_BASE_URL}/estados"
    IBGE_MUNICIPIOS_URL = f"{IBGE_BASE_URL}/estados/{{uf}}/municipios"

    # Cache em memória para evitar requisições repetidas
    _cache_ufs: Optional[List[Dict]] = None
    _cache_municipios: Dict[str, List[Dict]] = {}

    @classmethod
    async def obter_ufs(cls) -> List[Dict[str, str]]:
        """
        Retorna lista de UFs brasileiros ordenados por nome

        Returns:
            [
                {"sigla": "AC", "nome": "Acre"},
                {"sigla": "AL", "nome": "Alagoas"},
                ...
            ]
        """
        # Usar cache se disponível
        if cls._cache_ufs is not None:
            return cls._cache_ufs

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    cls.IBGE_UFS_URL, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        dados = await response.json()

                        # Transformar dados: API retorna com 'sigla' e 'nome'
                        ufs = [
                            {
                                "sigla": item.get("sigla", ""),
                                "nome": item.get("nome", ""),
                            }
                            for item in dados
                        ]

                        # Ordenar por sigla
                        ufs.sort(key=lambda x: x["sigla"])

                        # Armazenar em cache
                        cls._cache_ufs = ufs

                        logger.info(f"✅ Carregados {len(ufs)} UFs do IBGE")
                        return ufs
                    else:
                        logger.error(f"❌ Erro ao consultar IBGE: {response.status}")
                        return cls._get_ufs_fallback()

        except Exception as e:
            logger.error(f"❌ Erro ao conectar IBGE: {str(e)}")
            # Retornar lista hardcoded como fallback
            return cls._get_ufs_fallback()

    @classmethod
    async def obter_municipios(cls, uf: str) -> List[Dict[str, str]]:
        """
        Retorna lista de municípios de um UF

        Args:
            uf: Sigla do UF (ex: "SP", "RJ")

        Returns:
            [
                {"id": 3509007, "nome": "Abadia de Goiás"},
                {"id": 3509056, "nome": "Abadiânia"},
                ...
            ]
        """
        # Validar UF
        uf = uf.upper().strip()
        if len(uf) != 2:
            return []

        # Usar cache se disponível
        if uf in cls._cache_municipios:
            return cls._cache_municipios[uf]

        try:
            url = cls.IBGE_MUNICIPIOS_URL.format(uf=uf)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        dados = await response.json()

                        # Transformar dados: API retorna com 'id' e 'nome'
                        municipios = [
                            {
                                "id": item.get("id", ""),
                                "nome": item.get("nome", ""),
                            }
                            for item in dados
                        ]

                        # Ordenar por nome
                        municipios.sort(key=lambda x: x["nome"])

                        # Armazenar em cache
                        cls._cache_municipios[uf] = municipios

                        logger.info(
                            f"✅ Carregados {len(municipios)} municípios de {uf}"
                        )
                        return municipios
                    else:
                        logger.error(
                            f"❌ Erro ao consultar IBGE para {uf}: {response.status}"
                        )
                        return []

        except Exception as e:
            logger.error(f"❌ Erro ao conectar IBGE: {str(e)}")
            return []

    @staticmethod
    def _get_ufs_fallback() -> List[Dict[str, str]]:
        """Lista hardcoded de UFs como fallback"""
        return [
            {"sigla": "AC", "nome": "Acre"},
            {"sigla": "AL", "nome": "Alagoas"},
            {"sigla": "AP", "nome": "Amapá"},
            {"sigla": "AM", "nome": "Amazonas"},
            {"sigla": "BA", "nome": "Bahia"},
            {"sigla": "CE", "nome": "Ceará"},
            {"sigla": "DF", "nome": "Distrito Federal"},
            {"sigla": "ES", "nome": "Espírito Santo"},
            {"sigla": "GO", "nome": "Goiás"},
            {"sigla": "MA", "nome": "Maranhão"},
            {"sigla": "MT", "nome": "Mato Grosso"},
            {"sigla": "MS", "nome": "Mato Grosso do Sul"},
            {"sigla": "MG", "nome": "Minas Gerais"},
            {"sigla": "PA", "nome": "Pará"},
            {"sigla": "PB", "nome": "Paraíba"},
            {"sigla": "PR", "nome": "Paraná"},
            {"sigla": "PE", "nome": "Pernambuco"},
            {"sigla": "PI", "nome": "Piauí"},
            {"sigla": "RJ", "nome": "Rio de Janeiro"},
            {"sigla": "RN", "nome": "Rio Grande do Norte"},
            {"sigla": "RS", "nome": "Rio Grande do Sul"},
            {"sigla": "RO", "nome": "Rondônia"},
            {"sigla": "RR", "nome": "Roraima"},
            {"sigla": "SC", "nome": "Santa Catarina"},
            {"sigla": "SP", "nome": "São Paulo"},
            {"sigla": "SE", "nome": "Sergipe"},
            {"sigla": "TO", "nome": "Tocantins"},
        ]
