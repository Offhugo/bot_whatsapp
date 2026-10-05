import pytest
from pydantic import ValidationError

from app.schemas.ai_response import (
    AIResponseDTO,
    MAX_AI_RESPONSE_LENGTH,
    Intent,
)


def resposta_valida():
    return {
        "intent": "registrar_km",
        "dados": {
            "quilometros": 430
        },
        "resposta": "Registrei os 430 km."
    }


def test_ai_response_dto_aceita_resposta_valida():
    resultado = AIResponseDTO(
        **resposta_valida()
    )

    assert resultado.intent == Intent.REGISTRAR_KM
    assert resultado.dados == {
        "quilometros": 430
    }
    assert resultado.resposta == "Registrei os 430 km."


def test_ai_response_dto_rejeita_intent_ausente():
    dados = resposta_valida()
    del dados["intent"]

    with pytest.raises(ValidationError):
        AIResponseDTO(**dados)


def test_ai_response_dto_rejeita_intent_invalido():
    dados = resposta_valida()
    dados["intent"] = "intencao_inexistente"

    with pytest.raises(ValidationError):
        AIResponseDTO(**dados)


def test_ai_response_dto_rejeita_dados_ausentes():
    dados = resposta_valida()
    del dados["dados"]

    with pytest.raises(ValidationError):
        AIResponseDTO(**dados)


def test_ai_response_dto_rejeita_dados_com_tipo_invalido():
    dados = resposta_valida()
    dados["dados"] = "quilometros: 430"

    with pytest.raises(ValidationError):
        AIResponseDTO(**dados)


def test_ai_response_dto_rejeita_resposta_ausente():
    dados = resposta_valida()
    del dados["resposta"]

    with pytest.raises(ValidationError):
        AIResponseDTO(**dados)


def test_ai_response_dto_rejeita_resposta_vazia():
    dados = resposta_valida()
    dados["resposta"] = ""

    with pytest.raises(ValidationError):
        AIResponseDTO(**dados)


def test_ai_response_dto_rejeita_resposta_apenas_com_espacos():
    dados = resposta_valida()
    dados["resposta"] = "     "

    with pytest.raises(ValidationError):
        AIResponseDTO(**dados)


def test_ai_response_dto_rejeita_resposta_acima_do_limite():
    dados = resposta_valida()
    dados["resposta"] = "a" * (
        MAX_AI_RESPONSE_LENGTH + 1
    )

    with pytest.raises(ValidationError):
        AIResponseDTO(**dados)


def test_ai_response_dto_aceita_dados_vazios():
    dados = resposta_valida()
    dados["dados"] = {}

    resultado = AIResponseDTO(**dados)

    assert resultado.dados == {}


def test_ai_response_dto_aceita_dados_json_validos():
    dados = resposta_valida()

    dados["dados"] = {
        "quilometros": 430,
        "observacao": "Viagem concluída",
        "valores": [100, 200, 300],
        "confirmado": True,
        "detalhes": {
            "origem": "Aracaju",
            "destino": "Salvador"
        }
    }

    resultado = AIResponseDTO(**dados)

    assert resultado.dados["quilometros"] == 430
    assert resultado.dados["detalhes"]["destino"] == "Salvador"


def test_ai_response_dto_rejeita_dados_nao_json():
    dados = resposta_valida()

    dados["dados"] = {
        "valor": object()
    }

    with pytest.raises(ValidationError):
        AIResponseDTO(**dados)