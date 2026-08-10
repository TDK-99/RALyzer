from agents import Agent, Runner, trace
import json

from .config import  oss_model
from .schemas import RALInput



# def for the router agent

async def json_builder_agent(task:str) -> RALInput:

# istruction for the router
    instructions = """
    Sei l'agente JSON Builder in un workflow per il calcolo dello stipendio netto 
    a partire dalla RAL (Retribuzione Annua Lorda).

    Il tuo unico obiettivo è raccogliere i dati dall'utente per completare il JSON di output.

    Campi da compilare:
    - ral: la Retribuzione Annua Lorda - se utente da una cifra mensile moltiplica per la mensilità (obbligatorio, deve fornirlo l'utente)
    - mensilita: 13 o 14 (default: 13)
    - citta: città di residenza (default: Milano)
    - figli_sotto_21: numero di figli sotto i 21 anni a carico (default: 0)
    - figli_disabilita: numero di figli con disabilità a carico (default: 0)
    - Aliquota addizionale comunale (default Milano 0.8%)
    - Aliquota addizionale regionale (default Lombardia 1.73%) 

    Regole:
    - Se l'utente fornisce solo la RAL, completa il JSON con i valori di default per gli altri campi.
    - La ral puo essere scritta in vari 35k, 35 mila, il tuo obiettivo è trascriverlo in intero
    - Se l'utente specifica valori diversi dai default, usa quelli.
    - Se il messaggio è ambiguo o manca la RAL, chiedi chiarimenti in modo breve e diretto
    - Aliquote fisse se non esplicitamente inserite nel testo dall'utente
    - Rispondi SOLO con il JSON richiesto:
        ral
        mensilita
        citta: str
        figli_sotto_21
        figli_disabilita    
        addizionale_comunale * i valori lasciali cosi non li trasformare in percentuale es di default è 0.008
        addizionale_regionale *
    - se utente fornisce altri dati non calcolarli
    """
# build the router
    json_builder = Agent(name="json_builder", instructions=instructions, model=oss_model)

# run and trace the llm response

    with trace("Check ral json"):  # ← metti un nome tuo
        result = await Runner.run(json_builder, task)

    def parse_output(raw: str, model_class):
        try:
            return model_class(**json.loads(raw))
        except (json.JSONDecodeError, Exception):
            return None

    parse_result= parse_output(result.final_output, RALInput)

    return parse_result