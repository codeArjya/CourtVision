"use client";

import PlayerAnimation from "./PlayerAnimation";
import Sparkline from "./Sparkline";
import { getTeamColor } from "@/styles/tokens";

interface PlayerStat {
  player_id: string;
  name: string;
  pos: string;
  pts: number;
  reb: number;
  ast: number;
  plus_minus?: number;
  fgm?: number;
  fga?: number;
  last5_pts: number[];
}

interface PlayerHighlightCardProps {
  player: PlayerStat;
  teamAbbr: string;
  onClick: () => void;
}

export default function PlayerHighlightCard({
  player,
  teamAbbr,
  onClick,
}: PlayerHighlightCardProps) {
  const teamColor = getTeamColor(teamAbbr).primary;
  const seasonAvg = player.pts;
  const fgPct =
    player.fgm != null && player.fga && player.fga > 0
      ? `${((player.fgm / player.fga) * 100).toFixed(0)}%`
      : null;

  return (
    <button
      onClick={onClick}
      className="bg-surface border border-border rounded-xl p-4 text-left w-full cursor-pointer hover:border-orange/40 transition-all duration-200 group focus-visible:outline-orange"
    >
      {/* Animation banner */}
      <div
        className="rounded-lg overflow-hidden mb-3"
        style={{ height: "80px", background: `${teamColor}12` }}
      >
        <PlayerAnimation teamColor={teamColor} className="h-full w-full" />
      </div>

      {/* Player name + team */}
      <div className="mb-2.5">
        <p className="font-bold text-sm text-primary truncate group-hover:text-orange transition-colors">
          {player.name}
        </p>
        <p className="text-xs text-secondary">
          <span>{player.pos}</span>
          <span className="mx-1.5 text-dim">·</span>
          <span className="font-semibold" style={{ color: teamColor }}>
            {teamAbbr}
          </span>
          {fgPct && (
            <span className="ml-1.5 text-dim">· {fgPct} FG</span>
          )}
        </p>
      </div>

      {/* Stat row */}
      <div className="flex gap-3 mb-3">
        <StatPill label="PTS" value={player.pts} accent={teamColor} />
        <StatPill label="REB" value={player.reb} />
        <StatPill label="AST" value={player.ast} />
        {player.plus_minus != null && (
          <StatPill
            label="+/-"
            value={player.plus_minus}
            signed
          />
        )}
      </div>

      {/* Sparkline + last 5 dots */}
      {player.last5_pts && player.last5_pts.length > 0 && (
        <div>
          <p className="text-[9px] text-dim uppercase tracking-wider mb-1.5">
            Last 5 Games
          </p>
          <div className="flex items-center gap-2">
            <Sparkline data={player.last5_pts} width={60} height={26} />
            <div className="flex gap-1.5">
              {player.last5_pts.map((pts, i) => (
                <span
                  key={i}
                  className={`text-[9px] font-mono font-bold ${
                    pts >= seasonAvg ? "text-success" : "text-danger"
                  }`}
                >
                  {pts}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* AI card CTA */}
      <p className="mt-2.5 text-orange text-[10px] font-medium opacity-0 group-hover:opacity-100 transition-opacity">
        View AI Card →
      </p>
    </button>
  );
}

function StatPill({
  label,
  value,
  accent,
  signed = false,
}: {
  label: string;
  value: number;
  accent?: string;
  signed?: boolean;
}) {
  const display = signed && value > 0 ? `+${value}` : String(value);
  const signedColor =
    signed
      ? value > 0
        ? "#27AE60"
        : value < 0
          ? "#E74C3C"
          : "#555555"
      : undefined;

  return (
    <div className="text-center">
      <div
        className="font-mono font-bold text-sm"
        style={{ color: signedColor ?? accent ?? "#F0F0F0" }}
      >
        {display}
      </div>
      <div className="text-[9px] text-dim uppercase tracking-wide">{label}</div>
    </div>
  );
}
