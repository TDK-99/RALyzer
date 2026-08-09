from pydantic import BaseModel, Field
from enum import Enum

# agent router schema

class UserIntent(BaseModel):
    info: bool = Field(description="L'utente chiede info su tasse o stipendio")
    data: bool = Field(description="L'utente fornisce dati per il calcolo")
    update: bool = Field(description="L'utente vuole modificare dati già inseriti")
    off_topic: bool = Field(description="L'utente parla di altro")
    message: str