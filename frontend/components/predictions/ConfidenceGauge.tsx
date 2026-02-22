"use client";

interface ConfidenceGaugeProps {
  value: number;
}

export default function ConfidenceGauge({ value }: ConfidenceGaugeProps) {
  const dashLength = (value / 100) * 157;

  return (
    <svg width="120" height="70" viewBox="0 0 120 70">
      {/* Background arc */}
      <path
        d="M10,60 A50,50 0 0,1 110,60"
        stroke="#2E2E2E"
        strokeWidth="8"
        fill="none"
        strokeLinecap="round"
      />
      {/* Foreground arc */}
      <path
        d="M10,60 A50,50 0 0,1 110,60"
        stroke="#E87722"
        strokeWidth="8"
        fill="none"
        strokeLinecap="round"
        strokeDasharray={`${dashLength} 157`}
        style={{ transition: "stroke-dasharray 0.6s ease" }}
      />
      {/* Confidence value */}
      <text
        x="60"
        y="55"
        textAnchor="middle"
        fill="#F0F0F0"
        fontSize="18"
        fontWeight="bold"
        fontFamily="JetBrains Mono, monospace"
      >
        {value}%
      </text>
      {/* Label */}
      <text
        x="60"
        y="70"
        textAnchor="middle"
        fill="#9A9A9A"
        fontSize="11"
        fontFamily="Inter, sans-serif"
      >
        Confidence
      </text>
    </svg>
  );
}
