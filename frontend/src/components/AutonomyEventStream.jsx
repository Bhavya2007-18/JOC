import React from 'react';
import { motion as Motion, AnimatePresence } from 'framer-motion';
import { Activity, ShieldAlert } from 'lucide-react';

export function AutonomyEventStream({ autonomyFeed }) {
  // Extract action history
  // autonomyFeed usually comes from websocket: { action_history: [...], status: "active" }
  const actionHistory = autonomyFeed?.action_history || [];
  
  return (
    <div className="flex flex-col h-full max-h-[400px] overflow-hidden rounded-3xl bg-slate-900/60 border border-red-900/40 backdrop-blur-md shadow-[0_0_20px_rgba(220,38,38,0.05)] relative group cursor-default transition-all duration-500 hover:border-red-500/50">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-600 via-amber-500 to-red-600 opacity-80 group-hover:opacity-100 transition-opacity" />
      
      <div className="border-b border-red-900/30 bg-red-950/20 px-6 py-4 flex items-center justify-between">
        <h3 className="text-xs font-black text-red-500 flex items-center gap-3 uppercase tracking-[0.2em] shadow-red-500 drop-shadow-[0_0_5px_rgba(239,68,68,0.5)]">
          <Activity className="h-4 w-4 animate-pulse" />
          Autonomy Action Feed
        </h3>
        {autonomyFeed && <span className="text-[9px] text-red-500 bg-red-950/50 border border-red-900/50 px-2 py-0.5 rounded-full uppercase tracking-widest">Live Sync</span>}
      </div>
      
      <div className="flex-1 overflow-y-auto p-5 space-y-4 scrollbar-thin">
        <AnimatePresence initial={false} mode="popLayout">
          {actionHistory.length === 0 ? (
            <p className="text-[10px] text-center text-red-500/40 py-10 italic font-mono uppercase tracking-[0.1em]">No autonomous protocols executed.</p>
          ) : (
            actionHistory.map((action, idx) => (
              <Motion.div
                key={idx}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-start gap-4 rounded-xl border border-red-900/40 p-4 bg-red-950/10 hover:bg-red-950/30 transition-colors"
              >
                <div className="mt-0.5 flex-shrink-0 text-red-500 shadow-red-500 drop-shadow-[0_0_3px_rgba(239,68,68,0.8)]">
                  <ShieldAlert className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-black text-white uppercase tracking-wider block mb-1">
                    {action.action || 'SYSTEM_INTERVENTION'}
                  </p>
                  <p className="text-[10px] text-red-100/60 font-mono tracking-wider uppercase truncate">
                    TARGET: {action.target || 'N/A'}
                  </p>
                  <div className="mt-2 text-[9px] flex items-center gap-3 font-mono opacity-80 uppercase">
                    <span className="text-amber-400 bg-amber-950/50 px-1 py-0.5 rounded">CONF: {Math.round((action.confidence || 0) * 100)}%</span>
                  </div>
                </div>
              </Motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
