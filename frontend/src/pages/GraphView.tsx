import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router";
import ForceGraph2D from "react-force-graph-2d";
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  User,
  Building2,
  FileText,
  AlertTriangle,
  Loader2,
  ArrowLeft,
  ChevronDown,
} from "lucide-react";
import {
  fetchGraph,
  type GraphNode,
  type GraphEdge,
  type GraphResponse,
} from "../api/client";

// ===== Node visual config =====

const labelColors: Record<string, { fill: string; stroke: string }> = {
  Pessoa: { fill: "#4f7cff", stroke: "#3a5ec7" },
  Empresa: { fill: "#2fdd6f", stroke: "#22a854" },
  Contrato: { fill: "#ffaa2f", stroke: "#cc8826" },
  Licitacao: { fill: "#c084fc", stroke: "#9966cc" },
  Sancao: { fill: "#ff4f6f", stroke: "#cc3f59" },
};

const defaultNodeColor = { fill: "#8888a0", stroke: "#666680" };

const labelIcons: Record<string, React.ElementType> = {
  Pessoa: User,
  Empresa: Building2,
  Contrato: FileText,
  Licitacao: FileText,
  Sancao: AlertTriangle,
};

function getNodeColor(label: string) {
  return labelColors[label] ?? defaultNodeColor;
}

function getNodeDisplayName(node: GraphNode): string {
  const p = node.properties;
  return (
    (p.nome as string) ??
    (p.razao_social as string) ??
    (p.display_name as string) ??
    (p.name as string) ??
    node.id
  );
}

// ===== Types for force-graph =====

interface FGNode {
  id: string;
  label: string;
  properties: Record<string, unknown>;
  displayName: string;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

interface FGLink {
  source: string | FGNode;
  target: string | FGNode;
  type: string;
  properties: Record<string, unknown>;
}

interface FGGraphData {
  nodes: FGNode[];
  links: FGLink[];
}

export default function GraphView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const graphRef = useRef<any>(null); // eslint-disable-line @typescript-eslint/no-explicit-any
  const containerRef = useRef<HTMLDivElement>(null);

  const [graphData, setGraphData] = useState<FGGraphData>({
    nodes: [],
    links: [],
  });
  const [rawData, setRawData] = useState<GraphResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<FGNode | null>(null);
  const [depth, setDepth] = useState(2);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  // Load graph data
  useEffect(() => {
    if (!id) return;

    setLoading(true);
    setError(null);

    fetchGraph(id, depth)
      .then((data) => {
        setRawData(data);

        const nodes: FGNode[] = data.nodes.map((n: GraphNode) => ({
          id: n.id,
          label: n.label,
          properties: n.properties,
          displayName: getNodeDisplayName(n),
        }));

        const nodeIds = new Set(nodes.map((n) => n.id));

        const links: FGLink[] = data.edges
          .filter(
            (e: GraphEdge) => nodeIds.has(e.source) && nodeIds.has(e.target)
          )
          .map((e: GraphEdge) => ({
            source: e.source,
            target: e.target,
            type: e.type,
            properties: e.properties,
          }));

        setGraphData({ nodes, links });
        setLoading(false);

        // Select the root node
        const rootNode = nodes.find((n) => n.id === id);
        if (rootNode) setSelectedNode(rootNode);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Erro ao carregar grafo");
        setLoading(false);
      });
  }, [id, depth]);

  // Measure container
  useEffect(() => {
    function updateSize() {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setDimensions({ width: rect.width, height: rect.height });
      }
    }
    updateSize();
    window.addEventListener("resize", updateSize);
    return () => window.removeEventListener("resize", updateSize);
  }, []);

  // Zoom to fit after data load
  useEffect(() => {
    if (!loading && graphData.nodes.length > 0 && graphRef.current) {
      setTimeout(() => {
        graphRef.current?.zoomToFit(400, 60);
      }, 500);
    }
  }, [loading, graphData]);

  // Custom node rendering
  const paintNode = useCallback(
    (node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const { fill, stroke } = getNodeColor(node.label);
      const size = node.id === id ? 10 : 7;
      const x = node.x ?? 0;
      const y = node.y ?? 0;
      const isSelected = selectedNode?.id === node.id;

      // Glow for selected
      if (isSelected) {
        ctx.beginPath();
        ctx.arc(x, y, size + 4, 0, 2 * Math.PI);
        ctx.fillStyle = `${fill}33`;
        ctx.fill();
      }

      // Draw shape based on label
      ctx.beginPath();
      if (
        node.label === "Empresa" ||
        node.label === "Contrato" ||
        node.label === "Licitacao"
      ) {
        if (node.label === "Empresa") {
          // Rounded square
          const s = size * 1.6;
          const r = 2;
          ctx.moveTo(x - s / 2 + r, y - s / 2);
          ctx.lineTo(x + s / 2 - r, y - s / 2);
          ctx.quadraticCurveTo(x + s / 2, y - s / 2, x + s / 2, y - s / 2 + r);
          ctx.lineTo(x + s / 2, y + s / 2 - r);
          ctx.quadraticCurveTo(x + s / 2, y + s / 2, x + s / 2 - r, y + s / 2);
          ctx.lineTo(x - s / 2 + r, y + s / 2);
          ctx.quadraticCurveTo(x - s / 2, y + s / 2, x - s / 2, y + s / 2 - r);
          ctx.lineTo(x - s / 2, y - s / 2 + r);
          ctx.quadraticCurveTo(x - s / 2, y - s / 2, x - s / 2 + r, y - s / 2);
        } else {
          // Diamond
          const s = size * 1.3;
          ctx.moveTo(x, y - s);
          ctx.lineTo(x + s, y);
          ctx.lineTo(x, y + s);
          ctx.lineTo(x - s, y);
        }
        ctx.closePath();
      } else {
        // Circle for Pessoa, Sancao, others
        ctx.arc(x, y, size, 0, 2 * Math.PI);
      }

      ctx.fillStyle = fill;
      ctx.fill();
      ctx.strokeStyle = stroke;
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Label
      if (globalScale > 0.6) {
        const label = node.displayName || "";
        const truncated =
          label.length > 20 ? label.substring(0, 20) + "..." : label;
        const fontSize = Math.max(10 / globalScale, 3);
        ctx.font = `${fontSize}px Inter, sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        ctx.fillStyle = "rgba(232,232,240,0.85)";
        ctx.fillText(truncated, x, y + size + 3);
      }
    },
    [id, selectedNode]
  );

  // Custom link rendering
  const paintLink = useCallback(
    (link: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const sx = link.source.x ?? 0;
      const sy = link.source.y ?? 0;
      const tx = link.target.x ?? 0;
      const ty = link.target.y ?? 0;

      ctx.beginPath();
      ctx.moveTo(sx, sy);
      ctx.lineTo(tx, ty);
      ctx.strokeStyle = "rgba(79,124,255,0.2)";
      ctx.lineWidth = 1;
      ctx.stroke();

      // Edge label
      if (globalScale > 1.2) {
        const mx = (sx + tx) / 2;
        const my = (sy + ty) / 2;
        const fontSize = Math.max(8 / globalScale, 2.5);
        ctx.font = `${fontSize}px Inter, sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = "rgba(136,136,160,0.6)";
        ctx.fillText(link.type, mx, my);
      }
    },
    []
  );

  const handleNodeClick = useCallback((node: any) => {
    setSelectedNode(node as FGNode);
  }, []);

  // Get connections for selected node
  const selectedConnections = selectedNode
    ? graphData.links
        .filter((l) => {
          const sId =
            typeof l.source === "string" ? l.source : (l.source as FGNode).id;
          const tId =
            typeof l.target === "string" ? l.target : (l.target as FGNode).id;
          return sId === selectedNode.id || tId === selectedNode.id;
        })
        .map((l) => {
          const sId =
            typeof l.source === "string" ? l.source : (l.source as FGNode).id;
          const tId =
            typeof l.target === "string" ? l.target : (l.target as FGNode).id;
          const otherId = sId === selectedNode.id ? tId : sId;
          const otherNode = graphData.nodes.find((n) => n.id === otherId);
          return {
            type: l.type,
            direction: sId === selectedNode.id ? "saida" : "entrada",
            otherNode,
          };
        })
    : [];

  return (
    <div
      style={{
        display: "flex",
        height: "calc(100vh - 60px)",
        overflow: "hidden",
      }}
    >
      {/* Graph panel */}
      <div
        ref={containerRef}
        style={{
          flex: "0 0 70%",
          position: "relative",
          background: "var(--bg-primary)",
        }}
      >
        {/* Controls */}
        <div
          style={{
            position: "absolute",
            top: 16,
            left: 16,
            zIndex: 10,
            display: "flex",
            flexDirection: "column",
            gap: 8,
          }}
        >
          <button
            onClick={() => navigate(-1)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "8px 14px",
              borderRadius: "var(--radius-md)",
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
              color: "var(--text-primary)",
              fontSize: "0.85rem",
              fontWeight: 500,
            }}
          >
            <ArrowLeft size={16} /> Voltar
          </button>
        </div>

        {/* Zoom controls */}
        <div
          style={{
            position: "absolute",
            bottom: 16,
            left: 16,
            zIndex: 10,
            display: "flex",
            flexDirection: "column",
            gap: 4,
          }}
        >
          {[
            {
              icon: ZoomIn,
              action: () => {
                const currentZoom = graphRef.current?.zoom();
                graphRef.current?.zoom(currentZoom * 1.4, 300);
              },
            },
            {
              icon: ZoomOut,
              action: () => {
                const currentZoom = graphRef.current?.zoom();
                graphRef.current?.zoom(currentZoom / 1.4, 300);
              },
            },
            {
              icon: Maximize2,
              action: () => graphRef.current?.zoomToFit(400, 60),
            },
          ].map(({ icon: Icon, action }, i) => (
            <button
              key={i}
              onClick={action}
              style={{
                width: 36,
                height: 36,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                borderRadius: "var(--radius-md)",
                background: "var(--bg-card)",
                border: "1px solid var(--border)",
                color: "var(--text-primary)",
              }}
            >
              <Icon size={16} />
            </button>
          ))}
        </div>

        {/* Depth selector */}
        <div
          style={{
            position: "absolute",
            top: 16,
            right: "calc(30% + 16px)",
            zIndex: 10,
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <span
            style={{
              fontSize: "0.8rem",
              color: "var(--text-secondary)",
            }}
          >
            Profundidade:
          </span>
          <div style={{ position: "relative" }}>
            <select
              value={depth}
              onChange={(e) => setDepth(Number(e.target.value))}
              style={{
                appearance: "none",
                padding: "6px 32px 6px 12px",
                borderRadius: "var(--radius-md)",
                background: "var(--bg-card)",
                border: "1px solid var(--border)",
                color: "var(--text-primary)",
                fontSize: "0.85rem",
                cursor: "pointer",
                outline: "none",
              }}
            >
              <option value={1}>1</option>
              <option value={2}>2</option>
              <option value={3}>3</option>
            </select>
            <ChevronDown
              size={14}
              style={{
                position: "absolute",
                right: 8,
                top: "50%",
                transform: "translateY(-50%)",
                pointerEvents: "none",
                color: "var(--text-secondary)",
              }}
            />
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "rgba(10,10,15,0.8)",
              zIndex: 20,
            }}
          >
            <div style={{ textAlign: "center" }}>
              <Loader2
                size={32}
                color="var(--accent)"
                style={{
                  animation: "spin 1s linear infinite",
                  marginBottom: "1rem",
                }}
              />
              <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
              <p style={{ color: "var(--text-secondary)" }}>
                Carregando grafo...
              </p>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 20,
            }}
          >
            <div
              style={{
                textAlign: "center",
                padding: "2rem",
                background: "var(--bg-card)",
                borderRadius: "var(--radius-lg)",
                border: "1px solid var(--border)",
              }}
            >
              <AlertTriangle
                size={32}
                color="var(--danger)"
                style={{ marginBottom: "0.75rem" }}
              />
              <p style={{ color: "var(--danger)", marginBottom: "0.5rem" }}>
                {error}
              </p>
              <button
                onClick={() => navigate(-1)}
                style={{
                  padding: "8px 20px",
                  borderRadius: "var(--radius-md)",
                  background: "var(--accent)",
                  color: "#fff",
                  fontSize: "0.85rem",
                  fontWeight: 500,
                }}
              >
                Voltar
              </button>
            </div>
          </div>
        )}

        {/* Graph */}
        {!loading && !error && (
          <ForceGraph2D
            ref={graphRef}
            graphData={graphData}
            width={dimensions.width * 0.7}
            height={dimensions.height}
            nodeCanvasObject={paintNode}
            linkCanvasObject={paintLink}
            onNodeClick={handleNodeClick}
            nodeId="id"
            cooldownTicks={100}
            enableNodeDrag
            enableZoomInteraction
            enablePanInteraction
            backgroundColor="transparent"
          />
        )}

        {/* Legend */}
        <div
          style={{
            position: "absolute",
            bottom: 16,
            right: "calc(30% + 16px)",
            zIndex: 10,
            display: "flex",
            gap: 12,
            padding: "8px 14px",
            background: "rgba(26,26,46,0.9)",
            backdropFilter: "blur(8px)",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border)",
          }}
        >
          {Object.entries(labelColors).map(([label, { fill }]) => (
            <div
              key={label}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 5,
                fontSize: "0.7rem",
                color: "var(--text-secondary)",
              }}
            >
              <div
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: label === "Empresa" ? 2 : "50%",
                  background: fill,
                }}
              />
              {label}
            </div>
          ))}
        </div>
      </div>

      {/* Sidebar */}
      <div
        style={{
          flex: "0 0 30%",
          background: "var(--bg-secondary)",
          borderLeft: "1px solid var(--border)",
          overflowY: "auto",
          padding: "1.5rem",
        }}
      >
        {selectedNode ? (
          <div style={{ animation: "slideInRight 0.3s ease" }}>
            {/* Node type badge */}
            <div style={{ marginBottom: "1rem" }}>
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "4px 12px",
                  borderRadius: "var(--radius-sm)",
                  background: `${getNodeColor(selectedNode.label).fill}18`,
                  color: getNodeColor(selectedNode.label).fill,
                  fontSize: "0.8rem",
                  fontWeight: 500,
                }}
              >
                {(() => {
                  const Icon = labelIcons[selectedNode.label] ?? User;
                  return <Icon size={14} />;
                })()}
                {selectedNode.label}
              </span>
            </div>

            {/* Name */}
            <h2
              style={{
                fontSize: "1.25rem",
                fontWeight: 700,
                marginBottom: "1.5rem",
                lineHeight: 1.3,
              }}
            >
              {selectedNode.displayName}
            </h2>

            {/* Properties */}
            <div style={{ marginBottom: "2rem" }}>
              <h3
                style={{
                  fontSize: "0.75rem",
                  fontWeight: 600,
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  color: "var(--text-secondary)",
                  marginBottom: "0.75rem",
                }}
              >
                Propriedades
              </h3>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: 6,
                }}
              >
                {Object.entries(selectedNode.properties).map(([key, value]) => (
                  <div
                    key={key}
                    style={{
                      padding: "8px 12px",
                      borderRadius: "var(--radius-sm)",
                      background: "var(--bg-card)",
                      border: "1px solid var(--border)",
                    }}
                  >
                    <div
                      style={{
                        fontSize: "0.7rem",
                        color: "var(--text-secondary)",
                        marginBottom: 2,
                      }}
                    >
                      {key}
                    </div>
                    <div
                      style={{
                        fontSize: "0.85rem",
                        wordBreak: "break-all",
                      }}
                    >
                      {String(value ?? "---")}
                    </div>
                  </div>
                ))}
                {Object.keys(selectedNode.properties).length === 0 && (
                  <p
                    style={{
                      fontSize: "0.85rem",
                      color: "var(--text-secondary)",
                    }}
                  >
                    Nenhuma propriedade disponivel.
                  </p>
                )}
              </div>
            </div>

            {/* Connections */}
            <div>
              <h3
                style={{
                  fontSize: "0.75rem",
                  fontWeight: 600,
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  color: "var(--text-secondary)",
                  marginBottom: "0.75rem",
                }}
              >
                Conexoes ({selectedConnections.length})
              </h3>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: 6,
                }}
              >
                {selectedConnections.map((conn, i) => (
                  <div
                    key={i}
                    onClick={() => {
                      if (conn.otherNode) {
                        navigate(
                          `/graph/${encodeURIComponent(conn.otherNode.id)}`
                        );
                      }
                    }}
                    style={{
                      padding: "10px 12px",
                      borderRadius: "var(--radius-sm)",
                      background: "var(--bg-card)",
                      border: "1px solid var(--border)",
                      cursor: conn.otherNode ? "pointer" : "default",
                      transition: "all var(--transition-fast)",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background =
                        "var(--bg-card-hover)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "var(--bg-card)";
                    }}
                  >
                    <div
                      style={{
                        fontSize: "0.75rem",
                        color: "var(--accent)",
                        marginBottom: 4,
                      }}
                    >
                      {conn.direction === "saida" ? "\u2192" : "\u2190"}{" "}
                      {conn.type}
                    </div>
                    <div style={{ fontSize: "0.85rem", fontWeight: 500 }}>
                      {conn.otherNode?.displayName ?? "Desconhecido"}
                    </div>
                    {conn.otherNode && (
                      <div
                        style={{
                          fontSize: "0.7rem",
                          color: "var(--text-secondary)",
                          marginTop: 2,
                        }}
                      >
                        {conn.otherNode.label}
                      </div>
                    )}
                  </div>
                ))}
                {selectedConnections.length === 0 && (
                  <p
                    style={{
                      fontSize: "0.85rem",
                      color: "var(--text-secondary)",
                    }}
                  >
                    Nenhuma conexao encontrada.
                  </p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
              textAlign: "center",
              color: "var(--text-secondary)",
            }}
          >
            <User size={40} style={{ opacity: 0.3, marginBottom: "1rem" }} />
            <p style={{ fontSize: "0.9rem" }}>
              Clique em um no do grafo para ver seus detalhes.
            </p>
          </div>
        )}

        {/* Summary */}
        {rawData && (
          <div
            style={{
              marginTop: "2rem",
              padding: "1rem",
              borderRadius: "var(--radius-md)",
              background: "var(--bg-card)",
              border: "1px solid var(--border)",
            }}
          >
            <div
              style={{
                fontSize: "0.75rem",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                color: "var(--text-secondary)",
                marginBottom: "0.5rem",
              }}
            >
              Resumo do Grafo
            </div>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 8,
              }}
            >
              <div>
                <div
                  style={{
                    fontSize: "1.25rem",
                    fontWeight: 700,
                    color: "var(--accent)",
                  }}
                >
                  {rawData.nodes.length}
                </div>
                <div
                  style={{
                    fontSize: "0.75rem",
                    color: "var(--text-secondary)",
                  }}
                >
                  Nos
                </div>
              </div>
              <div>
                <div
                  style={{
                    fontSize: "1.25rem",
                    fontWeight: 700,
                    color: "var(--accent)",
                  }}
                >
                  {rawData.edges.length}
                </div>
                <div
                  style={{
                    fontSize: "0.75rem",
                    color: "var(--text-secondary)",
                  }}
                >
                  Arestas
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
