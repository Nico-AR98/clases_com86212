import os, asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def get_gemini_config():
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")

    if not api_key:
        raise ValueError("La variable GEMINI_API_KEY no esta seteada en el entorno.")
    if not model:
        raise ValueError("La variable GEMINI_MODEL no esta seteada en el entorno.")

    return {
        "api_key": api_key,
        "model": model
    }


_gemini_client = None

def get_gemini_client(gemini_config=None):
    global _gemini_client

    if _gemini_client is None:
        if gemini_config is None:
            gemini_config = get_gemini_config()

        _gemini_client = genai.Client(api_key=gemini_config["api_key"])

    return _gemini_client


def build_generate_content_config(system_role, tools, temperature=0.3, max_output_tokens=1024):
    return types.GenerateContentConfig(
        system_instruction=system_role,
        tools=tools,
        temperature=temperature,
        max_output_tokens=max_output_tokens
    )

def create_gemini_chat(system_role, tools, temperature=0.3, max_output_tokens=1024, gemini_config=None):
    if gemini_config is None:
        gemini_config = get_gemini_config()

    gemini_client = get_gemini_client(gemini_config)

    return gemini_client.aio.chats.create(
        model=gemini_config["model"],
        config=build_generate_content_config(system_role, tools, temperature, max_output_tokens)
    )


async def get_gemini_response(system_role, prompt, gemini_config=None, temperature=0.3, max_output_tokens=1024, tools=None, chat=None):
    try:
        if chat is not None:
            response = chat.send_message(prompt.strip())
        else:
            if gemini_config is None:
                gemini_config = get_gemini_config()

            gemini_client = get_gemini_client(gemini_config)

            response = await gemini_client.aio.models.generate_content(
                model=gemini_config["model"],
                config=build_generate_content_config(
                    system_role,
                    tools,
                    temperature,
                    max_output_tokens,
                ),
                contents=prompt.strip()
            )

        return response.text

    except Exception as e:
        return f"Error al obtener la respuesta de Gemini: {e}"


async def main():
    system_role = "Sos un experto en el area de las finanzas y asesoras a usuarios sobre cómo invertir su dinero"
    temperature = 0.2
    prompt = "Me gustaria saber cómo invertir mi proximo aguinaldo"
    response = await get_gemini_response(system_role=system_role, prompt=prompt, temperature=temperature)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())