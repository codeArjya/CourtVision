"use client";

import { useState } from "react";
import BoxScoreTable from "./BoxScoreTable";
import TeamLogo from "@/components/ui/TeamLogo";
import { MOCK_PLAYER_STATS } from "@/lib/mockData";
import { getTeamColor } from "@/styles/tokens";

interface GameExpandedProps {
  game: any;
  activeOverlay: string;
  onClose: () => void;
}

export default function GameExpanded({ game, activeOverlay, onClose }: GameExpandedProps) {
  const [activeTeam, setActiveTeam] = useState<"home" | "away">("home");

  const allPlayers = MOCK_PLAYER_STATS.filter((p) => p.game_id === game.game_id);
  const homePlayers = allPlayers.filter((p) => p.team_id === game.home_team_id);
  const awayPlayers = allPlayers.filter((p) => p.team_id === game.away_team_id);
  const displayed = activeTeam === "home" ? homePlayers : awayPlayers;

  const homeColor = getTeamColor(game.home_team_abbr).primary;
  const awayColor = getTeamColor(game.away_team_abbr).primary;

  return (
    <div
      className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-start justify-center pt-16 px-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
      role="dialog"
      aria-modal="true"
      aria-label={`${game.away_team_abbr} vs ${game.home_team_abbr} box score`}
    >
      <div
        className="bg-surface rounded-2xl max-w-4xl w-full mx-4 p-6 max-h-[80vh] overflow-y-auto border border-border"
        style={{ animation: "fadeSlideUp 0.22s ease-out" }}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <TeamLogo abbr={game.away_team_abbr} size={36} />
              <span className="text-lg font-bold text-primary">
                {game.away_team_name}
              </span>
            </div>
            <div className="text-center">
              {game.home_score !== null ? (
                <div className="font-mono text-xl font-bold text-orange">
                  {game.away_score} – {game.home_score}
                </div>
              ) : (
                <span className="text-secondary text-sm">vs</span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-primary">
                {game.home_team_name}
              </span>
              <TeamLogo abbr={game.home_team_abbr} size={36} />
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close box score"
            className="w-8 h-8 rounded-full bg-surfaceHigh hover:bg-border flex items-center justify-center text-secondary hover:text-primary transition-colors text-lg flex-shrink-0"
          >
            ✕
          </button>
        </div>

        {/* Team tabs with team colors */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setActiveTeam("home")}
            className="px-4 py-1.5 rounded-lg text-sm font-semibold transition-all"
            style={
              activeTeam === "home"
                ? { backgroundColor: homeColor, color: "#fff" }
                : { backgroundColor: "#242424", color: "#9A9A9A" }
            }
          >
            {game.home_team_abbr}
          </button>
          <button
            onClick={() => setActiveTeam("away")}
            className="px-4 py-1.5 rounded-lg text-sm font-semibold transition-all"
            style={
              activeTeam === "away"
                ? { backgroundColor: awayColor, color: "#fff" }
                : { backgroundColor: "#242424", color: "#9A9A9A" }
            }
          >
            {game.away_team_abbr}
          </button>
        </div>

        {/* Box score */}
        {displayed.length > 0 ? (
          <BoxScoreTable
            players={displayed}
            activeOverlay={activeOverlay as any}
            game={game}
          />
        ) : (
          <p className="text-secondary text-sm text-center py-8">
            Box score data not yet available for this game.
          </p>
        )}
      </div>
    </div>
  );
}
