import sys
sys.path.append("..")


# importa tutti py
from src.router_agent import router_agent
from src.json_builder_agent import json_builder_agent
from src.ral_maker import calcola_netto
from src.plot_maker import create_waterfall
from src.schemas import UserIntent, RALInput, RALResult
from src.config import oss_model
import asyncio


import os
from enum import Enum
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import json
from openai import AsyncOpenAI
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, output_guardrail, GuardrailFunctionOutput
load_dotenv(override=True)
import gradio as gr




tax_expert = Agent(name="tax_espert", instructions="esperto nella fiscalità italiana - max 50 parole", model=oss_model)

async def chat(message, history):
    fig = None  # di default nessun grafico
    risposta= ""

    # in cima alla funzione o come variabile globale
    ultimo_ral_input = None
    
    with trace("Build json"):  # ← metti un nome tuo
        result = await router_agent(message)  

    print(f"Category: '{result.category}'")

    # ROUTER If

    if result.category.upper() == "INFO": # informazioni campo fiscale reddito
        with trace("dai info"):
            info_result= await Runner.run(tax_expert, result.message)
        risposta = info_result.final_output

    elif result.category.upper() == "DATA": # prima richiesta di calcol oral
        with trace("dai info"):

            history.append({"role": "user", "content": message})
            yield history, None, ""

            history.append({"role": "assistant", "content": "⏳ Caricamento grafico in corso..."})
            yield history, None, ""
        
            data_result=await json_builder_agent(message)
            ultimo_ral_input = data_result
            
            if data_result is None:
                history.append({"role": "assistant", "content": "Non sono riuscito a elaborare i dati, riprova."})
                yield history, None, ""
            else:

                calculation = calcola_netto(data_result)
                fig = create_waterfall(calculation) 

                await asyncio.sleep(4)
                  
                history.append({"role": "assistant", "content": "✅ Ecco il calcolo del tuo stipendio"})
                yield history, fig, ""

                

    
    elif result.category.upper() == "UPDATE": # richiesta di update dati ral
        with trace("dai info"):
            update_result = await json_builder_agent(f"Dati attuali: {ultimo_ral_input}. Modifica: {message}")
            if update_result is None:
                risposta = "Non sono riuscito a elaborare i dati, riprova."
            else:
                calculation = calcola_netto(update_result)
                fig = create_waterfall(calculation)
                risposta = "Ho modificato i tuoi dati"
     
    elif result.category.upper() == "OFF_TOPIC": # chiede informazioni non inerenti
        risposta = "Argomento non inerente allo scopo del calcolatore"
    
    elif result.category.upper() == "NOT_CAPABLE": # chiede feature non disponibili dallo strumento  
        risposta = "Feature del calcolatore non disponibile puoi inviare il suggerimento alla mail tizio@caio.it"
    
    
    yield history, fig, ""

with gr.Blocks(theme=gr.themes.Soft()) as app:
    gr.Markdown("# 💰 RAL Agent - Calcolatore Stipendio Netto")
    gr.Markdown("Inserisci la tua RAL annuale e scopri il tuo stipendio netto. Puoi anche chiedere info su IRPEF, INPS e detrazioni.")
    
    with gr.Row():
        with gr.Column(scale=1):
            chatbot = gr.Chatbot(height=650, label="RAL AI")
            msg = gr.Textbox(
                placeholder="Es: 'Ho una RAL di 35mila euro' oppure 'Cos'è l'IRPEF?'",
                label="Scrivi qui",
                show_label=True
            )
        with gr.Column(scale=1):
            plot = gr.Plot(label="Waterfall")

    msg.submit(fn=chat, inputs=[msg, chatbot], outputs=[chatbot, plot, msg])

app.launch(share=True)