import os
from dotenv import load_dotenv
from ai_models.gemini_assistant import get_gemini_response

load_dotenv()

def get_user_input():
    """
    Prompt the user for input and return the input as a string.
    """
    user_input = input("Si queres salir ingresa 'salir' o 'exit'. Usuario: ")
    return user_input

def call_ai_model(user_input):
    system_role = "Sos un experto en el area de las finanzas y asesoras a usuarios sobre cómo invertir su dinero"
    return get_gemini_response(system_role=system_role, prompt=user_input)

def main():
    assistant_name = os.getenv("ASSISTANT_NAME", "Asistente")
    salidas = ['salir','exit']
    try:
        user_input = get_user_input()
        while user_input not in salidas:
            response = call_ai_model(user_input)
            print(response)
            user_input = get_user_input()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()