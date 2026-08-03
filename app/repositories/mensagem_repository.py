from sqlalchemy.orm import Session

import app.models as models


class MensagemRepository:

    def salvar(
        self,
        texto: str,
        usuario_id: int,
        db: Session
    ):

        mensagem = models.Mensagem(
            texto=texto,
            usuario_id=usuario_id
        )

        db.add(mensagem)

        db.commit()

        db.refresh(mensagem)

        return mensagem