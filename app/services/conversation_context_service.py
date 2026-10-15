import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.repositories.conversa_repository import ConversaRepository
from app.models import Conversa
import app.models as models

logger = logging.getLogger(__name__)


class ConversationContextService:
    """
    Serviço para gerenciar contexto de conversas.

    Responsável por:
    - Carregar histórico de conversas
    - Manter contexto entre mensagens
    - Formatar mensagens para envio à IA
    - Persistir histórico após respostas
    """

    def __init__(self):
        self.repository = ConversaRepository()
        # Limite de mensagens que mantemos no histórico
        self.MAX_HISTORICO = 20

    def obter_ou_criar_conversa(
        self,
        usuario_id: int,
        contexto: dict = None,
        db: Session = None
    ) -> Conversa:
        """
        Obtém a conversa ativa do usuário ou cria uma nova.

        Args:
            usuario_id: ID do usuário
            contexto: Contexto opcional (viagem_id, empresa_id, etc)
            db: Sessão do banco de dados

        Returns:
            Conversa ativa do usuário
        """
        try:
            # Buscar conversa existente
            conversa = self.repository.buscar_por_usuario(
                usuario_id,
                db
            )

            if conversa:
                # Se há contexto novo, atualizar
                if contexto:
                    self.repository.atualizar_contexto(
                        conversa.id,
                        contexto,
                        db
                    )
                return conversa

            # Criar nova conversa
            logger.info(
                f"Criando nova conversa para usuário {usuario_id}"
            )
            return self.repository.criar(
                usuario_id,
                contexto,
                db
            )

        except Exception as e:
            logger.error(
                f"Erro ao obter/criar conversa: {e}"
            )
            raise

    def adicionar_mensagem_usuario(
        self,
        conversa_id: int,
        mensagem: str,
        db: Session = None
    ) -> Conversa:
        """
        Adiciona mensagem do usuário ao histórico.

        Args:
            conversa_id: ID da conversa
            mensagem: Texto da mensagem
            db: Sessão do banco de dados

        Returns:
            Conversa atualizada
        """
        try:
            return self.repository.adicionar_mensagem(
                conversa_id,
                role="user",
                conteudo=mensagem,
                db=db
            )
        except Exception as e:
            logger.error(
                f"Erro ao adicionar mensagem do usuário: {e}"
            )
            raise

    def adicionar_mensagem_assistente(
        self,
        conversa_id: int,
        mensagem: str,
        db: Session = None
    ) -> Conversa:
        """
        Adiciona resposta do assistente ao histórico.

        Args:
            conversa_id: ID da conversa
            mensagem: Texto da resposta
            db: Sessão do banco de dados

        Returns:
            Conversa atualizada
        """
        try:
            return self.repository.adicionar_mensagem(
                conversa_id,
                role="assistant",
                conteudo=mensagem,
                db=db
            )
        except Exception as e:
            logger.error(
                f"Erro ao adicionar mensagem do assistente: {e}"
            )
            raise

    def obter_historico_para_prompt(
        self,
        conversa_id: int,
        limite: int = None,
        db: Session = None
    ) -> list:
        """
        Obtém histórico formatado para enviar à IA.

        Retorna as mensagens em formato pronto para a API do OpenAI:
        [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."},
            ...
        ]

        Args:
            conversa_id: ID da conversa
            limite: Limite de mensagens (usa MAX_HISTORICO se None)
            db: Sessão do banco de dados

        Returns:
            Lista de mensagens formatadas
        """
        limite = limite or self.MAX_HISTORICO

        try:
            mensagens = self.repository.obter_ultimas_mensagens(
                conversa_id,
                limite,
                db
            )

            # Remover timestamp para compatibilidade com API OpenAI
            historico = [
                {
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                }
                for msg in mensagens
            ]

            return historico

        except Exception as e:
            logger.error(
                f"Erro ao obter histórico para prompt: {e}"
            )
            return []

    def obter_contexto(
        self,
        conversa_id: int,
        db: Session = None
    ) -> dict:
        """
        Obtém o contexto da conversa.

        Args:
            conversa_id: ID da conversa
            db: Sessão do banco de dados

        Returns:
            Dicionário com contexto (viagem_id, empresa_id, etc)
        """
        try:
            conversa = self.repository.buscar_por_id(
                conversa_id,
                db
            )

            if not conversa:
                return {}

            return conversa.contexto or {}

        except Exception as e:
            logger.error(
                f"Erro ao obter contexto da conversa: {e}"
            )
            return {}

    def renovar_conversa(
        self,
        usuario_id: int,
        novo_contexto: dict = None,
        db: Session = None
    ) -> Conversa:
        """
        Cria uma nova conversa, limpando o histórico anterior.

        Útil quando o usuário quer começar uma nova conversa
        sobre um novo tópico ou dentro de uma nova viagem.

        Args:
            usuario_id: ID do usuário
            novo_contexto: Novo contexto para a conversa
            db: Sessão do banco de dados

        Returns:
            Nova conversa criada
        """
        try:
            logger.info(
                f"Renovando conversa para usuário {usuario_id}"
            )
            return self.repository.criar(
                usuario_id,
                novo_contexto,
                db
            )
        except Exception as e:
            logger.error(
                f"Erro ao renovar conversa: {e}"
            )
            raise

    def limpar_historico(
        self,
        conversa_id: int,
        db: Session = None
    ) -> Conversa:
        """
        Limpa o histórico de mensagens de uma conversa.

        Args:
            conversa_id: ID da conversa
            db: Sessão do banco de dados

        Returns:
            Conversa com histórico limpo
        """
        try:
            logger.info(
                f"Limpando histórico da conversa {conversa_id}"
            )
            return self.repository.limpar_historico(
                conversa_id,
                db
            )
        except Exception as e:
            logger.error(
                f"Erro ao limpar histórico: {e}"
            )
            raise

    def obter_tamanho_historico(
        self,
        conversa_id: int,
        db: Session = None
    ) -> int:
        """
        Obtém o número de mensagens no histórico.

        Args:
            conversa_id: ID da conversa
            db: Sessão do banco de dados

        Returns:
            Número de mensagens
        """
        try:
            conversa = self.repository.buscar_por_id(
                conversa_id,
                db
            )

            if not conversa:
                return 0

            return len(conversa.mensagens or [])

        except Exception as e:
            logger.error(
                f"Erro ao obter tamanho do histórico: {e}"
            )
            return 0

    def atualizar_viagem_empresa(
        self,
        conversa_id: int,
        viagem_id: int = None,
        empresa_id: int = None,
        db: Session = None
    ) -> Conversa:
        """
        Atualiza IDs de viagem e empresa na conversa (Item 9).

        Args:
            conversa_id: ID da conversa
            viagem_id: ID da viagem (None = manter existente)
            empresa_id: ID da empresa (None = manter existente)
            db: Sessão do banco de dados

        Returns:
            Conversa atualizada

        Raises:
            ValueError: Se conversa não existe
        """
        try:
            conversa = self.repository.buscar_por_id(conversa_id, db)
            if not conversa:
                raise ValueError(f"Conversa {conversa_id} não encontrada")

            # Validar se viagem e empresa existem
            if viagem_id is not None:
                viagem = db.query(models.Viagem).get(viagem_id)
                if not viagem:
                    logger.warning(f"Viagem {viagem_id} não encontrada")
                else:
                    conversa.viagem_id = viagem_id

            if empresa_id is not None:
                empresa = db.query(models.Empresa).get(empresa_id)
                if not empresa:
                    logger.warning(f"Empresa {empresa_id} não encontrada")
                else:
                    conversa.empresa_id = empresa_id

            conversa.atualizado_em = datetime.utcnow()

            db.add(conversa)
            db.commit()
            db.refresh(conversa)

            logger.info(
                f"Conversa {conversa_id} atualizada: "
                f"viagem_id={conversa.viagem_id}, empresa_id={conversa.empresa_id}"
            )

            return conversa

        except Exception as e:
            logger.error(f"Erro ao atualizar viagem/empresa: {e}")
            raise

    def obter_contexto_completo(
        self,
        conversa_id: int,
        db: Session = None
    ) -> dict:
        """
        Obtém contexto completo da conversa incluindo dados de viagem/empresa (Item 9).

        Args:
            conversa_id: ID da conversa
            db: Sessão do banco de dados

        Returns:
            Dict com contexto completo:
            {
                "viagem_id": 123,
                "empresa_id": 5,
                "viagem": {...},
                "empresa": {...},
                "metadata": {...}
            }
        """
        try:
            conversa = self.repository.buscar_por_id(conversa_id, db)
            if not conversa:
                return {}

            contexto = {
                "viagem_id": conversa.viagem_id,
                "empresa_id": conversa.empresa_id,
                "metadata": conversa.contexto or {}
            }

            # Lazy-load dados da viagem
            if conversa.viagem_id:
                viagem = db.query(models.Viagem).get(conversa.viagem_id)
                if viagem:
                    contexto["viagem"] = {
                        "id": viagem.id,
                        "usuario_id": viagem.usuario_id,
                        "status": viagem.status,
                        "detalhes": viagem.detalhes,
                        "criado_em": viagem.criado_em.isoformat() if viagem.criado_em else None
                    }

            # Lazy-load dados da empresa
            if conversa.empresa_id:
                empresa = db.query(models.Empresa).get(conversa.empresa_id)
                if empresa:
                    contexto["empresa"] = {
                        "id": empresa.id,
                        "nome": empresa.nome,
                        "cnpj": empresa.cnpj,
                        "criado_em": empresa.criado_em.isoformat() if empresa.criado_em else None
                    }

            return contexto

        except Exception as e:
            logger.error(f"Erro ao obter contexto completo: {e}")
            return {}

    def obter_ultima_mensagem(
        self,
        conversa_id: int,
        db: Session = None
    ) -> dict:
        """
        Obtém a última mensagem do histórico.

        Args:
            conversa_id: ID da conversa
            db: Sessão do banco de dados

        Returns:
            Dicionário com última mensagem ou None
        """
        try:
            historico = self.repository.obter_ultimas_mensagens(
                conversa_id,
                limite=1,
                db=db
            )

            return historico[0] if historico else None

        except Exception as e:
            logger.error(
                f"Erro ao obter última mensagem: {e}"
            )
            return None
