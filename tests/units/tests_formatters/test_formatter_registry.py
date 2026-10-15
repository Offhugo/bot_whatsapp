"""
Testes para FormatterRegistry.
"""

import pytest
from app.formatters.formatter_registry import FormatterRegistry
from app.formatters.base_formatter import BaseFormatter


class TestFormatterRegistry:
    """Testes para registry de formatadores."""

    def test_get_formatador_existente(self):
        """Deve retornar formatador para intent existente."""
        formatador = FormatterRegistry.get("consultar_km")
        assert formatador is not None
        assert isinstance(formatador, BaseFormatter)

    def test_get_formatador_inexistente(self):
        """Deve retornar None para intent inexistente."""
        formatador = FormatterRegistry.get("intent_inexistente")
        assert formatador is None

    def test_has_intent_existente(self):
        """Deve retornar True para intent existente."""
        assert FormatterRegistry.has("consultar_km") is True
        assert FormatterRegistry.has("consultar_viagens") is True
        assert FormatterRegistry.has("consultar_abastecimento") is True

    def test_has_intent_inexistente(self):
        """Deve retornar False para intent inexistente."""
        assert FormatterRegistry.has("intent_inexistente") is False

    def test_lista_intents(self):
        """Deve listar todos os intents registrados."""
        intents = FormatterRegistry.lista_intents()

        assert isinstance(intents, list)
        assert len(intents) > 0
        assert "consultar_km" in intents
        assert "consultar_viagens" in intents
        assert "consultar_abastecimento" in intents

    def test_registrar_novo_formatador(self):
        """Deve registrar um novo formatador."""

        class FormularioTeste(BaseFormatter):
            def format(self, data):
                return "Teste"

        formatador_teste = FormularioTeste()
        FormatterRegistry.registrar("teste_intent", formatador_teste)

        assert FormatterRegistry.has("teste_intent")
        assert FormatterRegistry.get("teste_intent") == formatador_teste

    def test_nao_registrar_duplicado(self):
        """Não deve permitir registrar intent duplicado."""
        class FormularioTeste(BaseFormatter):
            def format(self, data):
                return "Teste"

        with pytest.raises(ValueError) as exc_info:
            FormatterRegistry.registrar("consultar_km", FormularioTeste())

        assert "já está registrado" in str(exc_info.value)

    def test_nao_registrar_invalido(self):
        """Não deve permitir registrar formatador inválido."""
        with pytest.raises(ValueError) as exc_info:
            FormatterRegistry.registrar("novo_intent", "não é formatador")

        assert "BaseFormatter" in str(exc_info.value)

    def test_formato_com_intent_valido(self):
        """Deve formatar usando intent válido."""
        dados = {
            "km_total": 100.0,
            "periodo": "01/10 a 05/10",
            "registros": [],
        }

        resultado = FormatterRegistry.formato("consultar_km", dados)

        assert resultado is not None
        assert "100,0 km" in resultado

    def test_formato_com_intent_invalido(self):
        """Deve retornar None para intent inválido."""
        resultado = FormatterRegistry.formato("intent_inexistente", {})
        assert resultado is None

    def test_formato_com_dados_invalidos(self):
        """Deve lançar erro se dados são inválidos."""
        dados_invalidos = {"km_total": 100.0}  # Falta campos obrigatórios

        with pytest.raises(ValueError):
            FormatterRegistry.formato("consultar_km", dados_invalidos)
