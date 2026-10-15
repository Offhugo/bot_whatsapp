"""
Formatador para respostas de Abastecimento.
"""

from typing import Any, Dict
from app.formatters.base_formatter import BaseFormatter


class AbastecimentoFormatter(BaseFormatter):
    """Formata respostas de consultas de abastecimento."""

    def format(self, data: Dict[str, Any]) -> str:
        """
        Formata dados de abastecimento.

        Campos esperados:
        - valor_total: float
        - periodo: str
        - registros: list (com data, valor, combustivel, litros)
        - media_valor: float (opcional)

        Args:
            data: Dados de abastecimento

        Returns:
            String formatada
        """
        self._validar_dados(
            data,
            ["valor_total", "periodo", "registros"]
        )

        valor_total = data["valor_total"]
        periodo = data["periodo"]
        registros = data["registros"]
        media_valor = data.get("media_valor", 0)
        total_litros = data.get("total_litros", 0)

        resposta = (
            f"⛽ **Relatório de Abastecimento**\n"
            f"📅 Período: {periodo}\n\n"
            f"💰 **Total gasto: R$ {self._formatar_numero(valor_total, 2, '')}**\n"
        )

        if len(registros) > 0:
            media_valor = valor_total / len(registros)
            resposta += f"📊 Média por abastecimento: R$ {self._formatar_numero(media_valor, 2, '')}\n"

        if total_litros > 0:
            resposta += f"🛢️ Total de litros: {self._formatar_numero(total_litros, 1, 'L')}\n"
            media_preco = valor_total / total_litros if total_litros > 0 else 0
            resposta += f"💵 Preço médio por litro: R$ {self._formatar_numero(media_preco, 2, '')}\n"

        resposta += f"⏱️ Número de abastecimentos: {len(registros)}"

        # Adicionar últimos abastecimentos
        if registros:
            resposta += "\n\n📋 **Últimos abastecimentos:**\n"

            ultimos = registros[-5:] if len(registros) > 5 else registros

            for registro in ultimos:
                resposta += self._formatar_abastecimento(registro)

            if len(registros) > 5:
                resposta += f"\n... e mais {len(registros) - 5} abastecimentos"

        return resposta

    def _formatar_abastecimento(self, registro: Dict[str, Any]) -> str:
        """Formata um abastecimento individual."""
        data_str = self._formatar_data(registro.get("data", ""), "dd/mm")
        valor = registro.get("valor", 0)
        combustivel = registro.get("combustivel", "?")
        litros = registro.get("litros", 0)

        linha = f"• {data_str} - R$ {self._formatar_numero(valor, 2, '')}"

        if combustivel:
            linha += f" ({combustivel}"
            if litros > 0:
                linha += f", {self._formatar_numero(litros, 1, 'L')}"
            linha += ")"

        linha += "\n"

        return linha
