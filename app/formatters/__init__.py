"""
Módulo de formatadores de resposta.

Transforma dados técnicos em respostas legíveis para o usuário.
"""

from app.formatters.base_formatter import BaseFormatter
from app.formatters.km_formatter import KMFormatter, KMPorViagemFormatter
from app.formatters.viagem_formatter import ViagemFormatter
from app.formatters.abastecimento_formatter import AbastecimentoFormatter
from app.formatters.formatter_registry import FormatterRegistry

__all__ = [
    "BaseFormatter",
    "KMFormatter",
    "KMPorViagemFormatter",
    "ViagemFormatter",
    "AbastecimentoFormatter",
    "FormatterRegistry",
]
