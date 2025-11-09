"""
Schemas para endpoints de lembretes
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LembreteCreateRequest(BaseModel):
    """Request para criar lembrete de medicamento"""
    medicamento: str = Field(..., description="Nome do medicamento")
    frequencia: str = Field(..., description="Frequência em linguagem natural (ex: '3 vezes ao dia', 'a cada 8 horas')")
    duracao: Optional[str] = Field(
        None,
        description="Duração do tratamento em linguagem natural (ex: 'por 7 dias', 'até terminar a caixa')"
    )
    horario_inicio: Optional[str] = Field(
        None,
        description="Horário de início em formato HH:MM (ex: '08:00'). Se não informado, usa horário atual"
    )
    observacoes: Optional[str] = Field(None, description="Observações adicionais")

    class Config:
        json_schema_extra = {
            "example": {
                "medicamento": "Dormec",
                "frequencia": "3 vezes ao dia",
                "duracao": "por 7 dias",
                "horario_inicio": "08:00",
                "observacoes": "Tomar após as refeições"
            }
        }


class LembreteResponse(BaseModel):
    """Response após criar lembrete"""
    sucesso: bool = Field(..., description="Indica se o lembrete foi criado com sucesso")
    mensagem: str = Field(..., description="Mensagem de confirmação ou erro")
    evento_id: Optional[str] = Field(None, description="ID do evento criado no Google Calendar")
    medicamento: str = Field(..., description="Nome do medicamento")
    proximo_lembrete: Optional[datetime] = Field(None, description="Data e hora do próximo lembrete")

    class Config:
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "mensagem": "Lembretes criados com sucesso no Google Calendar",
                "evento_id": "abc123xyz",
                "medicamento": "Dormec",
                "proximo_lembrete": "2024-01-15T08:00:00"
            }
        }

