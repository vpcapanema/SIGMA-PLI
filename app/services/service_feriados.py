"""
SIGMA-PLI - Serviço de Feriados
Feriados Nacionais, Estaduais (SP) e Municipais (São Paulo)
"""

from datetime import date, datetime
from typing import List, Dict, Optional
from dateutil.easter import easter


class FeriadoService:
    """Serviço para gerenciar feriados nacionais, estaduais e municipais"""

    @staticmethod
    def calcular_feriados_moveis(ano: int) -> Dict[str, date]:
        """Calcula feriados móveis baseados na Páscoa"""
        pascoa = easter(ano)

        return {
            "carnaval": date(pascoa.year, pascoa.month, pascoa.day - 47),
            "sexta_feira_santa": date(pascoa.year, pascoa.month, pascoa.day - 2),
            "pascoa": pascoa,
            "corpus_christi": date(pascoa.year, pascoa.month, pascoa.day + 60),
        }

    @classmethod
    def obter_feriados_nacionais(cls, ano: int) -> List[Dict]:
        """Retorna lista de feriados nacionais"""
        moveis = cls.calcular_feriados_moveis(ano)

        feriados = [
            {
                "data": date(ano, 1, 1),
                "nome": "Confraternização Universal",
                "tipo": "nacional",
                "tipo_feriado": "fixo",
            },
            {
                "data": moveis["carnaval"],
                "nome": "Carnaval",
                "tipo": "nacional",
                "tipo_feriado": "movel",
            },
            {
                "data": moveis["sexta_feira_santa"],
                "nome": "Sexta-feira Santa",
                "tipo": "nacional",
                "tipo_feriado": "movel",
            },
            {
                "data": date(ano, 4, 21),
                "nome": "Tiradentes",
                "tipo": "nacional",
                "tipo_feriado": "fixo",
            },
            {
                "data": date(ano, 5, 1),
                "nome": "Dia do Trabalho",
                "tipo": "nacional",
                "tipo_feriado": "fixo",
            },
            {
                "data": moveis["corpus_christi"],
                "nome": "Corpus Christi",
                "tipo": "nacional",
                "tipo_feriado": "movel",
            },
            {
                "data": date(ano, 9, 7),
                "nome": "Independência do Brasil",
                "tipo": "nacional",
                "tipo_feriado": "fixo",
            },
            {
                "data": date(ano, 10, 12),
                "nome": "Nossa Senhora Aparecida",
                "tipo": "nacional",
                "tipo_feriado": "fixo",
            },
            {
                "data": date(ano, 11, 2),
                "nome": "Finados",
                "tipo": "nacional",
                "tipo_feriado": "fixo",
            },
            {
                "data": date(ano, 11, 15),
                "nome": "Proclamação da República",
                "tipo": "nacional",
                "tipo_feriado": "fixo",
            },
            {
                "data": date(ano, 11, 20),
                "nome": "Dia da Consciência Negra",
                "tipo": "nacional",
                "tipo_feriado": "fixo",
            },
            {
                "data": date(ano, 12, 25),
                "nome": "Natal",
                "tipo": "nacional",
                "tipo_feriado": "fixo",
            },
        ]

        return feriados

    @classmethod
    def obter_feriados_estaduais_sp(cls, ano: int) -> List[Dict]:
        """Retorna lista de feriados estaduais de São Paulo"""
        return [
            {
                "data": date(ano, 7, 9),
                "nome": "Revolução Constitucionalista de 1932",
                "tipo": "estadual_sp",
                "tipo_feriado": "fixo",
            },
        ]

    @classmethod
    def obter_feriados_municipais_sp(cls, ano: int) -> List[Dict]:
        """Retorna lista de feriados municipais da cidade de São Paulo"""
        return [
            {
                "data": date(ano, 1, 25),
                "nome": "Aniversário de São Paulo",
                "tipo": "municipal_sp",
                "tipo_feriado": "fixo",
            },
        ]

    @classmethod
    def obter_todos_feriados(cls, ano: int) -> List[Dict]:
        """Retorna todos os feriados (nacionais, estaduais e municipais)"""
        feriados = []
        feriados.extend(cls.obter_feriados_nacionais(ano))
        feriados.extend(cls.obter_feriados_estaduais_sp(ano))
        feriados.extend(cls.obter_feriados_municipais_sp(ano))

        # Ordena por data
        feriados.sort(key=lambda x: x["data"])

        return feriados

    @classmethod
    def obter_feriados_mes(cls, ano: int, mes: int) -> List[Dict]:
        """Retorna feriados de um mês específico"""
        todos_feriados = cls.obter_todos_feriados(ano)
        return [f for f in todos_feriados if f["data"].month == mes]

    @classmethod
    def eh_feriado(cls, data: date) -> Optional[Dict]:
        """Verifica se uma data é feriado e retorna suas informações"""
        feriados = cls.obter_todos_feriados(data.year)
        for feriado in feriados:
            if feriado["data"] == data:
                return feriado
        return None

    @classmethod
    def obter_proximo_feriado(
        cls, data_referencia: Optional[date] = None
    ) -> Optional[Dict]:
        """Retorna o próximo feriado a partir de uma data"""
        if data_referencia is None:
            data_referencia = date.today()

        feriados = cls.obter_todos_feriados(data_referencia.year)

        # Adiciona feriados do próximo ano se necessário
        if data_referencia.month >= 11:
            feriados.extend(cls.obter_todos_feriados(data_referencia.year + 1))

        for feriado in feriados:
            if feriado["data"] > data_referencia:
                return feriado

        return None

    @classmethod
    def contar_feriados_mes(cls, ano: int, mes: int) -> int:
        """Conta quantos feriados há em um mês"""
        return len(cls.obter_feriados_mes(ano, mes))

    @classmethod
    def obter_feriados_intervalo(cls, data_inicio: date, data_fim: date) -> List[Dict]:
        """Retorna feriados em um intervalo de datas"""
        feriados = []

        for ano in range(data_inicio.year, data_fim.year + 1):
            feriados.extend(cls.obter_todos_feriados(ano))

        # Filtra apenas os feriados dentro do intervalo
        return [f for f in feriados if data_inicio <= f["data"] <= data_fim]
