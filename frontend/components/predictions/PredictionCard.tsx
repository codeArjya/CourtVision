"use client";

import TeamLogo from "@/components/ui/TeamLogo";
import { getTeamColor } from "@/styles/tokens";
import Badge from "@/components/ui/Badge";

interface PredictionCardProps {
  game: any;
  prediction: any;
}

export default function PredictionCard({ game, prediction }: PredictionCardProps) {
  const confidence: number = prediction?.confidence ?? 65;
  const winnerAbbr: string = prediction?.winner_abbr ?? "";

  const isAwayWinner = winnerAbbr === game.away_team_abbr;
  const awayConf = isAwayWinner ? confidence : 100 - confidence;
  const homeConf = isAwayWinner ? 100 - confidence : confidence;

  const awayColor = getTeamColor(game.away_team_abbr).primary;
  const homeColor = getTeamColor(game.home_team_abbr).primary;
  const winnerColor = isAwayWinner ? awayColor : homeColor;

  const statusLabel =
    game.status === "live"
      ? `LIVE Q${game.quarter} ${game.clock}`
      : game.tipoff_time
        ? game.tipoff_time
        : game.status === "final"
          ? "FINAL"
          : "";

  const resultBadge =
    game.status === "final" && prediction?.result
      ? prediction.result === "correct"
        ? { label: "✓ Correct Call", variant: "success" as const }
        : prediction.result === "incorrect"
          ? { label: "✗ Missed", variant: "danger" as const }
          : { label: "⏳ Pending", variant: "warn" as const }
      : null;

  return (
    <div className="bg-surface border border-border rounded-xl p-5 hover:border-orange/30 transition-all duration-200 flex flex-col gap-4">
      {/* Status */}
      {statusLabel && (
        <div className="text-xs text-center">
          {game.status === "live" ? (
            <span className="inline-flex items-center gap-1.5 text-success font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
              {statusLabel}
            </span>
          ) : (
            <span className="text-dim">{statusLabel}</span>
          )}
        </div>
      )}

      {/* VS bracket — team logos side by side */}
      <div className="flex items-stretch gap-2">
        {/* Away team */}
        <div
          className={`flex-1 flex flex-col items-center gap-1.5 p-3 rounded-xl border transition-all ${
            isAwayWinner
              ? "border-orange/40 bg-orange/5"
              : "border-border"
          }`}
        >
          <TeamLogo abbr={game.away_team_abbr} size={44} />
          <span
            className="text-xs font-black"
            style={{ color: awayColor }}
          >
            {game.away_team_abbr}
          </span>
          <span className="text-[10px] text-secondary text-center leading-tight">
            {game.away_team_name}
          </span>
          {isAwayWinner && (
            <span className="text-[9px] text-orange font-semibold mt-0.5">
              ✓ Predicted
            </span>
          )}
        </div>

        <div className="flex items-center text-dim text-sm font-semibold">vs</div>

        {/* Home team */}
        <div
          className={`flex-1 flex flex-col items-center gap-1.5 p-3 rounded-xl border transition-all ${
            !isAwayWinner && winnerAbbr
              ? "border-orange/40 bg-orange/5"
              : "border-border"
          }`}
        >
          <TeamLogo abbr={game.home_team_abbr} size={44} />
          <span
            className="text-xs font-black"
            style={{ color: homeColor }}
          >
            {game.home_team_abbr}
          </span>
          <span className="text-[10px] text-secondary text-center leading-tight">
            {game.home_team_name}
          </span>
          {!isAwayWinner && winnerAbbr && (
            <span className="text-[9px] text-orange font-semibold mt-0.5">
              ✓ Predicted
            </span>
          )}
        </div>
      </div>

      {/* Horizontal confidence bar */}
      <div>
        <div className="flex justify-between text-[11px] mb-1.5">
          <span className="text-secondary">
            {game.away_team_abbr} {awayConf}%
          </span>
          <span className="font-bold" style={{ color: winnerColor }}>
            {homeConf}% {game.home_team_abbr}
          </span>
        </div>
        <div className="relative h-2.5 bg-border rounded-full overflow-hidden">
          {/* Away side — left */}
          <div
            className="absolute left-0 top-0 h-full rounded-l-full opacity-50 transition-all duration-700"
            style={{ width: `${awayConf}%`, backgroundColor: awayColor }}
          />
          {/* Home side — right */}
          <div
            className="absolute right-0 top-0 h-full rounded-r-full transition-all duration-700"
            style={{ width: `${homeConf}%`, backgroundColor: homeColor }}
          />
        </div>
      </div>

      {/* Predicted score */}
      {prediction?.score_home !== undefined && (
        <div className="text-center">
          <span className="font-mono text-2xl font-black text-primary">
            {prediction.score_away}
            <span className="text-dim text-lg mx-1">–</span>
            {prediction.score_home}
          </span>
          <p className="text-[10px] text-dim mt-0.5">Predicted score</p>
        </div>
      )}

      {/* Key factors */}
      {prediction?.key_factors && (
        <ul className="space-y-1.5">
          {prediction.key_factors.map((factor: string, i: number) => (
            <li
              key={i}
              className="flex items-start gap-2 text-xs text-secondary"
            >
              <span
                className="w-1.5 h-1.5 rounded-full mt-1 flex-shrink-0"
                style={{ backgroundColor: winnerColor }}
              />
              {factor}
            </li>
          ))}
        </ul>
      )}

      {/* Result badge */}
      {resultBadge && (
        <div>
          <Badge variant={resultBadge.variant}>{resultBadge.label}</Badge>
        </div>
      )}
    </div>
  );
}
