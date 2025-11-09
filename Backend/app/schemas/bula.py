"""
Schemas para endpoints de bulas
"""
from pydantic import BaseModel, Field
from typing import Optional


class BulaQueryRequest(BaseModel):
    """Request para consulta de bula"""
    medicamento: str = Field(..., description="Nome do medicamento a ser consultado")
    pergunta: Optional[str] = Field(
        None, 
        description="Pergunta específica sobre o medicamento (ex: 'Quais são os efeitos colaterais?')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "medicamento": "Dormec",
                "pergunta": "Quais são os efeitos colaterais?"
            }
        }


class BulaResponse(BaseModel):
    """Response com informações simplificadas da bula"""
    medicamento: str = Field(..., description="Nome do medicamento")
    resposta: str = Field(..., description="Resposta simplificada sobre o medicamento")
    fonte: str = Field(default="Base Curada", description="Fonte da informação (Base Curada ou Web)")
    tempo_resposta: float = Field(..., description="Tempo de resposta em segundos")

    class Config:
        json_schema_extra = {
            "example": {
                "medicamento": "Dormec",
                "resposta": "O Dormec é um medicamento usado para...",
                "fonte": "Base Curada",
                "tempo_resposta": 1.23
            }
        }

