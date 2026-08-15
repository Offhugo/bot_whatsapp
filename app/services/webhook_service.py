from sqlalchemy.orm import Session

from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.mensagem_repository import MensagemRepository
from app.repositories.registro_repository import RegistroRepository

from app.schemas.meta import MetaDTO
from app.schemas.ai_response import AIResponseDTO, Intent

from app.services.ai_service import AIService
from app.services.whatsapp_service import WhatsAppService

from app.use_cases.registrar_km import RegistrarKMUseCase
from app.use_cases.registrar_abastecimento import RegistrarAbastecimentoUseCase
from app.use_cases.registrar_viagem import RegistrarViagemUseCase
from app.use_cases.consultar_km import ConsultarKMUseCase
from app.use_cases.consultar_viagens import ConsultarViagensUseCase


class WebhookService:

    def __init__(self):

        self.usuario_repository = UsuarioRepository()
        self.mensagem_repository = MensagemRepository()

        self.ai_service = AIService()
        self.whatsapp_service = WhatsAppService()

        # Repository compartilhado pelos Use Cases
        self.registro_repository = RegistroRepository()

        # Use Cases
        self.registrar_km_use_case = RegistrarKMUseCase(
            self.registro_repository
        )

        self.registrar_abastecimento_use_case = RegistrarAbastecimentoUseCase(
            self.registro_repository
        )

        self.registrar_viagem_use_case = RegistrarViagemUseCase(
            self.registro_repository
        )

        self.consultar_km_use_case = ConsultarKMUseCase(
            self.registro_repository
        )

        self.consultar_viagens_use_case = ConsultarViagensUseCase(
            self.registro_repository
        )

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

        resultado = self._executar_intent(
            resposta_ai,
            usuario.id,
            db
        )

        resposta_final = self._obter_resposta(
            resposta_ai,
            resultado
        )

        await self.whatsapp_service.enviar_mensagem(
            telefone,
            resposta_final
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

    def _executar_intent(
        self,
        resposta: AIResponseDTO,
        usuario_id: int,
        db: Session
    ):

        if resposta.intent == Intent.REGISTRAR_KM:

            return self.registrar_km_use_case.executar(
                resposta,
                usuario_id,
                db
            )

        elif resposta.intent == Intent.REGISTRAR_ABASTECIMENTO:

            return self.registrar_abastecimento_use_case.executar(
                resposta,
                usuario_id,
                db
            )

        elif resposta.intent == Intent.REGISTRAR_VIAGEM:

            return self.registrar_viagem_use_case.executar(
                resposta,
                usuario_id,
                db
            )

        elif resposta.intent == Intent.CONSULTAR_KM:

            return self.consultar_km_use_case.executar(
                resposta,
                usuario_id,
                db
            )

        elif resposta.intent == Intent.CONSULTAR_VIAGENS:

            return self.consultar_viagens_use_case.executar(
                resposta,
                usuario_id,
                db
            )

        elif resposta.intent == Intent.CONVERSA:
            return None

        elif resposta.intent == Intent.AJUDA:
            return None

    def _obter_resposta(
        self,
        resposta_ai: AIResponseDTO,
        resultado
    ):

        # Conversa e ajuda utilizam diretamente a resposta da IA
        if resultado is None:
            return resposta_ai.resposta

        # Caso de sucesso no Use Case
        if resultado.get("sucesso") is True:
            return resultado.get(
                "mensagem",
                resposta_ai.resposta
            )

        # Caso de validação ou informação faltante
        return resultado.get(
            "mensagem",
            resposta_ai.resposta
        )