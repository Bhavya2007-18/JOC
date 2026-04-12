import React from 'react';
import { motion as Motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, Info, Zap, Settings, Activity } from 'lucide-react';
import { useCipher } from '../hooks/useCipher';

const icons = {
  info: Info,
  warning: AlertTriangle,
  success: Zap,
  config: Settings,
  activity: Activity
};

const colors = {
  info: 'text-blue-400 border-blue-900/50 bg-blue-950/20',
  warning: 'text-amber-400 border-amber-900/50 bg-amber-950/20',
  success: 'text-emerald-400 border-emerald-900/50 bg-emerald-950/20',
  config: 'text-purple-400 border-purple-900/50 bg-purple-950/20',
  activity: 'text-cyan-400 border-cyan-900/50 bg-cyan-950/20'
};

function CipheredText({ text }) {
  const { displayText } = useCipher(text);
  return <p className="text-sm font-medium font-mono leading-tight">{displayText}</p>;
}

export function EventStream({ events = [] }) {
  return (
    <div className="flex flex-col h-full max-h-[400px] overflow-hidden rounded-3xl nm-flat bg-slate-900 border border-slate-800">
      <div className="border-b border-slate-800 bg-slate-900/50 px-6 py-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-3 uppercase tracking-widest">
          <Activity className="h-4 w-4 text-accent-blue" />
          Neural Event Stream
        </h3>
      </div>
      <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin">
        <AnimatePresence initial={false} mode="popLayout">
          {events.length === 0 ? (
            <p className="text-sm text-center text-slate-500 py-8 italic font-mono">Standby... Waiting for telemetry</p>
          ) : (
            events.map((event) => {
              const Icon = icons[event.type] || Info;
              const colorClass = colors[event.type] || colors.info;
              
              return (
                <Motion.div
                  key={event.id}
                  initial={{ opacity: 0, y: 20, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className={`flex items-start gap-4 rounded-2xl border p-4 ${colorClass} transition-colors duration-300`}
                >
                  <div className="mt-1 rounded-xl nm-inset p-2 bg-slate-900">
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <CipheredText text={event.message} />
                    <span className="mt-2 block text-[10px] opacity-50 font-mono tracking-tighter uppercase whitespace-nowrap">
                      [{event.timestamp}] DECODED_LOG_{String(event.id).slice(-4)}
                    </span>
                  </div>
                </Motion.div>
              );
            })
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
