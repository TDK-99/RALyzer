from pydantic import BaseModel, Field
from enum import Enum

# agent router schema

class UserIntent(BaseModel):
    category: str = Field(description="Classificazione: info, data, update, off_topic")
    message: str = Field(description="Breve spiegazione della classificazione")


# agent json builder schema

class RALInput(BaseModel):
    ral: float = Field(description="Retribuzione Annua Lorda")
    mensilita: int = Field(default=13, description="Numero di mensilità (13 o 14)")
    citta: str = Field(default="Milano", description="Città di residenza per addizionale comunale")
    figli_sotto_21: int = Field(default=0, description="Numero di figli sotto i 21 anni a carico")
    figli_disabilita: int = Field(default=0, description="Numero di figli con disabilità a carico")