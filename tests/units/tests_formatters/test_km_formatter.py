"""
Testes para KMFormatter.
"""

import pytest
from app.formatters.km_formatter import KMFormatter, KMPorViagemFormatter


class TestKMFormatter:
    """Testes para formatador de KM."""

    @pytest.fixture
    def formatter(self):
        return KMFormatter()

    def test_formatar_dados_validos(self, formatter):
        """Deve formatar dados válidos de KM."""
        dados = {
            "km_total": 1250.5,
            "periodo": "01/10 a 13/10/2026",
            "registros": [
                {"data": "2026-10-01", "quilometros": 100.5},
                {"data": "2026-10-02", "quilometros": 120.0},
            ],
            "media_diaria": 117.2,
            "dias_com_registro": 12,
        }

        resultado = formatter.format(dados)

        assert "1.250,5 km" in resultado
        assert "Relatório de Quilometragem" in resultado
        assert "117,2 km" in resultado
        assert "12" in resultado

    def test_formatar_sem_media(self, formatter):
        """Deve formatar mesmo sem média diária."""
        dados = {
            "km_total": 500.0,
            "periodo": "01/10 a 05/10/2026",
            "registros": [{"data": "2026-10-01", "quilometros": 500.0}],
        }

        resultado = formatter.format(dados)

        assert "500,0 km" in resultado
        assert "Relatório de Quilometragem" in resultado

    def test_formatar_com_variacao_positiva(self, formatter):
        """Deve mostrar variação positiva."""
        dados = {
            "km_total": 250.0,
            "km_anterior": 200.0,
            "periodo": "01/10 a 05/10/2026",
            "registros": [],
        }

        resultado = formatter.format(dados)

        assert "📈" in resultado
        assert "25,0%" in resultado
        assert "acima" in resultado

    def test_formatar_com_variacao_negativa(self, formatter):
        """Deve mostrar variação negativa."""
        dados = {
            "km_total": 150.0,
            "km_anterior": 200.0,
            "periodo": "01/10 a 05/10/2026",
            "registros": [],
        }

        resultado = formatter.format(dados)

        assert "📉" in resultado
        assert "25,0%" in resultado
        assert "abaixo" in resultado

    def test_formatar_com_ultimos_registros(self, formatter):
        """Deve mostrar últimos registros."""
        dados = {
            "km_total": 600.0,
            "periodo": "01/10 a 10/10/2026",
            "registros": [
                {"data": "2026-10-01", "quilometros": 100.0},
                {"data": "2026-10-02", "quilometros": 120.0},
                {"data": "2026-10-03", "quilometros": 95.0},
                {"data": "2026-10-04", "quilometros": 110.0},
                {"data": "2026-10-05", "quilometros": 105.0},
            ],
        }

        resultado = formatter.format(dados)

        assert "01/10" in resultado
        assert "05/10" in resultado
        assert "Últimos registros" in resultado

    def test_formatar_com_mais_de_5_registros(self, formatter):
        """Deve indicar se há mais registros."""
        registros = [
            {"data": f"2026-10-{i:02d}", "quilometros": 100.0}
            for i in range(1, 11)
        ]

        dados = {
            "km_total": 1000.0,
            "periodo": "01/10 a 10/10/2026",
            "registros": registros,
        }

        resultado = formatter.format(dados)

        assert "... e mais" in resultado

    def test_validar_campos_obrigatorios(self, formatter):
        """Deve lançar erro se faltam campos obrigatórios."""
        dados_invalidos = {
            "km_total": 100.0,
            # Falta "periodo" e "registros"
        }

        with pytest.raises(ValueError) as exc_info:
            formatter.format(dados_invalidos)

        assert "Campos obrigatórios faltando" in str(exc_info.value)

    def test_validar_tipo_dados(self, formatter):
        """Deve lançar erro se dados não é dict."""
        with pytest.raises(ValueError) as exc_info:
            formatter.format("não é dict")

        assert "dicionário" in str(exc_info.value)

    def test_formatar_numero(self, formatter):
        """Deve formatar números corretamente."""
        assert formatter._formatar_numero(1250.5, 1, "km") == "1.250,5 km"
        assert formatter._formatar_numero(100.0, 1, "km") == "100,0 km"
        assert formatter._formatar_numero(10000.75, 2, "R$") == "10.000,75 R$"

    def test_formatar_data(self, formatter):
        """Deve formatar datas corretamente."""
        assert formatter._formatar_data("2026-10-13", "dd/mm") == "13/10"
        assert formatter._formatar_data("2026-10-13", "dd/mm/yyyy") == "13/10/2026"
        assert "outubro" in formatter._formatar_data("2026-10-13", "full")


class TestKMPorViagemFormatter:
    """Testes para formatador de KM por viagem."""

    @pytest.fixture
    def formatter(self):
        return KMPorViagemFormatter()

    def test_formatar_km_por_viagem(self, formatter):
        """Deve formatar KM agrupados por viagem."""
        dados = {
            "km_total": 350.0,
            "viagens": [
                {
                    "data": "2026-10-01",
                    "origem": "São Paulo",
                    "destino": "Rio de Janeiro",
                    "km": 350.0,
                },
                {
                    "data": "2026-10-02",
                    "origem": "Rio de Janeiro",
                    "destino": "Belo Horizonte",
                    "km": 450.0,
                },
            ],
        }

        resultado = formatter.format(dados)

        assert "São Paulo" in resultado
        assert "Rio de Janeiro" in resultado
        assert "2 viagens" in str(resultado.count("viagens"))
        assert "350,0 km" in resultado

    def test_formatar_campos_obrigatorios(self, formatter):
        """Deve validar campos obrigatórios."""
        dados_invalidos = {
            "km_total": 100.0,
            # Falta "viagens"
        }

        with pytest.raises(ValueError):
            formatter.format(dados_invalidos)
