from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.mensagem_repository import MensagemRepository
from app.repositories.registro_repository import RegistroRepository

from app.services.ai_service import AIService
from app.services.whatsapp_service import WhatsAppService
from app.services.webhook_service import WebhookService

from app.use_cases.registrar_km import RegistrarKMUseCase
from app.use_cases.registrar_abastecimento import RegistrarAbastecimentoUseCase
from app.use_cases.registrar_viagem import RegistrarViagemUseCase
from app.use_cases.consultar_km import ConsultarKMUseCase
from app.use_cases.consultar_viagens import ConsultarViagensUseCase

from app.schemas.meta import MetaDTO


router = APIRouter()


def criar_webhook_service() -> WebhookService:
    registro_repository = RegistroRepository()

    return WebhookService(
        usuario_repository=UsuarioRepository(),
        mensagem_repository=MensagemRepository(),
        ai_service=AIService(),
        whatsapp_service=WhatsAppService(),
        registrar_km_use_case=RegistrarKMUseCase(
            registro_repository
        ),
        registrar_abastecimento_use_case=RegistrarAbastecimentoUseCase(
            registro_repository
        ),
        registrar_viagem_use_case=RegistrarViagemUseCase(
            registro_repository
        ),
        consultar_km_use_case=ConsultarKMUseCase(
            registro_repository
        ),
        consultar_viagens_use_case=ConsultarViagensUseCase(
            registro_repository
        ),
    )


webhook_service = criar_webhook_service()


@router.post("/webhook")
async def webhook(
    payload: MetaDTO,
    db: Session = Depends(get_db)
):
    return await webhook_service.process(
        payload,
        db
    )