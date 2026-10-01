import hashlib
import hmac
import json
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app


META_APP_SECRET = "app-secret-teste"
META_VERIFY_TOKEN = "token-teste"


def criar_assinatura(payload: bytes) -> str:
    """
    Calcula a assinatura HMAC-SHA256 esperada pela aplicação
    para o corpo exato da requisição.
    """

    digest = hmac.new(
        META_APP_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()

    return f"sha256={digest}"


def criar_webhook_service_mock(monkeypatch):
    """
    Cria um WebhookService falso para os testes
    e substitui o service real utilizado pelo router.
    """

    webhook_service = Mock()

    webhook_service.process = AsyncMock(
        return_value={
            "status": "success"
        }
    )

    import app.routers.webhook as webhook_router

    monkeypatch.setattr(
        webhook_router,
        "webhook_service",
        webhook_service
    )

    return webhook_service


@pytest.fixture
def client(monkeypatch):
    """
    Cria um cliente HTTP de teste sem depender
    de uma conexão real com o PostgreSQL.
    """

    # Substitui temporariamente a dependência do banco.
    monkeypatch.setitem(
        app.dependency_overrides,
        get_db,
        lambda: Mock()
    )

    # Define os segredos utilizados pelos testes.
    monkeypatch.setenv(
        "META_APP_SECRET",
        META_APP_SECRET
    )

    monkeypatch.setenv(
        "META_VERIFY_TOKEN",
        META_VERIFY_TOKEN
    )

    return TestClient(app)


def test_webhook_verificacao_com_token_valido(
    client
):
    # Dados enviados pela Meta durante o handshake.
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": META_VERIFY_TOKEN,
            "hub.challenge": "123456789"
        }
    )

    # O endpoint deve aceitar a verificação.
    assert response.status_code == 200

    # Deve devolver exatamente o challenge recebido.
    assert response.text == "123456789"


def test_webhook_verificacao_rejeita_token_invalido(
    client
):
    # Envia um token diferente daquele configurado.
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "token-errado",
            "hub.challenge": "123456789"
        }
    )

    assert response.status_code == 403


def test_webhook_endpoint_com_assinatura_valida(
    client,
    monkeypatch
):
    # Cria o WebhookService falso.
    webhook_service = criar_webhook_service_mock(
        monkeypatch
    )

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

    # Serializa o corpo manualmente para garantir
    # que a assinatura seja calculada sobre os mesmos bytes
    # que serão enviados ao endpoint.
    payload_bytes = json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")

    assinatura = criar_assinatura(
        payload_bytes
    )

    response = client.post(
        "/webhook",
        content=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": assinatura
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "success"
    }

    # Confirma que a requisição realmente chegou
    # ao WebhookService depois da validação.
    webhook_service.process.assert_awaited_once()


def test_webhook_endpoint_rejeita_assinatura_invalida(
    client,
    monkeypatch
):
    webhook_service = criar_webhook_service_mock(
        monkeypatch
    )

    payload = {
        "object": "whatsapp_business_account"
    }

    payload_bytes = json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")

    resposta = client.post(
        "/webhook",
        content=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=assinatura-falsa"
        }
    )

    assert resposta.status_code == 401

    # A requisição deve ser rejeitada antes
    # de chegar ao WebhookService.
    webhook_service.process.assert_not_awaited()


def test_webhook_endpoint_rejeita_assinatura_ausente(
    client,
    monkeypatch
):
    webhook_service = criar_webhook_service_mock(
        monkeypatch
    )

    payload = {
        "object": "whatsapp_business_account"
    }

    payload_bytes = json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")

    response = client.post(
        "/webhook",
        content=payload_bytes,
        headers={
            "Content-Type": "application/json"
        }
    )

    assert response.status_code == 401

    webhook_service.process.assert_not_awaited()


def test_webhook_endpoint_rejeita_payload_alterado(
    client,
    monkeypatch
):
    webhook_service = criar_webhook_service_mock(
        monkeypatch
    )

    payload_original = {
        "object": "whatsapp_business_account"
    }

    payload_alterado = {
        "object": "objeto-alterado"
    }

    payload_original_bytes = json.dumps(
        payload_original,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")

    payload_alterado_bytes = json.dumps(
        payload_alterado,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")

    # A assinatura corresponde ao corpo original.
    assinatura = criar_assinatura(
        payload_original_bytes
    )

    # Mas enviamos outro corpo.
    response = client.post(
        "/webhook",
        content=payload_alterado_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": assinatura
        }
    )

    # A assinatura não corresponde ao corpo recebido.
    assert response.status_code == 401

    webhook_service.process.assert_not_awaited()


def test_webhook_endpoint_rejeita_payload_invalido(
    client,
    monkeypatch
):
    webhook_service = criar_webhook_service_mock(
        monkeypatch
    )

    # Payload propositalmente inválido:
    # não possui o campo "entry" exigido pelo MetaDTO.
    payload = {
        "object": "whatsapp_business_account"
    }

    payload_bytes = json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")

    # A assinatura é válida para este corpo.
    # Assim conseguimos testar especificamente
    # a validação do MetaDTO.
    assinatura = criar_assinatura(
        payload_bytes
    )

    response = client.post(
        "/webhook",
        content=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": assinatura
        }
    )

    # A assinatura passou, mas o MetaDTO deve rejeitar o payload.
    assert response.status_code == 422

    # O WebhookService não deve ser executado.
    webhook_service.process.assert_not_awaited()