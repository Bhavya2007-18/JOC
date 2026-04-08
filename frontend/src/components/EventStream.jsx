import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, Info, Zap, Settings, Activity } from 'lucide-react';

const icons = {
  info: Info,
  warning: AlertTriangle,
  success: Zap,
  config: Settings,
  activity: Activity
};

const colors = {
  info: 'text-blue-500 bg-blue-50 border-blue-100',
  warning: 'text-amber-500 bg-amber-50 border-amber-100',
  success: 'text-green-500 bg-green-50 border-green-100',
  config: 'text-purple-500 bg-purple-50 border-purple-100',
  activity: 'text-indigo-500 bg-indigo-50 border-indigo-100'
};

export function EventStream({ events = [] }) {
  return (
    <div className="flex flex-col h-full max-h-[400px] overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
      <div className="border-b border-gray-100 bg-gray-50/50 px-4 py-3">
        <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
          <Activity className="h-4 w-4 text-blue-500" />
          Real-Time Event Stream
        </h3>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin">
        <AnimatePresence initial={false}>
          {events.length === 0 ? (
            <p className="text-sm text-center text-gray-500 py-8 italic">No events recorded yet.</p>
          ) : (
            events.map((event) => {
              const Icon = icons[event.type] || Info;
              const colorClass = colors[event.type] || colors.info;
              
              return (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, x: -20, height: 0 }}
                  animate={{ opacity: 1, x: 0, height: 'auto' }}
                  exit={{ opacity: 0, x: 20, height: 0 }}
                  className={`flex items-start gap-3 rounded-lg border p-3 ${colorClass}`}
                >
                  <div className="mt-0.5 rounded-md bg-white p-1 shadow-sm">
                    <Icon className="h-3.5 w-3.5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium leading-tight">{event.message}</p>
                    <span className="mt-1 text-[10px] opacity-70 font-mono">{event.timestamp}</span>
                  </div>
                </motion.div>
              );
            })
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
