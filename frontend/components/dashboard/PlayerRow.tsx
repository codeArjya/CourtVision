"use client";

import { useState } from "react";
import Sparkline from "./Sparkline";
import PlayerModal from "../players/PlayerModal";

interface PlayerStat {
  player_id: string;
  name: string;
  pos: string;
  minutes: string;
  pts: number;
  reb: number;
  ast: number;
  stl: number;
  blk: number;
  turnovers: number;
  fgm: number;
  fga: number;
  plus_minus: number;
  last5_pts: number[];
  league_rank_pts: number | null;
  league_rank_reb: number | null;
  league_rank_ast: number | null;
  matchup_avg_pts: number | null;
}

interface PlayerRowProps {
  player: PlayerStat;
  activeOverlay: string;
  game: any;
}

export default function PlayerRow({
  player,
  activeOverlay,
  game,
}: PlayerRowProps) {
  const [showModal, setShowModal] = useState(false);

  const plusStyle =
    player.plus_minus > 0
      ? "text-success"
      : player.plus_minus < 0
        ? "text-danger"
        : "text-dim";

  const bestRank = player.league_rank_pts
    ? { rank: player.league_rank_pts, stat: "PTS" }
    : player.league_rank_reb
      ? { rank: player.league_rank_reb, stat: "REB" }
      : player.league_rank_ast
        ? { rank: player.league_rank_ast, stat: "AST" }
        : null;

  return (
    <>
      <tr
        onClick={() => setShowModal(true)}
        className="cursor-pointer hover:bg-surfaceHigh transition-colors border-t border-border/50"
      >
        <td className="py-2.5 px-3 text-primary font-medium text-sm whitespace-nowrap">
          {player.name}
        </td>
        <td className="py-2.5 px-2 text-secondary text-xs">{player.pos}</td>
        <td className="py-2.5 px-2 text-secondary text-xs font-mono">
          {player.minutes}
        </td>
        <td className="py-2.5 px-2 text-white font-bold text-sm">
          {player.pts}
        </td>
        <td className="py-2.5 px-2 text-secondary text-sm">{player.reb}</td>
        <td className="py-2.5 px-2 text-secondary text-sm">{player.ast}</td>
        <td className="py-2.5 px-2 text-secondary text-sm">{player.stl}</td>
        <td className="py-2.5 px-2 text-secondary text-sm">{player.blk}</td>
        <td className={`py-2.5 px-2 text-sm font-mono ${plusStyle}`}>
          {player.plus_minus > 0 ? `+${player.plus_minus}` : player.plus_minus}
        </td>
        <td className="py-2.5 px-2 text-secondary text-xs font-mono">
          {player.fgm}/{player.fga}
        </td>

        {/* Overlay column */}
        {activeOverlay === "rank" && (
          <td className="py-2.5 px-2">
            {bestRank ? (
              <span className="bg-orange-dim text-orange text-xs font-semibold px-2 py-0.5 rounded">
                #{bestRank.rank} {bestRank.stat}
              </span>
            ) : (
              <span className="text-dim text-xs">—</span>
            )}
          </td>
        )}
        {activeOverlay === "sparkline" && (
          <td className="py-2.5 px-2">
            <Sparkline data={player.last5_pts} width={64} height={28} />
          </td>
        )}
        {activeOverlay === "matchup" && (
          <td className="py-2.5 px-2 text-xs text-secondary whitespace-nowrap">
            {player.matchup_avg_pts != null
              ? `${player.matchup_avg_pts} avg vs opp`
              : "—"}
          </td>
        )}
      </tr>

      {showModal && (
        <tr>
          <td colSpan={activeOverlay !== "none" ? 11 : 10}>
            <PlayerModal
              player={player}
              game={game}
              onClose={() => setShowModal(false)}
            />
          </td>
        </tr>
      )}
    </>
  );
}
