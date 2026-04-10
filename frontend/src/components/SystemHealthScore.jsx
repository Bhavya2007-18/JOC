import React from 'react';
import { motion as Motion } from 'framer-motion';

export function SystemHealthScore({ score = 100 }) {
<<<<<<< HEAD
  const safeScore = typeof score === 'number' ? score : 100;
  
=======
  const normalizedScore = Math.max(0, Math.min(100, Number(score || 0)));

>>>>>>> 23325bbba76187f61f86875495880c5706cec060
  const getColor = (s) => {
    if (s >= 80) return 'text-emerald-500 stroke-emerald-500';
    if (s >= 50) return 'text-amber-500 stroke-amber-500';
    return 'text-red-500 stroke-red-500';
  };

<<<<<<< HEAD
  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (safeScore / 100) * circumference;

  return (
    <div className="relative flex flex-col items-center justify-center p-2">
      <svg className="h-36 w-36 -rotate-90 drop-shadow-[0_0_10px_rgba(0,0,0,0.5)]">
=======
  const circumference = 2 * Math.PI * 60;
  const offset = circumference - (normalizedScore / 100) * circumference;

  return (
    <div className="relative flex flex-col items-center justify-center p-4">
      <svg className="h-44 w-44 -rotate-90">
>>>>>>> 23325bbba76187f61f86875495880c5706cec060
        <circle
          className="stroke-slate-800"
          strokeWidth="10"
          fill="transparent"
<<<<<<< HEAD
          r="40"
          cx="72"
          cy="72"
        />
        <Motion.circle
          className={getColor(safeScore)}
          strokeWidth="10"
=======
          r="60"
          cx="88"
          cy="88"
        />
        <Motion.circle
          className={getColor(normalizedScore)}
          strokeWidth="8"
>>>>>>> 23325bbba76187f61f86875495880c5706cec060
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: "circOut" }}
          strokeLinecap="round"
          fill="transparent"
<<<<<<< HEAD
          r="40"
          cx="72"
          cy="72"
          style={{ filter: 'drop-shadow(0 0 8px currentColor)' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center pt-2">
        <span className={`text-4xl font-black font-mono ${getColor(safeScore).split(' ')[0]}`}>{safeScore}</span>
        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mt-1">Health_Idx</span>
=======
          r="60"
          cx="88"
          cy="88"
        />
      </svg>
      <div className="absolute inset-0 mt-0 flex flex-col items-center justify-center">
        <span className={`text-4xl font-bold leading-none whitespace-nowrap ${getColor(normalizedScore).split(' ')[0]}`}>
          {Math.round(normalizedScore)}%
        </span>
        <span className="text-sm font-medium text-gray-500 mt-1">HEALTH</span>
>>>>>>> 23325bbba76187f61f86875495880c5706cec060
      </div>
    </div>
  );
}
