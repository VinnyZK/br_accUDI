import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import {
  Search,
  Network,
  Shield,
  Database,
  GitBranch,
  ArrowRight,
} from "lucide-react";
import { fetchMeta, type MetaResponse } from "../api/client";
import StatCard from "../components/StatCard";
import SearchBar from "../components/SearchBar";

const features = [
  {
    icon: Search,
    title: "Busca Inteligente",
    description:
      "Pesquise por pessoas, empresas, contratos e licitacoes com busca fuzzy de alta performance sobre milhoes de registros publicos.",
    color: "var(--accent)",
  },
  {
    icon: Network,
    title: "Grafo de Conexoes",
    description:
      "Visualize redes de relacionamentos entre entidades com grafos interativos. Descubra conexoes ocultas entre empresas e pessoas.",
    color: "var(--success)",
  },
  {
    icon: Shield,
    title: "Deteccao de Padroes",
    description:
      "Algoritmos identificam automaticamente padroes suspeitos como empresas laranjas, cartel em licitacoes e conflitos de interesse.",
    color: "var(--warning)",
  },
];

export default function Landing() {
  const navigate = useNavigate();
  const [meta, setMeta] = useState<MetaResponse | null>(null);

  useEffect(() => {
    fetchMeta()
      .then(setMeta)
      .catch(() => {
        // API not available — use placeholder data for demo
        setMeta({
          node_labels: [
            { label: "Pessoa", count: 12450 },
            { label: "Empresa", count: 8320 },
            { label: "Contrato", count: 34210 },
            { label: "Licitacao", count: 5680 },
          ],
          total_nodes: 60660,
          total_relationships: 187400,
        });
      });
  }, []);

  const totalNodes = meta ? meta.total_nodes : 0;

  const handleSearch = (query: string) => {
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <div style={{ position: "relative", minHeight: "calc(100vh - 60px)" }}>
      {/* Animated background */}
      <div className="bg-animated-gradient" />

      {/* Content */}
      <div
        style={{
          position: "relative",
          zIndex: 1,
          maxWidth: 1100,
          margin: "0 auto",
          padding: "0 2rem",
        }}
      >
        {/* Hero */}
        <section
          style={{
            paddingTop: "6rem",
            paddingBottom: "3rem",
            textAlign: "center",
            animation: "fadeInUp 0.8s ease forwards",
          }}
        >
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              padding: "6px 16px",
              borderRadius: "var(--radius-xl)",
              background: "var(--accent-glow)",
              border: "1px solid rgba(79, 124, 255, 0.2)",
              fontSize: "0.8rem",
              color: "var(--accent)",
              fontWeight: 500,
              marginBottom: "1.5rem",
            }}
          >
            <Database size={14} />
            Inteligencia Civica Open-Source
          </div>

          <h1
            style={{
              fontSize: "clamp(2.5rem, 5vw, 4rem)",
              fontWeight: 800,
              lineHeight: 1.1,
              letterSpacing: "-0.03em",
              marginBottom: "1rem",
            }}
          >
            br_acc
            <span
              style={{
                color: "var(--accent)",
                textShadow: "0 0 40px var(--accent-glow)",
              }}
            >
              UDI
            </span>
          </h1>

          <p
            style={{
              fontSize: "clamp(1rem, 2vw, 1.25rem)",
              color: "var(--text-secondary)",
              maxWidth: 640,
              margin: "0 auto 2.5rem",
              lineHeight: 1.7,
            }}
          >
            Infraestrutura de grafo que cruza dados publicos municipais de
            Uberlandia para gerar inteligencia civica acionavel. Transparencia
            como ferramenta de cidadania.
          </p>

          {/* Search bar */}
          <div style={{ maxWidth: 600, margin: "0 auto 1rem" }}>
            <SearchBar onSearch={handleSearch} large autoFocus />
          </div>

          <p
            style={{
              fontSize: "0.8rem",
              color: "var(--text-secondary)",
              opacity: 0.7,
            }}
          >
            Experimente: "Prefeitura de Uberlandia", "CNPJ 12.345.678/0001-90"
          </p>
        </section>

        {/* Stats */}
        {meta && (
          <section
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "1rem",
              marginBottom: "4rem",
            }}
          >
            <StatCard
              label="Entidades no Grafo"
              value={totalNodes}
              icon={<Database size={22} color="var(--accent)" />}
              delay={100}
            />
            <StatCard
              label="Relacionamentos"
              value={meta.total_relationships}
              icon={<GitBranch size={22} color="var(--accent)" />}
              delay={250}
            />
            {meta.node_labels.slice(0, 2).map((node, i) => (
              <StatCard
                key={node.label}
                label={node.label === "Pessoa" ? "Pessoas" : node.label === "Empresa" ? "Empresas" : node.label}
                value={node.count}
                icon={<Database size={22} color="var(--accent)" />}
                delay={400 + i * 150}
              />
            ))}
          </section>
        )}

        {/* Features */}
        <section style={{ marginBottom: "5rem" }}>
          <h2
            style={{
              textAlign: "center",
              fontSize: "1.5rem",
              fontWeight: 700,
              marginBottom: "0.5rem",
              animation: "fadeIn 0.6s ease forwards",
            }}
          >
            Funcionalidades
          </h2>
          <p
            style={{
              textAlign: "center",
              color: "var(--text-secondary)",
              marginBottom: "2.5rem",
              fontSize: "0.95rem",
            }}
          >
            Ferramentas para investigar e compreender dados publicos
          </p>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
              gap: "1.25rem",
            }}
          >
            {features.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <div
                  key={feature.title}
                  style={{
                    background: "var(--bg-card)",
                    border: "1px solid var(--border)",
                    borderRadius: "var(--radius-lg)",
                    padding: "2rem",
                    transition: "all var(--transition-normal)",
                    animation: `fadeInUp 0.6s ease ${0.1 + i * 0.15}s both`,
                    cursor: "default",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = "var(--bg-card-hover)";
                    e.currentTarget.style.borderColor = feature.color;
                    e.currentTarget.style.transform = "translateY(-4px)";
                    e.currentTarget.style.boxShadow = `0 8px 30px ${feature.color}20`;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = "var(--bg-card)";
                    e.currentTarget.style.borderColor = "var(--border)";
                    e.currentTarget.style.transform = "translateY(0)";
                    e.currentTarget.style.boxShadow = "none";
                  }}
                >
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: "var(--radius-md)",
                      background: `${feature.color}18`,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      marginBottom: "1.25rem",
                    }}
                  >
                    <Icon size={22} color={feature.color} />
                  </div>
                  <h3
                    style={{
                      fontSize: "1.1rem",
                      fontWeight: 600,
                      marginBottom: "0.5rem",
                    }}
                  >
                    {feature.title}
                  </h3>
                  <p
                    style={{
                      fontSize: "0.9rem",
                      color: "var(--text-secondary)",
                      lineHeight: 1.65,
                    }}
                  >
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </section>

        {/* CTA */}
        <section
          style={{
            textAlign: "center",
            paddingBottom: "4rem",
            animation: "fadeIn 0.8s ease 0.5s both",
          }}
        >
          <button
            onClick={() => navigate("/search")}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              padding: "14px 32px",
              borderRadius: "var(--radius-lg)",
              background: "var(--accent)",
              color: "#fff",
              fontWeight: 600,
              fontSize: "1rem",
              transition: "all var(--transition-fast)",
              boxShadow: "var(--shadow-glow)",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "#3a68e8";
              e.currentTarget.style.transform = "translateY(-2px)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "var(--accent)";
              e.currentTarget.style.transform = "translateY(0)";
            }}
          >
            Comecar a Explorar
            <ArrowRight size={18} />
          </button>
        </section>

        {/* Footer */}
        <footer
          style={{
            textAlign: "center",
            padding: "2rem 0",
            borderTop: "1px solid var(--border)",
            color: "var(--text-secondary)",
            fontSize: "0.8rem",
          }}
        >
          br_accUDI — Dados publicos, inteligencia civica. Projeto open-source
          AGPL-3.0.
        </footer>
      </div>
    </div>
  );
}
