# Leer la configuración del entorno y resolver rutas respecto al script.
import os
from pathlib import Path

# Cargar credenciales locales y representar los mensajes.
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv(Path(__file__).resolve().parent / "secrets" / ".env")

llm = ChatOpenRouter(
    api_key=os.environ["OPENROUTER_API_KEY"],
    model=os.environ["LLM_MODEL"],
)

#instruccion = SystemMessage(content="Responde de forma clara y breve.")
instruccion = "Responde de forma clara y breve."

Historial = []
Resumen = instruccion

while True:
    solicitud = input("User: ").strip()

    if solicitud.lower() == "salir":
        break

    pregunta = HumanMessage(content=solicitud)

    contexto = [SystemMessage(content=Resumen)]

    respuesta = llm.invoke([instruccion] + contexto + [pregunta])

    Resumen_aux = contexto + [pregunta, respuesta]

    Resumen_1 = llm.invoke(Resumen_aux + [
        HumanMessage(content="Realiza un resumen en no más de 500 caracteres de la conversación anterior")])

    Resumen = Resumen_1.content

    Historial.append(respuesta.content)

    print(respuesta.content)
