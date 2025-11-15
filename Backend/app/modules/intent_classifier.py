# modules/intent_classifier.py
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import Optional


# Definir o que esperamos do LLM
class IntentResponse(BaseModel):
    intent: str = Field(description="A intenção do usuário. Ex: 'schedule', 'cancel', 'edit', 'query_rag', 'unknown'")
    medicamento: Optional[str] = Field(None, description="O nome do medicamento, se mencionado.")
    topic: Optional[str] = Field(None, description="O tópico da pergunta (ex: 'reações adversas', 'dose')")
    # Adicione outros campos se precisar (ex: horario)


# Prompt para o classificador
INTENT_PROMPT_TEMPLATE = """
Você é um classificador de intenções para um assistente de saúde.
Analise o texto do usuário e retorne APENAS um objeto JSON com a estrutura:
{{
  "intent": "...", // 'schedule', 'cancel', 'edit', 'query_rag', 'unknown'
  "medicamento": "...", // nome do medicamento, se houver
  "topic": "..." // 'reações adversas' ou 'outro'
}}

TEXTO DO USUÁRIO:
{user_query}

Exemplos:
Texto: "Quero agendar um remédio"
JSON: {{"intent": "schedule", "medicamento": null, "topic": null}}

Texto: "Quais as reações adversas da Dipirona?"
JSON: {{"intent": "query_rag", "medicamento": "Dipirona", "topic": "reações adversas"}}

Texto: "Qual a dose de Losartana?"
JSON: {{"intent": "query_rag", "medicamento": "Losartana", "topic": "outro"}}

Texto: "Cancelar minha agenda"
JSON: {{"intent": "cancel", "medicamento": null, "topic": null}}

Texto: "Oi, tudo bem?"
JSON: {{"intent": "unknown", "medicamento": null, "topic": null}}

JSON:
"""

prompt_template = PromptTemplate(
    input_variables=["user_query"],
    template=INTENT_PROMPT_TEMPLATE
)


def classify_intent(query: str, llm: ChatGoogleGenerativeAI) -> IntentResponse:
    """Classifica a intenção do usuário usando um LLM."""
    print(f"[Classifier] Classificando query: '{query}'")
    prompt = prompt_template.format(user_query=query)

    try:
        response = llm.invoke(prompt)
        content = response.content

        # Limpar a resposta do LLM (remover ```json e afins)
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if not json_match:
            print("[Classifier ERRO] LLM não retornou JSON.")
            return IntentResponse(intent="unknown")

        clean_json = json_match.group(0)
        data = json.loads(clean_json)

        # Validar com Pydantic
        intent_data = IntentResponse(**data)
        print(
            f"[Classifier] Intenção: {intent_data.intent}, Medicamento: {intent_data.medicamento}, Tópico: {intent_data.topic}")
        return intent_data

    except Exception as e:
        print(f"[Classifier ERRO] Falha ao parsear: {e}")
        return IntentResponse(intent="unknown")