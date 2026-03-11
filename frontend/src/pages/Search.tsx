import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router";
import {
  User,
  Building2,
  FileText,
  AlertTriangle,
  HelpCircle,
  SearchX,
} from "lucide-react";
import { useSearchStore } from "../stores/search";
import SearchBar from "../components/SearchBar";

const typeConfig: Record<
  string,
  { color: string; bg: string; icon: React.ElementType; label: string }
> = {
  Pessoa: {
    color: "var(--accent)",
    bg: "rgba(79,124,255,0.12)",
    icon: User,
    label: "Pessoa",
  },
  Empresa: {
    color: "var(--success)",
    bg: "rgba(47,221,111,0.12)",
    icon: Building2,
    label: "Empresa",
  },
  Contrato: {
    color: "var(--warning)",
    bg: "rgba(255,170,47,0.12)",
    icon: FileText,
    label: "Contrato",
  },
  Sancao: {
    color: "var(--danger)",
    bg: "rgba(255,79,111,0.12)",
    icon: AlertTriangle,
    label: "Sancao",
  },
  Licitacao: {
    color: "#c084fc",
    bg: "rgba(192,132,252,0.12)",
    icon: FileText,
    label: "Licitacao",
  },
};

function getTypeConfig(type: string) {
  return (
    typeConfig[type] ?? {
      color: "var(--text-secondary)",
      bg: "rgba(136,136,160,0.12)",
      icon: HelpCircle,
      label: type,
    }
  );
}

function SkeletonRow() {
  return (
    <tr>
      {[120, 250, 160, 60].map((w, i) => (
        <td key={i} style={{ padding: "14px 16px" }}>
          <div
            className="skeleton"
            style={{ height: 18, width: w, borderRadius: 6 }}
          />
        </td>
      ))}
    </tr>
  );
}

export default function SearchPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { query, results, loading, error, search, setQuery } = useSearchStore();

  const urlQuery = searchParams.get("q") || "";

  // Sync URL query to store on mount or URL change
  useEffect(() => {
    if (urlQuery && urlQuery !== query) {
      setQuery(urlQuery);
      search(urlQuery);
    }
  }, [urlQuery]);

  const handleSearch = (q: string) => {
    setSearchParams(q ? { q } : {});
    search(q);
  };

  const handleRowClick = (id: string) => {
    navigate(`/graph/${encodeURIComponent(id)}`);
  };

  return (
    <div
      style={{
        maxWidth: 1000,
        margin: "0 auto",
        padding: "2rem",
        animation: "fadeIn 0.4s ease",
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: "2rem" }}>
        <h1
          style={{
            fontSize: "1.75rem",
            fontWeight: 700,
            marginBottom: "0.75rem",
          }}
        >
          Busca de Entidades
        </h1>
        <SearchBar
          initialValue={urlQuery}
          onSearch={handleSearch}
          autoFocus
          large
        />
      </div>

      {/* Error */}
      {error && (
        <div
          style={{
            padding: "1rem 1.25rem",
            borderRadius: "var(--radius-md)",
            background: "rgba(255,79,111,0.1)",
            border: "1px solid rgba(255,79,111,0.25)",
            color: "var(--danger)",
            marginBottom: "1.5rem",
            fontSize: "0.9rem",
          }}
        >
          {error}
        </div>
      )}

      {/* Results Table */}
      {(results.length > 0 || loading) && (
        <div
          style={{
            background: "var(--bg-card)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-lg)",
            overflow: "hidden",
          }}
        >
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
            }}
          >
            <thead>
              <tr
                style={{
                  borderBottom: "1px solid var(--border)",
                }}
              >
                {["Tipo", "Nome", "CNPJ/CPF", "Score"].map((col) => (
                  <th
                    key={col}
                    style={{
                      padding: "12px 16px",
                      textAlign: "left",
                      fontSize: "0.75rem",
                      fontWeight: 600,
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                      color: "var(--text-secondary)",
                    }}
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading
                ? Array.from({ length: 5 }).map((_, i) => (
                    <SkeletonRow key={i} />
                  ))
                : results.map((result) => {
                    const cfg = getTypeConfig(result.type);
                    const Icon = cfg.icon;
                    return (
                      <tr
                        key={result.id}
                        onClick={() => handleRowClick(result.id)}
                        style={{
                          borderBottom: "1px solid var(--border)",
                          cursor: "pointer",
                          transition: "background var(--transition-fast)",
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background =
                            "var(--bg-card-hover)";
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = "transparent";
                        }}
                      >
                        <td style={{ padding: "14px 16px" }}>
                          <span
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: 6,
                              padding: "4px 10px",
                              borderRadius: "var(--radius-sm)",
                              background: cfg.bg,
                              color: cfg.color,
                              fontSize: "0.8rem",
                              fontWeight: 500,
                            }}
                          >
                            <Icon size={14} />
                            {cfg.label}
                          </span>
                        </td>
                        <td
                          style={{
                            padding: "14px 16px",
                            fontWeight: 500,
                            fontSize: "0.9rem",
                          }}
                        >
                          {result.display_name}
                        </td>
                        <td
                          style={{
                            padding: "14px 16px",
                            fontFamily: "var(--font-mono)",
                            fontSize: "0.85rem",
                            color: "var(--text-secondary)",
                          }}
                        >
                          {result.cnpj || "---"}
                        </td>
                        <td style={{ padding: "14px 16px" }}>
                          <span
                            style={{
                              display: "inline-block",
                              padding: "2px 8px",
                              borderRadius: "var(--radius-sm)",
                              background:
                                result.score >= 0.8
                                  ? "rgba(47,221,111,0.12)"
                                  : result.score >= 0.5
                                  ? "rgba(255,170,47,0.12)"
                                  : "rgba(136,136,160,0.1)",
                              color:
                                result.score >= 0.8
                                  ? "var(--success)"
                                  : result.score >= 0.5
                                  ? "var(--warning)"
                                  : "var(--text-secondary)",
                              fontSize: "0.85rem",
                              fontWeight: 600,
                              fontFamily: "var(--font-mono)",
                            }}
                          >
                            {(result.score * 100).toFixed(0)}%
                          </span>
                        </td>
                      </tr>
                    );
                  })}
            </tbody>
          </table>
        </div>
      )}

      {/* Empty State */}
      {!loading && results.length === 0 && query && !error && (
        <div
          style={{
            textAlign: "center",
            padding: "4rem 2rem",
            animation: "fadeIn 0.4s ease",
          }}
        >
          <SearchX
            size={48}
            color="var(--text-secondary)"
            style={{ marginBottom: "1rem", opacity: 0.5 }}
          />
          <h3
            style={{
              fontSize: "1.1rem",
              fontWeight: 600,
              marginBottom: "0.5rem",
            }}
          >
            Nenhum resultado encontrado
          </h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            Tente buscar com termos diferentes ou mais genericos.
          </p>
        </div>
      )}

      {/* Initial State */}
      {!loading && !query && results.length === 0 && (
        <div
          style={{
            textAlign: "center",
            padding: "4rem 2rem",
            animation: "fadeIn 0.4s ease",
          }}
        >
          <div
            style={{
              width: 80,
              height: 80,
              borderRadius: "50%",
              background: "var(--accent-glow)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 1.5rem",
            }}
          >
            <Building2 size={32} color="var(--accent)" />
          </div>
          <h3
            style={{
              fontSize: "1.1rem",
              fontWeight: 600,
              marginBottom: "0.5rem",
            }}
          >
            Pesquise no grafo de dados publicos
          </h3>
          <p
            style={{
              color: "var(--text-secondary)",
              fontSize: "0.9rem",
              maxWidth: 400,
              margin: "0 auto",
            }}
          >
            Digite o nome de uma pessoa, empresa, CNPJ ou numero de contrato
            para iniciar a busca.
          </p>
        </div>
      )}

      {/* Result count */}
      {!loading && results.length > 0 && (
        <div
          style={{
            marginTop: "1rem",
            fontSize: "0.8rem",
            color: "var(--text-secondary)",
          }}
        >
          {results.length} resultado{results.length !== 1 ? "s" : ""}{" "}
          encontrado{results.length !== 1 ? "s" : ""}
        </div>
      )}
    </div>
  );
}
