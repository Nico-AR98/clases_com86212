import os
from dotenv import load_dotenv

load_dotenv()

def get_user_input():
    """
    Prompt the user for input and return the input as a string.
    """
    user_input = input("Usuario: ")
    return user_input

def call_ai_model(user_input):
    if not user_input.strip():
        raise ValueError("Input no puede estar vacío. Por favor, ingrese un mensaje válido.")
    return f"El asistente responde: Entendí tu mensaje '{user_input}'"

def main():
    assistant_name = os.getenv("ASSISTANT_NAME", "Asistente")

    try:
        user_input = get_user_input()
        response = call_ai_model(user_input)
        print(response)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()