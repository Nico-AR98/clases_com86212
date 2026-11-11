import requests, os
from dotenv import load_dotenv

load_dotenv()

jsonplaceholder_url = os.getenv("JSONPLACEHOLDER_URL")

response = requests.get(f"{jsonplaceholder_url}/users")

if response.status_code == 200:
    users = response.json() # Transforma el texto plano en un objeto de Python (lista de diccionarios)
    for u in users:
        print(f"Nombre: {u['name']}, Email: {u['email']}")

else:
    print(f"Error al acceder a la lista de usuarios: {response.status_code}")