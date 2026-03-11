function App() {
  return (
    <div
      style={{
        fontFamily: "system-ui, -apple-system, sans-serif",
        maxWidth: 800,
        margin: "0 auto",
        padding: "4rem 2rem",
        color: "#1a1a2e",
      }}
    >
      <h1 style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>
        br_accUDI
      </h1>
      <p style={{ fontSize: "1.2rem", color: "#555", marginBottom: "2rem" }}>
        Infraestrutura open-source de grafo que cruza dados públicos municipais
        de Uberlândia para gerar inteligência cívica acionável.
      </p>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: "1rem",
          marginBottom: "2rem",
        }}
      >
        <div
          style={{
            background: "#f0f4ff",
            padding: "1.5rem",
            borderRadius: "12px",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>10</div>
          <div style={{ color: "#666", fontSize: "0.9rem" }}>
            Fontes de dados
          </div>
        </div>
        <div
          style={{
            background: "#f0fff4",
            padding: "1.5rem",
            borderRadius: "12px",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>8</div>
          <div style={{ color: "#666", fontSize: "0.9rem" }}>
            Padrões detectados
          </div>
        </div>
        <div
          style={{
            background: "#fff8f0",
            padding: "1.5rem",
            borderRadius: "12px",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "2rem", fontWeight: 700 }}>100%</div>
          <div style={{ color: "#666", fontSize: "0.9rem" }}>
            Dados públicos
          </div>
        </div>
      </div>
      <p style={{ color: "#888", fontSize: "0.9rem" }}>
        Em construção. Stack: Neo4j + FastAPI + React + Docker.
      </p>
    </div>
  );
}

export default App;
