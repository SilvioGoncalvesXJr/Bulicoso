"""
Serviço de RAG (Retrieval Augmented Generation) para consulta de bulas
"""
import time
from typing import Optional
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings


class RAGService:
    """Serviço para consulta de bulas usando RAG"""
    
    def __init__(
        self,
        chroma_db_dir: str,
        collection_name: str,
        embedding_model: str,
        google_api_key: str,
        gemini_model: str,
        temperature: float = 0.0
    ):
        """
        Inicializa o serviço RAG
        
        Args:
            chroma_db_dir: Diretório do ChromaDB
            collection_name: Nome da coleção no ChromaDB
            embedding_model: Nome do modelo de embeddings
            google_api_key: Chave da API do Google Gemini
            gemini_model: Modelo do Gemini a ser usado
            temperature: Temperatura do modelo (0.0 para respostas mais determinísticas)
        """
        self.chroma_db_dir = chroma_db_dir
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Inicializar embeddings
        print(f"[RAG] Carregando modelo de embeddings: {embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        
        # Conectar ao ChromaDB
        print(f"[RAG] Conectando ao ChromaDB em: {chroma_db_dir}")
        self.vectordb = Chroma(
            persist_directory=chroma_db_dir,
            embedding_function=self.embeddings,
            collection_name=collection_name
        )
        
        # Inicializar LLM
        print(f"[RAG] Inicializando Gemini: {gemini_model}")
        self.llm = ChatGoogleGenerativeAI(
            model=gemini_model,
            temperature=temperature,
            google_api_key=google_api_key
        )
        
        # Criar retriever e chain
        self.retriever = self.vectordb.as_retriever(search_kwargs={"k": 3})
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            return_source_documents=True
        )
        
        print("[RAG] Serviço inicializado com sucesso!")
    
    def consultar_bula(
        self,
        medicamento: str,
        pergunta: Optional[str] = None
    ) -> tuple[str, float, str]:
        """
        Consulta informações sobre um medicamento
        
        Args:
            medicamento: Nome do medicamento
            pergunta: Pergunta específica (opcional)
            
        Returns:
            Tupla com (resposta, tempo_resposta, fonte)
        """
        # Construir query
        if pergunta:
            query = f"Medicamento: {medicamento}. {pergunta}"
        else:
            query = f"Informações sobre o medicamento {medicamento}. Inclua dosagem, efeitos colaterais e modo de uso de forma simples e clara."
        
        # Executar consulta
        start_time = time.time()
        try:
            result = self.qa_chain.invoke({"query": query})
            resposta = result["result"]
            fonte = "Base Curada"
            
            # Verificar se há documentos recuperados
            if result.get("source_documents"):
                fonte = "Base Curada"
            else:
                fonte = "Base Curada (sem documentos encontrados)"
                
        except Exception as e:
            resposta = f"Erro ao consultar a bula: {str(e)}"
            fonte = "Erro"
        
        tempo_resposta = time.time() - start_time
        
        return resposta, tempo_resposta, fonte
    
    def buscar_medicamento(self, medicamento: str) -> list[dict]:
        """
        Busca documentos relacionados ao medicamento (sem LLM)
        
        Args:
            medicamento: Nome do medicamento
            
        Returns:
            Lista de documentos encontrados
        """
        try:
            docs = self.vectordb.similarity_search(medicamento, k=5)
            return [
                {
                    "conteudo": doc.page_content[:500],  # Primeiros 500 caracteres
                    "metadata": doc.metadata
                }
                for doc in docs
            ]
        except Exception as e:
            print(f"[RAG] Erro na busca: {e}")
            return []

