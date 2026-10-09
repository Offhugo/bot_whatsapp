
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from app.schemas.ai_response import AIResponseDTO


load_dotenv()

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        prompt_path = (
            Path(__file__).parent.parent
            / "prompts"
            / "system_prompt.txt"
        )

        with open(prompt_path, "r", encoding="utf-8") as file:
            return file.read()

    async def processar(self, mensagem: str) -> AIResponseDTO:
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt,
                    },
                    {
                        "role": "user",
                        "content": mensagem,
                    },
                ],
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
            return resposta.parsed

        logger.warning(
            "A API da OpenAI não retornou uma resposta interpretável."
        )

        raise RuntimeError(
            "Não foi possível interpretar a resposta da IA."
        )