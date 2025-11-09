"""
Aplicação principal FastAPI.

Este arquivo configura e inicializa a aplicação FastAPI com:
- CORS e middlewares
- Routers (meds, reminders, healthcheck)
- Documentação automática via Swagger/OpenAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import setup_logger
from app.api.routers import meds, reminders, healthcheck

# Configurar logger
logger = setup_logger()

# Criar instância da aplicação FastAPI
app = FastAPI(
    title="Sistema de Adesão Medicamentosa",
    description="API para gerenciamento de lembretes de medicação e simplificação de bulas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(healthcheck.router, tags=["Health"])
app.include_router(meds.router, prefix="/api/meds", tags=["Medications"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["Reminders"])


@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização da aplicação."""
    logger.info("🚀 Sistema de Adesão Medicamentosa iniciado")
    logger.info(f"📚 Documentação disponível em: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado no encerramento da aplicação."""
    logger.info("🛑 Sistema de Adesão Medicamentosa encerrado")

