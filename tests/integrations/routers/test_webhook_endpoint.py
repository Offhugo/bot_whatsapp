from unittest.mock import AsyncMock, Mock

from fastapi.testclient import TestClient

from app.main import app


def test_webhook_endpoint_com_sucesso(monkeypatch):

    # Simula o resultado do WebhookService
    webhook_service = Mock()

    webhook_service.process = AsyncMock(
        return_value={
            "status": "success"
        }
    )

    # Substitui temporariamente o WebhookService usado pela rota
    import app.routers.webhook as webhook_router

    monkeypatch.setattr(
        webhook_router,
        "webhook_service",
        webhook_service
    )

    client = TestClient(app)

    payload = {
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

    response = client.post(
        "/webhook",
        json=payload
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "success"
    }

    webhook_service.process.assert_awaited_once()


def test_webhook_endpoint_rejeita_payload_invalido(monkeypatch):

    # Cria um WebhookService falso para verificar
    # se a rota chega ou não até ele.
    webhook_service = Mock()

    webhook_service.process = AsyncMock(
        return_value={
            "status": "success"
        }
    )

    # Substitui temporariamente o service real da rota
    import app.routers.webhook as webhook_router

    monkeypatch.setattr(
        webhook_router,
        "webhook_service",
        webhook_service
    )

    client = TestClient(app)

    # Payload propositalmente inválido:
    # não possui o campo "entry" exigido pelo MetaDTO.
    payload = {
        "object": "whatsapp_business_account"
    }

    response = client.post(
        "/webhook",
        json=payload
    )

    # FastAPI/Pydantic deve rejeitar a requisição
    assert response.status_code == 422

    # O WebhookService não deve ser executado.
    webhook_service.process.assert_not_awaited()