import os
from dotenv import load_dotenv
from pathlib import Path
from ai_models.gemini_assistant import get_gemini_response, create_gemini_chat
from utils import obtener_estado_de_cuenta

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SYSTEM_ROLE_PATH = "prompts/asistente_general.txt"


def load_system_role():
    relative_path = os.getenv("SYSTEM_ROLE_PATH", DEFAULT_SYSTEM_ROLE_PATH)
    path = BASE_DIR / relative_path

    if not path.is_file():
        raise FileNotFoundError(f"No se encontro el archivo en {path}")

    system_role = path.read_text(encoding="utf-8").strip()

    if not system_role:
        raise ValueError(f"El archivo de prompt vacion {path}")

    return system_role

tools = [obtener_estado_de_cuenta]


def get_user_input():
    """
    Prompt the user for input and return the input as a string.
    """
    user_input = input("Si queres salir ingresa 'salir' o 'exit'. Usuario: ")
    return user_input

def call_ai_model(user_input, chat, system_role, tools):
    return get_gemini_response(system_role=system_role, prompt=user_input, chat=chat, tools=tools)

def main():
    assistant_name = os.getenv("ASSISTANT_NAME", "Asistente")
    salidas = ['salir','exit']
    try:
        system_role = load_system_role()
        chat = create_gemini_chat(system_role=system_role, tools=tools)
        user_input = get_user_input()
        while user_input not in salidas:
            response = call_ai_model(user_input=user_input, system_role=system_role, chat=chat, tools=tools)
            print(response)
            user_input = get_user_input()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()