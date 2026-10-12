from enum import Enum
import json
from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


MAX_AI_RESPONSE_LENGTH = 4096
MIN_QUILOMETROS = 0.1
MAX_QUILOMETROS = 5000
MIN_VALOR = 0.01
MAX_VALOR = 999999


class Intent(str, Enum):
    REGISTRAR_KM = "registrar_km"
    REGISTRAR_VIAGEM = "registrar_viagem"
    REGISTRAR_ABASTECIMENTO = "registrar_abastecimento"
    CONSULTAR_KM = "consultar_km"
    CONSULTAR_VIAGENS = "consultar_viagens"
    CONVERSA = "conversa"
    AJUDA = "ajuda"


# ============================================================
# Schemas por Intent
# ============================================================

class RegistrarKMDados(BaseModel):
    """Dados esperados para registrar quilometragem"""
    quilometros: float = Field(
        gt=MIN_QUILOMETROS,
        le=MAX_QUILOMETROS,
        description="Quilometragem registrada (0.1 a 5000 km)"
    )
    viagem_id: Optional[int] = Field(
        None,
        ge=1,
        description="ID da viagem (opcional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "quilometros": 120.5,
                "viagem_id": 42
            }
        }


class RegistrarViagemDados(BaseModel):
    """Dados esperados para registrar viagem"""
    origem: str = Field(
        min_length=1,
        max_length=200,
        description="Ponto de origem"
    )
    destino: str = Field(
        min_length=1,
        max_length=200,
        description="Ponto de destino"
    )
    empresa_id: Optional[int] = Field(
        None,
        ge=1,
        description="ID da empresa (opcional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "origem": "São Paulo",
                "destino": "Rio de Janeiro",
                "empresa_id": 1
            }
        }


class RegistrarAbastecimentoDados(BaseModel):
    """Dados esperados para registrar abastecimento"""
    valor: float = Field(
        ge=MIN_VALOR,
        le=MAX_VALOR,
        description="Valor do abastecimento (R$)"
    )
    combustivel: str = Field(
        min_length=1,
        max_length=50,
        description="Tipo de combustível"
    )
    viagem_id: Optional[int] = Field(
        None,
        ge=1,
        description="ID da viagem (opcional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "valor": 250.50,
                "combustivel": "gasolina",
                "viagem_id": 42
            }
        }


class ConsultarKMDados(BaseModel):
    """Dados esperados para consultar quilometragem"""
    data_inicio: Optional[str] = Field(
        None,
        description="Data inicial (YYYY-MM-DD)"
    )
    data_fim: Optional[str] = Field(
        None,
        description="Data final (YYYY-MM-DD)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "data_inicio": "2026-10-01",
                "data_fim": "2026-10-31"
            }
        }


class ConsultarViagensDados(BaseModel):
    """Dados esperados para consultar viagens"""
    data_inicio: Optional[str] = Field(
        None,
        description="Data inicial (YYYY-MM-DD)"
    )
    data_fim: Optional[str] = Field(
        None,
        description="Data final (YYYY-MM-DD)"
    )
    status: Optional[str] = Field(
        None,
        description="Status da viagem"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "data_inicio": "2026-10-01",
                "data_fim": "2026-10-31"
            }
        }


class ConversaDados(BaseModel):
    """Dados para conversa genérica"""
    context: Optional[str] = Field(
        None,
        description="Contexto adicional"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "context": "usuário pediu ajuda"
            }
        }


class AjudaDados(BaseModel):
    """Dados para requisição de ajuda"""
    topico: Optional[str] = Field(
        None,
        description="Tópico de ajuda"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topico": "como registrar quilometragem"
            }
        }


# Mapeamento de intent para schema de dados
INTENT_DADOS_SCHEMA = {
    Intent.REGISTRAR_KM: RegistrarKMDados,
    Intent.REGISTRAR_VIAGEM: RegistrarViagemDados,
    Intent.REGISTRAR_ABASTECIMENTO: RegistrarAbastecimentoDados,
    Intent.CONSULTAR_KM: ConsultarKMDados,
    Intent.CONSULTAR_VIAGENS: ConsultarViagensDados,
    Intent.CONVERSA: ConversaDados,
    Intent.AJUDA: AjudaDados,
}


# ============================================================
# DTO Principal com Validações Robustas
# ============================================================

class AIResponseDTO(BaseModel):
    """
    DTO para resposta da IA com validações robustas por intent.

    Garante que:
    - Intent é válido
    - Resposta não é vazia
    - Dados correspondem ao intent esperado
    - Dados são JSON-serializáveis
    """
    intent: Intent
    dados: dict
    resposta: str = Field(
        min_length=1,
        max_length=MAX_AI_RESPONSE_LENGTH
    )

    @field_validator("resposta", mode="before")
    @classmethod
    def validar_resposta(cls, valor: str) -> str:
        """Validar que resposta não é vazia e não tem apenas espaços"""
        if not isinstance(valor, str):
            raise ValueError(
                "A resposta deve ser uma string."
            )

        if not valor.strip():
            raise ValueError(
                "A resposta da IA não pode estar vazia."
            )

        if len(valor) > MAX_AI_RESPONSE_LENGTH:
            raise ValueError(
                f"A resposta não pode exceder {MAX_AI_RESPONSE_LENGTH} caracteres."
            )

        return valor.strip()

    @field_validator("dados", mode="before")
    @classmethod
    def validar_dados_json(cls, valor: dict) -> dict:
        """Garantir que dados são JSON-serializáveis"""
        if not isinstance(valor, dict):
            raise ValueError(
                "Os dados devem ser um dicionário."
            )

        try:
            json.dumps(valor)
        except (TypeError, ValueError) as e:
            raise ValueError(
                f"Os dados da IA devem ser compatíveis com JSON: {str(e)}"
            )

        return valor

    @model_validator(mode="after")
    def validar_dados_por_intent(self) -> "AIResponseDTO":
        """
        Validar que os dados correspondem ao intent.

        Cada intent tem um schema de dados esperado.
        Esta validação garante que os dados estão corretos.
        """
        try:
            schema = INTENT_DADOS_SCHEMA.get(self.intent)

            if schema:
                # Validar dados contra schema específico
                schema(**self.dados)

        except ValueError as e:
            raise ValueError(
                f"Dados inválidos para intent '{self.intent.value}': {str(e)}"
            )

        return self

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "intent": "registrar_km",
                    "dados": {"quilometros": 120.5, "viagem_id": 1},
                    "resposta": "Registrei 120.5 km para você!"
                },
                {
                    "intent": "conversa",
                    "dados": {"context": None},
                    "resposta": "Olá! Como posso ajudá-lo?"
                }
            ]
        }