"""
Formatador para respostas de ConsultarKM.

Transforma dados técnicos de quilometragem em respostas
legíveis e informativas para o usuário.
"""

from typing import Any, Dict, List
from app.formatters.base_formatter import BaseFormatter


class KMFormatter(BaseFormatter):
    """Formata respostas de consultas de quilometragem."""

    def format(self, data: Dict[str, Any]) -> str:
        """
        Formata dados de KM em resposta legível.

        Campos esperados:
        - km_total: float (quilometros totais)
        - periodo: str (período de consulta)
        - registros: list (registros de KM por data)
        - media_diaria: float (opcional)
        - dias_com_registro: int (opcional)

        Args:
            data: Dados de quilometragem

        Returns:
            String formatada em português
        """
        # Validar campos obrigatórios
        self._validar_dados(
            data,
            ["km_total", "periodo", "registros"]
        )

        km_total = data["km_total"]
        periodo = data["periodo"]
        registros = data["registros"]
        media_diaria = data.get("media_diaria", 0)
        dias_com_registro = data.get("dias_com_registro", len(registros))

        # Calcular variação se houver dado anterior
        km_anterior = data.get("km_anterior")
        variacao = ""
        if km_anterior is not None and km_anterior > 0:
            percentual = self._calcular_percentual_variacao(km_anterior, km_total)
            seta = "📈" if percentual >= 0 else "📉"
            variacao = f"\n{seta} Variação: {abs(percentual):.1f}% {'acima' if percentual >= 0 else 'abaixo'}"

        # Montar resposta
        resposta = (
            f"📊 **Relatório de Quilometragem**\n"
            f"📅 Período: {periodo}\n"
            f"\n"
            f"🚗 **Total: {self._formatar_numero(km_total, 1, 'km')}**\n"
        )

        if media_diaria > 0:
            resposta += f"📈 Média diária: {self._formatar_numero(media_diaria, 1, 'km')}\n"

        resposta += f"📍 Dias com registro: {dias_com_registro}"
        resposta += variacao

        # Adicionar últimos registros
        if registros:
            resposta += "\n\n📋 **Últimos registros:**\n"

            # Mostrar até 5 últimos registros
            ultimos = registros[-5:] if len(registros) > 5 else registros

            for registro in ultimos:
                data_str = self._formatar_data(registro.get("data", ""), "dd/mm")
                km = registro.get("quilometros", 0)
                resposta += f"• {data_str}: {self._formatar_numero(km, 1, 'km')}\n"

            if len(registros) > 5:
                resposta += f"\n... e mais {len(registros) - 5} registros"

        return resposta


class KMPorViagemFormatter(BaseFormatter):
    """Formata respostas de KM agrupados por viagem."""

    def format(self, data: Dict[str, Any]) -> str:
        """
        Formata dados de KM por viagem.

        Campos esperados:
        - km_total: float
        - viagens: list[{origem, destino, km, data}]

        Args:
            data: Dados de quilometragem por viagem

        Returns:
            String formatada
        """
        self._validar_dados(
            data,
            ["km_total", "viagens"]
        )

        km_total = data["km_total"]
        viagens = data["viagens"]

        resposta = (
            f"📊 **KM por Viagem**\n"
            f"🚗 Total: {self._formatar_numero(km_total, 1, 'km')}\n"
            f"✈️ Número de viagens: {len(viagens)}\n\n"
            f"📋 **Detalhes:**\n"
        )

        for viagem in viagens:
            data_str = self._formatar_data(viagem.get("data", ""), "dd/mm")
            origem = viagem.get("origem", "?")
            destino = viagem.get("destino", "?")
            km = viagem.get("km", 0)

            resposta += f"• {data_str}: {origem} → {destino} ({self._formatar_numero(km, 1, 'km')})\n"

        return resposta
