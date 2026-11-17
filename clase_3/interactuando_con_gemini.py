import os
import requests
from dotenv import load_dotenv

load_dotenv()

url_gemini = os.getenv("URL_GEMINI")
api_key_gemini = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL")

headers = {
    "x-goog-api-key": api_key_gemini,
    "Content-Type": "application/json"
}

data = {
    "model": model,
    "input": "Define que es un agente de IA en una sola oración"
}

response = requests.post(url_gemini, headers=headers, json=data)

print(f"Respuesta: {response.json()}")