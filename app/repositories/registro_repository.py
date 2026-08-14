from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import Registro


class RegistroRepository:

    # Metodo que salva um user no sistem, com o minimo de informações importantes
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

    # Método busca ALGO em uma janela de tempo
    def buscar_por_tipo_e_periodo(
            self,
            usuario_id: int,
            tipo: str,
            data_inicio: datetime,
            data_fim: datetime,
            db: Session
    ):
        return (
            db.query(Registro)
            .filter(
                Registro.usuario_id == usuario_id,
                Registro.tipo == tipo,
                Registro.criado_em >= data_inicio,
                Registro.criado_em < data_fim
            )
            .all()
        )