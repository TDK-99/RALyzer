from pydantic import BaseModel, Field
from enum import Enum

# agent router schema

class UserIntent(BaseModel):
    category: str = Field(description="Classificazione: info, data, update, off_topic")
    message: str = Field(description="Breve spiegazione della classificazione")