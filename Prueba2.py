import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv(Path(__file__).resolve().parent / "secrets" / ".env")

llm = ChatOpenRouter(
    api_key=os.environ["OPENROUTER_API_KEY"],
    model=os.environ["LLM_MODEL"],
)

instruccion = SystemMessage(content="Responde de forma clara y breve.")

Historial = []
posturas = ["Argumenta a Favor.", "Argumenta en contra.",]
Resumen = ""
respuesta =""
Resumen_aux=[]
anterior=""
USAR_MEMORIA=True
CHAT_THINKING=True
CHAT_VS=False
PRINT_RESUME=True

while True:
    solicitud = input("User: ").strip()

    if solicitud.lower() == "salir":
        break


    pregunta = HumanMessage(content=solicitud + "\n Resumen Anterior:" + Resumen)

    if CHAT_VS:
        for turno in range(0, 4):
            instruccion = posturas[turno % 2]
            respuesta_turno=llm.invoke(f"instrucciones {instruccion} \n Tema {solicitud} \n anterior {anterior}").content
            print(f"Turno {turno + 1}:")
            anterior = respuesta_turno
            respuesta = respuesta+respuesta_turno

    if CHAT_THINKING:
        analisis=llm.invoke([SystemMessage(content="""
        Analiza la solicitud del usuario, pero no redactes todavía la respuesta
final.

Genera un resumen de análisis con esta estructura:

OBJETIVO DEL USUARIO:
Describe brevemente qué quiere conseguir.

INFORMACIÓN DISPONIBLE:
Enumera los datos y condiciones presentes en la solicitud.

POSIBLES AMBIGÜEDADES:
Indica qué aspectos podrían tener varias interpretaciones.

DESCOMPOSICIÓN DEL PROBLEMA:
Divide la solicitud en pasos o componentes manejables.

RESULTADO ESPERADO:
Explica qué debería contener una buena respuesta.

No inventes información.
No escribas una respuesta final.
        """), pregunta]).content
        plan = llm.invoke([SystemMessage(content="A partir del analisis recibido, genera un plan paso a paso claro y accionable para satisfacer la solicitud del usuario y que sirva de insumo para construir la respuesta final. El plan debe generar un maximo de 5 items. No redactes la respuesta final, solo la estructura y puntos clave que debe cubrir.:")
        , HumanMessage(content=f"LA solicitud original del usuario es {pregunta.content} y el analisis generado es {analisis}")]).content

        respuesta = llm.invoke([SystemMessage(content="""Eres un asistente experto.
Redacta la respuesta final para el usuario siguiendo estrictamente el plan proporcionado.
Responde de forma clara, precisa y directa sin mencionar que seguiste un análisis o un plan interno."""),HumanMessage(content=f"Responde esta solicitud {pregunta} usando este analisis {analisis} y este plan {plan}" )])
    else:
        respuesta = llm.invoke([instruccion] + [pregunta])

    if USAR_MEMORIA:
        Resumen_aux.extend([pregunta, respuesta])
    else:
        Resumen_aux.extend([pregunta])

    #Resumen_aux = [pregunta, respuesta]
    Resumen_1 = llm.invoke(
        [SystemMessage(content="Resume la conversación en máximo 500 caracteres. Conserva la información importante. Este es el resumen anterior: " + Resumen)]
        + Resumen_aux
        + [HumanMessage(content=f"{pregunta}")]
    )

    Resumen = Resumen_1.content

    if PRINT_RESUME:
        print(Resumen)
    else:
        print(respuesta.content)
    # Se deberian programar clases del diplomado durante la novena católica (del 16 al 24 de diciembre)  y la epoca navidena?