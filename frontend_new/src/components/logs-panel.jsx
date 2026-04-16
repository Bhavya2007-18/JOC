import React, { memo, useMemo } from 'react';
import { Activity, AlertTriangle, ThermometerSun } from 'lucide-react';
import { Card } from './Card';
import { cn } from '../utils/cn';

const TRACKED_EVENTS = new Set([
  'THERMAL_SPIKE',
  'THERMAL_GUARD_TRIGGERED',
  'THERMAL_PREDICTION_ALERT',
  'THERMAL_SOURCE_SWITCH',
]);

function extractEventName(event) {
  const raw =
    event?.payload?.event ||
    event?.payload?.event_type ||
    event?.payload?.type ||
    event?.event_type ||
    event?.type ||
    event?.message ||
    '';
  const upper = String(raw).toUpperCase();
  for (const name of TRACKED_EVENTS) {
    if (upper.includes(name)) return name;
  }
  return null;
}

function formatEventName(name) {
  return name.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
  ).join(' ');
}

function LogsPanelComponent({ events = [] }) {
  const thermalEvents = useMemo(
    () =>
      events
        .map((evt) => ({ evt, name: extractEventName(evt) }))
        .filter((item) => Boolean(item.name))
        .slice(0, 40),
    [events]
  );

  return (
    <Card title="Thermal Event Log" description="Risk and guard events" icon={ThermometerSun}>
      <div className="max-h-[420px] space-y-3 overflow-y-auto pr-1">
        {thermalEvents.length === 0 && (
          <div className="rounded-xl border border-white/10 bg-black/30 p-4 text-xs text-slate-500">
            No thermal events captured yet.
          </div>
        )}

        {thermalEvents.map(({ evt, name }, idx) => {
          const payload = evt.payload || {};
          const tone =
            name === 'THERMAL_GUARD_TRIGGERED' || name === 'THERMAL_PREDICTION_ALERT'
              ? 'text-red-200 border-red-500/30 bg-red-950/20 shadow-lg shadow-red-500/5'
              : 'text-cyan-200 border-white/10 bg-white/[0.03]';
          return (
            <div key={`${evt.id}-${idx}`} className={cn('rounded-xl border p-4 transition-all', tone)}>
              <div className="flex items-center justify-between gap-2">
                <span className="inline-flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest">
                  {name.includes('GUARD') || name.includes('ALERT') ? (
                    <AlertTriangle className="h-3.5 w-3.5" />
                  ) : (
                    <Activity className="h-3.5 w-3.5" />
                  )}
                  {formatEventName(name)}
                </span>
                <span className="text-[10px] text-slate-500 font-medium">{evt.timestamp || '--:--:--'}</span>
              </div>
              <div className="mt-3 grid grid-cols-2 gap-3 text-[11px] text-slate-400">
                <span className="font-medium">Temp: <span className="text-white">{payload.temp ?? payload.temperature ?? 'N/A'}</span></span>
                <span className="font-medium">Mode: <span className="text-white uppercase">{payload.mode_after ?? payload.mode_before ?? 'N/A'}</span></span>
                <span className="col-span-2 leading-relaxed">
                  <span className="text-slate-500 uppercase text-[9px] font-bold block mb-0.5">Primary Root</span>
                  {payload.reason || evt.message || 'N/A'}
                </span>
              </div>
            </div>
          );
        })}
      </div>

    </Card>
  );
}

export const LogsPanel = memo(LogsPanelComponent);

