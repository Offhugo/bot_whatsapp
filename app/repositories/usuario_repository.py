from sqlalchemy.orm import Session

import app.models as models


class UsuarioRepository:

    def buscar_por_telefone(
        self,
        telefone: str,
        db: Session
    ):

        return (
            db.query(models.Usuario)
            .filter(models.Usuario.telefone == telefone)
            .first()
        )

    def criar(
        self,
        telefone: str,
        db: Session
    ):

        usuario = models.Usuario(
            telefone=telefone
        )

        db.add(usuario)

        db.commit()

        db.refresh(usuario)

        return usuario