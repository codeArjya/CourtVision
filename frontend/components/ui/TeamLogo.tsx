"use client";

import { useState } from "react";
import { getTeamLogoUrl, getTeamColor } from "@/styles/tokens";

interface TeamLogoProps {
  abbr: string;
  size?: number;
  className?: string;
}

export default function TeamLogo({
  abbr,
  size = 40,
  className = "",
}: TeamLogoProps) {
  const [imgError, setImgError] = useState(false);
  const color = getTeamColor(abbr).primary;

  if (imgError) {
    return (
      <div
        className={`rounded-full flex items-center justify-center font-black text-white flex-shrink-0 ${className}`}
        style={{
          width: size,
          height: size,
          backgroundColor: color,
          fontSize: Math.round(size * 0.3),
        }}
      >
        {abbr.slice(0, 3)}
      </div>
    );
  }

  return (
    <img
      src={getTeamLogoUrl(abbr)}
      alt={abbr}
      width={size}
      height={size}
      className={`object-contain flex-shrink-0 ${className}`}
      onError={() => setImgError(true)}
    />
  );
}
