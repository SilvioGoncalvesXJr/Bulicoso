// O endereço onde o back ta rodando
const API_URL = "http://127.0.0.1:8000/v1";

export const api = {

  // 1. O CÉREBRO: Classifica o que o usuário quer dizer
  classifyIntent: async (text) => {
    try {
      const response = await fetch(`${API_URL}/chat/classify_intent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text }),
      });

      if (!response.ok) {
        throw new Error(`Erro API: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Erro ao classificar intenção:", error);
      return null;
    }
  },

  // 2. O RAG: Consulta a bula do medicamento
  queryRag: async (originalQuery, topic) => {
    try {
      const response = await fetch(`${API_URL}/rag/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            original_query: originalQuery,
            topic: topic
        }),
      });

      if (!response.ok) {
        throw new Error(`Erro API RAG: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Erro no RAG:", error);
      // Retorna um objeto de erro seguro para não quebrar o front
      return { response: JSON.stringify({ answer: "Desculpe, não consegui conectar ao servidor." }) };
    }
  },

  // 3. CALENDAR: Agendar um tratamento
  scheduleTreatment: async (instrucao, startTime = "agora") => {
    try {
      const response = await fetch(`${API_URL}/calendar/schedule`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            instrucao: instrucao,
            start_time_str: startTime
        }),
      });
      return await response.json();
    } catch (error) {
      console.error("Erro ao agendar:", error);
      return { message: "Erro ao agendar." };
    }
  },

  // 4. CALENDAR: Listar eventos de um medicamento (para edição/cancelamento)
  getEvents: async (medicamento) => {
    try {
      const response = await fetch(`${API_URL}/calendar/events/${medicamento}`);
      return await response.json();
    } catch (error) {
      console.error("Erro ao buscar eventos:", error);
      return { events: [] };
    }
  },

  // 5. CALENDAR: Deletar eventos
  deleteEvents: async (eventIds) => {
    try {
      const response = await fetch(`${API_URL}/calendar/delete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event_ids: eventIds }),
      });
      return await response.json();
    } catch (error) {
      console.error("Erro ao deletar:", error);
      return { message: "Erro ao deletar." };
    }
  },

  // 6. [NOVO] CALENDAR: Editar um evento
  editEvent: async (eventId, newStartTime) => {
    try {
      const response = await fetch(`${API_URL}/calendar/edit/${eventId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_start_time_str: newStartTime }),
      });

      if (!response.ok) {
         const err = await response.json();
         throw new Error(err.detail || "Erro ao editar");
      }
      return await response.json();
    } catch (error) {
      console.error("Erro ao editar:", error);
      throw error;
    }
  }
};