from sqlalchemy.orm import Session

from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.mensagem_repository import MensagemRepository
from app.schemas.meta import MetaDTO


class WebhookService:

    def __init__(self):

        self.usuario_repository = UsuarioRepository()
        self.mensagem_repository = MensagemRepository()

    async def process(
        self,
        payload: MetaDTO,
        db: Session
    ):

        value = payload.entry[0].changes[0].value

        if not value.messages:
            return {
                "status": "ignored"
            }

        telefone = value.contacts[0].wa_id
        texto = value.messages[0].text.body

        usuario = self.usuario_repository.buscar_por_telefone(
            telefone,
            db
        )

        if usuario is None:

            usuario = self.usuario_repository.criar(
                telefone,
                db
            )

        self.mensagem_repository.salvar(
            texto,
            usuario.id,
            db
        )

        return {
            "status": "success"
        }