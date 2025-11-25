import React from "react";
import "./MainContent.css";


export default function MainContent() {

  const exemplos = [
    { id: 1, likes: "1.2K", text: "sadasdasdasdasdasdasdasdasdasdasdasda" },
    { id: 2, likes: "26.9K", text: "sadasdasdasdasdasdasdasdasdasdasdasda" },
    { id: 3, likes: "800", text: "sadasdasdasdasdasdasdasdasdasdasdasda" },
    { id: 4, likes: "17.2K", text: "sadasdasdasdasdasdasdasdasdasdasdasda" },
    { id: 5, likes: "4.6K", text: "sadasdasdasdasdasdasdasdasdasdasdasda" },
    { id: 6, likes: "21.4K", text: "sadasdasdasdasdasdasdasdasdasdasdasda" },
  ];

  return (

    <div className="main-container">

      <div className="initial-search">
        <input className="initial-input-search" type="text" placeholder="conversas" />
        <button className="initial-button-search">+ Iniciar uma conversar</button>
      </div>

      <header className="main-header">

        <h1 className="welcome">Bem vindo, Paulo</h1>
        
        <p className="subtitle">Exemplo xxx - xxx - xxx</p>

        <div className="input-container">
          <input
            type="text"
            placeholder="Como posso ajudá-lo hoje?"
            className="input-field"
          />
          <button className="send-btn">P</button>
        </div>
      </header>

      <div className="cards-container">
        {exemplos.map((ex) => (
          <div key={ex.id} className="card">
            <div className="card-header">
              
            </div>
            <p className="card-text">{ex.text}</p>
            <div className="card-footer">
              
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
