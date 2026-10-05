from enum import Enum
import json

from pydantic import BaseModel, Field, field_validator


MAX_AI_RESPONSE_LENGTH = 4096


class Intent(str, Enum):
    REGISTRAR_KM = "registrar_km"
    REGISTRAR_VIAGEM = "registrar_viagem"
    REGISTRAR_ABASTECIMENTO = "registrar_abastecimento"
    CONSULTAR_KM = "consultar_km"
    CONSULTAR_VIAGENS = "consultar_viagens"
    CONVERSA = "conversa"
    AJUDA = "ajuda"


class AIResponseDTO(BaseModel):
    intent: Intent
    dados: dict
    resposta: str = Field(
        min_length=1,
        max_length=MAX_AI_RESPONSE_LENGTH
    )

    @field_validator("resposta")
    @classmethod
    def validar_resposta(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError(
                "A resposta da IA não pode estar vazia."
            )

        return valor

    @field_validator("dados")
    @classmethod
    def validar_dados(cls, valor: dict) -> dict:
        try:
            json.dumps(valor)
        except (TypeError, ValueError):
            raise ValueError(
                "Os dados da IA devem ser compatíveis com JSON."
            )

        return valor