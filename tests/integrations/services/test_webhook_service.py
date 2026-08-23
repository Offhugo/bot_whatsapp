from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.schemas.ai_response import AIResponseDTO, Intent
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

    registrar_km_use_case.executar.return_value = {
        "sucesso": True,
        "mensagem": "430 km registrados."
    }

    return (
        WebhookService(
            usuario_repository=usuario_repository,
            mensagem_repository=mensagem_repository,
            ai_service=ai_service,
            whatsapp_service=whatsapp_service,
            registrar_km_use_case=registrar_km_use_case,
            registrar_abastecimento_use_case=registrar_abastecimento_use_case,
            registrar_viagem_use_case=registrar_viagem_use_case,
            consultar_km_use_case=consultar_km_use_case,
            consultar_viagens_use_case=consultar_viagens_use_case,
        ),
        usuario_repository,
        mensagem_repository,
        ai_service,
        whatsapp_service,
        registrar_km_use_case,
    )


@pytest.mark.anyio
async def test_webhook_encaminha_registrar_km():
    (
        service,
        usuario_repository,
        mensagem_repository,
        ai_service,
        whatsapp_service,
        registrar_km_use_case,
    ) = criar_webhook_service_para_teste()

    usuario = SimpleNamespace(id=1)

    usuario_repository.buscar_por_telefone.return_value = usuario

    ai_service.processar = AsyncMock(
        return_value=AIResponseDTO(
            intent=Intent.REGISTRAR_KM,
            dados={
                "quilometros": 430
            },
            resposta="Registrei os 430 km."
        )
    )

    whatsapp_service.enviar_mensagem = AsyncMock()

    payload = SimpleNamespace(
        entry=[
            SimpleNamespace(
                changes=[
                    SimpleNamespace(
                        value=SimpleNamespace(
                            messages=[
                                SimpleNamespace(
                                    text=SimpleNamespace(
                                        body="Rodei 430 km."
                                    )
                                )
                            ],
                            contacts=[
                                SimpleNamespace(
                                    wa_id="5511999999999"
                                )
                            ]
                        )
                    )
                ]
            )
        ]
    )

    db = Mock()

    resultado = await service.process(
        payload,
        db
    )

    assert resultado == {
        "status": "success"
    }

    registrar_km_use_case.executar.assert_called_once()

    whatsapp_service.enviar_mensagem.assert_awaited_once_with(
        "5511999999999",
        "430 km registrados."
    )

    @pytest.mark.anyio
    async def test_webhook_trata_conversa_sem_use_case():
        (
            service,
            usuario_repository,
            mensagem_repository,
            ai_service,
            whatsapp_service,
            registrar_km_use_case,
        ) = criar_webhook_service_para_teste()

        usuario = SimpleNamespace(id=1)

        usuario_repository.buscar_por_telefone.return_value = usuario

        ai_service.processar = AsyncMock(
            return_value=AIResponseDTO(
                intent=Intent.CONVERSA,
                dados={},
                resposta="Bom dia! Como posso ajudar?"
            )
        )

        whatsapp_service.enviar_mensagem = AsyncMock()

        payload = SimpleNamespace(
            entry=[
                SimpleNamespace(
                    changes=[
                        SimpleNamespace(
                            value=SimpleNamespace(
                                messages=[
                                    SimpleNamespace(
                                        text=SimpleNamespace(
                                            body="Bom dia!"
                                        )
                                    )
                                ],
                                contacts=[
                                    SimpleNamespace(
                                        wa_id="5511999999999"
                                    )
                                ]
                            )
                        )
                    ]
                )
            ]
        )

        db = Mock()

        resultado = await service.process(
            payload,
            db
        )

        assert resultado == {
            "status": "success"
        }

        registrar_km_use_case.executar.assert_not_called()

        whatsapp_service.enviar_mensagem.assert_awaited_once_with(
            "5511999999999",
            "Bom dia! Como posso ajudar?"
        )