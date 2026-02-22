"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { MOCK_GAMES } from "@/lib/mockData";
import { getTeamColor, getTeamLogoUrl } from "@/styles/tokens";

export default function ScoreTicker() {
  const { data: games } = useQuery({
    queryKey: ["games"],
    queryFn: async () => {
      try {
        const res = await api.get("/api/games");
        return res.data;
      } catch {
        return MOCK_GAMES;
      }
    },
    refetchInterval: 30000,
    staleTime: 20000,
  });

  const displayGames = games || MOCK_GAMES;
  const liveCount = displayGames.filter((g: any) => g.status === "live").length;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 h-7 bg-surfaceHigh border-b border-border flex items-center">
      {/* Brand pill */}
      <div className="flex-shrink-0 flex items-center gap-1.5 px-3 h-full border-r border-border bg-orange/10">
        {liveCount > 0 && (
          <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
        )}
        <span className="text-orange text-[10px] font-black tracking-widest uppercase">
          ⚡ NBA
        </span>
      </div>

      {/* Game items */}
      <div className="flex items-center h-full divide-x divide-border overflow-x-auto no-scrollbar">
        {displayGames.map((game: any) => (
          <TickerGame key={game.game_id} game={game} />
        ))}
      </div>
    </div>
  );
}

function TickerGame({ game }: { game: any }) {
  const hasScore = game.home_score !== null && game.away_score !== null;
  const awayWins = (game.away_score ?? 0) > (game.home_score ?? 0);
  const homeWins = (game.home_score ?? 0) > (game.away_score ?? 0);
  const awayColor = getTeamColor(game.away_team_abbr).primary;
  const homeColor = getTeamColor(game.home_team_abbr).primary;

  return (
    <div className="flex items-center gap-2 px-4 h-full text-[11px] whitespace-nowrap">
      {/* Live indicator */}
      {game.status === "live" && (
        <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live flex-shrink-0" />
      )}

      {/* Away */}
      <img
        src={getTeamLogoUrl(game.away_team_abbr)}
        alt={game.away_team_abbr}
        width={16}
        height={16}
        className="object-contain"
        onError={(e) => {
          (e.target as HTMLImageElement).style.display = "none";
        }}
      />
      <span
        className="font-bold"
        style={{ color: awayWins ? awayColor : "#9A9A9A" }}
      >
        {game.away_team_abbr}
      </span>
      {hasScore && (
        <span
          className={`font-mono font-bold ${awayWins ? "text-primary" : "text-secondary"}`}
        >
          {game.away_score}
        </span>
      )}

      <span className="text-dim">–</span>

      {hasScore && (
        <span
          className={`font-mono font-bold ${homeWins ? "text-primary" : "text-secondary"}`}
        >
          {game.home_score}
        </span>
      )}
      <span
        className="font-bold"
        style={{ color: homeWins ? homeColor : "#9A9A9A" }}
      >
        {game.home_team_abbr}
      </span>
      <img
        src={getTeamLogoUrl(game.home_team_abbr)}
        alt={game.home_team_abbr}
        width={16}
        height={16}
        className="object-contain"
        onError={(e) => {
          (e.target as HTMLImageElement).style.display = "none";
        }}
      />

      {/* Status chip */}
      <span
        className={`text-[9px] font-semibold ml-1 ${
          game.status === "live"
            ? "text-success"
            : game.status === "final"
              ? "text-dim"
              : "text-warn"
        }`}
      >
        {game.status === "live"
          ? `Q${game.quarter} ${game.clock}`
          : game.status === "final"
            ? "F"
            : game.tipoff_time ?? "TBD"}
      </span>
    </div>
  );
}
