# main.py
import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware  # <--- [NOVO] Import crucial para o React
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from langchain_google_genai import ChatGoogleGenerativeAI
# NOSSOS MÓDULOS
from google_calendar_auth import get_calendar_service
from modules.rag_manager import RAGManager
from modules.intent_classifier import classify_intent, IntentResponse
import modules.calendar_manager as calendar

# Carregar .env
load_dotenv(".env", override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY não encontrada no .env!")

# Estado global da aplicação
app_state: Dict[str, Any] = {}


# --- Gerenciamento do Ciclo de Vida (Startup/Shutdown) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ao iniciar
    print("--- 🚀 Iniciando API ---")

    # 1. Carregar LLM principal (para Classificador e Parser)
    print("[INIT] Carregando LLM principal (Gemini Flash)...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.5,
        google_api_key=GOOGLE_API_KEY
    )
    app_state["llm"] = llm

    # 2. Carregar Módulo RAG
    print("[INIT] Carregando RAG Manager...")
    app_state["rag_manager"] = RAGManager(google_api_key=GOOGLE_API_KEY)

    # 3. Carregar Módulo Calendar
    print("[INIT] Autenticando no Google Calendar...")
    app_state["calendar_service"] = get_calendar_service()

    print("--- ✅ API Pronta ---")
    yield
    # Ao desligar
    print("--- 🛑 Encerrando API ---")
    app_state.clear()


# --- Funções "Depends" para Injeção ---
def get_llm():
    return app_state["llm"]


def get_rag_manager():
    return app_state["rag_manager"]


def get_calendar_service_dep():
    return app_state["calendar_service"]


# --- Inicialização do FastAPI ---
app = FastAPI(
    title="Assistente de Medicação API",
    description="API modular com RAG e Google Calendar.",
    lifespan=lifespan
)

# [NOVO] Configuração do CORS
# Isso permite que o seu Frontend (React) converse com o Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite qualquer origem (React, Vue, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)


# --- Modelos Pydantic ---

# [NOVO] Modelo para a requisição do RAG
class RagQueryRequest(BaseModel):
    original_query: str = Field(..., example="Quais são as reações adversas da Dipirona Sódica?")
    topic: str = Field(..., example="reações adversas")

class ChatQuery(BaseModel):
    query: str = Field(..., example="Quais as reações da Dipirona?")


class ScheduleRequest(BaseModel):
    instrucao: str = Field(..., example="Dipirona de 8 em 8 horas por 5 dias")
    start_time_str: str = Field(..., example="agora")


class DeleteRequest(BaseModel):
    event_ids: List[str] = Field(..., description="Lista de IDs de eventos para deletar.")


class EditRequest(BaseModel):
    new_start_time_str: str = Field(..., example="25/12/2025 10:00")


# === ENDPOINTS DA API ===

@app.post("/v1/chat/classify_intent", response_model=IntentResponse, summary="1. Classificar Intenção do Usuário")
async def handle_chat_query(
        query: ChatQuery,
        llm: ChatGoogleGenerativeAI = Depends(get_llm)
):
    """
    Recebe a query de chat do usuário.
    Usa o LLM para classificar a intenção e extrair entidades.
    """
    intent_data = classify_intent(query.query, llm)
    return intent_data


# --- Endpoints do RAG ---

# [ATUALIZADO] Agora usa POST e recebe a query original + tópico
@app.post("/v1/rag/query", summary="2. Executar consulta RAG")
async def post_rag_query(
        request: RagQueryRequest,
        rag_manager: RAGManager = Depends(get_rag_manager)
):
    """
    Endpoint principal para o RAG. Recebe a query ORIGINAL do usuário
    e o 'topic' extraído pelo classificador.
    """
    # Chama a função query passando os dados corretos
    result = rag_manager.query(request.original_query, request.topic)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


# --- Endpoints do CALENDAR (Agendamento) ---

@app.post("/v1/calendar/schedule", summary="3. Agendar novo tratamento")
async def schedule_treatment(
        request: ScheduleRequest,
        llm: ChatGoogleGenerativeAI = Depends(get_llm),
        service=Depends(get_calendar_service_dep)
):
    """
    Recebe uma prescrição e uma data. Parseia e cria os eventos.
    """
    details = calendar.parse_instruction(request.instrucao, llm)
    if not details:
        raise HTTPException(status_code=400, detail="Não foi possível entender a prescrição.")

    start_time = calendar.get_start_time_from_string(request.start_time_str)
    if not start_time:
        raise HTTPException(status_code=400, detail="Formato de data inválido.")

    try:
        result = calendar.create_calendar_events(service, details, start_time)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar eventos: {e}")


# --- Endpoints do CALENDAR (Leitura e Remoção) ---

@app.get("/v1/calendar/events/{medicamento_nome}", summary="4. Listar eventos futuros")
async def get_future_events(
        medicamento_nome: str,
        service=Depends(get_calendar_service_dep)
):
    """
    Busca e retorna todos os eventos futuros para um medicamento.
    """
    events = calendar.find_future_events_by_name(service, medicamento_nome)
    return {"medicamento": medicamento_nome, "events": events}


@app.post("/v1/calendar/delete", summary="5. Cancelar eventos (um ou 'todos')")
async def delete_calendar_events(
        request: DeleteRequest,
        service=Depends(get_calendar_service_dep)
):
    """
    Deleta uma lista de eventos.
    """
    if not request.event_ids:
        raise HTTPException(status_code=400, detail="Nenhum ID de evento fornecido.")

    result = calendar.delete_events(service, request.event_ids)
    return result


# --- Endpoints do CALENDAR (Edição) ---

@app.put("/v1/calendar/edit/{event_id}", summary="6. Editar um evento")
async def edit_calendar_event(
        event_id: str,
        request: EditRequest,
        service=Depends(get_calendar_service_dep)
):
    """
    Altera o horário de um único evento.
    """
    result = calendar.edit_single_event(service, event_id, request.new_start_time_str)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/auth/login", summary="Forçar Login no Google Calendar")
async def login_google():
    """
    1. Apaga o token antigo (se existir) para forçar o login.
    2. Inicia o fluxo de autenticação (abre o navegador).
    3. Atualiza o serviço na API.
    """
    print("[AUTH] Iniciando fluxo de Login manual...")

    # 1. Remove token antigo para garantir que a janela abra
    if os.path.exists("token.json"):
        os.remove("token.json")
        print("[AUTH] Token antigo removido.")

    # 2. Chama a função de autenticação (Isso vai travar a API até você logar no browser)
    try:
        new_service = get_calendar_service()

        if new_service:
            # 3. Atualiza o estado global da aplicação
            app_state["calendar_service"] = new_service
            return {"message": "Autenticação realizada com sucesso! O token foi salvo."}
        else:
            raise HTTPException(status_code=500, detail="Falha ao obter serviço do Google.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro durante o login: {e}")


@app.post("/auth/logout", summary="Fazer Logout (Apagar Token)")
async def logout_google():
    """
    1. Limpa o serviço da memória da API.
    2. Apaga o arquivo 'token.json' do disco.
    """
    print("[AUTH] Realizando Logout...")

    # 1. Limpa da memória
    app_state["calendar_service"] = None

    # 2. Apaga do disco
    deleted = False
    if os.path.exists("token.pickle"):
        os.remove("token.pickle")
        deleted = True
        print("[AUTH] Arquivo token.pickle apagado.")
    else:
        print("[AUTH] Arquivo token.pickle não encontrado (já estava deslogado).")

    return {
        "message": "Logout realizado com sucesso.",
        "token_deleted": deleted,
        "info": "Para acessar o calendário novamente, você precisará fazer login."
    }

# --- Ponto de Entrada para Execução ---
if __name__ == "__main__":
    print("Iniciando servidor FastAPI com Uvicorn...")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )