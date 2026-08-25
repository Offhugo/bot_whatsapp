import pytest

from app.services.whatsapp_service import WhatsAppService


@pytest.mark.anyio
async def test_whatsapp_service_sem_access_token(monkeypatch):

    # Remove o token do ambiente de teste
    monkeypatch.delenv(
        "WHATSAPP_ACCESS_TOKEN",
        raising=False
    )

    # Mantém as outras configurações disponíveis
    monkeypatch.setenv(
        "WHATSAPP_PHONE_NUMBER_ID",
        "123456789"
    )

    monkeypatch.setenv(
        "WHATSAPP_API_VERSION",
        "v1.0"
    )

    service = WhatsAppService()

    # Sem token, o serviço deve interromper antes de tentar
    # qualquer requisição HTTP
    with pytest.raises(
        RuntimeError,
        match="WHATSAPP_ACCESS_TOKEN não configurado."
    ):
        await service.enviar_mensagem(
            telefone="5511999999999",
            mensagem="Mensagem de teste."
        )


@pytest.mark.anyio
async def test_whatsapp_service_sem_phone_number_id(monkeypatch):

    # Mantém o token configurado
    monkeypatch.setenv(
        "WHATSAPP_ACCESS_TOKEN",
        "token-teste"
    )

    # Remove o Phone Number ID
    monkeypatch.delenv(
        "WHATSAPP_PHONE_NUMBER_ID",
        raising=False
    )

    monkeypatch.setenv(
        "WHATSAPP_API_VERSION",
        "v1.0"
    )

    service = WhatsAppService()

    with pytest.raises(
        RuntimeError,
        match="WHATSAPP_PHONE_NUMBER_ID não configurado."
    ):
        await service.enviar_mensagem(
            telefone="5511999999999",
            mensagem="Mensagem de teste."
        )