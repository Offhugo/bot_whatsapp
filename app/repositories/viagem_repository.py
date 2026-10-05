from sqlalchemy.orm import Session

from app.models import Viagem


class ViagemRepository:

    def buscar_por_id(
        self,
        viagem_id: int,
        db: Session
    ):
        return (
            db.query(Viagem)
            .filter(Viagem.id == viagem_id)
            .first()
        )