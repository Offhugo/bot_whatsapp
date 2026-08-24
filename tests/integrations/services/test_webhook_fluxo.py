from unittest.mock import AsyncMock, Mock

import pytest

from app.models import Registro, Usuario
from app.repositories.mensagem_repository import MensagemRepository
from app.repositories.registro_repository import RegistroRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.ai_response import AIResponseDTO, Intent
from app.schemas.meta import (
    ChangeDTO,
    ContactDTO,
    EntryDTO,
    MessageDTO,
    MetaDTO,
    TextDTO,
    ValueDTO,
)
from app.services.webhook_service import WebhookService
from app.use_cases.consultar_km import ConsultarKMUseCase
from app.use_cases.consultar_viagens import ConsultarViagensUseCase
from app.use_cases.registrar_abastecimento import RegistrarAbastecimentoUseCase
from app.use_cases.registrar_km import RegistrarKMUseCase
from app.use_cases.registrar_viagem import RegistrarViagemUseCase


@pytest.mark.anyio
async def test_fluxo_completo_registrar_km(db):

    # Cria o Repository responsável pelos registros
    registro_repository = RegistroRepository()

    # Cria os Use Cases reais
    registrar_km_use_case = RegistrarKMUseCase(
        registro_repository
    )

    registrar_abastecimento_use_case = RegistrarAbastecimentoUseCase(
        registro_repository
    )

    registrar_viagem_use_case = RegistrarViagemUseCase(
        registro_repository
    )

    consultar_km_use_case = ConsultarKMUseCase(
        registro_repository
    )

    consultar_viagens_use_case = ConsultarViagensUseCase(
        registro_repository
    )

    # Cria os componentes externos simulados
    ai_service = Mock()

    whatsapp_service = Mock()

    ai_service.processar = AsyncMock(
        return_value=AIResponseDTO(
            intent=Intent.REGISTRAR_KM,
            dados={
                "quilometros": 430
            },
            resposta="Registrei seus 430 km."
        )
    )

    whatsapp_service.enviar_mensagem = AsyncMock()

    # Cria o WebhookService real com todas as dependências
    service = WebhookService(
        usuario_repository=UsuarioRepository(),
        mensagem_repository=MensagemRepository(),
        ai_service=ai_service,
        whatsapp_service=whatsapp_service,
        registrar_km_use_case=registrar_km_use_case,
        registrar_abastecimento_use_case=registrar_abastecimento_use_case,
        registrar_viagem_use_case=registrar_viagem_use_case,
        consultar_km_use_case=consultar_km_use_case,
        consultar_viagens_use_case=consultar_viagens_use_case,
    )

    # Simula o JSON recebido da Meta através dos Schemas reais
    payload = MetaDTO(
        object="whatsapp_business_account",
        entry=[
            EntryDTO(
                changes=[
                    ChangeDTO(
                        value=ValueDTO(
                            contacts=[
                                ContactDTO(
                                    wa_id="5511999999999"
                                )
                            ],
                            messages=[
                                MessageDTO(
                                    text=TextDTO(
                                        body="Rodei 430 km hoje."
                                    )
                                )
                            ]
                        )
                    )
                ]
            )
        ]
    )

    # Executa o fluxo completo
    resultado = await service.process(
        payload,
        db
    )

    # Valida a resposta final do WebhookService
    assert resultado == {
        "status": "success"
    }

    # Garante que a IA realmente foi chamada
    ai_service.processar.assert_awaited_once_with(
        "Rodei 430 km hoje."
    )

    # Garante que a resposta foi enviada ao WhatsApp
    whatsapp_service.enviar_mensagem.assert_awaited_once_with(
        "5511999999999",
        "Registrei seus 430 km."
    )

    # Confirma que o usuário foi realmente criado
    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.telefone == "5511999999999"
        )
        .first()
    )

    assert usuario is not None

    # Confirma que o registro foi realmente persistido
    registro = (
        db.query(Registro)
        .filter(
            Registro.usuario_id == usuario.id,
            Registro.tipo == "km"
        )
        .first()
    )

    assert registro is not None
    assert registro.dados["quilometros"] == 430