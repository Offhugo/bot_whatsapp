"""
Testes para TimezoneNormalizationService.

Valida:
- Obter timezone do usuário
- Atualizar timezone do usuário
- Conversões de timestamps
- Validação de timezones
- Listagem de timezones do Brasil
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytz

from app.services.timezone_normalization_service import TimezoneNormalizationService
from app.models import Usuario


class TestTimezoneNormalizationService:
    """Testes para TimezoneNormalizationService."""

    @pytest.fixture
    def service(self):
        """Cria instância do serviço."""
        return TimezoneNormalizationService()

    @pytest.fixture
    def mock_db(self):
        """Mock da sessão do banco de dados."""
        return MagicMock()

    @pytest.fixture
    def mock_usuario(self):
        """Mock de um usuário."""
        usuario = MagicMock(spec=Usuario)
        usuario.id = 123
        usuario.timezone = "America/Fortaleza"
        return usuario

    def test_timezone_padrao(self, service):
        """Deve ter timezone padrão definido."""
        assert service.DEFAULT_TIMEZONE == "America/Fortaleza"

    def test_obter_timezone_usuario_existente(self, service, mock_db, mock_usuario):
        """Deve obter timezone do usuário existente."""
        mock_db.query.return_value.get.return_value = mock_usuario

        result = service.obter_timezone_usuario(123, mock_db)

        assert result == "America/Fortaleza"
        mock_db.query.assert_called_once()

    def test_obter_timezone_usuario_nao_encontrado(self, service, mock_db):
        """Deve retornar timezone padrão se usuário não existe."""
        mock_db.query.return_value.get.return_value = None

        result = service.obter_timezone_usuario(999, mock_db)

        assert result == service.DEFAULT_TIMEZONE

    def test_obter_timezone_usuario_null(self, service, mock_db, mock_usuario):
        """Deve retornar timezone padrão se usuário não tem timezone."""
        mock_usuario.timezone = None
        mock_db.query.return_value.get.return_value = mock_usuario

        result = service.obter_timezone_usuario(123, mock_db)

        assert result == service.DEFAULT_TIMEZONE

    def test_agora_utc(self, service):
        """Deve retornar data/hora atual em UTC."""
        resultado = service.agora_utc()

        assert isinstance(resultado, datetime)
        # UTC é sempre um pouco antes do horário local
        assert resultado.year >= 2026

    def test_agora_usuario(self, service, mock_db, mock_usuario):
        """Deve retornar data/hora no timezone do usuário."""
        mock_db.query.return_value.get.return_value = mock_usuario

        resultado = service.agora_usuario(123, mock_db)

        assert isinstance(resultado, datetime)
        assert resultado.tzinfo is not None

    def test_converter_para_usuario_iso_com_z(self, service, mock_db, mock_usuario):
        """Deve converter timestamp ISO com Z."""
        mock_db.query.return_value.get.return_value = mock_usuario

        resultado = service.converter_para_usuario(
            "2026-10-15T02:30:00Z",
            123,
            mock_db,
            formato="%d/%m/%Y %H:%M"
        )

        assert "/" in resultado  # Deve ter formato de data
        assert len(resultado) > 0

    def test_converter_para_usuario_iso_com_offset(self, service, mock_db, mock_usuario):
        """Deve converter timestamp ISO com offset."""
        mock_db.query.return_value.get.return_value = mock_usuario

        resultado = service.converter_para_usuario(
            "2026-10-15T02:30:00+00:00",
            123,
            mock_db,
            formato="%d/%m/%Y %H:%M"
        )

        assert "/" in resultado

    def test_converter_para_usuario_diferentes_timezones(
        self, service, mock_db, mock_usuario
    ):
        """Deve converter corretamente para diferentes timezones."""
        timezones = [
            "America/Fortaleza",
            "America/Sao_Paulo",
            "America/Manaus"
        ]

        for tz in timezones:
            mock_usuario.timezone = tz
            mock_db.query.return_value.get.return_value = mock_usuario

            resultado = service.converter_para_usuario(
                "2026-10-15T02:30:00Z",
                123,
                mock_db
            )

            assert resultado is not None
            assert len(resultado) > 0

    def test_converter_para_usuario_dict(self, service, mock_db, mock_usuario):
        """Deve retornar dict com múltiplos formatos."""
        mock_db.query.return_value.get.return_value = mock_usuario

        resultado = service.converter_para_usuario_dict(
            "2026-10-15T02:30:00Z",
            123,
            mock_db
        )

        assert "utc" in resultado
        assert "usuario" in resultado
        assert "data" in resultado
        assert "hora" in resultado
        assert "timestamp" in resultado

    def test_converter_lista_mensagens(self, service, mock_db, mock_usuario):
        """Deve converter timestamps de lista de mensagens."""
        mock_db.query.return_value.get.return_value = mock_usuario

        mensagens = [
            {"role": "user", "content": "Olá", "timestamp": "2026-10-15T02:30:00Z"},
            {"role": "assistant", "content": "Oi!", "timestamp": "2026-10-15T02:30:05Z"},
        ]

        resultado = service.converter_lista_mensagens(mensagens, 123, mock_db)

        assert len(resultado) == 2
        assert all("timestamp_usuario" in msg for msg in resultado)
        assert all("timestamp_info" in msg for msg in resultado)
        # Timestamps originais devem ser preservados
        assert resultado[0]["timestamp"] == "2026-10-15T02:30:00Z"

    def test_converter_lista_mensagens_vazio(self, service, mock_db, mock_usuario):
        """Deve lidar com lista vazia."""
        mock_db.query.return_value.get.return_value = mock_usuario

        resultado = service.converter_lista_mensagens([], 123, mock_db)

        assert resultado == []

    def test_converter_lista_mensagens_sem_timestamp(self, service, mock_db, mock_usuario):
        """Deve ignorar mensagens sem timestamp."""
        mock_db.query.return_value.get.return_value = mock_usuario

        mensagens = [
            {"role": "user", "content": "Olá"},
        ]

        resultado = service.converter_lista_mensagens(mensagens, 123, mock_db)

        assert len(resultado) == 1
        assert "timestamp_usuario" not in resultado[0]

    def test_validar_timezone_valido(self, service):
        """Deve validar timezone válido."""
        assert service.validar_timezone("America/Fortaleza") is True
        assert service.validar_timezone("America/Sao_Paulo") is True
        assert service.validar_timezone("UTC") is True

    def test_validar_timezone_invalido(self, service):
        """Deve rejeitar timezone inválido."""
        assert service.validar_timezone("Timezone_Inexistente") is False
        assert service.validar_timezone("Invalid/Zone") is False

    def test_listar_timezones_brasil(self, service):
        """Deve listar timezones do Brasil."""
        timezones = service.listar_timezones_brasil()

        assert isinstance(timezones, list)
        assert len(timezones) > 0
        assert "America/Fortaleza" in timezones
        assert "America/Sao_Paulo" in timezones
        assert all(isinstance(tz, str) for tz in timezones)

    def test_listar_timezones_ordenado(self, service):
        """Deve retornar timezones em ordem alfabética."""
        timezones = service.listar_timezones_brasil()

        assert timezones == sorted(timezones)

    def test_atualizar_timezone_usuario_valido(self, service, mock_db, mock_usuario):
        """Deve atualizar timezone do usuário."""
        mock_db.query.return_value.get.return_value = mock_usuario

        result = service.atualizar_timezone_usuario(
            123,
            "America/Sao_Paulo",
            mock_db
        )

        assert result is True
        assert mock_usuario.timezone == "America/Sao_Paulo"
        mock_db.commit.assert_called_once()

    def test_atualizar_timezone_usuario_invalido(self, service, mock_db, mock_usuario):
        """Deve rejeitar timezone inválido."""
        mock_db.query.return_value.get.return_value = mock_usuario

        result = service.atualizar_timezone_usuario(
            123,
            "Timezone_Inexistente",
            mock_db
        )

        assert result is False
        mock_db.commit.assert_not_called()

    def test_atualizar_timezone_usuario_nao_encontrado(self, service, mock_db):
        """Deve retornar False se usuário não existe."""
        mock_db.query.return_value.get.return_value = None

        result = service.atualizar_timezone_usuario(
            999,
            "America/Fortaleza",
            mock_db
        )

        assert result is False

    def test_converter_timestamp_malformado(self, service, mock_db, mock_usuario):
        """Deve retornar timestamp original se malformado."""
        mock_db.query.return_value.get.return_value = mock_usuario

        timestamp_malformado = "timestamp_invalido"
        resultado = service.converter_para_usuario(
            timestamp_malformado,
            123,
            mock_db
        )

        assert resultado == timestamp_malformado
