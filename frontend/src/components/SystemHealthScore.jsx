import React from 'react';
import { motion as Motion } from 'framer-motion';

export function SystemHealthScore({ score = 100 }) {
  const normalizedScore = Math.max(0, Math.min(100, Number(score || 0)));

  const getColor = (s) => {
    if (s >= 80) return 'text-emerald-500 stroke-emerald-500';
    if (s >= 50) return 'text-amber-500 stroke-amber-500';
    return 'text-red-500 stroke-red-500';
  };

  const circumference = 2 * Math.PI * 60;
  const offset = circumference - (normalizedScore / 100) * circumference;

  return (
    <div className="relative flex flex-col items-center justify-center p-4">
      <svg className="h-44 w-44 -rotate-90 drop-shadow-[0_0_10px_rgba(0,0,0,0.5)]">
        <circle
          className="stroke-slate-800"
          strokeWidth="10"
          fill="transparent"
          r="60"
          cx="88"
          cy="88"
        />
        <Motion.circle
          className={getColor(normalizedScore)}
          strokeWidth="8"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: "circOut" }}
          strokeLinecap="round"
          fill="transparent"
          r="60"
          cx="88"
          cy="88"
          style={{ filter: 'drop-shadow(0 0 8px currentColor)' }}
        />
      </svg>
      <div className="absolute inset-0 mt-0 flex flex-col items-center justify-center">
        <span className={`text-4xl font-black font-mono leading-none whitespace-nowrap ${getColor(normalizedScore).split(' ')[0]}`}>
          {Math.round(normalizedScore)}%
        </span>
        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mt-1">Health_Idx</span>
      </div>
    </div>
  );
}
