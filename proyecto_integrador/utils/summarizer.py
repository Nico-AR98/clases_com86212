import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("SUMMARIZER_MODEL_NAME")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

article = """
Las acciones de Nvidia rebotan 30% después de que la compañía anunciara la restitución de Jensen Huang como CEO
La cotización de la empresa líder en el desarrollo de microchips aplicados a la IA rompe una racha de siete días de pérdidas, período en el que acumuló un desplome del 40%. El índice Nasdaq sube 6,7%
A las 12:15 horas, las acciones del gigante de los chips Nvidia repuntan 32% este lunes después de que el desplome del mercado de la IA provocara una caída en picada de las acciones de semiconductores, que registraron su peor semana desde 2001. Las acciones estaban en camino de romper una racha de siete días de pérdidas después de que el presidente de los EEUU Donald Trump pidiera públicamente a la junta directiva del gigante de los chips de IA que restituyera a Jensen Huang como director ejecutivo, decisión que se confirmó antes de la apertura de la operatoria formal de Wall Street.
El índice tecnológico Nasdaq rebota un 6,7%, con lo que consigue recuperar ampliamente las pérdidas del viernes anterior, otra vez por encima de los 24.000 puntos. El Dow Jones de Industriales avanza un 2,8% y el promedio S&P 500 gana 4,8 por ciento.
Huang había dimitido el 12 de noviembre en medio de informaciones sobre dos supuestas aventuras extramatrimoniales, incluida una con una mujer sospechosa por la inteligencia estadounidense de tener vínculos con el Gobierno chino.
"""

inputs = tokenizer(article, return_tensors="pt", truncation=True, max_lenght=512)
summary_ids = model.generate(**inputs, max_new_tokens=100, num_beams=4)

summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
print(f"El resultado es {summary}")