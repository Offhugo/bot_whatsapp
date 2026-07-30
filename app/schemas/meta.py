from pydantic import BaseModel
from typing import Optional

class ValueDTO(BaseModel):
    contacts: Optional[list[ContactDTO]] = None
    messages: Optional[list[MessageDTO]] = None


class TextDTO(BaseModel):
    body: str


class MessageDTO(BaseModel):
    text: TextDTO


class ContactDTO(BaseModel):
    wa_id: str


class ValueDTO(BaseModel):
    contacts: list[ContactDTO]
    messages: list[MessageDTO]


class ChangeDTO(BaseModel):
    value: ValueDTO


class EntryDTO(BaseModel):
    changes: list[ChangeDTO]


class MetaDTO(BaseModel):
    object: str
    entry: list[EntryDTO]