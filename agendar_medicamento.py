import os
import json
import re
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import pytz

# ==========================
# CONFIGURAÇÕES
# ==========================
load_dotenv(".env", override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from google_calendar_auth import get_calendar_service  # Importa do nosso outro arquivo

# ==========================
# 1. O PARSER (LLM)
# ==========================
llm_parser = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",  # Usando o flash para respostas rápidas
    temperature=0.5,
    google_api_key=GOOGLE_API_KEY
)

PARSER_PROMPT = """
Você é um assistente inteligente que extrai dados de prescrições médicas.
Analise a instrução do usuário e retorne APENAS um objeto JSON com 3 chaves:
1. "medicamento": (string) O nome do medicamento.
2. "intervalo_horas": (int) O intervalo em horas entre as doses. Se for "1 vez ao dia", use 24.
3. "duracao_dias": (int) O número total de dias. Se for "uma semana", use 7.

Instrução do Usuário:
{instrucao}

JSON:
"""

prompt_template = PromptTemplate(
    input_variables=["instrucao"],
    template=PARSER_PROMPT
)


def parse_instruction(text: str) -> dict:
    """Usa o LLM para converter texto em um JSON estruturado."""
    print(f"[LLM] Analisando instrução: '{text}'")

    prompt = prompt_template.format(instrucao=text)
    try:
        response = llm_parser.invoke(prompt)
        content = response.content

        # Limpa a resposta do LLM para garantir que é um JSON válido
        # Remove ```json e ```
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if not json_match:
            print("[ERRO] LLM não retornou um JSON válido.")
            return None

        clean_json = json_match.group(0)
        details = json.loads(clean_json)

        # Validação básica
        if "medicamento" not in details or "intervalo_horas" not in details or "duracao_dias" not in details:
            print("[ERRO] JSON retornado não contém as chaves necessárias.")
            return None

        print(f"[LLM] Dados extraídos: {details}")
        return details

    except Exception as e:
        print(f"[ERRO] Falha ao analisar com o LLM: {e}")
        return None


# ==========================
# 2. O EXECUTOR (Google Calendar)
# ==========================
def create_calendar_events(service, details: dict):
    """Cria os eventos no Google Calendar."""

    medicamento = details["medicamento"]
    intervalo_horas = details["intervalo_horas"]
    duracao_dias = details["duracao_dias"]

    # Calcula o número total de doses
    total_doses = (duracao_dias * 24) // intervalo_horas

    # O fuso horário local
    # (Importante para o Google Calendar saber a hora certa)
    local_tz = pytz.timezone("America/Sao_Paulo")  # ou outro fuso válido
    start_time = datetime.now(local_tz)

    print(f"[CAL] Agendando {total_doses} doses de {medicamento}...")

    for i in range(total_doses):
        # Calcula a hora da dose atual
        dose_time = start_time + timedelta(hours=(i * intervalo_horas))
        # O evento terá 30 minutos de duração
        end_time = dose_time + timedelta(minutes=30)

        event_body = {
            'summary': f'Tomar {medicamento.upper()}',
            'description': f'Dose {i + 1} de {total_doses} do tratamento.',
            'start': {
                'dateTime': dose_time.isoformat(),
                'timeZone': "America/Sao_Paulo",
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': "America/Sao_Paulo",
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 10},
                    {'method': 'email', 'minutes': 30},
                ],
            },
        }

        try:
            event = service.events().insert(
                calendarId='primary',  # 'primary' é a sua agenda principal
                body=event_body
            ).execute()
            print(f"  -> Evento criado: {event.get('htmlLink')}")

        except Exception as e:
            print(f"[ERRO] Falha ao criar evento: {e}")


# ==========================
# 3. O LOOP PRINCIPAL
# ==========================
if __name__ == "__main__":
    print("--- Agendador de Medicamentos v1.0 ---")

    # Passo 1: Autenticar no Google
    print("[AUTH] Iniciando autenticação no Google Calendar...")
    print("(Uma janela do navegador pode abrir para você dar permissão)")

    service = get_calendar_service()

    if not service:
        print("[AUTH] Falha na autenticação. Encerrando.")
    else:
        print("[AUTH] Autenticado com sucesso!")

        # Loop para receber comandos
        while True:
            try:
                instrucao = input("\nDigite a instrução (ou 'sair' para fechar): \n> ")
                if instrucao.lower() == 'sair':
                    break

                # Passo 2: Analisar a instrução
                details = parse_instruction(instrucao)

                if details:
                    # Passo 3: Criar os eventos
                    create_calendar_events(service, details)
                    print(f"\n[SUCESSO] Tratamento de {details['medicamento']} agendado!")

            except KeyboardInterrupt:
                print("\nEncerrando...")
                break
            except Exception as e:
                print(f"[ERRO INESPERADO] {e}")