"""
🔹 SERVIÇO DE VETORIZAÇÃO - Ingestão e processamento de bulas

Este serviço é responsável pelo processo offline de ingestão:

1. Carregar PDFs de bulas (pasta local ou URL)
2. Extrair texto usando LangChain loaders (PyPDFLoader, etc.)
3. Fazer split em chunks com TextSplitter
4. Gerar embeddings usando Gemini embeddings
5. Armazenar no ChromaDB para busca semântica

IMPLEMENTAÇÃO NECESSÁRIA:
- Configurar loaders de PDF (LangChain)
- Implementar text splitting otimizado
- Configurar embeddings (Gemini embedding model)
- Persistir no ChromaDB com metadados
"""

from pathlib import Path
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.core.config import settings
from app.core.logger import setup_logger
from app.db.chroma_client import get_chroma_client

logger = setup_logger()


class VectorService:
    """
    Serviço para vetorização e ingestão de bulas de medicamentos.
    
    Responsabilidades:
    - Carregar documentos (PDFs, textos)
    - Processar e dividir em chunks
    - Gerar embeddings
    - Armazenar no ChromaDB
    """
    
    def __init__(self):
        """Inicializa o serviço de vetorização."""
        self.chroma_client = get_chroma_client()
        
        # TODO: Configurar embeddings
        # self.embeddings = GoogleGenerativeAIEmbeddings(
        #     model=settings.EMBEDDING_MODEL,
        #     google_api_key=settings.GOOGLE_API_KEY
        # )
        
        # TODO: Configurar text splitter
        # self.text_splitter = RecursiveCharacterTextSplitter(
        #     chunk_size=settings.CHUNK_SIZE,
        #     chunk_overlap=settings.CHUNK_OVERLAP,
        #     length_function=len
        # )
        
        logger.info("VectorService inicializado")
    
    
    async def process_pdf(self, pdf_path: str, medication_name: str) -> bool:
        """
        🔹 IMPLEMENTAR: Processa um PDF de bula e adiciona ao ChromaDB.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            medication_name: Nome do medicamento (para metadados)
            
        Returns:
            True se processado com sucesso
        """
        logger.info(f"Processando PDF: {pdf_path}")
        
        try:
            # TODO: Passo 1 - Carregar PDF
            # loader = PyPDFLoader(pdf_path)
            # documents = loader.load()
            
            # TODO: Passo 2 - Dividir em chunks
            # chunks = self.text_splitter.split_documents(documents)
            
            # TODO: Passo 3 - Adicionar metadados
            # for chunk in chunks:
            #     chunk.metadata["medication_name"] = medication_name
            #     chunk.metadata["source"] = pdf_path
            
            # TODO: Passo 4 - Gerar embeddings e armazenar
            # vector_store = Chroma.from_documents(
            #     documents=chunks,
            #     embedding=self.embeddings,
            #     client=self.chroma_client,
            #     collection_name=settings.CHROMA_COLLECTION_NAME,
            #     persist_directory=settings.CHROMA_DB_PATH
            # )
            
            logger.info(f"PDF processado: {pdf_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar PDF: {str(e)}")
            raise
    
    
    async def process_text(self, text: str, medication_name: str, source: str = "web") -> bool:
        """
        🔹 IMPLEMENTAR: Processa texto de bula e adiciona ao ChromaDB.
        
        Args:
            text: Texto da bula
            medication_name: Nome do medicamento
            source: Origem do texto (web, manual, etc.)
            
        Returns:
            True se processado com sucesso
        """
        logger.info(f"Processando texto para: {medication_name}")
        
        try:
            # TODO: Implementar processamento de texto similar ao PDF
            # 1. Dividir em chunks
            # 2. Adicionar metadados
            # 3. Vetorizar e armazenar
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar texto: {str(e)}")
            raise
    
    
    async def process_directory(self, directory_path: str) -> int:
        """
        🔹 IMPLEMENTAR: Processa todos os PDFs de um diretório.
        
        Args:
            directory_path: Caminho do diretório com PDFs
            
        Returns:
            Número de arquivos processados
        """
        logger.info(f"Processando diretório: {directory_path}")
        
        # TODO: Iterar sobre arquivos PDF no diretório
        # for pdf_file in Path(directory_path).glob("*.pdf"):
        #     medication_name = pdf_file.stem  # Nome do arquivo sem extensão
        #     await self.process_pdf(str(pdf_file), medication_name)
        
        return 0
    
    
    async def add_document(self, medication_name: str, content: str, source: str = "web"):
        """
        🔹 IMPLEMENTAR: Adiciona um documento ao ChromaDB.
        
        Método auxiliar para adicionar documentos de qualquer fonte.
        
        Args:
            medication_name: Nome do medicamento
            content: Conteúdo do documento
            source: Origem do documento
        """
        await self.process_text(content, medication_name, source)

