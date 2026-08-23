import pytest
import httpx

from app.services.whatsapp_service import WhatsAppService


@pytest.mark.anyio
async def test_enviar_mensagem_com_erro(monkeypatch):

    # Configura credenciais fictícias para o ambiente de teste
    monkeypatch.setenv(
        "WHATSAPP_ACCESS_TOKEN",
        "token-teste"
    )

    monkeypatch.setenv(
        "WHATSAPP_PHONE_NUMBER_ID",
        "123456789"
    )

    monkeypatch.setenv(
        "WHATSAPP_API_VERSION",
        "v1.0"
    )

    # Simula uma resposta de erro da Meta
    def handler(request: httpx.Request):

        return httpx.Response(
            status_code=400,
            json={
                "error": {
                    "message": "Número de telefone inválido"
                }
            }
        )

    transport = httpx.MockTransport(handler)

    service = WhatsAppService()

    # Substitui temporariamente o cliente HTTP real pelo cliente de teste
    original_client = httpx.AsyncClient

    class TestAsyncClient(original_client):

        def __init__(self, *args, **kwargs):
            super().__init__(
                transport=transport,
                *args,
                **kwargs
            )

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        TestAsyncClient
    )

    # A API respondeu com erro e o serviço deve propagar a exceção
    with pytest.raises(httpx.HTTPStatusError):
        await service.enviar_mensagem(
            telefone="5511999999999",
            mensagem="Teste de erro."
        )