from pydantic import BaseModel, Field, field_validator


# Limites da entrada recebida pelo webhook.
MAX_MESSAGE_TEXT_LENGTH = 4096
MIN_WA_ID_LENGTH = 8
MAX_WA_ID_LENGTH = 32


class TextDTO(BaseModel):
    body: str = Field(
        min_length=1,
        max_length=MAX_MESSAGE_TEXT_LENGTH
    )

    @field_validator("body")
    @classmethod
    def validar_body(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("O texto da mensagem não pode estar vazio.")

        return valor


class MessageDTO(BaseModel):
    text: TextDTO


class ContactDTO(BaseModel):
    wa_id: str = Field(
        min_length=MIN_WA_ID_LENGTH,
        max_length=MAX_WA_ID_LENGTH
    )

    @field_validator("wa_id")
    @classmethod
    def validar_wa_id(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("O wa_id não pode estar vazio.")

        if not valor.isdigit():
            raise ValueError("O wa_id deve conter apenas números.")

        return valor


class ValueDTO(BaseModel):
    contacts: list[ContactDTO] | None = None
    messages: list[MessageDTO] | None = None


class ChangeDTO(BaseModel):
    value: ValueDTO


class EntryDTO(BaseModel):
    changes: list[ChangeDTO] = Field(min_length=1)


class MetaDTO(BaseModel):
    object: str
    entry: list[EntryDTO] = Field(min_length=1)