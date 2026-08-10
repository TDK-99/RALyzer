from agents import Agent, Runner, trace
import json

from config import  oss_model
from schemas import UserIntent



# def for the router agent

async def router_agent(task:str) -> UserIntent:

# istruction for the router
    instructions = """ 
    Sei un router in un workflow per calcolare lo stipendio netto 
    a partire dalla RAL (Retribuzione Annua Lorda).

    Classifica il messaggio dell'utente in una delle seguenti categorie:

    - DATA: l'utente fornisce dati per avviare il calcolo.
    Esempio: "Ho una ral di 35mila euro"

    - UPDATE: l'utente vuole modificare dati di un calcolo già effettuato, qui devi valutare bene
    Esempio: "E se la ral fosse 40mila?"

    - INFO: l'utente chiede spiegazioni su temi legati al calcolo dello stipendio.
    Esempio: "che cos'è IRPEF?"

    - OFF_TOPIC: l'utente parla di argomenti non relativi a stipendio e tasse.
    Esempio: "Chi è Donald Trump?"

    Rispondi SOLO con il JSON richiesto.
    """
# build the router
    router = Agent(name="router", instructions=instructions, model=oss_model)

# run and trace the llm response

    with trace("Check ral json"):  # ← metti un nome tuo
        result = await Runner.run(router, task)

        def parse_output(raw: str, model_class):
            return model_class(**json.loads(raw))

    print(parse_output(result.final_output, UserIntent))

    return result.final_output