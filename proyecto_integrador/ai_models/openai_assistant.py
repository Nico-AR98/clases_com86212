import os, asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


def get_openai_config():
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")

    if not api_key:
        raise ValueError("La variable OPENAI_API_KEY no esta seteada en el entorno.")
    if not model:
        raise ValueError("La variable OPENAI_MODEL no esta seteada en el entorno.")

    return {
        "api_key": api_key,
        "model": model
    }


_openai_client = None

def get_openai_client(openai_config=None):
    global _openai_client

    if _openai_client is None:
        if openai_config is None:
            openai_config = get_openai_config()

        _openai_client = AsyncOpenAI(api_key=openai_config["api_key"])

    return _openai_client

def create_openai_chat(system_role):
    return [{'role': 'system', 'content': system_role}]


async def get_openai_response(system_role, prompt, openai_config=None, temperature=0.3, max_output_tokens=1024, tools=None, chat=None):
    try:
        if openai_config is None:
            openai_config = get_openai_config()

        openai_client = get_openai_client(openai_config)

        user_message = {"role": "user", "content": prompt.strip()}

        if chat is not None: #En este caso, no es la primera interacción
            messages = chat + [user_message]
        else: #Es la primera interacción
            messages = [
                {"role": "system", "content": system_role},
                user_message
            ]

        params = {
            "model": openai_config["model"],
            "messages": messages,
            "temperature": temperature,
            "max_completion_tokens": max_output_tokens,
        }

        if tools:
            params["tools"] = tools

        response = await openai_client.chat.completions.create(**params)
        text = response.choices[0].message.content

        if chat is not None:
            chat.append(user_message)
            chat.append({"role": "assistant", "content": text})

        return text

    except Exception as e:
        return f"Error al obtener la respuesta de OpenAI: {e}"


async def main():
    system_role = "Sos un experto en el area de las finanzas y asesoras a usuarios sobre cómo invertir su dinero"
    temperature = 0.2
    prompt = "Me gustaria saber cómo invertir mi proximo aguinaldo"
    response = await get_openai_response(system_role=system_role, prompt=prompt, temperature=temperature)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())