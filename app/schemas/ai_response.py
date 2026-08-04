from enum import Enum

from pydantic import BaseModel


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
    resposta: str