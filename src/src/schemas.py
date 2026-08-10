from pydantic import BaseModel, Field
from enum import Enum

# agent router schema

class UserIntent(BaseModel):
    category: str = Field(description="Classificazione: info, data, update, off_topic,not capable")
    message: str = Field(description="Breve spiegazione della classificazione")


# agent json builder schema

class RALInput(BaseModel):
    ral: float = Field(description="Retribuzione Annua Lorda")
    mensilita: int = Field(default=13, description="Numero di mensilità (13 o 14)")
    citta: str = Field(default="Milano", description="Città di residenza per addizionale comunale")
    figli_sotto_21: int = Field(default=0, description="Numero di figli sotto i 21 anni a carico")
    figli_disabilita: int = Field(default=0, description="Numero di figli con disabilità a carico")
    addizionale_comunale: float = Field(default=0.008, description="Aliquota addizionale comunale (default Milano 0.8%)")
    addizionale_regionale: float = Field(default=0.0173, description="Aliquota addizionale regionale (default Lombardia 1.73%)")

# schema for the ral maker

class RALResult(BaseModel):
    ral_lorda: float = Field(description="Retribuzione Annua Lorda")
    inps: float = Field(description="Contributi INPS dipendente")
    imponibile: float = Field(description="Reddito imponibile (RAL - INPS)")
    irpef_lorda: float = Field(description="IRPEF lorda progressiva")
    detrazioni: float = Field(description="Detrazioni lavoro dipendente")
    irpef_netta: float = Field(description="IRPEF netta (lorda - detrazioni)")
    addizionale_regionale: float = Field(description="Addizionale regionale")
    addizionale_comunale: float = Field(description="Addizionale comunale")
    netto_annuale: float = Field(description="Stipendio netto annuale")
    netto_mensile: float = Field(description="Stipendio netto mensile")
    costo_azienda: float = Field(description="Costo totale per l'azienda")