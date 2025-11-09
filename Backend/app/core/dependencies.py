"""
Dependências compartilhadas para injeção no FastAPI
"""
from functools import lru_cache
from app.core.config import settings
from app.services.rag_service import RAGService
from app.services.calendar_service import CalendarService


@lru_cache()
def get_rag_service() -> RAGService:
    """Retorna instância singleton do RAGService"""
    return RAGService(
        chroma_db_dir=settings.CHROMA_DB_DIR,
        collection_name=settings.CHROMA_COLLECTION_NAME,
        embedding_model=settings.EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        gemini_model=settings.GEMINI_MODEL,
        temperature=settings.GEMINI_TEMPERATURE
    )


@lru_cache()
def get_calendar_service() -> CalendarService:
    """Retorna instância singleton do CalendarService"""
    return CalendarService(
        credentials_path=settings.GOOGLE_CALENDAR_CREDENTIALS_PATH,
        calendar_id=settings.GOOGLE_CALENDAR_ID
    )

