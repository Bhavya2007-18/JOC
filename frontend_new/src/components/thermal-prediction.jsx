import React, { memo, useMemo } from 'react';
import { motion as Motion } from 'framer-motion';
import { AlertTriangle, GaugeCircle } from 'lucide-react';
import { Card } from './Card';
import { cn } from '../utils/cn';

const RISK_TONES = {
  SAFE: 'text-emerald-300 border-emerald-500/30 bg-emerald-500/10',
  WARNING: 'text-amber-300 border-amber-500/30 bg-amber-500/10',
  HIGH: 'text-orange-300 border-orange-500/30 bg-orange-500/10',
  CRITICAL: 'text-red-300 border-red-500/30 bg-red-500/10',
};

function ThermalPredictionComponent({ prediction }) {
  const predictedTemp = Number(prediction?.predicted_temp || 0);
  const risk = String(prediction?.risk || 'SAFE').toUpperCase();
  const timeToCritical = prediction?.time_to_critical;
  const confidence = String(prediction?.confidence || 'low');
  const progress = Math.max(0, Math.min(100, (predictedTemp / 90) * 100));
  const isElevated = risk === 'HIGH' || risk === 'CRITICAL';

  const barColor = useMemo(() => {
    if (risk === 'CRITICAL') return 'from-red-500 to-rose-400';
    if (risk === 'HIGH') return 'from-orange-500 to-amber-400';
    if (risk === 'WARNING') return 'from-amber-500 to-yellow-300';
    return 'from-emerald-500 to-cyan-400';
  }, [risk]);

  return (
    <Card
      title="Thermal Forecast"
      description="5s forward prediction"
      icon={GaugeCircle}
      glowColor={risk === 'CRITICAL' ? 'red' : risk === 'HIGH' ? 'amber' : 'purple'}
    >
      {isElevated && (
        <Motion.div
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 flex items-center gap-2 rounded-xl border border-red-500/30 bg-red-950/30 px-3 py-2 text-xs text-red-200"
        >
          <AlertTriangle className="h-4 w-4" />
          <span>Thermal risk elevated. Pre-emptive safeguards are active.</span>
        </Motion.div>
      )}

      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">Predicted Temp</p>
          <p className="text-4xl font-black text-white">
            {predictedTemp.toFixed(1)}<span className="text-xl text-slate-400">°C</span>
          </p>
        </div>
        <span className={cn('rounded-full border px-3 py-1 text-[10px] font-black uppercase tracking-widest', RISK_TONES[risk] || RISK_TONES.SAFE)}>
          {risk}
        </span>
      </div>

      <div
        className="mt-4 rounded-xl border border-white/10 bg-black/30 p-3"
        title="Linear trend forecast using recent thermal history and 5-second prediction window."
      >
        <div className="mb-2 flex items-center justify-between text-[10px] uppercase tracking-widest text-slate-400">
          <span>Critical Threshold Progress</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
          <Motion.div
            initial={false}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.35 }}
            className={cn('h-full bg-gradient-to-r', barColor)}
          />
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
        <span>
          Time To Critical:{' '}
          <span className="font-semibold text-white">
            {typeof timeToCritical === 'number' ? `${timeToCritical.toFixed(1)}s` : 'N/A'}
          </span>
        </span>
        <span className="uppercase tracking-wider text-[10px]">Confidence: {confidence}</span>
      </div>
    </Card>
  );
}

export const ThermalPrediction = memo(ThermalPredictionComponent);

