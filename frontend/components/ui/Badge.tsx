interface BadgeProps {
  children: React.ReactNode;
  variant?: "orange" | "success" | "danger" | "warn" | "dim";
  className?: string;
}

export default function Badge({
  children,
  variant = "orange",
  className = "",
}: BadgeProps) {
  const styles: Record<string, string> = {
    orange: "bg-orange-dim text-orange border border-orange/30",
    success: "bg-success/20 text-success border border-success/30",
    danger: "bg-danger/20 text-danger border border-danger/30",
    warn: "bg-warn/20 text-warn border border-warn/30",
    dim: "bg-surfaceHigh text-secondary border border-border",
  };
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-3 py-0.5 text-xs font-medium ${styles[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
