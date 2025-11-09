"""
Configurações da aplicação usando Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Buliçoso API"
    VERSION: str = "0.1.0"
    
    # Google Gemini
    GOOGLE_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-pro"
    GEMINI_TEMPERATURE: float = 0.0
    
    # ChromaDB
    CHROMA_DB_DIR: str = "./chroma_bulas_db"
    CHROMA_COLLECTION_NAME: str = "bulas_poc"
    
    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Google Calendar API (para lembretes)
    GOOGLE_CALENDAR_CREDENTIALS_PATH: Optional[str] = None
    GOOGLE_CALENDAR_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

