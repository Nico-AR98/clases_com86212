import asyncio, os
import json
from pathlib import Path

from dotenv import load_dotenv

from ai_models.gemini_assistant import create_gemini_chat, get_gemini_response
from tools.customer_tools import (
    buscar_cliente_por_email,
    calcular_reintegro as _calcular_reintegro,
    crear_interaccion,
    obtener_estado_de_cuenta as _obtener_estado_de_cuenta,
    resetear_contrasena as _resetear_contrasena,
)
from utils.emotion_analysis import analyze_emotion

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
SALIDAS = ["salir", "exit"] 

MENSAJE_DESPEDIDA = "¡Muchas gracias por contactarte con nosotros! Fue un gusto poder ayudarte."

DEFAULT_SYSTEM_ROLE_PATH = os.getenv("DEFAULT_SYSTEM_ROLE_PATH", "prompts/asistente_general.txt")

def load_system_role():
    relative_path = os.getenv("SYSTEM_ROLE_PATH", DEFAULT_SYSTEM_ROLE_PATH)
    path = BASE_DIR / relative_path

    if not path.is_file():
        raise FileNotFoundError(f"No se encontro el archivo en {path}")

    system_role = path.read_text(encoding="utf-8").strip()

    if not system_role:
        raise ValueError(f"El archivo de prompt vacion {path}")

    return system_role


def build_customer_tools(customer_id: int, estado: dict) -> list:

    async def obtener_estado_de_cuenta() -> dict:
        """Consulta el saldo (estado de cuenta) del cliente ya identificado.

        Returns:
            dict: balance (el saldo, puede ser negativo) y balance_status
                ('a_favor', 'debe' o 'al_dia').
        """
        return await _obtener_estado_de_cuenta(customer_id)

    async def calcular_reintegro(dias_sin_servicio: int, indice_malestar: float) -> dict:
        """Calcula y registra el reintegro que le corresponde al cliente por días sin servicio.

        Args:
            dias_sin_servicio: Cantidad de días que el cliente estuvo sin servicio.
            indice_malestar: Índice de insatisfacción del cliente, de 1.0
                (cliente tranquilo) a 2.0 (cliente muy molesto), estimado
                según la forma en que se expresa el cliente.

        Returns:
            dict: Detalle del cálculo y el reembolso creado.
        """
        return await _calcular_reintegro(customer_id, dias_sin_servicio, indice_malestar)

    async def resetear_contrasena() -> dict:
        """Resetea la contraseña del cliente ya identificado y envía el mail con el enlace.

        Returns:
            dict: Confirmación del envío y el enlace de reseteo.
        """
        return await _resetear_contrasena(customer_id)


    def finalizar_conversacion() -> str:
        """Cierra la atención cuando el cliente ya no tiene más consultas.

        Usar esta herramienta apenas el cliente deje en claro que no necesita
        nada más (por ejemplo: "no, nada más", "eso sería todo", "listo,
        gracias"). No usarla mientras el cliente siga haciendo consultas o
        mientras no haya quedado claro que terminó.

        Returns:
            str: El mensaje de despedida que ya se le mostró al cliente.
        """
        estado["finalizada"] = True
        print(MENSAJE_DESPEDIDA)
        return MENSAJE_DESPEDIDA

    return [
        obtener_estado_de_cuenta,
        calcular_reintegro,
        resetear_contrasena,
        finalizar_conversacion,
    ]


def extraer_transcripcion(chat) -> str:
    """Arma la transcripción cliente/asistente a partir del historial de Gemini.

    Usamos el historial que ya mantiene el `chat` de Gemini (chat.get_history())
    en vez de armar la nuestra a mano: así queda garantizado que coincide con lo
    que realmente se dijeron, y no hace falta ir appendeando cada turno aparte.
    Los turnos que son solo llamadas a herramientas (sin texto) se omiten.
    """
    roles = {"user": "Cliente", "model": "Asistente"}
    lineas = []
    for content in chat.get_history():
        texto = "".join(part.text for part in (content.parts or []) if part.text)
        if texto:
            lineas.append(f"{roles.get(content.role, content.role)}: {texto}")
    return "\n".join(lineas)


async def identificar_cliente() -> dict:
    """Saluda al usuario y le pide el mail hasta identificar a un cliente existente."""
    assistant_name = os.getenv("ASSISTANT_NAME", "Asistente")
    print(f"¡Hola! Soy {assistant_name}. Estoy aquí para ayudarte.")

    while True:
        email = input("Para empezar, decime tu correo electrónico: ").strip()
        if not email:
            continue

        cliente = await buscar_cliente_por_email(email)
        if cliente is not None:
            return cliente

        print(f"No encontré ningún cliente con el correo {email}. Probá de nuevo.")


def pedir_puntaje(mensaje: str) -> int:
    """Pide un puntaje entero de 1 a 5 por consola, reintentando si no es válido."""
    while True:
        valor = input(mensaje).strip()
        if valor.isdigit() and 1 <= int(valor) <= 5:
            return int(valor)
        print("Ingresá un número entero del 1 al 5.")


def realizar_encuesta() -> dict | None:
    """Ofrece la encuesta de calidad y devuelve las respuestas, o None si se rechaza."""
    quiere_encuesta = input(
        "¿Te gustaría responder una breve encuesta de calidad? (si/no): "
    ).strip().lower()

    if quiere_encuesta not in ("si", "sí", "s", "yes", "y"):
        return None

    amabilidad = pedir_puntaje("Del 1 al 5, ¿qué tan amable fue la atención?: ")
    resolucion = pedir_puntaje("Del 1 al 5, ¿qué tan bien se resolvió tu consulta?: ")
    comentario = input("¿Querés dejar algún comentario adicional? (enter para omitir): ").strip()

    return {
        "amabilidad": amabilidad,
        "resolución": resolucion,
        "comentario": comentario or None,
    }


async def main():
    system_role = load_system_role()

    cliente = await identificar_cliente()

    customer_id = cliente["id"]
    nombre = cliente.get("first_name", "")

    print(f"¡Qué alegría atenderte, {nombre}! Contame en qué te puedo ayudar.")
    primera_consulta = input("Tu consulta: ").strip()

    sentimiento_inicial = analyze_emotion(primera_consulta)
    print(
        f"[info] Estado emocional inicial detectado: {sentimiento_inicial['emocion']} "
        f"(confianza {sentimiento_inicial['confianza']})"
    )

    system_role_con_contexto = (
        f"{system_role}\n\n"
        "[Contexto interno sobre este cliente, no es un mensaje suyo: su estado "
        f"emocional inicial parece ser '{sentimiento_inicial['emocion']}' "
        f"(confianza {sentimiento_inicial['confianza']}). Tenelo en cuenta para "
        "el tono de tu respuesta.]"
    )

    estado = {"finalizada": False}
    tools = build_customer_tools(customer_id, estado)
    chat = create_gemini_chat(system_role=system_role_con_contexto, tools=tools)

    respuesta = await get_gemini_response(
        system_role=system_role, prompt=primera_consulta, chat=chat, tools=tools
    )

    if not estado["finalizada"]:
        print(respuesta)

    while not estado["finalizada"]:
        user_input = input("Vos: ").strip()
        if user_input in SALIDAS:  # vía de escape manual
            print(MENSAJE_DESPEDIDA)
            break

        respuesta = await get_gemini_response(
            system_role=system_role, prompt=user_input, chat=chat, tools=tools
        )
        if not estado["finalizada"]:
            print(respuesta)


    encuesta = realizar_encuesta()

    print("¡Gracias por completar la encuesta! Que tengas un buen día.")

    sentimiento_final = None
    if encuesta and encuesta.get("comentario"):
        sentimiento_final = analyze_emotion(encuesta["comentario"])

    contenido_conversacion = extraer_transcripcion(chat)

    content = {
        "sentimiento_inicial": sentimiento_inicial,
        "contenido": contenido_conversacion,
        "encuesta": encuesta,
        "sentimiento_final": sentimiento_final,
    }


    try:
        await crear_interaccion(customer_id, content=json.dumps(content, ensure_ascii=False))
        print(f"[aviso] La interacción se guardo correctamente.")
    except Exception as e:
        print(f"[aviso] No se pudo registrar la interacción en customer_api: {e}")


if __name__ == "__main__":
    asyncio.run(main())
