import React, { useState, useRef, useEffect } from "react";
import "./MainContent.css";
import { api } from "../../services/api";
import Card from "../Card/Card";
import Message from "../Message/Message";
import BulicosoAvatar from "../../assets/bulicosoAvatar.png";

export default function MainContent() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);

  // Estado inicial das mensagens
  const [messages, setMessages] = useState([{}]);

  // --- ESTADOS DOS MODAIS ---
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [scheduleData, setScheduleData] = useState({ instrucao: "", inicio: "agora" });

  const [showCancelModal, setShowCancelModal] = useState(false);

  const [showEditModal, setShowEditModal] = useState(false);
  const [editNewTime, setEditNewTime] = useState("");

  // Estados compartilhados (Busca de eventos)
  const [medNameSearch, setMedNameSearch] = useState("");
  const [eventsFound, setEventsFound] = useState([]);
  const [selectedEventIds, setSelectedEventIds] = useState([]);
  const [isSearchingEvents, setIsSearchingEvents] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Cartões de Exemplo (Balões)
  const exemplos = [
    { id: 1, text: "Quais as reações da Dipirona?" },
    { id: 2, text: "Quero agendar medicamento" },
    { id: 3, text: "Cancelar meu agendamento" },
    { id: 4, text: "Editar horário de remédio" },
  ];

  // --- FUNÇÃO PRINCIPAL DE ENVIO ---
  // Agora aceita um argumento opcional 'textoManual' para quando clicar no card
  async function handleEnviar(textoManual = null) {
    // Se textoManual existir (clique no card), usa ele. Se não, usa o estado 'prompt' (input).
    const textoUsuario = (typeof textoManual === "string" ? textoManual : prompt).trim();

    if (!textoUsuario) return;

    setPrompt(""); // Limpa o input
    setLoading(true);

    // Adiciona mensagem do usuário no chat
    setMessages(prev => [...prev, { role: 'user', text: textoUsuario }]);

    try {
      const intentData = await api.classifyIntent(textoUsuario);
      if (!intentData) throw new Error("Sem resposta do cérebro.");

      setMessages(prev => [...prev, { role: 'bot', text: intentData.message }]);

      // PREPARAR ESTADOS COMUNS
      if (intentData.medicamento) {
          setMedNameSearch(intentData.medicamento);
      } else {
          setMedNameSearch("");
      }
      setEventsFound([]);
      setSelectedEventIds([]);

      // --- ROTEAMENTO DE INTENÇÃO ---

      if (intentData.intent === 'schedule') {
        setShowScheduleForm(true);
      }

      else if (intentData.intent === 'query_rag') {
        setMessages(prev => [...prev, { role: 'bot', text: "🔍 Consultando a bula..." }]);
        const ragResult = await api.queryRag(textoUsuario, intentData.topic);
        let respostaFinal = ragResult.response;
        try { const parsed = JSON.parse(ragResult.response); respostaFinal = parsed.answer; } catch(e) {}
        setMessages(prev => [...prev, { role: 'bot', text: respostaFinal }]);
      }

      else if (intentData.intent === 'cancel') {
          setShowCancelModal(true);
          if (intentData.medicamento) fetchEvents(intentData.medicamento);
      }

      else if (intentData.intent === 'edit') {
          setShowEditModal(true);
          if (intentData.medicamento) fetchEvents(intentData.medicamento);
      }

    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'bot', text: "Ocorreu um erro. Tente novamente." }]);
    } finally {
      setLoading(false);
    }
  }

  // --- FUNÇÕES AUXILIARES ---

  const fetchEvents = async (name) => {
      if(!name) return;
      setIsSearchingEvents(true);
      try {
          const result = await api.getEvents(name);
          setEventsFound(result.events || []);
          if (result.events.length === 0) alert("Nenhum evento encontrado.");
      } catch { alert("Erro ao buscar eventos."); }
      finally { setIsSearchingEvents(false); }
  };

  // --- AGENDAMENTO ---
  const handleConfirmSchedule = async () => {
      if(!scheduleData.instrucao) return;
      setShowScheduleForm(false);
      setLoading(true);
      try {
          const res = await api.scheduleTreatment(scheduleData.instrucao, scheduleData.inicio);
          setMessages(prev => [...prev, { role: 'bot', text: `✅ Agendado! ${res.message}` }]);
      } catch { setMessages(prev => [...prev, { role: 'bot', text: "Erro ao agendar." }]); }
      finally { setLoading(false); setScheduleData({ instrucao: "", inicio: "agora" }); }
  };

  // --- CANCELAMENTO ---
  const handleConfirmCancel = async () => {
      if(selectedEventIds.length === 0) return;
      setShowCancelModal(false);
      setLoading(true);
      try {
          const res = await api.deleteEvents(selectedEventIds);
          setMessages(prev => [...prev, { role: 'bot', text: `✅ Cancelado! ${res.message}` }]);
      } catch { setMessages(prev => [...prev, { role: 'bot', text: "Erro ao cancelar." }]); }
      finally { setLoading(false); }
  };

  // --- EDIÇÃO ---
  const handleConfirmEdit = async () => {
      if(selectedEventIds.length !== 1 || !editNewTime) return;
      setShowEditModal(false);
      setLoading(true);
      try {
          const res = await api.editEvent(selectedEventIds[0], editNewTime);
          setMessages(prev => [...prev, { role: 'bot', text: `✅ Editado! Novo horário: ${res.start_time}` }]);
      } catch (e) {
          setMessages(prev => [...prev, { role: 'bot', text: `Erro ao editar: ${e.message}` }]);
      }
      finally { setLoading(false); setEditNewTime(""); }
  };

  const toggleSelect = (id, single = false) => {
      if (single) {
          setSelectedEventIds([id]);
      } else {
          if (selectedEventIds.includes(id)) setSelectedEventIds(selectedEventIds.filter(x => x !== id));
          else setSelectedEventIds([...selectedEventIds, id]);
      }
  };

  const handleKeyDown = (e) => { if (e.key === 'Enter') handleEnviar(); };

  return (
    <div className="main-container">
      <header className="main-header">
        <h1 className="welcome">Bem vindo, Paulo</h1>
        <p className="subtitle">Assistente Inteligente de Medicação</p>
      </header>

      <div className="content-area">
        <div className="chat-container">

            {/* Renderiza a Saudação Inicial (index 0) */}
            <Message
                role="bot"
                text="Olá! Sou o Buliçoso. Posso te ajudar a agendar, editar, cancelar ou tirar dúvidas sobre medicamentos."
                avatar={BulicosoAvatar}
            />

            {/* --- CARTÕES (BALÕES) SEMPRE VISÍVEIS AQUI --- */}
            {/* Eles ficam entre a saudação e o resto do chat, ou no topo se preferir */}
            <div className="cards-container">
            {exemplos.map((exemplo) => (
                <Card 
                key={exemplo.id} 
                text={exemplo.text} 
                onClick={() => handleEnviar(exemplo.text)} 
                />
            ))}
            </div>

            {/* Renderiza o Resto das Mensagens (Histórico) */}
            {messages.slice(1).map((msg, index) => (
              <div key={index} className={`chat-message ${msg.role}`}>
                <div className="message-bubble">{msg.text}</div>
              </div>
            ))}

            {loading && <div className="chat-message bot"><div className="message-bubble">...</div></div>}
            <div ref={messagesEndRef} />
        </div>
      </div>

      {/* ================= MODAIS ================= */}

      {/* 1. MODAL AGENDAR */}
      {showScheduleForm && (
          <div className="modal-overlay">
              <div className="modal-content">
                  <h3>Agendar</h3>
                  <input className="modal-input" placeholder="Instrução (Ex: Dipirona 8/8h por 5 dias)" value={scheduleData.instrucao} onChange={(e) => setScheduleData({...scheduleData, instrucao: e.target.value})} />
                  <input className="modal-input" style={{marginTop: 10}} placeholder="Início (agora)" value={scheduleData.inicio} onChange={(e) => setScheduleData({...scheduleData, inicio: e.target.value})} />
                  <div className="modal-actions">
                      <button className="cancel-btn" onClick={() => setShowScheduleForm(false)}>Voltar</button>
                      <button className="confirm-btn" onClick={handleConfirmSchedule}>Confirmar</button>
                  </div>
              </div>
          </div>
      )}

      {/* 2. MODAL CANCELAR */}
      {showCancelModal && (
          <div className="modal-overlay">
              <div className="modal-content cancel-modal">
                  <h3>Cancelar Medicamento</h3>
                  <div className="search-box">
                      <input className="modal-input" placeholder="Nome..." value={medNameSearch} onChange={(e) => setMedNameSearch(e.target.value)} />
                      <button className="search-btn" onClick={() => fetchEvents(medNameSearch)}>{isSearchingEvents ? "..." : "🔍"}</button>
                  </div>

                    {/* Checkbox Selecionar Todos */}
                    {eventsFound.length > 0 && (
                        <div style={{ marginBottom: 10 }}>
                        <label>
                            <input
                            type="checkbox"
                            checked={selectedEventIds.length === eventsFound.length}
                            onChange={(e) => {
                                if (e.target.checked) {
                                setSelectedEventIds(eventsFound.map((ev) => ev.id)); // seleciona todos
                                } else {
                                setSelectedEventIds([]); // desmarca todos
                                }
                            }}
                            />{" "}
                            Selecionar Todos
                        </label>
                        </div>
                    )}

                  <div className="events-list">
                      <ul>
                        {eventsFound.map(ev => (
                            <li key={ev.id} className="event-item">
                                <label>
                                    <input type="checkbox" checked={selectedEventIds.includes(ev.id)} onChange={() => toggleSelect(ev.id)} />
                                    <span className="event-date">{ev.start_time_formatted}</span> <span className="event-name">{ev.summary}</span>
                                </label>
                            </li>
                        ))}
                      </ul>
                  </div>

                  <div className="modal-actions">
                      <button className="cancel-btn" onClick={() => setShowCancelModal(false)}>Fechar</button>
                      <button className="confirm-btn delete-action" onClick={handleConfirmCancel} disabled={selectedEventIds.length === 0}>Cancelar Selecionados</button>
                  </div>
              </div>
          </div>
      )}

      {/* 3. MODAL EDITAR */}
      {showEditModal && (
          <div className="modal-overlay">
              <div className="modal-content cancel-modal">
                  <h3>Editar Horário</h3>
                  <p style={{fontSize: 13, color: '#666'}}>Selecione <b>uma</b> dose para mudar o horário.</p>

                  <div className="search-box">
                      <input className="modal-input" placeholder="Nome..." value={medNameSearch} onChange={(e) => setMedNameSearch(e.target.value)} />
                      <button className="search-btn" onClick={() => fetchEvents(medNameSearch)}>{isSearchingEvents ? "..." : "🔍"}</button>
                  </div>

                  <div className="events-list">
                      <ul>
                          {eventsFound.map(ev => (
                              <li key={ev.id} className="event-item">
                                  <label>
                                      <input type="checkbox" checked={selectedEventIds.includes(ev.id)} onChange={() => toggleSelect(ev.id, true)} />
                                      <span className="event-date">{ev.start_time_formatted}</span> <span className="event-name">{ev.summary}</span>
                                  </label>
                              </li>
                          ))}
                      </ul>
                  </div>

                  {selectedEventIds.length === 1 && (
                      <div style={{marginTop: 15}}>
                          <p style={{marginBottom: 5}}>Novo Horário:</p>
                          <input className="modal-input" placeholder="DD/MM/AAAA HH:MM" value={editNewTime} onChange={(e) => setEditNewTime(e.target.value)} />
                      </div>
                  )}

                  <div className="modal-actions">
                      <button className="cancel-btn" onClick={() => setShowEditModal(false)}>Fechar</button>
                      <button className="confirm-btn" onClick={handleConfirmEdit} disabled={selectedEventIds.length !== 1 || !editNewTime}>Salvar Edição</button>
                  </div>
              </div>
          </div>
      )}

      {/* FOOTER INPUT */}
      <div className="footer-input-container">
        <div className="input-wrapper">
          <input className="input-field" placeholder="Digite aqui..." value={prompt} onChange={(e) => setPrompt(e.target.value)} onKeyDown={handleKeyDown} disabled={loading} />
          <button className="send-btn" onClick={() => handleEnviar()} disabled={loading}>›</button>
        </div>
      </div>
    </div>
  );
}