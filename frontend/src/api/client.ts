// ===== TypeScript Interfaces =====

export interface NodeMeta {
  label: string;
  count: number;
}

export interface MetaResponse {
  node_labels: NodeMeta[];
  total_nodes: number;
  total_relationships: number;
}

export interface SearchResult {
  type: string;
  id: string;
  display_name: string;
  cnpj: string | null;
  score: number;
}

export interface SearchResponse {
  results: SearchResult[];
}

export interface GraphNode {
  id: string;
  label: string;
  properties: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;
  type: string;
  source: string;
  target: string;
  properties: Record<string, unknown>;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface PatternEvidence {
  [key: string]: unknown;
}

export interface Pattern {
  pattern_id: string;
  pattern_name: string;
  description: string;
  evidence: PatternEvidence[];
  risk_signal: number;
}

export interface PatternsResponse {
  patterns: Pattern[];
}

// ===== API Client =====

const BASE_URL = "/api/v1";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => "Unknown error");
    throw new Error(`API Error ${response.status}: ${errorText}`);
  }

  return response.json() as Promise<T>;
}

export function fetchMeta(): Promise<MetaResponse> {
  return apiFetch<MetaResponse>("/meta");
}

export function searchEntities(
  query: string,
  limit: number = 20
): Promise<SearchResponse> {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  return apiFetch<SearchResponse>(`/search?${params.toString()}`);
}

export function fetchGraph(
  elementId: string,
  depth: number = 2
): Promise<GraphResponse> {
  const params = new URLSearchParams({ depth: String(depth) });
  return apiFetch<GraphResponse>(
    `/graph/${encodeURIComponent(elementId)}?${params.toString()}`
  );
}

export function fetchPatterns(): Promise<PatternsResponse> {
  return apiFetch<PatternsResponse>("/patterns");
}
