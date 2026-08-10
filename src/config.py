import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

# load .env variables into process
load_dotenv(override=True)

# Groq provider setup
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
groq_client = AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=os.getenv('groq_api_key'))

# LLM model via Groq (OpenAI-compatible endpoint)
oss_model = OpenAIChatCompletionsModel(model="openai/gpt-oss-120b", openai_client=groq_client)