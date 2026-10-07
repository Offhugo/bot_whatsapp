from unittest.mock import MagicMock

from app.schemas.ai_response import AIResponseDTO
from app.schemas.ai_response import Intent
from app.services.webhook_service import WebhookService


def criar_service():
    return WebhookService(
        usuario_repository=MagicMock(),
        mensagem_repository=MagicMock(),
        ai_service=MagicMock(),
        whatsapp_service=MagicMock(),
        registrar_km_use_case=MagicMock(),
        registrar_abastecimento_use_case=MagicMock(),
        registrar_viagem_use_case=MagicMock(),
        consultar_km_use_case=MagicMock(),
        consultar_viagens_use_case=MagicMock(),
        viagem_repository=MagicMock(),
        autorizacao_service=MagicMock(),
    )


def criar_resposta(dados):
    return AIResponseDTO(
        intent=Intent.CONVERSA,
        dados=dados,
        resposta="Resposta válida."
    )


def test_id_viagem_inteiro_positivo_e_aceito():
    service = criar_service()

    resposta = criar_resposta({
        "viagem_id": 123
    })

    assert service._validar_id_recurso(
        resposta.dados["viagem_id"]
    ) is True


def test_id_empresa_inteiro_positivo_e_aceito():
    service = criar_service()

    resposta = criar_resposta({
        "empresa_id": 123
    })

    assert service._validar_id_recurso(
        resposta.dados["empresa_id"]
    ) is True


def test_id_ausente_e_aceito():
    service = criar_service()

    assert service._validar_id_recurso(None) is True


def test_id_booleano_e_rejeitado():
    service = criar_service()

    assert service._validar_id_recurso(True) is False


def test_id_string_e_rejeitado():
    service = criar_service()

    assert service._validar_id_recurso("123") is False


def test_id_zero_e_rejeitado():
    service = criar_service()

    assert service._validar_id_recurso(0) is False


def test_id_negativo_e_rejeitado():
    service = criar_service()

    assert service._validar_id_recurso(-1) is False

def test_executar_intent_rejeita_viagem_id_invalido():
    service = criar_service()

    resposta = criar_resposta({
        "viagem_id": "123"
    })

    usuario = MagicMock()
    db = MagicMock()

    resultado = service._executar_intent(
        resposta,
        usuario,
        db
    )

    assert resultado["mensagem"] == (
        "O identificador da viagem informado é inválido."
    )

    service.viagem_repository.buscar_por_id.assert_not_called()


def test_executar_intent_rejeita_empresa_id_invalido():
    service = criar_service()

    resposta = criar_resposta({
        "empresa_id": -10
    })

    usuario = MagicMock()
    db = MagicMock()

    resultado = service._executar_intent(
        resposta,
        usuario,
        db
    )

    assert resultado["mensagem"] == (
        "O identificador da empresa informado é inválido."
    )

    service.viagem_repository.buscar_por_id.assert_not_called()

def test_executar_intent_nao_acessa_viagem_com_id_invalido():
    service = criar_service()

    resposta = criar_resposta({
        "viagem_id": True
    })

    usuario = MagicMock()
    db = MagicMock()

    resultado = service._executar_intent(
        resposta,
        usuario,
        db
    )

    assert resultado["mensagem"] == (
        "O identificador da viagem informado é inválido."
    )

    service.viagem_repository.buscar_por_id.assert_not_called()