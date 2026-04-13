import React from "react";

export function IntelligenceStrip({ prediction, bestAction, confidence, riskLevel, lastUpdated }) {
  const risk = riskLevel || "NORMAL";
  const ram = prediction?.predicted_ram?.["1m"];

  const getColor = () => {
    if (risk === "CRITICAL") return "bg-red-50 border-red-300 text-red-700 shadow-md shadow-red-200";
    if (risk === "HIGH") return "bg-amber-50 border-amber-300 text-amber-700";
    return "bg-green-50 border-green-300 text-green-700";
  };

  return (
    <div className={`w-full border rounded-xl px-4 py-3 flex items-center justify-between gap-4 ${getColor()} ${risk === "CRITICAL" ? "animate-[pulse_2s_ease-in-out_infinite]" : ""}`}>
      {/* LEFT: RISK + PREDICTION */}
      <div className="text-sm font-medium uppercase tracking-wide">
        {risk === "CRITICAL" && "⚠️ CRITICAL"}
        {risk === "HIGH" && "⚠️ HIGH"}
        {risk === "NORMAL" && "✔ NORMAL"}

        {ram !== undefined && (
          <span className="ml-2 text-xs opacity-80 uppercase tracking-wide">
            RAM → {Math.round(ram)}%
          </span>
        )}
      </div>

      {/* CENTER: BEST ACTION */}
      <div className="text-sm font-bold tracking-wide uppercase">
        {bestAction?.target
          ? `Fix: ${bestAction.target}`
          : "System Stable"}
      </div>

      {/* RIGHT: CONFIDENCE */}
      <div className="flex items-center gap-1 text-[10px] opacity-60 uppercase tracking-wide">
        <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
        LIVE
      </div>
      <div className="text-xs opacity-70 uppercase tracking-wide">
        {confidence !== null
          ? `${Math.round(confidence * 100)}%`
          : ""}
      </div>
    </div>
  );
}
