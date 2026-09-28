from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request
)
from fastapi.responses import PlainTextResponse
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

from app.utils.meta_webhook_security import (
    verificar_token_meta,
    verificar_assinatura_meta
)


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


@router.get(
    "/webhook",
    response_class=PlainTextResponse
)
async def verificar_webhook(
    mode: str | None = Query(
        default=None,
        alias="hub.mode"
    ),
    verify_token: str | None = Query(
        default=None,
        alias="hub.verify_token"
    ),
    challenge: str | None = Query(
        default=None,
        alias="hub.challenge"
    )
):
    """
    Endpoint utilizado pela Meta para verificar
    se o webhook está configurado corretamente.
    """

    if mode != "subscribe":
        raise HTTPException(
            status_code=403,
            detail="Modo de verificação inválido."
        )

    if not verificar_token_meta(verify_token):
        raise HTTPException(
            status_code=403,
            detail="Token de verificação inválido."
        )

    if challenge is None:
        raise HTTPException(
            status_code=403,
            detail="Challenge não informado."
        )

    return challenge


async def validar_assinatura_do_webhook(
    request: Request
):
    """
    Intercepta o POST antes do processamento
    do WebhookService e valida a assinatura enviada
    pela Meta.
    """

    payload = await request.body()

    assinatura = request.headers.get(
        "X-Hub-Signature-256"
    )

    if not verificar_assinatura_meta(
        payload,
        assinatura
    ):
        raise HTTPException(
            status_code=401,
            detail="Assinatura do webhook inválida."
        )


@router.post("/webhook")
async def webhook(
    payload: MetaDTO,
    db: Session = Depends(get_db),
    _: None = Depends(validar_assinatura_do_webhook)
):
    return await webhook_service.process(
        payload,
        db
    )