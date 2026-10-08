from unittest.mock import MagicMock

from app.schemas.ai_response import AIResponseDTO, Intent
from app.services.webhook_service import WebhookService


def criar_service():
    service = WebhookService.__new__(WebhookService)

    service.autorizacao_service = MagicMock()
    service.viagem_repository = MagicMock()

    service.registrar_km_use_case = MagicMock()
    service.registrar_abastecimento_use_case = MagicMock()
    service.registrar_viagem_use_case = MagicMock()
    service.consultar_km_use_case = MagicMock()
    service.consultar_viagens_use_case = MagicMock()

    return service


def test_executar_intent_rejeita_dado_invalido_antes_do_use_case():
    service = criar_service()

    resposta = AIResponseDTO(
        intent=Intent.REGISTRAR_KM,
        dados={
            "quilometros": "430"
        },
        resposta="Registrando quilometragem.",
    )

    usuario = MagicMock()
    db = MagicMock()

    resultado = service._executar_intent(
        resposta,
        usuario,
        db,
    )

    assert resultado["mensagem"] == (
        "Não consegui validar os dados recebidos."
    )

    service.autorizacao_service.pode_registrar.assert_not_called()
    service.viagem_repository.buscar_por_id.assert_not_called()
    service.registrar_km_use_case.executar.assert_not_called()


def test_executar_intent_permite_dado_valido():
    service = criar_service()

    service.autorizacao_service.pode_registrar.return_value = True

    service.registrar_km_use_case.executar.return_value = {
        "sucesso": True,
        "mensagem": "Quilometragem registrada.",
    }

    resposta = AIResponseDTO(
        intent=Intent.REGISTRAR_KM,
        dados={
            "quilometros": 430
        },
        resposta="Registrando 430 km.",
    )

    usuario = MagicMock(id=1)
    db = MagicMock()

    resultado = service._executar_intent(
        resposta,
        usuario,
        db,
    )

    assert resultado["sucesso"] is True
    service.registrar_km_use_case.executar.assert_called_once()