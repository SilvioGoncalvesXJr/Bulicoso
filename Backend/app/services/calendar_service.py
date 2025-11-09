"""
Serviço para integração com Google Calendar (lembretes de medicamentos)
"""
from typing import Optional
from datetime import datetime, timedelta
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings


class CalendarService:
    """Serviço para criar lembretes no Google Calendar"""
    
    def __init__(
        self,
        credentials_path: Optional[str] = None,
        calendar_id: Optional[str] = None
    ):
        """
        Inicializa o serviço de calendário
        
        Args:
            credentials_path: Caminho para arquivo de credenciais do Google
            calendar_id: ID do calendário do Google
        """
        self.credentials_path = credentials_path
        self.calendar_id = calendar_id
        self.llm = None
        
        # Inicializar LLM para interpretar linguagem natural
        if settings.GOOGLE_API_KEY:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                temperature=0.0,
                google_api_key=settings.GOOGLE_API_KEY
            )
    
    def interpretar_frequencia(self, frequencia: str) -> dict:
        """
        Interpreta a frequência em linguagem natural usando Gemini
        
        Args:
            frequencia: Frequência em linguagem natural (ex: "3 vezes ao dia", "a cada 8 horas")
            
        Returns:
            Dicionário com informações estruturadas da frequência
        """
        if not self.llm:
            raise ValueError("LLM não inicializado. Configure GOOGLE_API_KEY.")
        
        prompt = f"""
        Analise a seguinte frequência de medicamento e retorne APENAS um JSON válido com:
        - "vezes_por_dia": número inteiro (ex: 3)
        - "intervalo_horas": número decimal (ex: 8.0)
        - "horarios_sugeridos": array de strings no formato HH:MM (ex: ["08:00", "14:00", "20:00"])
        
        Frequência: "{frequencia}"
        
        Se não conseguir determinar, use valores padrão razoáveis.
        Retorne APENAS o JSON, sem markdown, sem explicações.
        """
        
        try:
            response = self.llm.invoke(prompt)
            # Extrair JSON da resposta (pode estar em markdown code block)
            content = response.content.strip()
            
            # Remover markdown code blocks se existirem
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            import json
            parsed = json.loads(content)
            
            return {
                "vezes_por_dia": parsed.get("vezes_por_dia", 1),
                "intervalo_horas": parsed.get("intervalo_horas", 24.0),
                "horarios_sugeridos": parsed.get("horarios_sugeridos", ["08:00"])
            }
        except Exception as e:
            print(f"[Calendar] Erro ao interpretar frequência: {e}")
            # Valores padrão
            return {
                "vezes_por_dia": 1,
                "intervalo_horas": 24.0,
                "horarios_sugeridos": ["08:00"]
            }
    
    def interpretar_duracao(self, duracao: str) -> int:
        """
        Interpreta a duração do tratamento em linguagem natural
        
        Args:
            duracao: Duração em linguagem natural (ex: "por 7 dias", "até terminar")
            
        Returns:
            Número de dias
        """
        if not self.llm:
            raise ValueError("LLM não inicializado. Configure GOOGLE_API_KEY.")
        
        prompt = f"""
        Analise a seguinte duração de tratamento e retorne APENAS um número inteiro representando 
        quantos dias o tratamento deve durar.
        
        Duração: "{duracao}"
        
        Se mencionar "até terminar" ou similar, retorne 30 dias como padrão.
        Retorne APENAS o número, sem texto adicional.
        """
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            # Extrair número
            numbers = re.findall(r'\d+', content)
            if numbers:
                return int(numbers[0])
            return 30  # Padrão
        except Exception as e:
            print(f"[Calendar] Erro ao interpretar duração: {e}")
            return 30  # Padrão
    
    def criar_lembretes(
        self,
        medicamento: str,
        frequencia: str,
        duracao: Optional[str] = None,
        horario_inicio: Optional[str] = None,
        observacoes: Optional[str] = None
    ) -> dict:
        """
        Cria lembretes no Google Calendar
        
        Args:
            medicamento: Nome do medicamento
            frequencia: Frequência em linguagem natural
            duracao: Duração do tratamento (opcional)
            horario_inicio: Horário de início no formato HH:MM (opcional)
            observacoes: Observações adicionais (opcional)
            
        Returns:
            Dicionário com resultado da operação
        """
        # TODO: Implementar integração real com Google Calendar API
        # Por enquanto, retorna estrutura simulada
        
        try:
            # Interpretar frequência e duração
            freq_info = self.interpretar_frequencia(frequencia)
            dias_duracao = self.interpretar_duracao(duracao) if duracao else 30
            
            # Determinar horário de início
            if horario_inicio:
                hora, minuto = map(int, horario_inicio.split(":"))
                inicio = datetime.now().replace(hour=hora, minute=minuto, second=0, microsecond=0)
            else:
                inicio = datetime.now()
            
            # Calcular próximo lembrete
            if freq_info["horarios_sugeridos"]:
                primeiro_horario = freq_info["horarios_sugeridos"][0]
                hora, minuto = map(int, primeiro_horario.split(":"))
                proximo = inicio.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                if proximo < datetime.now():
                    proximo += timedelta(days=1)
            else:
                proximo = inicio + timedelta(hours=freq_info["intervalo_horas"])
            
            return {
                "sucesso": True,
                "mensagem": f"Lembretes configurados para {medicamento} ({frequencia}) por {dias_duracao} dias",
                "evento_id": "simulado_123",  # TODO: ID real do Google Calendar
                "medicamento": medicamento,
                "proximo_lembrete": proximo.isoformat(),
                "frequencia_interpretada": freq_info
            }
        except Exception as e:
            return {
                "sucesso": False,
                "mensagem": f"Erro ao criar lembretes: {str(e)}",
                "evento_id": None,
                "medicamento": medicamento,
                "proximo_lembrete": None
            }

