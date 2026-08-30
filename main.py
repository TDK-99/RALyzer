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

            history.append({"role": "user", "content": message})
            yield history, None, ""

            info_result= await Runner.run(tax_expert, result.message)
            history.append({"role": "assistant", "content": info_result.final_output})
            yield history, None, ""

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

                await asyncio.sleep(10)
                  
                history.append({"role": "assistant", "content": "✅ Ecco il calcolo del tuo stipendio"})
                yield history, fig, ""

                

    
    elif result.category.upper() == "UPDATE": # richiesta di update dati ral
        with trace("dai info"):
            history.append({"role": "user", "content": message})
            yield history, None, ""

            history.append({"role": "assistant", "content": "⏳ Caricamento grafico in corso..."})
            yield history, None, ""

            update_result = await json_builder_agent(f"Dati attuali: {ultimo_ral_input}. Modifica: {message}")
            if update_result is None:
                history.append({"role": "assistant", "content": "Non sono riuscito a elaborare i dati, riprova."})
                yield history, None, ""
            else:
                
                calculation = calcola_netto(update_result)
                fig = create_waterfall(calculation)

                await asyncio.sleep(10)
                  
                history.append({"role": "assistant", "content": "✅ Ecco il calcolo del tuo stipendio"})
                yield history, fig, ""
     
    elif result.category.upper() == "OFF_TOPIC": # chiede informazioni non inerenti

            history.append({"role": "user", "content": message})
            yield history, None, ""

            
            history.append({"role": "assistant", "content": "Argomento non inerente allo scopo del calcolatore"})
            yield history, None, ""

    elif result.category.upper() == "NOT_CAPABLE": # chiede feature non disponibili dallo strumento 
            history.append({"role": "user", "content": message})
            yield history, None, ""

            history.append({"role": "assistant", "content": "Feature del calcolatore non disponibile puoi inviare il suggerimento alla mail tizio@caio.it"})
            yield history, None, ""
    
    
    yield history, fig, ""

with gr.Blocks(
    theme=gr.themes.Ocean(
        primary_hue="green",
        secondary_hue="emerald",
        neutral_hue="gray",
    ),
) as app:
    gr.HTML("""
        <div style="background: linear-gradient(135deg, #16A34A 0%, #059669 50%, #0D9488 100%);
                    padding: 2rem 2rem 1.5rem 2rem; border-radius: 14px; margin-bottom: 1rem;
                    box-shadow: 0 4px 20px rgba(22, 163, 74, 0.25);">
            <h1 style="color: white; font-size: 2.2rem; font-weight: 800; margin: 0 0 0.3rem 0;">💰 RALyzer</h1>
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.05rem; margin: 0;">Da RAL lorda a netto in tasca. Chiedi tutto su IRPEF, INPS e detrazioni.💸</p>
        </div>
    """)
    with gr.Row():
        with gr.Column(scale=1):
            chatbot = gr.Chatbot(height=480, label="🤖 AI")
            msg = gr.Textbox(
                placeholder="Es: RAL 35k, cos'è l'IRPEF?...",
                show_label=False,
            )
        with gr.Column(scale=2):
            plot = gr.Plot(label="📊 Waterfall")

    msg.submit(fn=chat, inputs=[msg, chatbot], outputs=[chatbot, plot, msg])
app.launch(share=True)