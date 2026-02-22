"use client";

import PlayerRow from "./PlayerRow";

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

interface BoxScoreTableProps {
  players: PlayerStat[];
  activeOverlay: "none" | "rank" | "sparkline" | "matchup";
  game: any;
}

export default function BoxScoreTable({
  players,
  activeOverlay,
  game,
}: BoxScoreTableProps) {
  const sorted = [...players].sort((a, b) => b.pts - a.pts);

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-max text-sm">
        <thead>
          <tr className="bg-surfaceHigh">
            <th className="py-2 px-3 text-left text-dim text-xs uppercase tracking-wider">
              Player
            </th>
            <th className="py-2 px-2 text-left text-dim text-xs uppercase tracking-wider">
              POS
            </th>
            <th className="py-2 px-2 text-left text-dim text-xs uppercase tracking-wider">
              MIN
            </th>
            <th className="py-2 px-2 text-left text-dim text-xs uppercase tracking-wider">
              PTS
            </th>
            <th className="py-2 px-2 text-left text-dim text-xs uppercase tracking-wider">
              REB
            </th>
            <th className="py-2 px-2 text-left text-dim text-xs uppercase tracking-wider">
              AST
            </th>
            <th className="py-2 px-2 text-left text-dim text-xs uppercase tracking-wider">
              STL
            </th>
            <th className="py-2 px-2 text-left text-dim text-xs uppercase tracking-wider">
              BLK
            </th>
            <th className="py-2 px-2 text-left text-dim text-xs uppercase tracking-wider">
              +/-
            </th>
            <th className="py-2 px-2 text-left text-dim text-xs uppercase tracking-wider">
              FG
            </th>
            {activeOverlay !== "none" && (
              <th className="py-2 px-2 text-left text-dim text-xs uppercase tracking-wider">
                {activeOverlay === "rank"
                  ? "Rank"
                  : activeOverlay === "sparkline"
                    ? "Form"
                    : "Matchup"}
              </th>
            )}
          </tr>
        </thead>
        <tbody>
          {sorted.map((player) => (
            <PlayerRow
              key={player.player_id}
              player={player}
              activeOverlay={activeOverlay}
              game={game}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}
