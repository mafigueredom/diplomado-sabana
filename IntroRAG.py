import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import SystemMessage, HumanMessage

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
# from langchain_chroma import Chroma


# 1. Conectarnos a OpenRouter.
BASE = Path(__file__).resolve().parent

load_dotenv(BASE / "secrets" / ".env")

llm = ChatOpenRouter(
    api_key=os.environ["OPENROUTER_API_KEY"],
    model=os.environ["LLM_MODEL"],
)


# 2. Cargar el documento.
loader = PyPDFLoader(str(BASE / "data" / "Anillos.pdf"))

documentos = loader.load()


# 3. Dividir el documento en chunks.
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50
)

chunks = splitter.split_documents(documentos)

# 4. Modelo de embeddings.
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

'''
# 5. Crear el almacén vectorial en memoria fisica
base_vectorial = Chroma(
    collection_name="documentos_rag",
    embedding_function=embeddings,
    persist_directory="./base_vectorial"
)
#base_vectorial.reset_collection()
if (not Path("./base_vectorial").is_dir()) or (not base_vectorial.get(limit=1)["ids"]):
    base_vectorial.add_documents(chunks)
'''

# 5. Crear el almacén vectorial en memoria
base_vectorial = InMemoryVectorStore(embeddings)
#base_vectorial.reset_collection()
base_vectorial.add_documents(chunks)


# 6. Crear el recuperador.
retriever = base_vectorial.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)


# 7. Metaprompt.
system_Documental = """
    Eres el especialista documental.
    Responde únicamente con la información del texto proporcionado.
    Si el texto no contiene la respuesta, indícalo. No inventes datos.
"""

# 8. Ejecución del chat.
while True:

    usuario = input("Usuario: ").strip()

    if usuario.lower() == "salir":
        break

    if not usuario:
        continue

    system_reinterpretacion = "Re interpreta la solicitud del usuario y escribela brevemente de forma clara y sencilla usando palabras tecnicas si el usuario las utiliza"
    reinterpretacion = llm.invoke([system_reinterpretacion, usuario])
    # Recuperar los documentos más similares.
    resultados= retriever.invoke(reinterpretacion.content)

    # Construir el contexto.
    contexto = ""

    for documento in resultados:
        contexto += documento.page_content + "\n\n"

    # Construir los mensajes.
    instruccion_RAG = SystemMessage(content=system_Documental)

    solicitud = HumanMessage(
        content=f"""
        Contexto_Recuperado_Base: {contexto}
        Pregunta_Usuario: {usuario}
        """
    )

    respuesta = llm.invoke([
        instruccion_RAG,
        solicitud
    ])

    print("Respuesta:", respuesta.content, "\n")
