from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import Registro


class RegistroRepository:

    def salvar(
        self,
        usuario_id: int,
        tipo: str,
        dados: dict,
        db: Session
    ) -> Registro:

        registro = Registro(
            usuario_id=usuario_id,
            tipo=tipo,
            dados=dados,
            criado_em=datetime.now(timezone.utc)
        )

        db.add(registro)
        db.commit()
        db.refresh(registro)

        return registro