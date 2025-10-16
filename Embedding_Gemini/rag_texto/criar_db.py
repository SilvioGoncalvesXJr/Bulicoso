import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_BASE = os.path.join(BASE_DIR, 'base')
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Chave de API do Google não encontrada. Verifique seu arquivo .env")

def criar_db():
    documentos = carregar_documentos()
    chunks = dividir_chunks(documentos)
    vetorizar_chunks(chunks)

def carregar_documentos():
    if not os.path.isdir(PASTA_BASE):
        raise FileNotFoundError(f"Pasta base não encontrada: {PASTA_BASE}. Certifique-se de que 'rag_texto/base' exista e contenha PDFs.")
    carregador = PyPDFDirectoryLoader(PASTA_BASE, glob="*.pdf")
    documentos = carregador.load()
    return documentos

def dividir_chunks(documentos):
    separador_documentos = RecursiveCharacterTextSplitter(
        chunk_size=2000,#Delimitar o tamanho de cada chinck. Testar valores que melhor se adaptem ao sistema
        chunk_overlap=500, #permite que o chunck seguinte tenha trechos do chunk anterior, para fazer uma espécie de conexão entre eles, melhorando o contexto e garantindo a não perda de informações (integridade)
        length_function=len,#delimitar qual a base para verificar o tamanho do texto. Len padrão do python
        add_start_index=True#Diz qual o caracter inicial de cada chunk
    )
    chunks = separador_documentos.split_documents(documentos)
    print(len(chunks))
    return chunks

def vetorizar_chunks(chunks):
    # 1. Crie a instância do modelo de embeddings primeiro
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")#Tem que ser essa versão. usar só embedding-001 ou gemini-embedding-1.0 da pau
    
    # 2. Passe a instância para o Chroma
    db = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory="db"
    )
    
    print("Banco de Dados criado com sucesso!")

criar_db()