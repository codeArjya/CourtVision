"use client";

interface AIVerdictBoxProps {
  verdict: {
    steelman: string;
    challenge: string;
    verdict_label: string;
  };
}

export default function AIVerdictBox({ verdict }: AIVerdictBoxProps) {
  const labelStyles: Record<string, string> = {
    "Backed by data": "bg-success/20 text-success border-success/30",
    "Partially supported": "bg-warn/20 text-warn border-warn/30",
    Overblown: "bg-danger/20 text-danger border-danger/30",
  };
  const labelStyle =
    labelStyles[verdict.verdict_label] || labelStyles["Partially supported"];

  return (
    <div className="bg-surfaceHigh border border-orange/30 rounded-lg p-4 mt-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <span className="text-orange text-sm font-semibold">
          🤖 CourtVision AI Verdict
        </span>
        <span
          className={`rounded-full px-3 py-0.5 text-xs border font-medium ${labelStyle}`}
        >
          {verdict.verdict_label}
        </span>
      </div>

      {/* Steelman */}
      <div className="flex items-start gap-2 mb-2">
        <span className="text-success font-bold text-sm mt-0.5">✓</span>
        <p className="text-sm text-primary">{verdict.steelman}</p>
      </div>

      {/* Challenge */}
      <div className="flex items-start gap-2 mb-3">
        <span className="text-danger font-bold text-sm mt-0.5">✗</span>
        <p className="text-sm text-primary">{verdict.challenge}</p>
      </div>

      {/* Footer */}
      <p className="text-dim text-xs">Powered by Gemini 1.5 Flash</p>
    </div>
  );
}
