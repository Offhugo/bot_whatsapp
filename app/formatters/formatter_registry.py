"""
Registry de formatadores.

Centraliza todos os formatadores disponíveis e fornece
uma forma simples de acessá-los por tipo de intent.
"""

from typing import Dict, Optional
from app.formatters.base_formatter import BaseFormatter
from app.formatters.km_formatter import KMFormatter, KMPorViagemFormatter
from app.formatters.viagem_formatter import ViagemFormatter
from app.formatters.abastecimento_formatter import AbastecimentoFormatter


class FormatterRegistry:
    """Registry centralizado de formatadores."""

    # Registry privado
    _formatadores: Dict[str, BaseFormatter] = {
        "consultar_km": KMFormatter(),
        "consultar_km_viagem": KMPorViagemFormatter(),
        "consultar_viagens": ViagemFormatter(),
        "consultar_abastecimento": AbastecimentoFormatter(),
    }

    @classmethod
    def get(cls, intent: str) -> Optional[BaseFormatter]:
        """
        Obtém formatador para um intent específico.

        Args:
            intent: Nome do intent (ex: "consultar_km")

        Returns:
            Formatador ou None se não encontrado
        """
        return cls._formatadores.get(intent)

    @classmethod
    def has(cls, intent: str) -> bool:
        """
        Verifica se existe formatador para um intent.

        Args:
            intent: Nome do intent

        Returns:
            True se existe, False caso contrário
        """
        return intent in cls._formatadores

    @classmethod
    def registrar(cls, intent: str, formatador: BaseFormatter) -> None:
        """
        Registra um novo formatador.

        Args:
            intent: Nome do intent
            formatador: Instância do formatador

        Raises:
            ValueError: Se intent já existe ou formatador é inválido
        """
        if intent in cls._formatadores:
            raise ValueError(f"Intent '{intent}' já está registrado")

        if not isinstance(formatador, BaseFormatter):
            raise ValueError("Formatador deve ser instância de BaseFormatter")

        cls._formatadores[intent] = formatador

    @classmethod
    def lista_intents(cls) -> list[str]:
        """
        Lista todos os intents registrados.

        Returns:
            Lista de intents
        """
        return list(cls._formatadores.keys())

    @classmethod
    def formato(cls, intent: str, dados: dict) -> Optional[str]:
        """
        Formata dados usando o formatador apropriado.

        Esta é a principal forma de usar o registry.

        Args:
            intent: Nome do intent
            dados: Dados a formatar

        Returns:
            String formatada ou None se intent não existe

        Raises:
            ValueError: Se dados são inválidos para o formatador
        """
        formatador = cls.get(intent)
        if not formatador:
            return None

        return formatador.format(dados)
