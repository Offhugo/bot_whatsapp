from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.services.webhook_service import WebhookService


def criar_webhook_service_para_teste():

    usuario_repository = Mock()
    mensagem_repository = Mock()

    ai_service = Mock()
    whatsapp_service = Mock()

    registrar_km_use_case = Mock()
    registrar_abastecimento_use_case = Mock()
    registrar_viagem_use_case = Mock()
    consultar_km_use_case = Mock()
    consultar_viagens_use_case = Mock()

    return WebhookService(
        usuario_repository=usuario_repository,
        mensagem_repository=mensagem_repository,
        ai_service=ai_service,
        whatsapp_service=whatsapp_service,
        registrar_km_use_case=registrar_km_use_case,
        registrar_abastecimento_use_case=registrar_abastecimento_use_case,
        registrar_viagem_use_case=registrar_viagem_use_case,
        consultar_km_use_case=consultar_km_use_case,
        consultar_viagens_use_case=consultar_viagens_use_case,
    ), ai_service, whatsapp_service


@pytest.mark.anyio
async def test_webhook_ignora_evento_sem_mensagem():

    service, ai_service, whatsapp_service = (
        criar_webhook_service_para_teste()
    )

    payload = SimpleNamespace(
        entry=[
            SimpleNamespace(
                changes=[
                    SimpleNamespace(
                        value=SimpleNamespace(
                            messages=[]
                        )
                    )
                ]
            )
        ]
    )

    resultado = await service.process(
        payload,
        Mock()
    )

    assert resultado == {
        "status": "ignored"
    }

    ai_service.processar.assert_not_called()

    whatsapp_service.enviar_mensagem.assert_not_called()