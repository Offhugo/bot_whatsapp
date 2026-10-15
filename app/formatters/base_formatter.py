"""
Classe base para formatadores de resposta.

Formatadores transformam dados técnicos (JSON) em respostas
legíveis para o usuário em português.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseFormatter(ABC):
    """
    Classe abstrata para formatadores.

    Cada tipo de consulta (KM, Viagem, Abastecimento) tem seu próprio
    formatador que converte dados brutos em respostas amigáveis.
    """

    @abstractmethod
    def format(self, data: Dict[str, Any]) -> str:
        """
        Formata dados em uma resposta legível.

        Args:
            data: Dicionário com dados a formatar

        Returns:
            String formatada em português

        Raises:
            ValueError: Se dados estão inválidos
        """
        pass

    def _validar_dados(self, data: Dict[str, Any], campos_obrigatorios: list) -> None:
        """
        Valida se os dados têm os campos obrigatórios.

        Args:
            data: Dados a validar
            campos_obrigatorios: Lista de campos que devem existir

        Raises:
            ValueError: Se falta algum campo obrigatório
        """
        if not isinstance(data, dict):
            raise ValueError("Dados devem ser um dicionário")

        faltantes = [c for c in campos_obrigatorios if c not in data]
        if faltantes:
            raise ValueError(f"Campos obrigatórios faltando: {', '.join(faltantes)}")

    def _formatar_numero(self, valor: float, casas: int = 1, unidade: str = "") -> str:
        """
        Formata um número em padrão brasileiro.

        Args:
            valor: Número a formatar
            casas: Casas decimais
            unidade: Unidade (ex: "km", "R$")

        Returns:
            String formatada (ex: "1.250,5 km")
        """
        if valor is None:
            return "—"

        # Formatar com casas decimais
        formatado = f"{valor:.{casas}f}".replace(".", ",")

        # Adicionar separadores de milhar
        partes = formatado.split(",")
        inteira = partes[0]
        decimal = partes[1] if len(partes) > 1 else ""

        # Adicionar pontos a cada 3 dígitos
        inteira_formatada = ""
        for i, digito in enumerate(reversed(inteira)):
            if i > 0 and i % 3 == 0:
                inteira_formatada = "." + inteira_formatada
            inteira_formatada = digito + inteira_formatada

        resultado = inteira_formatada
        if decimal:
            resultado += "," + decimal

        if unidade:
            resultado += f" {unidade}"

        return resultado

    def _formatar_data(self, data_str: str, formato: str = "dd/mm") -> str:
        """
        Formata uma data.

        Args:
            data_str: Data como string (ex: "2026-10-13")
            formato: Formato desejado ("dd/mm", "dd/mm/yyyy", "full")

        Returns:
            Data formatada
        """
        if not data_str:
            return "—"

        try:
            # Espera formato ISO: 2026-10-13
            partes = data_str.split("T")[0].split("-")
            if len(partes) != 3:
                return data_str

            ano, mes, dia = partes

            meses = {
                "01": "janeiro", "02": "fevereiro", "03": "março",
                "04": "abril", "05": "maio", "06": "junho",
                "07": "julho", "08": "agosto", "09": "setembro",
                "10": "outubro", "11": "novembro", "12": "dezembro"
            }

            if formato == "dd/mm":
                return f"{dia}/{mes}"
            elif formato == "dd/mm/yyyy":
                return f"{dia}/{mes}/{ano}"
            elif formato == "full":
                mes_nome = meses.get(mes, mes)
                return f"{dia} de {mes_nome} de {ano}"
            else:
                return data_str
        except Exception:
            return data_str

    def _calcular_media(self, total: float, quantidade: int) -> float:
        """
        Calcula média de forma segura.

        Args:
            total: Valor total
            quantidade: Quantidade de itens

        Returns:
            Média ou 0 se quantidade for 0
        """
        if quantidade == 0:
            return 0.0
        return total / quantidade

    def _calcular_percentual_variacao(self, anterior: float, atual: float) -> float:
        """
        Calcula percentual de variação.

        Args:
            anterior: Valor anterior
            atual: Valor atual

        Returns:
            Percentual de variação (pode ser negativo)
        """
        if anterior == 0:
            return 0.0
        return ((atual - anterior) / anterior) * 100
