from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models import Usuario, UsuarioEmpresa, Viagem
from app.schemas.ai_response import AIResponseDTO, Intent
from app.services.autorizacao_service import AutorizacaoService
from app.services.webhook_service import WebhookService


def criar_webhook_service():
    return WebhookService(
        usuario_repository=MagicMock(),
        mensagem_repository=MagicMock(),
        viagem_repository=MagicMock(),
        ai_service=MagicMock(),
        whatsapp_service=MagicMock(),
        autorizacao_service=AutorizacaoService(),
        registrar_km_use_case=MagicMock(),
        registrar_abastecimento_use_case=MagicMock(),
        registrar_viagem_use_case=MagicMock(),
        consultar_km_use_case=MagicMock(),
        consultar_viagens_use_case=MagicMock(),
    )


def criar_payload(
    telefone="5511999999999",
    texto="Na viagem 10 rodei 500 km"
):
    payload = MagicMock()

    value = payload.entry[0].changes[0].value

    mensagem = MagicMock()
    mensagem.text.body = texto

    contato = MagicMock()
    contato.wa_id = telefone

    value.messages = [mensagem]
    value.contacts = [contato]

    return payload


@pytest.mark.anyio
async def test_process_executa_operacao_quando_usuario_e_autorizado():
    service = criar_webhook_service()

    usuario = Usuario(
        id=1,
        telefone="5511999999999",
        perfil="motorista"
    )

    viagem = Viagem(
        id=10,
        usuario_id=1,
        empresa_id=5
    )

    resposta_ai = AIResponseDTO(
        intent=Intent.REGISTRAR_KM,
        dados={
            "viagem_id": 10,
            "quilometros": 500
        },
        resposta="Entendi."
    )

    service.usuario_repository.buscar_por_telefone.return_value = usuario
    service.viagem_repository.buscar_por_id.return_value = viagem
    service.ai_service.processar = AsyncMock(
        return_value=resposta_ai
    )

    service.registrar_km_use_case.executar.return_value = {
        "mensagem": "KM registrado."
    }

    service.whatsapp_service.enviar_mensagem = AsyncMock()

    resultado = await service.process(
        criar_payload(),
        MagicMock()
    )

    assert resultado == {
        "status": "success"
    }

    service.mensagem_repository.salvar.assert_called_once()

    service.ai_service.processar.assert_awaited_once_with(
        "Na viagem 10 rodei 500 km"
    )

    assert service.viagem_repository.buscar_por_id.call_args.args[0] == 10

    service.registrar_km_use_case.executar.assert_called_once()

    service.whatsapp_service.enviar_mensagem.assert_awaited_once_with(
        "5511999999999",
        "KM registrado."
    )


@pytest.mark.anyio
async def test_process_bloqueia_operacao_quando_usuario_nao_tem_autorizacao():
    service = criar_webhook_service()

    usuario = Usuario(
        id=1,
        telefone="5511999999999",
        perfil="motorista"
    )

    viagem = Viagem(
        id=10,
        usuario_id=2,
        empresa_id=5
    )

    resposta_ai = AIResponseDTO(
        intent=Intent.REGISTRAR_KM,
        dados={
            "viagem_id": 10,
            "quilometros": 500
        },
        resposta="Entendi."
    )

    service.usuario_repository.buscar_por_telefone.return_value = usuario
    service.viagem_repository.buscar_por_id.return_value = viagem
    service.ai_service.processar = AsyncMock(
        return_value=resposta_ai
    )

    service.whatsapp_service.enviar_mensagem = AsyncMock()

    resultado = await service.process(
        criar_payload(),
        MagicMock()
    )

    assert resultado == {
        "status": "success"
    }

    service.registrar_km_use_case.executar.assert_not_called()

    service.whatsapp_service.enviar_mensagem.assert_awaited_once_with(
        "5511999999999",
        "Você não possui autorização para acessar essa viagem."
    )


@pytest.mark.anyio
async def test_process_cria_usuario_quando_telefone_nao_existe():
    service = criar_webhook_service()

    usuario = Usuario(
        id=1,
        telefone="5511999999999",
        perfil="motorista"
    )

    resposta_ai = AIResponseDTO(
        intent=Intent.CONVERSA,
        dados={},
        resposta="Olá! Como posso ajudar?"
    )

    service.usuario_repository.buscar_por_telefone.return_value = None
    service.usuario_repository.criar.return_value = usuario

    service.ai_service.processar = AsyncMock(
        return_value=resposta_ai
    )

    service.whatsapp_service.enviar_mensagem = AsyncMock()

    resultado = await service.process(
        criar_payload(
            texto="Olá"
        ),
        MagicMock()
    )

    assert resultado == {
        "status": "success"
    }

    service.usuario_repository.criar.assert_called_once_with(
        "5511999999999",
        service.usuario_repository.criar.call_args.args[1]
    )

    service.mensagem_repository.salvar.assert_called_once()

    service.whatsapp_service.enviar_mensagem.assert_awaited_once_with(
        "5511999999999",
        "Olá! Como posso ajudar?"
    )


@pytest.mark.anyio
async def test_process_ignora_payload_sem_mensagens():
    service = criar_webhook_service()

    payload = MagicMock()

    value = payload.entry[0].changes[0].value
    value.messages = []

    resultado = await service.process(
        payload,
        MagicMock()
    )

    assert resultado == {
        "status": "ignored"
    }

    service.usuario_repository.buscar_por_telefone.assert_not_called()
    service.ai_service.processar.assert_not_called()
    service.whatsapp_service.enviar_mensagem.assert_not_called()