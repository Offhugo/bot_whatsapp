"""
Formatador para respostas de ConsultarViagens.
"""

from typing import Any, Dict
from app.formatters.base_formatter import BaseFormatter


class ViagemFormatter(BaseFormatter):
    """Formata respostas de consultas de viagens."""

    def format(self, data: Dict[str, Any]) -> str:
        """
        Formata dados de viagens.

        Campos esperados:
        - total_viagens: int
        - periodo: str
        - km_total: float
        - viagens: list (viagens com origem, destino, km, data, status)

        Args:
            data: Dados de viagens

        Returns:
            String formatada
        """
        self._validar_dados(
            data,
            ["total_viagens", "periodo", "viagens"]
        )

        total_viagens = data["total_viagens"]
        periodo = data["periodo"]
        km_total = data.get("km_total", 0)
        viagens = data["viagens"]

        # Contar por status
        status_counts = self._contar_por_status(viagens)

        resposta = (
            f"🚗 **Relatório de Viagens**\n"
            f"📅 Período: {periodo}\n\n"
            f"📊 **Resumo:**\n"
            f"✈️ Total de viagens: {total_viagens}\n"
        )

        if km_total > 0:
            resposta += f"📍 Total KM: {self._formatar_numero(km_total, 1, 'km')}\n"

        # Adicionar contagem por status
        for status, count in status_counts.items():
            emoji = self._emoji_status(status)
            resposta += f"{emoji} {self._status_label(status)}: {count}\n"

        # Adicionar últimas viagens
        if viagens:
            resposta += f"\n📋 **Últimas viagens:**\n"

            ultimas = viagens[-5:] if len(viagens) > 5 else viagens

            for viagem in ultimas:
                resposta += self._formatar_viagem(viagem)

            if len(viagens) > 5:
                resposta += f"\n... e mais {len(viagens) - 5} viagens"

        return resposta

    def _contar_por_status(self, viagens: list) -> Dict[str, int]:
        """Conta viagens por status."""
        counts = {}
        for viagem in viagens:
            status = viagem.get("status", "pendente")
            counts[status] = counts.get(status, 0) + 1
        return counts

    def _emoji_status(self, status: str) -> str:
        """Retorna emoji para status."""
        emojis = {
            "concluida": "✅",
            "em_progresso": "🔄",
            "pendente": "⏳",
            "cancelada": "❌",
        }
        return emojis.get(status, "•")

    def _status_label(self, status: str) -> str:
        """Retorna label legível para status."""
        labels = {
            "concluida": "Concluída",
            "em_progresso": "Em Progresso",
            "pendente": "Pendente",
            "cancelada": "Cancelada",
        }
        return labels.get(status, status)

    def _formatar_viagem(self, viagem: Dict[str, Any]) -> str:
        """Formata uma viagem individual."""
        data_str = self._formatar_data(viagem.get("data", ""), "dd/mm")
        origem = viagem.get("origem", "?")
        destino = viagem.get("destino", "?")
        km = viagem.get("km", 0)
        status = viagem.get("status", "?")

        emoji = self._emoji_status(status)

        linha = f"• {data_str} {emoji} {origem} → {destino}"

        if km > 0:
            linha += f" ({self._formatar_numero(km, 1, 'km')})"

        linha += "\n"

        return linha
