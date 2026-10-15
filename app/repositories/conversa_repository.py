from datetime import datetime
from sqlalchemy.orm import Session

import app.models as models


class ConversaRepository:
    """
    Repositório para operações com conversas.

    Responsável por persistir e recuperar históricos de conversas
    com mensagens e contexto.
    """

    def criar(
        self,
        usuario_id: int,
        contexto: dict = None,
        db: Session = None
    ) -> models.Conversa:
        """
        Cria uma nova conversa para um usuário.

        Args:
            usuario_id: ID do usuário
            contexto: Contexto opcional (ex: viagem_id, empresa_id)
            db: Sessão do banco de dados

        Returns:
            Conversa criada
        """
        agora = datetime.utcnow()

        conversa = models.Conversa(
            usuario_id=usuario_id,
            mensagens=[],
            contexto=contexto or {},
            criado_em=agora,
            atualizado_em=agora
        )

        db.add(conversa)
        db.commit()
        db.refresh(conversa)

        return conversa

    def buscar_por_id(
        self,
        conversa_id: int,
        db: Session
    ) -> models.Conversa:
        """
        Busca uma conversa por ID.

        Args:
            conversa_id: ID da conversa
            db: Sessão do banco de dados

        Returns:
            Conversa encontrada ou None
        """
        return (
            db.query(models.Conversa)
            .filter(models.Conversa.id == conversa_id)
            .first()
        )

    def buscar_por_usuario(
        self,
        usuario_id: int,
        db: Session
    ) -> models.Conversa:
        """
        Busca a conversa ativa mais recente de um usuário.

        Args:
            usuario_id: ID do usuário
            db: Sessão do banco de dados

        Returns:
            Conversa mais recente do usuário ou None
        """
        return (
            db.query(models.Conversa)
            .filter(models.Conversa.usuario_id == usuario_id)
            .order_by(models.Conversa.atualizado_em.desc())
            .first()
        )

    def adicionar_mensagem(
        self,
        conversa_id: int,
        role: str,
        conteudo: str,
        timestamp: str = None,
        db: Session = None
    ) -> models.Conversa:
        """
        Adiciona uma mensagem ao histórico da conversa.

        Args:
            conversa_id: ID da conversa
            role: "user" ou "assistant"
            conteudo: Texto da mensagem
            timestamp: Timestamp ISO (opcional, usa UTC agora)
            db: Sessão do banco de dados

        Returns:
            Conversa atualizada

        Raises:
            ValueError: Se role inválido
        """
        if role not in ["user", "assistant"]:
            raise ValueError(f"Role inválido: {role}. Use 'user' ou 'assistant'")

        conversa = self.buscar_por_id(conversa_id, db)
        if not conversa:
            raise ValueError(f"Conversa {conversa_id} não encontrada")

        timestamp = timestamp or datetime.utcnow().isoformat()

        # Adicionar mensagem ao array
        nova_mensagem = {
            "role": role,
            "content": conteudo,
            "timestamp": timestamp
        }

        # mensagens é um JSONB array
        mensagens = conversa.mensagens or []
        mensagens.append(nova_mensagem)

        conversa.mensagens = mensagens
        conversa.atualizado_em = datetime.utcnow()

        db.add(conversa)
        db.commit()
        db.refresh(conversa)

        return conversa

    def obter_ultimas_mensagens(
        self,
        conversa_id: int,
        limite: int = 10,
        db: Session = None
    ) -> list:
        """
        Obtém as últimas N mensagens de uma conversa.

        Args:
            conversa_id: ID da conversa
            limite: Número máximo de mensagens (default 10)
            db: Sessão do banco de dados

        Returns:
            Lista de mensagens mais recentes
        """
        conversa = self.buscar_por_id(conversa_id, db)
        if not conversa:
            return []

        mensagens = conversa.mensagens or []

        # Retorna as últimas 'limite' mensagens
        return mensagens[-limite:] if len(mensagens) > limite else mensagens

    def atualizar_contexto(
        self,
        conversa_id: int,
        contexto: dict,
        db: Session = None
    ) -> models.Conversa:
        """
        Atualiza o contexto de uma conversa.

        Args:
            conversa_id: ID da conversa
            contexto: Novo contexto (será merged com existente)
            db: Sessão do banco de dados

        Returns:
            Conversa atualizada
        """
        conversa = self.buscar_por_id(conversa_id, db)
        if not conversa:
            raise ValueError(f"Conversa {conversa_id} não encontrada")

        # Merge com contexto existente
        contexto_atual = conversa.contexto or {}
        contexto_atual.update(contexto)

        conversa.contexto = contexto_atual
        conversa.atualizado_em = datetime.utcnow()

        db.add(conversa)
        db.commit()
        db.refresh(conversa)

        return conversa

    def limpar_historico(
        self,
        conversa_id: int,
        db: Session = None
    ) -> models.Conversa:
        """
        Limpa o histórico de mensagens de uma conversa.

        Args:
            conversa_id: ID da conversa
            db: Sessão do banco de dados

        Returns:
            Conversa com histórico limpo
        """
        conversa = self.buscar_por_id(conversa_id, db)
        if not conversa:
            raise ValueError(f"Conversa {conversa_id} não encontrada")

        conversa.mensagens = []
        conversa.atualizado_em = datetime.utcnow()

        db.add(conversa)
        db.commit()
        db.refresh(conversa)

        return conversa

    def buscar_conversas_usuario(
        self,
        usuario_id: int,
        limite: int = 10,
        db: Session = None
    ) -> list:
        """
        Busca todas as conversas de um usuário.

        Args:
            usuario_id: ID do usuário
            limite: Número máximo de conversas
            db: Sessão do banco de dados

        Returns:
            Lista de conversas ordenadas por atualização recente
        """
        return (
            db.query(models.Conversa)
            .filter(models.Conversa.usuario_id == usuario_id)
            .order_by(models.Conversa.atualizado_em.desc())
            .limit(limite)
            .all()
        )
