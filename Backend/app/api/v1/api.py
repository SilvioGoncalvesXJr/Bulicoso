"""
Router principal da API v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import bulas, lembretes

api_router = APIRouter()

api_router.include_router(bulas.router, prefix="/bulas", tags=["bulas"])
api_router.include_router(lembretes.router, prefix="/lembretes", tags=["lembretes"])

