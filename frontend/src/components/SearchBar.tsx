import { useEffect, useRef, useState } from "react";
import { Search } from "lucide-react";

interface SearchBarProps {
  initialValue?: string;
  placeholder?: string;
  onSearch: (query: string) => void;
  debounceMs?: number;
  autoFocus?: boolean;
  large?: boolean;
}

export default function SearchBar({
  initialValue = "",
  placeholder = "Buscar entidades, empresas, contratos...",
  onSearch,
  debounceMs = 300,
  autoFocus = false,
  large = false,
}: SearchBarProps) {
  const [value, setValue] = useState(initialValue);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  const handleChange = (newValue: string) => {
    setValue(newValue);

    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      onSearch(newValue);
    }, debounceMs);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (timerRef.current) clearTimeout(timerRef.current);
    onSearch(value);
  };

  return (
    <form onSubmit={handleSubmit} style={{ width: "100%" }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          background: "var(--bg-card)",
          border: "1px solid var(--border)",
          borderRadius: large ? "var(--radius-xl)" : "var(--radius-lg)",
          padding: large ? "16px 24px" : "10px 16px",
          transition: "all var(--transition-fast)",
          boxShadow: "var(--shadow-sm)",
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = "var(--accent)";
          e.currentTarget.style.boxShadow = "var(--shadow-glow)";
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = "var(--border)";
          e.currentTarget.style.boxShadow = "var(--shadow-sm)";
        }}
      >
        <Search
          size={large ? 22 : 18}
          color="var(--text-secondary)"
          style={{ flexShrink: 0 }}
        />
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => handleChange(e.target.value)}
          placeholder={placeholder}
          style={{
            flex: 1,
            fontSize: large ? "1.1rem" : "0.95rem",
            color: "var(--text-primary)",
            background: "transparent",
            border: "none",
            outline: "none",
          }}
        />
        {value && (
          <button
            type="button"
            onClick={() => {
              setValue("");
              onSearch("");
              inputRef.current?.focus();
            }}
            style={{
              color: "var(--text-secondary)",
              fontSize: "0.8rem",
              padding: "4px 8px",
              borderRadius: "var(--radius-sm)",
              background: "rgba(255,255,255,0.05)",
            }}
          >
            Limpar
          </button>
        )}
        <button
          type="submit"
          style={{
            padding: large ? "10px 24px" : "6px 16px",
            borderRadius: large ? "var(--radius-lg)" : "var(--radius-md)",
            background: "var(--accent)",
            color: "#fff",
            fontWeight: 600,
            fontSize: large ? "0.95rem" : "0.85rem",
            transition: "all var(--transition-fast)",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "#3a68e8";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "var(--accent)";
          }}
        >
          Buscar
        </button>
      </div>
    </form>
  );
}
