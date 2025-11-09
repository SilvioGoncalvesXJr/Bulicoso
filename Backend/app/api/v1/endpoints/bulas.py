"""
Endpoints para consulta de bulas de medicamentos
"""
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.bula import BulaQueryRequest, BulaResponse
from app.services.rag_service import RAGService
from app.core.dependencies import get_rag_service

router = APIRouter()


@router.post("/consultar", response_model=BulaResponse)
async def consultar_bula(
    request: BulaQueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Consulta informações sobre um medicamento usando RAG
    
    - **medicamento**: Nome do medicamento
    - **pergunta**: (Opcional) Pergunta específica sobre o medicamento
    """
    try:
        resposta, tempo_resposta, fonte = rag_service.consultar_bula(
            medicamento=request.medicamento,
            pergunta=request.pergunta
        )
        
        return BulaResponse(
            medicamento=request.medicamento,
            resposta=resposta,
            fonte=fonte,
            tempo_resposta=round(tempo_resposta, 2)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar bula: {str(e)}"
        )


@router.get("/buscar/{medicamento}")
async def buscar_medicamento(
    medicamento: str,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Busca documentos relacionados ao medicamento (sem processamento LLM)
    
    Útil para verificar se o medicamento existe na base de dados
    """
    try:
        documentos = rag_service.buscar_medicamento(medicamento)
        return {
            "medicamento": medicamento,
            "documentos_encontrados": len(documentos),
            "documentos": documentos
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar medicamento: {str(e)}"
        )

