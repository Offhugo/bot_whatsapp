import pytest
from pydantic import ValidationError

from app.schemas.meta import (
    MAX_MESSAGE_TEXT_LENGTH,
    MAX_WA_ID_LENGTH,
    MetaDTO,
)


def payload_valido():
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "contacts": [
                                {
                                    "wa_id": "5511999999999"
                                }
                            ],
                            "messages": [
                                {
                                    "text": {
                                        "body": "Rodei 430 km."
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }


def test_meta_dto_aceita_payload_valido():
    payload = payload_valido()

    resultado = MetaDTO(**payload)

    assert resultado.object == "whatsapp_business_account"
    assert resultado.entry[0].changes[0].value.messages[0].text.body == "Rodei 430 km."


def test_meta_dto_rejeita_texto_vazio():
    payload = payload_valido()

    payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"] = ""

    with pytest.raises(ValidationError):
        MetaDTO(**payload)


def test_meta_dto_rejeita_texto_apenas_com_espacos():
    payload = payload_valido()

    payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"] = "     "

    with pytest.raises(ValidationError):
        MetaDTO(**payload)


def test_meta_dto_rejeita_texto_acima_do_limite():
    payload = payload_valido()

    payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"] = (
        "a" * (MAX_MESSAGE_TEXT_LENGTH + 1)
    )

    with pytest.raises(ValidationError):
        MetaDTO(**payload)


def test_meta_dto_rejeita_body_ausente():
    payload = payload_valido()

    del payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

    with pytest.raises(ValidationError):
        MetaDTO(**payload)


def test_meta_dto_rejeita_text_ausente():
    payload = payload_valido()

    del payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]

    with pytest.raises(ValidationError):
        MetaDTO(**payload)


def test_meta_dto_rejeita_wa_id_vazio():
    payload = payload_valido()

    payload["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"] = ""

    with pytest.raises(ValidationError):
        MetaDTO(**payload)


def test_meta_dto_rejeita_wa_id_invalido():
    payload = payload_valido()

    payload["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"] = "abc123"

    with pytest.raises(ValidationError):
        MetaDTO(**payload)


def test_meta_dto_rejeita_wa_id_acima_do_limite():
    payload = payload_valido()

    payload["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"] = (
        "1" * (MAX_WA_ID_LENGTH + 1)
    )

    with pytest.raises(ValidationError):
        MetaDTO(**payload)


def test_meta_dto_rejeita_messages_que_nao_seja_lista():
    payload = payload_valido()

    payload["entry"][0]["changes"][0]["value"]["messages"] = "mensagem"

    with pytest.raises(ValidationError):
        MetaDTO(**payload)


def test_meta_dto_rejeita_entry_que_nao_seja_lista():
    payload = payload_valido()

    payload["entry"] = {}

    with pytest.raises(ValidationError):
        MetaDTO(**payload)


def test_meta_dto_rejeita_entry_vazio():
    payload = payload_valido()

    payload["entry"] = []

    with pytest.raises(ValidationError):
        MetaDTO(**payload)


def test_meta_dto_rejeita_changes_vazio():
    payload = payload_valido()

    payload["entry"][0]["changes"] = []

    with pytest.raises(ValidationError):
        MetaDTO(**payload)


def test_meta_dto_rejeita_campo_obrigatorio_ausente():
    payload = payload_valido()

    del payload["entry"]

    with pytest.raises(ValidationError):
        MetaDTO(**payload)


def test_meta_dto_aceita_payload_sem_messages():
    payload = payload_valido()

    del payload["entry"][0]["changes"][0]["value"]["messages"]

    resultado = MetaDTO(**payload)

    assert resultado.entry[0].changes[0].value.messages is None