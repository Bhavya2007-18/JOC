import React from "react";

export function DecisionTracePanel({ decisions }) {
  const now = Date.now();

  const getRelativeTime = (timestamp) => {
    if (!timestamp) return "just now";

    const raw = typeof timestamp === "number" ? timestamp : Date.parse(timestamp);
    if (Number.isNaN(raw)) return "just now";

    // Support seconds or milliseconds input.
    const tsMs = raw < 1e12 ? raw * 1000 : raw;
    const diffMs = Math.max(0, now - tsMs);
    const diffSec = Math.floor(diffMs / 1000);

    if (diffSec < 60) return "just now";
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
    return `${Math.floor(diffSec / 86400)}d ago`;
  };

  return (
    <div className="bg-white shadow rounded-2xl p-4 space-y-3">
      <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
        Decision Trace
      </h3>

      {decisions.length === 0 && (
        <div className="text-xs text-gray-400">
          No active decisions
        </div>
      )}

      {decisions.map((d, idx) => (
        <div key={idx} className="border-l-2 border-slate-700 pl-3 space-y-1">
          <div className="text-[10px] text-gray-400">
            {getRelativeTime(d.timestamp)}
          </div>
          <div className="text-xs text-gray-500">
            {d.title}
          </div>

          {d.cause && (
            <div className="text-xs text-gray-400">
              Cause: {d.cause}
            </div>
          )}

          {d.confidence !== undefined && (
            <div className="text-xs text-gray-400">
              Confidence: {Math.round(d.confidence * 100)}%
            </div>
          )}

          {d.best_action?.target && (
            <div className="text-xs text-blue-500">
              Action: {d.best_action.target}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
