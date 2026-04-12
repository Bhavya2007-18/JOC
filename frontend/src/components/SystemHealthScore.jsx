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
    <div className="relative flex flex-col items-center justify-center p-4 group select-none">
      {/* Vitality Core - Subtle background pulses */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <Motion.div
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.03, 0.08, 0.03]
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className={`w-40 h-40 rounded-full blur-3xl ${normalizedScore >= 80 ? 'bg-emerald-500' : normalizedScore >= 50 ? 'bg-amber-500' : 'bg-red-500'}`}
        />
      </div>

      <svg className="h-44 w-44 -rotate-90 drop-shadow-[0_0_15px_rgba(0,0,0,0.5)]">
        {/* Background track */}
        <circle
          className="stroke-slate-800"
          strokeWidth="12"
          fill="transparent"
          r="60"
          cx="88"
          cy="88"
          opacity="0.3"
        />

        {/* Neural Mesh - Filling the empty center */}
        <Motion.g
          animate={{ rotate: 360 }}
          transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
          style={{ originX: "88px", originY: "88px" }}
        >
          {[...Array(6)].map((_, i) => (
            <line
              key={i}
              x1="58" y1="88" x2="118" y2="88"
              stroke="currentColor"
              className={getColor(normalizedScore).split(' ')[1]}
              strokeWidth="0.5"
              opacity="0.05"
              transform={`rotate(${i * 30}, 88, 88)`}
            />
          ))}
          <circle cx="88" cy="88" r="30" fill="none" stroke="currentColor" className={getColor(normalizedScore).split(' ')[1]} strokeWidth="0.5" opacity="0.05" />
          <circle cx="88" cy="88" r="15" fill="none" stroke="currentColor" className={getColor(normalizedScore).split(' ')[1]} strokeWidth="0.5" opacity="0.03" />
        </Motion.g>

        {/* Drifting Data Bits */}
        {[...Array(8)].map((_, i) => (
          <Motion.circle
            key={i}
            r="1"
            fill="currentColor"
            className={getColor(normalizedScore).split(' ')[1]}
            initial={{ 
              x: 88 + (Math.random() - 0.5) * 60, 
              y: 88 + (Math.random() - 0.5) * 60,
              opacity: 0
            }}
            animate={{ 
              y: [null, 88 + (Math.random() - 0.5) * 40],
              opacity: [0, 0.3, 0]
            }}
            transition={{
              duration: 3 + Math.random() * 4,
              repeat: Infinity,
              delay: Math.random() * 5
            }}
          />
        ))}
        
        {/* Scanner Sweep */}
        <Motion.g
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          style={{ originX: "88px", originY: "88px" }}
        >
          <line
            x1="88" y1="88" x2="88" y2="28"
            className={getColor(normalizedScore).split(' ')[1]}
            strokeWidth="1.5"
            opacity="0.15"
            strokeLinecap="round"
          />
          <circle cx="88" cy="28" r="2.5" className={getColor(normalizedScore).split(' ')[0].replace('text-', 'fill-')} opacity="0.3" />
        </Motion.g>

        {/* The Health Index Gauge */}
        <Motion.circle
          className={getColor(normalizedScore)}
          strokeWidth="10"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 2, ease: "circOut" }}
          strokeLinecap="round"
          fill="transparent"
          r="60"
          cx="88"
          cy="88"
          style={{ filter: `drop-shadow(0 0 15px currentColor)` }}
        />
      </svg>

      <div className="absolute inset-0 mt-0 flex flex-col items-center justify-center relative z-10">
        <Motion.span 
          animate={{ scale: [1, 1.02, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
          className={`text-4xl font-black font-mono leading-none whitespace-nowrap ${getColor(normalizedScore).split(' ')[0]}`}
        >
          {Math.round(normalizedScore)}%
        </Motion.span>
        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mt-1 opacity-80">Health_Idx</span>
      </div>
    </div>
  );
}
