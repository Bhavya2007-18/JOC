import React, { memo, useMemo } from 'react';
import { motion as Motion } from 'framer-motion';
import { Thermometer, Flame, TrendingUp, Minus } from 'lucide-react';
import { Card } from './Card';
import { cn } from '../utils/cn';

const STATE_TONES = {
  COOL: 'text-cyan-300 border-cyan-500/30 bg-cyan-500/10',
  WARM: 'text-purple-300 border-purple-500/30 bg-purple-500/10',
  HOT: 'text-orange-300 border-orange-500/30 bg-orange-500/10',
  CRITICAL: 'text-red-300 border-red-500/30 bg-red-500/10',
};

const VELOCITY_META = {
  stable: { label: 'Stable', icon: Minus, className: 'text-cyan-300' },
  rising: { label: 'Rising', icon: TrendingUp, className: 'text-amber-300' },
  spiking: { label: 'Spiking', icon: Flame, className: 'text-red-300' },
};

function ThermalPanelComponent({ thermal }) {
  const state = String(thermal?.state || 'COOL').toUpperCase();
  const velocity = String(thermal?.velocity || 'stable').toLowerCase();
  const cpuTemp = Number(thermal?.temperature || 0);
  const gpuTemp = thermal?.gpu_temperature;
  const showGpu = typeof gpuTemp === 'number' && Number.isFinite(gpuTemp);
  const confidence = String(thermal?.confidence || 'low').toLowerCase();
  const source = thermal?.source || 'SyntheticAdapter';
  const isSynthetic = source === 'SyntheticAdapter' || confidence === 'low';
  const velocityMeta = VELOCITY_META[velocity] || VELOCITY_META.stable;
  const VelocityIcon = velocityMeta.icon;

  const heatGlowClass = useMemo(() => {
    if (state === 'CRITICAL') return 'shadow-[0_0_30px_rgba(255,61,87,0.35)] animate-pulse';
    if (state === 'HOT') return 'shadow-[0_0_24px_rgba(255,179,0,0.3)] animate-pulse';
    return '';
  }, [state]);

  return (
    <Card
      title="Thermal Status"
      description="Live CPU/GPU telemetry"
      icon={Thermometer}
      glowColor={state === 'CRITICAL' ? 'red' : state === 'HOT' ? 'amber' : 'cyan'}
      className={cn('transition-all duration-500', heatGlowClass)}
    >
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
          <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">CPU Temp</p>
          <Motion.p
            key={cpuTemp}
            initial={{ opacity: 0.5, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-2 text-4xl font-black text-white"
          >
            {cpuTemp.toFixed(1)}<span className="text-xl text-slate-400">°C</span>
          </Motion.p>
        </div>

        {showGpu && (
          <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
            <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">GPU Temp</p>
            <Motion.p
              key={gpuTemp}
              initial={{ opacity: 0.5, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-2 text-4xl font-black text-white"
            >
              {Number(gpuTemp).toFixed(1)}<span className="text-xl text-slate-400">°C</span>
            </Motion.p>
          </div>
        )}
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <span className={cn('rounded-full border px-3 py-1 text-[10px] font-black uppercase tracking-widest', STATE_TONES[state] || STATE_TONES.COOL)}>
          {state}
        </span>
        <span className={cn('inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[10px] uppercase tracking-widest', velocityMeta.className, velocity === 'spiking' ? 'animate-pulse' : '')}>
          <VelocityIcon className="h-3.5 w-3.5" />
          {velocityMeta.label}
        </span>
        {isSynthetic && (
          <span
            title="Estimated temperature based on system load"
            className="rounded-full border border-slate-700 bg-slate-800/60 px-3 py-1 text-[10px] font-bold uppercase tracking-widest text-slate-300"
          >
            Synthetic Mode
          </span>
        )}
      </div>
    </Card>
  );
}

export const ThermalPanel = memo(ThermalPanelComponent);

