"""
Endpoints para criação de lembretes de medicamentos
"""
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.lembrete import LembreteCreateRequest, LembreteResponse
from app.services.calendar_service import CalendarService
from app.core.dependencies import get_calendar_service

router = APIRouter()


@router.post("/criar", response_model=LembreteResponse)
async def criar_lembrete(
    request: LembreteCreateRequest,
    calendar_service: CalendarService = Depends(get_calendar_service)
):
    """
    Cria lembretes de medicamento no Google Calendar
    
    - **medicamento**: Nome do medicamento
    - **frequencia**: Frequência em linguagem natural (ex: "3 vezes ao dia")
    - **duracao**: (Opcional) Duração do tratamento
    - **horario_inicio**: (Opcional) Horário de início no formato HH:MM
    - **observacoes**: (Opcional) Observações adicionais
    """
    try:
        resultado = calendar_service.criar_lembretes(
            medicamento=request.medicamento,
            frequencia=request.frequencia,
            duracao=request.duracao,
            horario_inicio=request.horario_inicio,
            observacoes=request.observacoes
        )
        
        return LembreteResponse(
            sucesso=resultado["sucesso"],
            mensagem=resultado["mensagem"],
            evento_id=resultado.get("evento_id"),
            medicamento=resultado["medicamento"],
            proximo_lembrete=resultado.get("proximo_lembrete")
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar lembrete: {str(e)}"
        )

