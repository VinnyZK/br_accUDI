import { useEffect, useState } from "react";
import {
  Shield,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Loader2,
  AlertOctagon,
  Info,
  Zap,
} from "lucide-react";
import { fetchPatterns, type Pattern } from "../api/client";

const riskConfig: Record<
  string,
  { color: string; bg: string; label: string; icon: React.ElementType }
> = {
  high: {
    color: "var(--danger)",
    bg: "rgba(255,79,111,0.12)",
    label: "Alto Risco",
    icon: AlertOctagon,
  },
  medium: {
    color: "var(--warning)",
    bg: "rgba(255,170,47,0.12)",
    label: "Risco Medio",
    icon: AlertTriangle,
  },
  low: {
    color: "#ffdd2f",
    bg: "rgba(255,221,47,0.12)",
    label: "Risco Baixo",
    icon: Info,
  },
};

function getRiskConfig(signal: number) {
  if (signal >= 3) return riskConfig.high;
  if (signal >= 1) return riskConfig.medium;
  return riskConfig.low;
}

function riskSortOrder(signal: number): number {
  if (signal >= 3) return 0;
  if (signal >= 1) return 1;
  return 2;
}

function PatternCard({ pattern }: { pattern: Pattern }) {
  const [expanded, setExpanded] = useState(false);
  const risk = getRiskConfig(pattern.risk_signal);
  const RiskIcon = risk.icon;

  return (
    <div
      style={{
        background: "var(--bg-card)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-lg)",
        overflow: "hidden",
        transition: "all var(--transition-normal)",
        animation: "fadeInUp 0.5s ease both",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = risk.color;
        e.currentTarget.style.boxShadow = `0 4px 20px ${risk.color}15`;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = "var(--border)";
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      {/* Header */}
      <div style={{ padding: "1.5rem" }}>
        <div
          style={{
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            marginBottom: "1rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div
              style={{
                width: 42,
                height: 42,
                borderRadius: "var(--radius-md)",
                background: risk.bg,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <Zap size={20} color={risk.color} />
            </div>
            <div>
              <h3
                style={{
                  fontSize: "1.05rem",
                  fontWeight: 600,
                  lineHeight: 1.3,
                  marginBottom: 4,
                }}
              >
                {pattern.pattern_name}
              </h3>
              <span
                style={{
                  fontSize: "0.7rem",
                  color: "var(--text-secondary)",
                  fontFamily: "var(--font-mono)",
                }}
              >
                {pattern.pattern_id}
              </span>
            </div>
          </div>

          {/* Risk badge */}
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 5,
              padding: "5px 12px",
              borderRadius: "var(--radius-sm)",
              background: risk.bg,
              color: risk.color,
              fontSize: "0.78rem",
              fontWeight: 600,
              flexShrink: 0,
            }}
          >
            <RiskIcon size={14} />
            {risk.label}
          </span>
        </div>

        {/* Description */}
        <p
          style={{
            fontSize: "0.9rem",
            color: "var(--text-secondary)",
            lineHeight: 1.65,
          }}
        >
          {pattern.description}
        </p>

        {/* Evidence toggle */}
        {pattern.evidence.length > 0 && (
          <button
            onClick={() => setExpanded(!expanded)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              marginTop: "1rem",
              padding: "8px 14px",
              borderRadius: "var(--radius-md)",
              background: "rgba(255,255,255,0.03)",
              border: "1px solid var(--border)",
              color: "var(--text-secondary)",
              fontSize: "0.82rem",
              fontWeight: 500,
              transition: "all var(--transition-fast)",
              width: "100%",
              justifyContent: "center",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "rgba(255,255,255,0.06)";
              e.currentTarget.style.color = "var(--text-primary)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "rgba(255,255,255,0.03)";
              e.currentTarget.style.color = "var(--text-secondary)";
            }}
          >
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            {expanded ? "Ocultar" : "Ver"} evidencias ({pattern.evidence.length}
            )
          </button>
        )}
      </div>

      {/* Evidence list */}
      {expanded && pattern.evidence.length > 0 && (
        <div
          style={{
            borderTop: "1px solid var(--border)",
            padding: "1rem 1.5rem",
            background: "rgba(0,0,0,0.15)",
          }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 8,
            }}
          >
            {pattern.evidence.map((ev, i) => (
              <div
                key={i}
                style={{
                  padding: "10px 14px",
                  borderRadius: "var(--radius-sm)",
                  background: "var(--bg-card)",
                  border: "1px solid var(--border)",
                  animation: `fadeIn 0.3s ease ${i * 0.05}s both`,
                }}
              >
                {/* Show company name as title if available */}
                {"company" in ev && ev.company != null && (
                  <div
                    style={{
                      fontSize: "0.88rem",
                      fontWeight: 600,
                      marginBottom: 6,
                      color: "var(--text-primary)",
                    }}
                  >
                    {String(ev.company)}
                  </div>
                )}
                {/* Show all fields */}
                {Object.entries(ev)
                  .filter(([k]) => k !== "company")
                  .map(([k, v]) => {
                    const label = k.replace(/_/g, " ");
                    const val =
                      typeof v === "number" && k.includes("value")
                        ? `R$ ${v.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`
                        : Array.isArray(v)
                        ? `${v.length} itens`
                        : String(v ?? "---");
                    return (
                      <div
                        key={k}
                        style={{
                          fontSize: "0.78rem",
                          color: "var(--text-secondary)",
                          marginTop: 3,
                          display: "flex",
                          gap: 6,
                        }}
                      >
                        <span style={{ color: "var(--accent)", minWidth: 100 }}>
                          {label}:
                        </span>
                        <span>{val}</span>
                      </div>
                    );
                  })}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function Patterns() {
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPatterns()
      .then((data) => {
        // Sort by risk descending
        const sorted = [...data.patterns].sort(
          (a, b) => riskSortOrder(a.risk_signal) - riskSortOrder(b.risk_signal)
        );
        setPatterns(sorted);
        setLoading(false);
      })
      .catch((err) => {
        setError(
          err instanceof Error ? err.message : "Erro ao carregar padroes"
        );
        setLoading(false);
      });
  }, []);

  // Summary counts
  const highCount = patterns.filter((p) => p.risk_signal >= 3).length;
  const mediumCount = patterns.filter(
    (p) => p.risk_signal >= 1 && p.risk_signal < 3
  ).length;
  const lowCount = patterns.length - highCount - mediumCount;

  return (
    <div
      style={{
        maxWidth: 900,
        margin: "0 auto",
        padding: "2rem",
        animation: "fadeIn 0.4s ease",
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: "2rem" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            marginBottom: "0.5rem",
          }}
        >
          <Shield size={28} color="var(--accent)" />
          <h1 style={{ fontSize: "1.75rem", fontWeight: 700 }}>
            Deteccao de Padroes
          </h1>
        </div>
        <p
          style={{
            color: "var(--text-secondary)",
            fontSize: "0.95rem",
          }}
        >
          Padroes suspeitos identificados automaticamente nos dados publicos
          municipais.
        </p>
      </div>

      {/* Summary bar */}
      {!loading && patterns.length > 0 && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "1rem",
            marginBottom: "2rem",
          }}
        >
          {[
            {
              label: "Alto Risco",
              count: highCount,
              color: "var(--danger)",
              bg: "rgba(255,79,111,0.08)",
            },
            {
              label: "Risco Medio",
              count: mediumCount,
              color: "var(--warning)",
              bg: "rgba(255,170,47,0.08)",
            },
            {
              label: "Risco Baixo",
              count: lowCount,
              color: "#ffdd2f",
              bg: "rgba(255,221,47,0.08)",
            },
          ].map(({ label, count, color, bg }) => (
            <div
              key={label}
              style={{
                padding: "1rem 1.25rem",
                borderRadius: "var(--radius-md)",
                background: bg,
                border: `1px solid ${color}25`,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontSize: "1.5rem",
                  fontWeight: 700,
                  color,
                }}
              >
                {count}
              </div>
              <div
                style={{
                  fontSize: "0.8rem",
                  color: "var(--text-secondary)",
                  marginTop: 2,
                }}
              >
                {label}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: "center", padding: "4rem 2rem" }}>
          <Loader2
            size={32}
            color="var(--accent)"
            style={{ animation: "spin 1s linear infinite", marginBottom: "1rem" }}
          />
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          <p style={{ color: "var(--text-secondary)" }}>
            Carregando padroes detectados...
          </p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div
          style={{
            padding: "1.5rem",
            borderRadius: "var(--radius-md)",
            background: "rgba(255,79,111,0.1)",
            border: "1px solid rgba(255,79,111,0.25)",
            color: "var(--danger)",
            textAlign: "center",
            marginBottom: "1.5rem",
          }}
        >
          <AlertTriangle
            size={24}
            style={{ marginBottom: "0.5rem" }}
          />
          <p>{error}</p>
        </div>
      )}

      {/* Pattern Cards */}
      {!loading && !error && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "1rem",
          }}
        >
          {patterns.map((pattern, i) => (
            <div
              key={pattern.pattern_id}
              style={{ animationDelay: `${i * 0.08}s` }}
            >
              <PatternCard pattern={pattern} />
            </div>
          ))}

          {patterns.length === 0 && (
            <div
              style={{
                textAlign: "center",
                padding: "4rem 2rem",
              }}
            >
              <Shield
                size={48}
                color="var(--success)"
                style={{ marginBottom: "1rem", opacity: 0.5 }}
              />
              <h3
                style={{
                  fontSize: "1.1rem",
                  fontWeight: 600,
                  marginBottom: "0.5rem",
                }}
              >
                Nenhum padrao detectado
              </h3>
              <p
                style={{
                  color: "var(--text-secondary)",
                  fontSize: "0.9rem",
                }}
              >
                Os algoritmos de deteccao nao identificaram padroes suspeitos
                nos dados atuais.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
