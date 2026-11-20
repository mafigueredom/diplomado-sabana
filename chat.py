"""Chat básico con OpenRouter: activar o desactivar el historial conversacional."""

# Leer la configuración del entorno y resolver rutas respecto al script.
import os
from pathlib import Path

# Cargar credenciales locales y representar los mensajes que recibe el modelo.
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage, SystemMessage

# Cambia este valor a False para enviar solo la pregunta actual.
USAR_MEMORIA = True

# La carpeta secrets está junto a este archivo, en la raíz del proyecto.
load_dotenv(Path(__file__).resolve().parent / "secrets" / ".env")

# Crear el cliente; las peticiones se envían al ejecutar invoke().
llm = ChatOpenRouter(
    api_key=os.environ["OPENROUTER_API_KEY"],
    model=os.environ["LLM_MODEL"],
)

# El mensaje de sistema orienta el estilo de todas las respuestas.
instruccion = SystemMessage(content="Responde de forma clara y breve.")
# Guardar los turnos en memoria; se pierden al cerrar el programa.
historial = []

print("Chat básico. Escribe 'salir' para terminar.")
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

    # Representar la entrada del usuario como un mensaje de LangChain.
    mensaje = HumanMessage(content=pregunta)
    # Con memoria enviamos también los turnos anteriores.
    mensajes = [instruccion] + (historial if USAR_MEMORIA else []) + [mensaje]
    # Consultar al modelo y mostrar el contenido de su AIMessage.
    respuesta = llm.invoke(mensajes)
    print("Bot:", respuesta.content, "\n")

    # Conservar pregunta y respuesta final para el próximo turno.
    if USAR_MEMORIA:
        historial.extend([mensaje, respuesta])
