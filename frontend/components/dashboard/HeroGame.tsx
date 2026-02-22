"use client";

import TeamLogo from "@/components/ui/TeamLogo";
import { getTeamColor } from "@/styles/tokens";

interface HeroGameProps {
  game: any;
  homePlayers: any[];
  awayPlayers: any[];
}

function computeTeamStats(players: any[]) {
  if (!players.length) return { fgPct: "--", ast: 0, pts: 0, reb: 0 };
  const totalFgm = players.reduce((s: number, p: any) => s + (p.fgm ?? 0), 0);
  const totalFga = players.reduce((s: number, p: any) => s + (p.fga ?? 0), 0);
  const ast = players.reduce((s: number, p: any) => s + (p.ast ?? 0), 0);
  const pts = players.reduce((s: number, p: any) => s + (p.pts ?? 0), 0);
  const reb = players.reduce((s: number, p: any) => s + (p.reb ?? 0), 0);
  return {
    fgPct: totalFga > 0 ? `${((totalFgm / totalFga) * 100).toFixed(1)}%` : "--",
    ast,
    pts,
    reb,
  };
}

export default function HeroGame({
  game,
  homePlayers,
  awayPlayers,
}: HeroGameProps) {
  const homeColor = getTeamColor(game.home_team_abbr).primary;
  const awayColor = getTeamColor(game.away_team_abbr).primary;
  const hasScore = game.home_score !== null && game.away_score !== null;
  const homeWins = (game.home_score ?? 0) > (game.away_score ?? 0);
  const awayWins = (game.away_score ?? 0) > (game.home_score ?? 0);

  const homeStats = computeTeamStats(homePlayers);
  const awayStats = computeTeamStats(awayPlayers);
  const hasPlayerStats = homePlayers.length > 0 || awayPlayers.length > 0;

  return (
    <div className="bg-surface border border-border rounded-2xl p-5 mb-4 animate-slide-up">
      {/* Status banner */}
      <div className="flex justify-center mb-4">
        {game.status === "live" && (
          <span className="inline-flex items-center gap-2 bg-success/10 border border-success/30 text-success text-xs font-bold px-4 py-1.5 rounded-full tracking-wider">
            <span className="w-2 h-2 rounded-full bg-success animate-pulse-live" />
            LIVE &nbsp;·&nbsp; Q{game.quarter} &nbsp;·&nbsp; {game.clock}
          </span>
        )}
        {game.status === "final" && (
          <span className="text-dim text-xs font-semibold tracking-widest uppercase">
            Final
          </span>
        )}
        {game.status === "upcoming" && (
          <span className="text-warn text-xs font-semibold">
            Tip-off: {game.tipoff_time ?? "TBD"}
          </span>
        )}
      </div>

      {/* Teams + Score row */}
      <div className="flex items-center">
        {/* Away team */}
        <div className="flex-1 flex flex-col items-center gap-2">
          <TeamLogo abbr={game.away_team_abbr} size={64} />
          <div className="text-center">
            <p
              className="text-base font-black tracking-wide"
              style={{ color: awayColor }}
            >
              {game.away_team_abbr}
            </p>
            <p className="text-[11px] text-secondary leading-tight">
              {game.away_team_name}
            </p>
          </div>
        </div>

        {/* Score */}
        <div className="shrink-0 px-4 text-center">
          {hasScore ? (
            <div className="font-mono font-black text-5xl flex items-center gap-1.5">
              <span style={{ color: awayWins ? awayColor : "#9A9A9A" }}>
                {game.away_score}
              </span>
              <span className="text-dim text-3xl">–</span>
              <span style={{ color: homeWins ? homeColor : "#9A9A9A" }}>
                {game.home_score}
              </span>
            </div>
          ) : (
            <div className="font-mono font-black text-4xl text-dim">VS</div>
          )}
          {game.status === "live" && (
            <p className="text-secondary text-xs mt-1">
              Q{game.quarter} · {game.clock}
            </p>
          )}
        </div>

        {/* Home team */}
        <div className="flex-1 flex flex-col items-center gap-2">
          <TeamLogo abbr={game.home_team_abbr} size={64} />
          <div className="text-center">
            <p
              className="text-base font-black tracking-wide"
              style={{ color: homeColor }}
            >
              {game.home_team_abbr}
            </p>
            <p className="text-[11px] text-secondary leading-tight">
              {game.home_team_name}
            </p>
          </div>
        </div>
      </div>

      {/* Head-to-head stats */}
      {hasPlayerStats && (
        <div className="mt-5 pt-4 border-t border-border">
          <div className="grid grid-cols-[1fr_40px_1fr] gap-3 items-center">
            {/* Away stats */}
            <div className="flex gap-2 justify-start">
              <MiniStat label="FG%" value={awayStats.fgPct} />
              <MiniStat label="AST" value={String(awayStats.ast)} />
              {hasScore && <MiniStat label="PTS" value={String(awayStats.pts)} />}
            </div>

            <div className="text-center text-dim text-sm">↔</div>

            {/* Home stats */}
            <div className="flex gap-2 justify-end">
              {hasScore && <MiniStat label="PTS" value={String(homeStats.pts)} />}
              <MiniStat label="AST" value={String(homeStats.ast)} />
              <MiniStat label="FG%" value={homeStats.fgPct} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center bg-surfaceHigh rounded-lg px-2.5 py-1.5 min-w-[46px]">
      <div className="font-mono text-sm font-bold text-primary">{value}</div>
      <div className="text-[9px] text-dim uppercase tracking-wider">{label}</div>
    </div>
  );
}
