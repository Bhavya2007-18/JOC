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
              ? 'text-red-200 border-red-500/30 bg-red-950/20'
              : 'text-cyan-200 border-cyan-500/20 bg-cyan-950/10';
          return (
            <div key={`${evt.id}-${idx}`} className={cn('rounded-xl border p-3', tone)}>
              <div className="flex items-center justify-between gap-2">
                <span className="inline-flex items-center gap-2 text-[10px] font-black uppercase tracking-widest">
                  {name.includes('GUARD') || name.includes('ALERT') ? (
                    <AlertTriangle className="h-3.5 w-3.5" />
                  ) : (
                    <Activity className="h-3.5 w-3.5" />
                  )}
                  {name}
                </span>
                <span className="text-[10px] text-slate-400">{evt.timestamp || '--:--:--'}</span>
              </div>
              <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                <span>Temp: {payload.temp ?? payload.temperature ?? 'N/A'}</span>
                <span>Mode: {payload.mode_after ?? payload.mode_before ?? 'N/A'}</span>
                <span className="col-span-2">Reason: {payload.reason || evt.message || 'N/A'}</span>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

export const LogsPanel = memo(LogsPanelComponent);

