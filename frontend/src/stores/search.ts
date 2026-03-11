import { create } from "zustand";
import type { SearchResult } from "../api/client";
import { searchEntities } from "../api/client";

interface SearchState {
  query: string;
  results: SearchResult[];
  loading: boolean;
  error: string | null;
  selectedEntity: SearchResult | null;
  setQuery: (query: string) => void;
  search: (query: string, limit?: number) => Promise<void>;
  setSelectedEntity: (entity: SearchResult | null) => void;
  clearResults: () => void;
}

export const useSearchStore = create<SearchState>((set) => ({
  query: "",
  results: [],
  loading: false,
  error: null,
  selectedEntity: null,

  setQuery: (query: string) => set({ query }),

  search: async (query: string, limit: number = 20) => {
    if (!query.trim()) {
      set({ results: [], loading: false, error: null });
      return;
    }

    set({ loading: true, error: null, query });

    try {
      const data = await searchEntities(query, limit);
      set({ results: data.results, loading: false });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Erro ao realizar busca";
      set({ error: message, loading: false, results: [] });
    }
  },

  setSelectedEntity: (entity: SearchResult | null) =>
    set({ selectedEntity: entity }),

  clearResults: () => set({ results: [], query: "", error: null }),
}));
