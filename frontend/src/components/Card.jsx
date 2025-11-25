import React from "react";

function Card({ likes }) {
  return (
    <div className="card">
      <h3>
        Exemplo <span style={{ cursor: "pointer" }}>×</span>
      </h3>
      <p>sadasdasdasdasdasdasdasdasdasdasdasdasdasd...</p>
      <div className="card-footer">
        <span>❤️ {likes}</span>
        <span>🔗</span>
      </div>
    </div>
  );
}

export default Card;
