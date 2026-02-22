"use client";

interface OverlaySelectorProps {
  active: string;
  onChange: (v: string) => void;
}

const options = [
  { id: "none", label: "No Overlay" },
  { id: "rank", label: "📊 League Rank" },
  { id: "sparkline", label: "📈 Form" },
  { id: "matchup", label: "🆚 Matchup" },
];

export default function OverlaySelector({
  active,
  onChange,
}: OverlaySelectorProps) {
  return (
    <div className="flex gap-2 py-2 flex-wrap">
      {options.map(({ id, label }) => (
        <button
          key={id}
          onClick={() => onChange(id)}
          className={
            active === id
              ? "bg-orange text-white rounded-full px-3 py-1 text-sm font-semibold transition-all"
              : "bg-surface text-secondary border border-border hover:border-orange rounded-full px-3 py-1 text-sm transition-all"
          }
        >
          {label}
        </button>
      ))}
    </div>
  );
}
