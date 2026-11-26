import os
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("EMOTION_DETECTOR_MODEL_NAME")

emotion_detector = pipeline(
    task="text-classification",
    model=MODEL_NAME
)

def analyze_emotion(text: str) -> dict[str, str | float]:
    
    try:
        result = emotion_detector(text)[0]
    
        return {
            "emocion": result["label"],
            "confianza": round(result["score"], 4),
        }

    except Exception as e:
        print("[aviso] Hubo un error al ejecutar analyze_emotion: {e}")
        return {
            "emocion": "no identificada",
            "confianza": 0.0
        }


if __name__ == "__main__":
    test_messages = [
        "Hace tres días que hice el pago y mi cuenta sigue suspendida. Nadie me da una solución. Estoy harto de los problemas que siempre tengo con ustedes",
        "Muchas gracias por la rápida atención, ya pude ingresar sin problemas. Excelente servicio",
        "No sé si hice bien el trámite y me preocupa perder el turno."
    ]

    for msg in test_messages:
        analysis = analyze_emotion(msg)
        print(f"Texto: {msg}")
        print(f"Resultado: Emoción {analysis["emocion"]}, Confianza: {analysis["confianza"]}")