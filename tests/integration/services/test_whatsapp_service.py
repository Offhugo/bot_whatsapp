
import httpx
import pytest

from app.services.whatsapp_service import WhatsAppService


@pytest.fixture
def configurar_whatsapp(monkeypatch):
    monkeypatch.setenv("WHATSAPP_ACCESS_TOKEN", "token-teste")
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "123456789")
    monkeypatch.setenv("WHATSAPP_API_VERSION", "v1.0")


@pytest.mark.anyio
async def test_enviar_mensagem_com_sucesso(
    monkeypatch,
    configurar_whatsapp,
):
    def handler(request: httpx.Request):
        assert str(request.url) == (
            "https://graph.facebook.com/v1.0/123456789/messages"
        )
        assert request.headers["authorization"] == "Bearer token-teste"
        assert request.headers["content-type"] == "application/json"

        return httpx.Response(
            status_code=200,
            json={"messages": [{"id": "wamid.test"}]},
        )

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    class TestAsyncClient(original_client):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = transport
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", TestAsyncClient)

    service = WhatsAppService()

    resposta = await service.enviar_mensagem(
        telefone="5511999999999",
        mensagem="Registrei seus 430 km.",
    )

    assert resposta["messages"][0]["id"] == "wamid.test"


@pytest.mark.anyio
async def test_enviar_mensagem_com_erro_http(
    monkeypatch,
    configurar_whatsapp,
):
    def handler(request: httpx.Request):
        return httpx.Response(
            status_code=400,
            json={"error": {"message": "Número inválido"}},
        )

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    class TestAsyncClient(original_client):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = transport
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", TestAsyncClient)

    service = WhatsAppService()

    with pytest.raises(httpx.HTTPStatusError):
        await service.enviar_mensagem(
            telefone="5511999999999",
            mensagem="Teste de erro.",
        )


@pytest.mark.anyio
async def test_enviar_mensagem_com_timeout(
    monkeypatch,
    configurar_whatsapp,
):
    def handler(request: httpx.Request):
        raise httpx.ReadTimeout("timeout simulado")

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    class TestAsyncClient(original_client):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = transport
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", TestAsyncClient)

    service = WhatsAppService()

    with pytest.raises(httpx.TimeoutException):
        await service.enviar_mensagem(
            telefone="5511999999999",
            mensagem="Teste de timeout.",
        )


@pytest.mark.anyio
async def test_enviar_mensagem_com_falha_de_conexao(
    monkeypatch,
    configurar_whatsapp,
):
    def handler(request: httpx.Request):
        raise httpx.ConnectError("conexão simulada")

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient

    class TestAsyncClient(original_client):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = transport
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", TestAsyncClient)

    service = WhatsAppService()

    with pytest.raises(httpx.ConnectError):
        await service.enviar_mensagem(
            telefone="5511999999999",
            mensagem="Teste de conexão.",
        )

        