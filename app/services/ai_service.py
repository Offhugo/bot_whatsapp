import logging
import os
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
import pytz
from sqlalchemy.orm import Session

from app.schemas.ai_response import AIResponseDTO
from app.services.conversation_context_service import ConversationContextService


load_dotenv()

logger = logging.getLogger(__name__)


class AIService:
    # ⚡ NOVO: Timezone padrão para contexto temporal
    DEFAULT_TIMEZONE = "America/Fortaleza"

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.system_prompt_base = self._load_system_prompt()
        # ⚡ NOVO: Serviço para gerenciar histórico de conversas (Item 3)
        self.conversation_service = ConversationContextService()

    def _load_system_prompt(self) -> str:
        prompt_path = (
            Path(__file__).parent.parent
            / "prompts"
            / "system_prompt.txt"
        )

        with open(prompt_path, "r", encoding="utf-8") as file:
            return file.read()

    # ⚡ NOVO: Método para gerar prompt com contexto temporal (Item 2)
    def _get_system_prompt_with_context(self, timezone: str = None) -> str:
        """
        Gera prompt do sistema com contexto temporal dinâmico.

        Inclui data/hora atual para que a IA tenha conhecimento
        do contexto temporal e possa fazer inferências melhores.

        Args:
            timezone: Timezone a usar (ex: "America/Fortaleza")
                     Se None, usa DEFAULT_TIMEZONE

        Returns:
            String com prompt enriquecido com data/hora
        """
        if timezone is None:
            timezone = self.DEFAULT_TIMEZONE

        try:
            # Converter para timezone local
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)

            # Formatar data em português
            meses = {
                1: "janeiro", 2: "fevereiro", 3: "março",
                4: "abril", 5: "maio", 6: "junho",
                7: "julho", 8: "agosto", 9: "setembro",
                10: "outubro", 11: "novembro", 12: "dezembro"
            }

            mes_nome = meses.get(now.month, str(now.month))
            date_str = f"{now.day} de {mes_nome} de {now.year}"
            time_str = now.strftime("%H:%M")
            tz_offset = now.strftime("%z")  # ex: -0300
            tz_formatted = f"{tz_offset[:3]}:{tz_offset[3:]}"  # ex: -03:00

            # Adicionar contexto temporal ao prompt
            context = (
                f"\n\n=== CONTEXTO TEMPORAL ===\n"
                f"Data/Hora Atual: {date_str}, {time_str} ({tz_formatted})\n"
                f"Timezone: {timezone}\n"
                f"============================\n"
            )

            return self.system_prompt_base + context

        except Exception as e:
            logger.warning(
                f"Erro ao adicionar contexto temporal ao prompt: {e}. "
                f"Usando prompt sem contexto."
            )
            return self.system_prompt_base

    async def processar(
        self,
        mensagem: str,
        timezone: str = None,
        usuario_id: int = None,
        db: Session = None
    ) -> AIResponseDTO:
        """
        Processa mensagem com IA.

        Args:
            mensagem: Mensagem do usuário
            timezone: Timezone para contexto (ex: "America/Fortaleza")
            usuario_id: ID do usuário (opcional, para usar histórico)
            db: Sessão do banco de dados (necessário se usuario_id fornecido)

        Returns:
            AIResponseDTO com resposta parseada

        Raises:
            RuntimeError: Se há erro na chamada ou parsing
        """
        try:
            # ⚡ NOVO: Usar prompt com contexto temporal (Item 2)
            system_prompt = self._get_system_prompt_with_context(timezone)

            # ⚡ NOVO: Construir lista de mensagens com histórico (Item 3)
            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
            ]

            # Se usuario_id e db foram fornecidos, carregar histórico
            conversa = None
            if usuario_id and db:
                try:
                    conversa = self.conversation_service.obter_ou_criar_conversa(
                        usuario_id,
                        db=db
                    )

                    # Adicionar mensagem do usuário ao histórico
                    self.conversation_service.adicionar_mensagem_usuario(
                        conversa.id,
                        mensagem,
                        db=db
                    )

                    # Obter histórico formatado
                    historico = self.conversation_service.obter_historico_para_prompt(
                        conversa.id,
                        db=db
                    )

                    # Adicionar histórico às mensagens
                    messages.extend(historico)

                except Exception as e:
                    logger.warning(
                        f"Erro ao carregar histórico da conversa: {e}. "
                        f"Continuando sem histórico."
                    )
            else:
                # Fallback: usar apenas a mensagem atual
                messages.append({
                    "role": "user",
                    "content": mensagem,
                })

            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=AIResponseDTO,
            )

        except OpenAIError as exc:
            logger.error(
                "Falha na chamada à API da OpenAI (%s).",
                type(exc).__name__,
            )
            raise RuntimeError(
                "Não foi possível processar a mensagem com a IA."
            ) from exc

        resposta = completion.choices[0].message

        if resposta.parsed:
            # ⚡ NOVO: Salvar resposta no histórico (Item 3)
            if conversa and db:
                try:
                    # Formatar resposta como string para histórico
                    resposta_str = str(resposta.parsed)
                    self.conversation_service.adicionar_mensagem_assistente(
                        conversa.id,
                        resposta_str,
                        db=db
                    )
                except Exception as e:
                    logger.warning(
                        f"Erro ao salvar resposta no histórico: {e}"
                    )

            return resposta.parsed

        logger.warning(
            "A API da OpenAI não retornou uma resposta interpretável."
        )

        raise RuntimeError(
            "Não foi possível interpretar a resposta da IA."
        )