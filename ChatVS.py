"""Chat VS: dos participantes debaten alternando llamadas a un mismo LLM."""

# Leer la configuración del entorno y resolver rutas respecto al script.
import os
from pathlib import Path

# Cargar credenciales locales y representar los mensajes que recibe el modelo.
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage, SystemMessage

# True: recibe todo el debate; False: recibe solo el argumento anterior.
USAR_MEMORIA = True
# Número total de intervenciones, alternando ambas posturas.
NUM_TURNOS = 4

# Leer el archivo privado, sin sobrescribir variables ya definidas en el entorno.
load_dotenv(Path(__file__).resolve().parent / "secrets" / ".env")
# Crear el cliente; las peticiones se envían al ejecutar invoke().
llm = ChatOpenRouter(
    api_key=os.environ["OPENROUTER_API_KEY"],
    model=os.environ["LLM_MODEL"],
)

# Un mismo modelo interpreta dos posturas mediante mensajes de sistema distintos.
posturas = [
    "Defiende el tema con argumentos breves y respetuosos. No inventes datos.",
    "Cuestiona el tema con argumentos breves y respetuosos. No inventes datos.",
]

# El tema del usuario inicia el debate; no cuenta como intervención.
try:
    tema = input("Tema del debate: ").strip()
except (EOFError, KeyboardInterrupt):
    # Una entrada cerrada equivale a no iniciar el debate.
    tema = ""
    print("\nHasta luego.")
# Un tema vacío no genera llamadas al proveedor.
if tema:
    # Mantener el último argumento y, opcionalmente, el debate completo.
    anterior = tema
    historial = []

    # El módulo (%) alterna los índices 0 y 1 para escoger la postura.
    for turno in range(NUM_TURNOS):
        rol = "A FAVOR" if turno % 2 == 0 else "EN CONTRA"
        # Con memoria se reenvía todo el debate; sin ella, solo la intervención previa.
        contexto = "\n".join(historial) if USAR_MEMORIA and historial else anterior

        # Invocar el modelo con su postura, el tema y los argumentos disponibles.
        respuesta = llm.invoke([
            SystemMessage(content=posturas[turno % 2]),
            HumanMessage(content=f"Tema: {tema}\nArgumentos previos:\n{contexto}\nResponde al argumento anterior."),
        ]).content

        # Mostrar y guardar la intervención para el siguiente participante.
        print(f"\nTurno {turno + 1} - {rol}:\n{respuesta}")
        historial.append(f"{rol}: {respuesta}")
        anterior = respuesta
