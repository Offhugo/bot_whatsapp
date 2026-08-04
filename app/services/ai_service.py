import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.ai_response import AIResponseDTO


# Carrega variáveis do .env
load_dotenv()


class AIService:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.model = os.getenv(
            "OPENAI_MODEL",
            "gpt-4o-mini"
        )

        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:

        prompt_path = (
            Path(__file__)
            .parent.parent
            / "prompts"
            / "system_prompt.txt"
        )

        with open(
            prompt_path,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    async def processar(
        self,
        mensagem: str
    ) -> AIResponseDTO:

        completion = self.client.beta.chat.completions.parse(

            model=self.model,

            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": mensagem
                }
            ],

            response_format=AIResponseDTO
        )

        resposta = completion.choices[0].message

        if resposta.parsed:
            return resposta.parsed

        raise Exception(
            "Não foi possível interpretar a resposta da IA."
        )