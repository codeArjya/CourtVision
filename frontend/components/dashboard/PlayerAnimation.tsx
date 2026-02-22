"use client";

interface PlayerAnimationProps {
  teamColor?: string;
  className?: string;
}

/**
 * CSS-animated basketball player silhouette dribbling.
 * Uses @keyframes defined in globals.css (anim-player, anim-ball, anim-shadow).
 */
export default function PlayerAnimation({
  teamColor = "#E87722",
  className = "",
}: PlayerAnimationProps) {
  // Slightly darken the team color for lines/details
  const lineColor = "rgba(0,0,0,0.35)";

  return (
    <div
      className={`relative flex items-end justify-center overflow-hidden ${className}`}
      aria-hidden="true"
    >
      {/* Background radial glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `radial-gradient(ellipse 80% 60% at 60% 90%, ${teamColor}22, transparent)`,
        }}
      />

      <svg
        viewBox="0 0 100 108"
        className="w-full h-full relative z-10"
        style={{ maxHeight: "100%", maxWidth: "100%" }}
      >
        {/* Ground shadow */}
        <ellipse
          cx="30"
          cy="106"
          rx="10"
          ry="2.5"
          fill={teamColor}
          className="anim-shadow"
        />

        {/* Player body group – bobs up/down */}
        <g className="anim-player">
          {/* Head */}
          <circle cx="65" cy="14" r="10" fill={teamColor} opacity="0.92" />

          {/* Torso */}
          <rect
            x="55"
            y="26"
            width="20"
            height="26"
            rx="5"
            fill={teamColor}
            opacity="0.92"
          />

          {/* Neck */}
          <rect x="62" y="23" width="6" height="5" fill={teamColor} opacity="0.92" />

          {/* Left arm – dribbling arm */}
          <path
            d="M57,33 Q44,43 38,52"
            stroke={teamColor}
            strokeWidth="7"
            strokeLinecap="round"
            fill="none"
            opacity="0.92"
          />

          {/* Right arm – raised for balance */}
          <path
            d="M73,33 Q81,27 86,22"
            stroke={teamColor}
            strokeWidth="7"
            strokeLinecap="round"
            fill="none"
            opacity="0.92"
          />

          {/* Left leg – slightly bent */}
          <path
            d="M60,52 Q54,68 50,82"
            stroke={teamColor}
            strokeWidth="8"
            strokeLinecap="round"
            fill="none"
            opacity="0.92"
          />

          {/* Right leg */}
          <path
            d="M70,52 Q76,68 82,80"
            stroke={teamColor}
            strokeWidth="8"
            strokeLinecap="round"
            fill="none"
            opacity="0.92"
          />

          {/* Left shoe */}
          <ellipse cx="48" cy="84" rx="9" ry="4" fill={teamColor} opacity="0.75" />

          {/* Right shoe */}
          <ellipse cx="83" cy="81" rx="9" ry="4" fill={teamColor} opacity="0.75" />
        </g>

        {/* Basketball – bounces independently */}
        <g className="anim-ball">
          {/* Ball */}
          <circle cx="30" cy="88" r="9" fill="#E87722" opacity="0.96" />
          {/* Ball seam – horizontal */}
          <path
            d="M21,88 Q30,82 39,88"
            stroke={lineColor}
            strokeWidth="1.3"
            fill="none"
          />
          <path
            d="M21,88 Q30,94 39,88"
            stroke={lineColor}
            strokeWidth="1.3"
            fill="none"
          />
          {/* Ball seam – vertical */}
          <line x1="30" y1="79" x2="30" y2="97" stroke={lineColor} strokeWidth="1.3" />
        </g>
      </svg>
    </div>
  );
}
