from sqlalchemy.orm import Session

from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.mensagem_repository import MensagemRepository

from app.schemas.meta import MetaDTO
from app.schemas.ai_response import AIResponseDTO, Intent

from app.services.ai_service import AIService
from app.services.whatsapp_service import WhatsAppService


class WebhookService:

    def __init__(self):

        self.usuario_repository = UsuarioRepository()

        self.mensagem_repository = MensagemRepository()

        self.ai_service = AIService()

        self.whatsapp_service = WhatsAppService()

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

        usuario = self._obter_ou_criar_usuario(
            telefone,
            db
        )

        self._salvar_mensagem(
            texto,
            usuario.id,
            db
        )

        resposta_ai = await self.ai_service.processar(
            texto
        )

        await self._executar_intent(
            resposta_ai,
            usuario.id,
            db
        )

        await self.whatsapp_service.enviar_mensagem(
            telefone,
            resposta_ai.resposta
        )

        return {
            "status": "success"
        }

    def _obter_ou_criar_usuario(
        self,
        telefone: str,
        db: Session
    ):

        usuario = self.usuario_repository.buscar_por_telefone(
            telefone,
            db
        )

        if usuario is None:

            usuario = self.usuario_repository.criar(
                telefone,
                db
            )

        return usuario

    def _salvar_mensagem(
        self,
        texto: str,
        usuario_id: int,
        db: Session
    ):

        self.mensagem_repository.salvar(
            texto,
            usuario_id,
            db
        )

    async def _executar_intent(
        self,
        resposta: AIResponseDTO,
        usuario_id: int,
        db: Session
    ):

        if resposta.intent == Intent.REGISTRAR_KM:
            pass

        elif resposta.intent == Intent.REGISTRAR_VIAGEM:
            pass

        elif resposta.intent == Intent.REGISTRAR_ABASTECIMENTO:
            pass

        elif resposta.intent == Intent.CONSULTAR_KM:
            pass

        elif resposta.intent == Intent.CONSULTAR_VIAGENS:
            pass

        elif resposta.intent == Intent.CONVERSA:
            pass

        elif resposta.intent == Intent.AJUDA:
            pass