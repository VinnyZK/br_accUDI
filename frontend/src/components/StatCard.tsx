import { useEffect, useState, type ReactNode } from "react";

interface StatCardProps {
  label: string;
  value: number;
  icon: ReactNode;
  delay?: number;
  suffix?: string;
}

export default function StatCard({
  label,
  value,
  icon,
  delay = 0,
  suffix = "",
}: StatCardProps) {
  const [displayed, setDisplayed] = useState(0);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timeout = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(timeout);
  }, [delay]);

  useEffect(() => {
    if (!visible) return;

    const duration = 1200;
    const steps = 40;
    const stepTime = duration / steps;
    let current = 0;

    const interval = setInterval(() => {
      current++;
      const progress = current / steps;
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayed(Math.round(eased * value));

      if (current >= steps) {
        setDisplayed(value);
        clearInterval(interval);
      }
    }, stepTime);

    return () => clearInterval(interval);
  }, [value, visible]);

  return (
    <div
      style={{
        background: "var(--bg-card)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-lg)",
        padding: "1.5rem",
        display: "flex",
        alignItems: "center",
        gap: "1rem",
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(12px)",
        transition: "all 0.5s ease",
      }}
    >
      <div
        style={{
          width: 48,
          height: 48,
          borderRadius: "var(--radius-md)",
          background: "var(--accent-glow)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}
      >
        {icon}
      </div>
      <div>
        <div
          style={{
            fontSize: "1.75rem",
            fontWeight: 700,
            lineHeight: 1.2,
            color: "var(--text-primary)",
          }}
        >
          {displayed.toLocaleString("pt-BR")}
          {suffix}
        </div>
        <div
          style={{
            fontSize: "0.825rem",
            color: "var(--text-secondary)",
            marginTop: 2,
          }}
        >
          {label}
        </div>
      </div>
    </div>
  );
}
