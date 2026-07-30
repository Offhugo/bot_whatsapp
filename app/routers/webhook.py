from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.meta import MetaDTO
from app.services.webhook_service import WebhookService

router = APIRouter()

webhook_service = WebhookService()


@router.post("/webhook")
async def receber_mensagem(
    payload: MetaDTO,
    db: Session = Depends(get_db)
):
    return await webhook_service.process(payload, db)