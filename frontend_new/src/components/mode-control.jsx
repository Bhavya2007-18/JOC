import React, { memo, useMemo, useState } from 'react';
import { BrainCircuit, Clock3, ShieldAlert, Zap } from 'lucide-react';
import { motion as Motion, AnimatePresence } from 'framer-motion';
import { cn } from '../utils/cn';
import { Card } from './Card';
import { Button } from './Button';

const MODES = [
  { id: 'chill', label: 'Chill', icon: Clock3, desc: 'Power saving profile' },
  { id: 'smart', label: 'Smart', icon: BrainCircuit, desc: 'Balanced profile' },
  { id: 'beast', label: 'Beast', icon: Zap, desc: 'Maximum performance' },
];

function ModeControlComponent({
  systemMode,
  thermal,
  thermalPrediction,
  modeLoading,
  onModeChange,
  onStatus,
}) {
  const [forceOverride, setForceOverride] = useState(false);
  const [pendingMode, setPendingMode] = useState(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const risk = String(thermalPrediction?.risk || 'SAFE').toUpperCase();
  const isCriticalNow = Boolean(thermal?.is_critical);
  const isBeastBlocked = (isCriticalNow || risk === 'CRITICAL') && !forceOverride;

  const blockedReason = useMemo(() => {
    if (!isBeastBlocked) return '';
    if (isCriticalNow) return 'Blocked due to thermal risk (critical temperature)';
    if (risk === 'CRITICAL') return 'Blocked due to thermal risk (critical forecast)';
    return 'Blocked due to thermal risk';
  }, [isBeastBlocked, isCriticalNow, risk]);

  const handleSelectMode = (modeId) => {
    if (modeId === 'beast' && isBeastBlocked) {
      onStatus?.({ type: 'error', message: 'Blocked by thermal protection' });
      return;
    }
    if (modeId === 'beast' && forceOverride) {
      setPendingMode(modeId);
      setConfirmOpen(true);
      return;
    }
    onModeChange(modeId);
  };

  const confirmOverride = () => {
    if (pendingMode) {
      onModeChange(pendingMode);
    }
    setConfirmOpen(false);
    setPendingMode(null);
  };

  return (
    <Card title="Mode Control" description="Thermal-aware command modes" icon={ShieldAlert}>
      <div className="space-y-3">
        {MODES.map((mode) => {
          const isActive = systemMode === mode.id;
          const isBeast = mode.id === 'beast';
          const isDisabled = modeLoading || (isBeast && isBeastBlocked);
          const Icon = mode.icon;
          return (
            <button
              key={mode.id}
              title={isBeast && isBeastBlocked ? blockedReason : ''}
              onClick={() => handleSelectMode(mode.id)}
              disabled={isDisabled}
              className={cn(
                'w-full rounded-2xl border px-4 py-3 text-left transition-all',
                isActive
                  ? 'border-cyan-400/40 bg-cyan-500/10 text-white'
                  : 'border-white/10 bg-white/[0.02] text-slate-300 hover:border-slate-500/40',
                isDisabled ? 'cursor-not-allowed opacity-50' : ''
              )}
            >
              <div className="flex items-center gap-3">
                <Icon className="h-5 w-5" />
                <div>
                  <p className="text-sm font-bold uppercase">{mode.label}</p>
                  <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">{mode.desc}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      <label className="mt-4 flex items-center justify-between rounded-xl border border-red-500/20 bg-red-950/20 px-3 py-2 text-xs text-red-200">
        <span className="uppercase tracking-wider">Force Override (Unsafe)</span>
        <input
          type="checkbox"
          checked={forceOverride}
          onChange={(e) => setForceOverride(e.target.checked)}
          className="h-4 w-4 accent-red-500"
        />
      </label>

      <AnimatePresence>
        {confirmOpen && (
          <Motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
          >
            <div className="w-full max-w-md rounded-2xl border border-red-500/30 bg-[#0B0E16] p-6">
              <h3 className="text-lg font-black text-white">Unsafe Override</h3>
              <p className="mt-2 text-sm text-slate-300">System may overheat. Proceed?</p>
              <div className="mt-5 flex justify-end gap-3">
                <Button variant="secondary" onClick={() => setConfirmOpen(false)}>Cancel</Button>
                <Button onClick={confirmOverride} className="bg-red-600 text-white">Proceed</Button>
              </div>
            </div>
          </Motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
}

export const ModeControl = memo(ModeControlComponent);

