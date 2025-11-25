import React from "react";
import "./Sidebar.css";

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-top">
        <h2 className="user-name">Paulo Henrique</h2>
      </div>
   
      <nav className="nav-section">      
        <input className="nav-search" type="text" placeholder="Pesquisar por conversas..." ></input>  
        <button className="nav-btn active">
          
          <span className="label">Conversas</span>
        </button>

        <button className="nav-btn">
          
          <span className="label">Modo de usar</span>
        </button>

        <button className="nav-btn">
          
          <span className="label">Preferência</span>
        </button>
      </nav>

      <div className="section">
        <h3 className="section-title">EXEMPLOS DE USO</h3>
        <ul className="list">
          <li>Exemplo 01</li>
          <li>Exemplo 02</li>
          <li>Exemplo 03</li>
          <li>Exemplo 04</li>
        </ul>
      </div>

      <div className="section">
        <h3 className="section-title">HISTÓRICO DE CONVERSA</h3>
        <ul className="list">
          <li>Chat 01</li>
          <li>Chat 01</li>
          <li>Chat 01</li>
          <li>Chat 01</li>
        </ul>
      </div>

      <button className="new-chat">＋ Iniciar uma nova conversa</button>
    </aside>
  );
}
