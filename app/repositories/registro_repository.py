import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models import Registro


logger = logging.getLogger(__name__)


class RegistroRepository:

    def salvar(
        self,
        usuario_id: int,
        tipo: str,
        dados: dict,
        db: Session
    ) -> Registro:
        """
        Salva um registro sem idempotência.

        Use este método quando não há risco de requisições duplicadas.
        Para operações que podem ser retentadas, use salvar_idempotente().

        Args:
            usuario_id: ID do usuário
            tipo: Tipo de registro (registrar_km, registrar_viagem, etc)
            dados: Dados do registro (JSON)
            db: Sessão SQLAlchemy

        Returns:
            Registro criado
        """
        registro = Registro(
            usuario_id=usuario_id,
            tipo=tipo,
            dados=dados,
            criado_em=datetime.now(timezone.utc)
        )

        db.add(registro)
        db.commit()
        db.refresh(registro)

        logger.info(
            f"Registro criado: usuario_id={usuario_id}, tipo={tipo}, id={registro.id}"
        )

        return registro

    def salvar_idempotente(
        self,
        usuario_id: int,
        tipo: str,
        dados: dict,
        idempotency_key: str,
        db: Session,
        viagem_id: Optional[int] = None,
        empresa_id: Optional[int] = None,
    ) -> tuple[Registro, bool]:
        """
        Salva um registro com garantia de idempotência.

        Se um registro com a mesma (usuario_id, tipo, idempotency_key)
        já existe, retorna o existente em vez de criar um novo.

        Isso garante que requisições duplicadas (retentativas) não
        criam registros duplicados no banco de dados.

        Args:
            usuario_id: ID do usuário
            tipo: Tipo de registro
            dados: Dados do registro
            idempotency_key: Chave única para idempotência (ex: UUID v4)
            db: Sessão SQLAlchemy
            viagem_id: ID da viagem (opcional)
            empresa_id: ID da empresa (opcional)

        Returns:
            Tupla (Registro, foi_criado):
            - Registro: O registro criado ou existente
            - foi_criado: True se foi criado agora, False se já existia
        """
        # Buscar registro existente com mesma idempotency_key
        registro_existente = self.buscar_por_idempotency_key(
            usuario_id=usuario_id,
            tipo=tipo,
            idempotency_key=idempotency_key,
            db=db
        )

        if registro_existente:
            logger.info(
                f"Registro duplicado detectado: usuario_id={usuario_id}, "
                f"tipo={tipo}, idempotency_key={idempotency_key}. "
                f"Retornando registro existente id={registro_existente.id}"
            )
            return registro_existente, False

        # Criar novo registro
        registro = Registro(
            usuario_id=usuario_id,
            tipo=tipo,
            dados=dados,
            idempotency_key=idempotency_key,
            viagem_id=viagem_id,
            empresa_id=empresa_id,
            criado_em=datetime.now(timezone.utc)
        )

        db.add(registro)
        db.commit()
        db.refresh(registro)

        logger.info(
            f"Novo registro criado com idempotência: "
            f"usuario_id={usuario_id}, tipo={tipo}, "
            f"idempotency_key={idempotency_key}, id={registro.id}"
        )

        return registro, True

    def buscar_por_idempotency_key(
        self,
        usuario_id: int,
        tipo: str,
        idempotency_key: str,
        db: Session
    ) -> Optional[Registro]:
        """
        Busca um registro existente por sua idempotency_key.

        Args:
            usuario_id: ID do usuário
            tipo: Tipo de registro
            idempotency_key: Chave de idempotência
            db: Sessão SQLAlchemy

        Returns:
            Registro existente ou None
        """
        return (
            db.query(Registro)
            .filter(
                and_(
                    Registro.usuario_id == usuario_id,
                    Registro.tipo == tipo,
                    Registro.idempotency_key == idempotency_key
                )
            )
            .first()
        )

    def buscar_por_tipo_e_periodo(
            self,
            usuario_id: int,
            tipo: str,
            data_inicio: datetime,
            data_fim: datetime,
            db: Session
    ):
        """
        Busca registros em uma janela de tempo.

        Args:
            usuario_id: ID do usuário
            tipo: Tipo de registro
            data_inicio: Data/hora inicial (inclusive)
            data_fim: Data/hora final (exclusive)
            db: Sessão SQLAlchemy

        Returns:
            Lista de registros
        """
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