import React from 'react';
import { motion } from 'framer-motion';

export function SystemHealthScore({ score = 100 }) {
  const getColor = (s) => {
    if (s >= 80) return 'text-green-500 stroke-green-500';
    if (s >= 50) return 'text-amber-500 stroke-amber-500';
    return 'text-red-500 stroke-red-500';
  };

  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative flex flex-col items-center justify-center p-4">
      <svg className="h-32 w-32 -rotate-90">
        <circle
          className="stroke-gray-100"
          strokeWidth="8"
          fill="transparent"
          r="40"
          cx="64"
          cy="64"
        />
        <motion.circle
          className={getColor(score)}
          strokeWidth="8"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: "easeOut" }}
          strokeLinecap="round"
          fill="transparent"
          r="40"
          cx="64"
          cy="64"
        />
      </svg>
      <div className="absolute inset-0 mt-2 flex flex-col items-center justify-center">
        <span className={`text-3xl font-bold ${getColor(score).split(' ')[0]}`}>{score}</span>
        <span className="text-xs font-medium text-gray-500">HEALTH</span>
      </div>
    </div>
  );
}
