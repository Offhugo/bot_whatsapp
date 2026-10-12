"""
Testes para AIResponseDTO com validações robustas.

Valida que:
- Cada intent tem dados corretos
- Resposta não é vazia
- Dados são JSON-serializáveis
"""

import pytest
from pydantic import ValidationError

from app.schemas.ai_response import (
    AIResponseDTO,
    Intent,
    RegistrarKMDados,
    RegistrarViagemDados,
)


class TestAIResponseDTOBasico:
    """Testes básicos de validação"""

    def test_criar_resposta_valida_registrar_km(self):
        """Deve criar resposta válida para registrar_km"""
        resposta = AIResponseDTO(
            intent=Intent.REGISTRAR_KM,
            dados={"quilometros": 120.5},
            resposta="Registrei 120.5 km"
        )

        assert resposta.intent == Intent.REGISTRAR_KM
        assert resposta.dados["quilometros"] == 120.5
        assert resposta.resposta == "Registrei 120.5 km"

    def test_criar_resposta_valida_conversa(self):
        """Deve criar resposta válida para conversa"""
        resposta = AIResponseDTO(
            intent=Intent.CONVERSA,
            dados={},
            resposta="Olá! Como posso ajudar?"
        )

        assert resposta.intent == Intent.CONVERSA
        assert resposta.resposta == "Olá! Como posso ajudar?"


class TestAIResponseDTOValidacaoResposta:
    """Testes de validação da resposta"""

    def test_rejeitar_resposta_vazia(self):
        """Deve rejeitar resposta vazia"""
        with pytest.raises(ValidationError) as exc_info:
            AIResponseDTO(
                intent=Intent.CONVERSA,
                dados={},
                resposta=""
            )

        assert "resposta" in str(exc_info.value).lower()

    def test_rejeitar_resposta_apenas_espacos(self):
        """Deve rejeitar resposta com apenas espaços"""
        with pytest.raises(ValidationError):
            AIResponseDTO(
                intent=Intent.CONVERSA,
                dados={},
                resposta="   "
            )

    def test_rejeitar_resposta_muito_longa(self):
        """Deve rejeitar resposta que excede limite"""
        resposta_longa = "x" * 5000  # Mais que MAX_AI_RESPONSE_LENGTH

        with pytest.raises(ValidationError):
            AIResponseDTO(
                intent=Intent.CONVERSA,
                dados={},
                resposta=resposta_longa
            )

    def test_aceitar_resposta_valida_com_espacos(self):
        """Deve aceitar resposta válida e remover espaços extras"""
        resposta = AIResponseDTO(
            intent=Intent.CONVERSA,
            dados={},
            resposta="  Olá! Como posso ajudar?  "
        )

        # Deve remover espaços extras
        assert resposta.resposta == "Olá! Como posso ajudar?"


class TestAIResponseDTOValidacaoDados:
    """Testes de validação dos dados"""

    def test_rejeitar_dados_nao_json_serializable(self):
        """Deve rejeitar dados que não são JSON-serializáveis"""
        class NaoSerializavel:
            pass

        with pytest.raises(ValidationError):
            AIResponseDTO(
                intent=Intent.CONVERSA,
                dados={"obj": NaoSerializavel()},
                resposta="Test"
            )

    def test_aceitar_dados_json_validos(self):
        """Deve aceitar dados JSON-serializáveis"""
        resposta = AIResponseDTO(
            intent=Intent.CONVERSA,
            dados={
                "string": "value",
                "number": 42,
                "float": 3.14,
                "bool": True,
                "null": None,
                "list": [1, 2, 3],
                "nested": {"key": "value"}
            },
            resposta="Test"
        )

        assert resposta.dados["string"] == "value"


class TestAIResponseDTOValidacaoPorIntent:
    """Testes de validação contextual por intent"""

    def test_registrar_km_com_dados_validos(self):
        """Deve aceitar dados válidos para registrar_km"""
        resposta = AIResponseDTO(
            intent=Intent.REGISTRAR_KM,
            dados={"quilometros": 100.0, "viagem_id": 1},
            resposta="Registrei 100 km"
        )

        assert resposta.dados["quilometros"] == 100.0

    def test_registrar_km_rejeita_quilometros_negativo(self):
        """Deve rejeitar quilometragem negativa"""
        with pytest.raises(ValidationError):
            AIResponseDTO(
                intent=Intent.REGISTRAR_KM,
                dados={"quilometros": -10.0},
                resposta="Registrei"
            )

    def test_registrar_km_rejeita_quilometros_zero(self):
        """Deve rejeitar quilometragem zero"""
        with pytest.raises(ValidationError):
            AIResponseDTO(
                intent=Intent.REGISTRAR_KM,
                dados={"quilometros": 0.0},
                resposta="Registrei"
            )

    def test_registrar_km_rejeita_quilometros_muito_alto(self):
        """Deve rejeitar quilometragem acima do limite"""
        with pytest.raises(ValidationError):
            AIResponseDTO(
                intent=Intent.REGISTRAR_KM,
                dados={"quilometros": 6000.0},  # Acima de MAX_QUILOMETROS
                resposta="Registrei"
            )

    def test_registrar_viagem_com_dados_validos(self):
        """Deve aceitar dados válidos para registrar_viagem"""
        resposta = AIResponseDTO(
            intent=Intent.REGISTRAR_VIAGEM,
            dados={
                "origem": "São Paulo",
                "destino": "Rio de Janeiro"
            },
            resposta="Registrei a viagem"
        )

        assert resposta.dados["origem"] == "São Paulo"

    def test_registrar_viagem_rejeita_origem_vazia(self):
        """Deve rejeitar viagem sem origem"""
        with pytest.raises(ValidationError):
            AIResponseDTO(
                intent=Intent.REGISTRAR_VIAGEM,
                dados={"origem": "", "destino": "Rio"},
                resposta="Test"
            )

    def test_registrar_viagem_rejeita_destino_vazio(self):
        """Deve rejeitar viagem sem destino"""
        with pytest.raises(ValidationError):
            AIResponseDTO(
                intent=Intent.REGISTRAR_VIAGEM,
                dados={"origem": "São Paulo", "destino": ""},
                resposta="Test"
            )

    def test_registrar_abastecimento_com_dados_validos(self):
        """Deve aceitar dados válidos para registrar_abastecimento"""
        resposta = AIResponseDTO(
            intent=Intent.REGISTRAR_ABASTECIMENTO,
            dados={
                "valor": 150.50,
                "combustivel": "gasolina"
            },
            resposta="Registrei o abastecimento"
        )

        assert resposta.dados["valor"] == 150.50

    def test_registrar_abastecimento_rejeita_valor_negativo(self):
        """Deve rejeitar valor negativo de abastecimento"""
        with pytest.raises(ValidationError):
            AIResponseDTO(
                intent=Intent.REGISTRAR_ABASTECIMENTO,
                dados={"valor": -50.0, "combustivel": "gasolina"},
                resposta="Test"
            )

    def test_consultar_km_com_datas_validas(self):
        """Deve aceitar datas válidas para consultar_km"""
        resposta = AIResponseDTO(
            intent=Intent.CONSULTAR_KM,
            dados={
                "data_inicio": "2026-10-01",
                "data_fim": "2026-10-31"
            },
            resposta="Consultei KM"
        )

        assert resposta.dados["data_inicio"] == "2026-10-01"

    def test_consultar_km_sem_datas(self):
        """Deve aceitar consultar_km sem datas"""
        resposta = AIResponseDTO(
            intent=Intent.CONSULTAR_KM,
            dados={},
            resposta="Consultei seu KM total"
        )

        assert resposta.dados == {}


class TestAIResponseDTODadosFaltando:
    """Testes de dados faltando para um intent"""

    def test_registrar_km_falta_quilometros(self):
        """Deve rejeitar registrar_km sem quilometros"""
        with pytest.raises(ValidationError):
            AIResponseDTO(
                intent=Intent.REGISTRAR_KM,
                dados={"viagem_id": 1},  # Falta quilometros
                resposta="Test"
            )

    def test_registrar_viagem_falta_origem(self):
        """Deve rejeitar registrar_viagem sem origem"""
        with pytest.raises(ValidationError):
            AIResponseDTO(
                intent=Intent.REGISTRAR_VIAGEM,
                dados={"destino": "Rio"},  # Falta origem
                resposta="Test"
            )

    def test_registrar_viagem_falta_destino(self):
        """Deve rejeitar registrar_viagem sem destino"""
        with pytest.raises(ValidationError):
            AIResponseDTO(
                intent=Intent.REGISTRAR_VIAGEM,
                dados={"origem": "SP"},  # Falta destino
                resposta="Test"
            )

    def test_registrar_abastecimento_falta_valor(self):
        """Deve rejeitar abastecimento sem valor"""
        with pytest.raises(ValidationError):
            AIResponseDTO(
                intent=Intent.REGISTRAR_ABASTECIMENTO,
                dados={"combustivel": "gasolina"},  # Falta valor
                resposta="Test"
            )


class TestAIResponseDTODadosOpcionais:
    """Testes de campos opcionais"""

    def test_registrar_km_viagem_id_opcional(self):
        """Deve aceitar registrar_km sem viagem_id"""
        resposta = AIResponseDTO(
            intent=Intent.REGISTRAR_KM,
            dados={"quilometros": 100.0},  # Sem viagem_id
            resposta="Registrei"
        )

        assert "viagem_id" not in resposta.dados

    def test_consultar_km_datas_opcionais(self):
        """Deve aceitar consultar_km sem datas"""
        resposta = AIResponseDTO(
            intent=Intent.CONSULTAR_KM,
            dados={},  # Sem datas
            resposta="Consultei"
        )

        assert resposta.dados == {}