"""Chat Thinking: analizar, planificar y responder mediante tres llamadas al LLM."""

# Leer la configuración del entorno y resolver rutas respecto al script.
import os
from pathlib import Path

# Cargar credenciales locales y representar los mensajes que recibe el modelo.
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# False: no recuerda conversaciones anteriores; las tres etapas siguen conectadas.
USAR_MEMORIA = True

# Leer el archivo privado, sin sobrescribir variables ya definidas en el entorno.
load_dotenv(Path(__file__).resolve().parent / "secrets" / ".env")
# Crear el cliente; las peticiones se envían al ejecutar invoke().
llm = ChatOpenRouter(
    api_key=os.environ["OPENROUTER_API_KEY"],
    model=os.environ["LLM_MODEL"],
)

# Guardar los turnos en memoria; se pierden al cerrar el programa.
historial = []
print("Chat Thinking. Escribe 'salir' para terminar.")

# Repetir la conversación hasta recibir salir o cerrar la entrada.
while True:
    # Leer el texto y permitir salir con Ctrl+C o Ctrl+D.
    try:
        pregunta = input("Tú: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nHasta luego.")
        break
    # El comando de salida y las entradas vacías no se envían al modelo.
    if pregunta.lower() == "salir":
        break
    if not pregunta:
        continue

    # El historial de otras preguntas es opcional.
    contexto = historial if USAR_MEMORIA else []

    # Primera llamada: obtener un resumen del objetivo y las restricciones.
    analisis = llm.invoke([
        SystemMessage(content="Identifica el objetivo y las restricciones. No respondas todavía."),
        *contexto,
        HumanMessage(content=pregunta),
    ]).content

    # Segunda llamada: preparar un plan usando el resumen anterior.
    plan = llm.invoke([
        SystemMessage(content="Propón un plan breve de máximo tres pasos."),
        *contexto,
        HumanMessage(content=f"Pregunta: {pregunta}\nAnálisis: {analisis}"),
    ]).content

    # Tercera llamada: elaborar la respuesta con la pregunta, el resumen y el plan.
    respuesta = llm.invoke([
        SystemMessage(content="Responde al usuario de forma clara usando el plan."),
        *contexto,
        HumanMessage(content=f"Pregunta: {pregunta}\nAnálisis: {analisis}\nPlan: {plan}"),
    ]).content

    # Son textos generados en llamadas separadas, no el razonamiento interno del modelo.
    print("\nANÁLISIS:", analisis)
    print("PLAN:", plan)
    print("RESPUESTA:", respuesta, "\n")

    # Conservar pregunta y respuesta final para el próximo turno.
    if USAR_MEMORIA:
        historial.extend([HumanMessage(content=pregunta), AIMessage(content=respuesta)])
