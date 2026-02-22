"use client";

import { useState } from "react";
import api from "@/lib/api";
import AIVerdictBox from "./AIVerdictBox";
import LoadingSpinner from "../ui/LoadingSpinner";

interface Take {
  id: string;
  personality: string;
  outlet: string;
  outlet_color: string;
  avatar: string;
  take_text: string;
  category: string;
  agrees: number;
  disagrees: number;
}

interface TakeCardProps {
  take: Take;
}

const categoryLabel: Record<string, string> = {
  hot: "🔥 Hot",
  "stat-backed": "📊 Stat-Backed",
  prediction: "🎯 Prediction",
  popular: "👥 Popular",
};

export default function TakeCard({ take }: TakeCardProps) {
  const storedVote =
    typeof window !== "undefined"
      ? localStorage.getItem(`courtiq_voted_${take.id}`)
      : null;

  const [localAgrees, setLocalAgrees] = useState(take.agrees);
  const [localDisagrees, setLocalDisagrees] = useState(take.disagrees);
  const [hasVoted, setHasVoted] = useState<string | null>(storedVote);
  const [verdict, setVerdict] = useState<any>(null);
  const [isLoadingVerdict, setIsLoadingVerdict] = useState(false);

  const total = localAgrees + localDisagrees;
  const agreePercent = total > 0 ? Math.round((localAgrees / total) * 100) : 50;

  const handleVote = async (vote: "agree" | "disagree") => {
    if (hasVoted) return;
    try {
      const res = await api.post("/api/takes/vote", { take_id: take.id, vote });
      setLocalAgrees(res.data.agrees);
      setLocalDisagrees(res.data.disagrees);
    } catch {
      if (vote === "agree") setLocalAgrees((n) => n + 1);
      else setLocalDisagrees((n) => n + 1);
    }
    setHasVoted(vote);
    localStorage.setItem(`courtiq_voted_${take.id}`, vote);
  };

  const handleVerdict = async () => {
    if (verdict) return;
    setIsLoadingVerdict(true);
    try {
      const res = await api.post("/api/takes/verdict", {
        take_id: take.id,
        take_text: take.take_text,
      });
      setVerdict(res.data);
    } catch {
      setVerdict({
        steelman: "Supporting argument unavailable.",
        challenge: "Counter-argument unavailable.",
        verdict_label: "Partially supported",
      });
    } finally {
      setIsLoadingVerdict(false);
    }
  };

  return (
    <div className="bg-surface border border-border rounded-xl p-5 hover:border-border/60 transition-colors">
      {/* Header */}
      <div className="flex items-start gap-3 mb-3">
        {/* Avatar */}
        <div
          className="w-9 h-9 rounded-full flex items-center justify-center text-white text-xs font-black flex-shrink-0"
          style={{ backgroundColor: take.outlet_color }}
        >
          {take.avatar}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold text-primary text-sm">
              {take.personality}
            </span>
            <span
              className="text-xs px-2 py-0.5 rounded-full text-white font-medium flex-shrink-0"
              style={{ backgroundColor: take.outlet_color }}
            >
              {take.outlet}
            </span>
            <span className="text-xs px-2 py-0.5 bg-surfaceHigh text-secondary rounded-full">
              {categoryLabel[take.category] || take.category}
            </span>
          </div>
          <p className="text-dim text-xs mt-0.5">Feb 21</p>
        </div>
      </div>

      {/* Take text */}
      <p className="text-primary text-sm leading-relaxed mb-4 border-l-2 border-orange/40 pl-3 italic">
        {take.take_text}
      </p>

      {/* Vote row */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => handleVote("agree")}
            disabled={!!hasVoted}
            aria-pressed={hasVoted === "agree"}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all border ${
              hasVoted === "agree"
                ? "border-success/50 bg-success/10 text-success"
                : "border-border text-secondary hover:border-success/50 hover:text-success disabled:opacity-50"
            }`}
          >
            👍 {localAgrees.toLocaleString()}
          </button>
          <button
            onClick={() => handleVote("disagree")}
            disabled={!!hasVoted}
            aria-pressed={hasVoted === "disagree"}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all border ${
              hasVoted === "disagree"
                ? "border-danger/50 bg-danger/10 text-danger"
                : "border-border text-secondary hover:border-danger/50 hover:text-danger disabled:opacity-50"
            }`}
          >
            👎 {localDisagrees.toLocaleString()}
          </button>

          <button
            onClick={handleVerdict}
            disabled={isLoadingVerdict || !!verdict}
            className="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-orange/40 text-orange text-sm hover:bg-orange-dim transition-colors disabled:opacity-60"
          >
            {isLoadingVerdict ? (
              <>
                <span className="w-3 h-3 border border-orange border-t-transparent rounded-full animate-spin" />
                Analyzing...
              </>
            ) : verdict ? (
              "🤖 Verdict ✓"
            ) : (
              "🤖 AI Verdict"
            )}
          </button>
        </div>

        {/* Consensus bar */}
        <div className="h-1.5 bg-border rounded-full overflow-hidden">
          <div
            className="h-full bg-success rounded-full transition-all duration-500"
            style={{ width: `${agreePercent}%` }}
          />
        </div>

        {hasVoted && (
          <div className="flex justify-between text-xs text-dim">
            <span>{agreePercent}% agree</span>
            <span>{100 - agreePercent}% disagree</span>
          </div>
        )}
      </div>

      {/* AI Verdict */}
      {verdict && <AIVerdictBox verdict={verdict} />}
    </div>
  );
}
