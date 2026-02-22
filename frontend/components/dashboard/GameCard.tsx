"use client";

interface Game {
  game_id: string;
  home_team_name: string;
  home_team_abbr: string;
  home_score: number | null;
  away_team_name: string;
  away_team_abbr: string;
  away_score: number | null;
  status: string;
  quarter: number | null;
  clock: string | null;
  tipoff_time: string | null;
}

interface GameCardProps {
  game: Game;
  onClick: () => void;
  isSelected: boolean;
}

function StatusBadge({ game }: { game: Game }) {
  if (game.status === "live") {
    return (
      <div className="flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-success animate-pulse-live" />
        <span className="text-success text-xs font-bold tracking-wider">
          LIVE
        </span>
      </div>
    );
  }
  if (game.status === "final") {
    return (
      <span className="text-dim text-xs font-semibold tracking-wider">
        FINAL
      </span>
    );
  }
  return (
    <span className="text-warn text-xs font-semibold">
      {game.tipoff_time || "Upcoming"}
    </span>
  );
}

export default function GameCard({ game, onClick, isSelected }: GameCardProps) {
  const homeWins = (game.home_score ?? 0) > (game.away_score ?? 0);
  const awayWins = (game.away_score ?? 0) > (game.home_score ?? 0);
  const hasScore = game.home_score !== null && game.away_score !== null;

  return (
    <div
      onClick={onClick}
      className={`
        bg-surface border rounded-xl p-4 cursor-pointer hover:border-orange/50 transition-all duration-200 group
        ${isSelected ? "border-orange-glow border-orange" : "border-border"}
      `}
    >
      {/* Status */}
      <div className="mb-3">
        <StatusBadge game={game} />
      </div>

      {/* Teams + Scores */}
      <div className="space-y-2">
        {/* Away team */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-surfaceHigh flex items-center justify-center text-xs font-bold text-secondary">
            {game.away_team_abbr.slice(0, 2)}
          </div>
          <span className="font-bold text-lg flex-1">
            {game.away_team_abbr}
          </span>
          {hasScore && (
            <span
              className={`font-mono text-3xl font-bold ${awayWins ? "text-orange" : "text-primary"}`}
            >
              {game.away_score}
            </span>
          )}
        </div>
        {/* Home team */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-surfaceHigh flex items-center justify-center text-xs font-bold text-secondary">
            {game.home_team_abbr.slice(0, 2)}
          </div>
          <span className="font-bold text-lg flex-1">
            {game.home_team_abbr}
          </span>
          {hasScore && (
            <span
              className={`font-mono text-3xl font-bold ${homeWins ? "text-orange" : "text-primary"}`}
            >
              {game.home_score}
            </span>
          )}
        </div>
      </div>

      {/* Quarter/Clock for live games */}
      {game.status === "live" && game.quarter && (
        <div className="mt-2 text-orange text-sm">
          Q{game.quarter} {game.clock}
        </div>
      )}

      {/* Hover footer */}
      <div className="mt-3 text-orange text-sm opacity-0 group-hover:opacity-100 transition-opacity">
        View Box Score →
      </div>
    </div>
  );
}
