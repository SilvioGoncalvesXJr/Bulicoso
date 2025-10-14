import time
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
import re
from langchain.docstore.document import Document

# ==========================
# 1. Configurações iniciais
# ==========================
PDF_PATH = "guia-medicamentos.pdf"
DB_DIR = "./chroma_bulas_db"
COLLECTION_NAME = "bulas_poc"

# ==========================
# 2. Carregar documento PDF
# ==========================
print("[INFO] Carregando documento PDF...")
loader = PyPDFLoader(PDF_PATH)
pages = loader.load_and_split()
print(f"[INFO] Total de páginas carregadas: {len(pages)}")

# ==========================
# 3. Dividir em chunks
# ==========================
print("[INFO] Dividindo texto por medicamento...")

# Concatena todas as páginas em um único texto
full_text = "\n".join([page.page_content for page in pages])

# Expressão regular que identifica o início de cada medicamento
# Exemplo: "1.1 ACETÍLSALICÍLICO ÁCIDO", "1.2 ACICLOVIR", etc.
pattern = r"\n\d+\.\d+\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ\s\-]+"

# Encontra todos os medicamentos
matches = list(re.finditer(pattern, full_text))

chunks = []

for i, match in enumerate(matches):
    start = match.start()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
    med_text = full_text[start:end].strip()

    # Nome do medicamento = linha que começa com o número
    title_line = med_text.split("\n", 1)[0].strip()

    chunks.append(Document(page_content=med_text, metadata={"title": title_line}))

print(f"[INFO] Total de medicamentos identificados: {len(chunks)}")
print(f"[INFO] Exemplo de título: {chunks[0].metadata['title']}")

# ==========================
# 4. Criar embeddings locais com SentenceTransformers
# ==========================
print("[INFO] Gerando embeddings localmente com SentenceTransformers...")
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # LangChain wrapper

# ==========================
# 5. Criar/Conectar ChromaDB
# ==========================
print("[INFO] Criando ou conectando ao banco vetorial ChromaDB...")
vectordb = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=DB_DIR,
    collection_name=COLLECTION_NAME
)
vectordb.persist()
print(f"[INFO] Base vetorial persistida em: {DB_DIR}")

# ==========================
# 6. Inicializar modelos Gemini
# ==========================
GOOGLE_API_KEY = "your_key"
llm_rag = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0,
    google_api_key=GOOGLE_API_KEY
)

llm_sem_rag = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0,
    google_api_key=GOOGLE_API_KEY
)

retriever = vectordb.as_retriever(search_kwargs={"k": 3})
qa_rag = RetrievalQA.from_chain_type(llm=llm_rag, retriever=retriever)

# ==========================
# 7. Funções de comparação
# ==========================
def query_rag(query):
    start = time.time()
    try:
        result = qa_rag.run(query)
    except Exception as e:
        result = f"Erro no RAG: {e}"
    end = time.time()
    return result, end - start

def query_sem_rag(query):
    start = time.time()
    try:
        result = llm_sem_rag.invoke(query).content
    except Exception as e:
        result = f"Erro sem RAG: {e}"
    end = time.time()
    return result, end - start

# ==========================
# 8. Execução dos testes
# ==========================
consultas = [
    "Quais são os efeitos colaterais do medicamento Dormec?",
    "Qual é a dose recomendada para adultos dado o medicamento Dormec?",
    "Há alguma interação medicamentosa para o remédio Dormec?",
]

for q in consultas:
    print(f"\n{'=' * 80}\n[PERGUNTA] {q}")

    resp_rag, tempo_rag = query_rag(q)
    print(f"[RAG] Tempo: {tempo_rag:.2f}s\nResposta:\n{resp_rag}\n")

    resp_sem, tempo_sem = query_sem_rag(q)
    print(f"[SEM RAG] Tempo: {tempo_sem:.2f}s\nResposta:\n{resp_sem}")