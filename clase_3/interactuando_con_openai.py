import os
import requests
from dotenv import load_dotenv

load_dotenv()

openai_url = os.getenv("URL_OPENAI")
api_key_openai = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")

headers = {
    "Authorization": f"Bearer {api_key_openai}",
    "Content-Type": "application/json"
}

data = {
  "model": model,
  "messages": [
    {
      "role": "user",
      "content": "Define qué es el clima en una oración"
    }
  ],
  "temperature": 0.7
}


response = requests.post(openai_url, headers=headers, json=data)

print(response.json())