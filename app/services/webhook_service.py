from sqlalchemy.orm import Session

import app.models as models
from app.schemas.meta import MetaDTO


class WebhookService:

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

        print(f"Telefone: {telefone}")
        print(f"Mensagem: {texto}")

        usuario = (
            db.query(models.Usuario)
            .filter(models.Usuario.telefone == telefone)
            .first()
        )

        if usuario is None:

            usuario = models.Usuario(
                telefone=telefone
            )

            db.add(usuario)

            db.commit()

            db.refresh(usuario)

        mensagem = models.Mensagem(
            texto=texto,
            usuario_id=usuario.id
        )

        db.add(mensagem)

        db.commit()

        return {
            "status": "success"
        }