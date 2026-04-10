import React, { useState } from 'react';
import { useSimulation } from '../hooks/useSimulation';
import { Button } from './Button';
import { Card } from './Card';
import { motion as Motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Square, 
  AlertTriangle, 
  CheckCircle2, 
  Loader2, 
  BarChart3,
  Flame,
  Zap,
  Network,
  Settings
} from 'lucide-react';
import { cn } from '../utils/cn';

const SIMULATION_TYPES = [
  { id: 'cpu_spike', name: 'CPU Stress', icon: Flame, description: 'Simulate high CPU load across all cores' },
  { id: 'memory_stress', name: 'Memory Leak', icon: Zap, description: 'Simulate rapid memory consumption' },
  { id: 'network_burst', name: 'Network Burst', icon: Network, description: 'Simulate high network traffic' },
];

export function SimulationPanel() {
  const { isRunning, report, runSimulation, stopSimulation } = useSimulation();
  const [selectedType, setSelectedType] = useState('cpu_spike');
  const [intensity, setIntensity] = useState(50);
  const [duration, setDuration] = useState(30);

  const handleStart = () => {
    runSimulation({
      simulation_type: selectedType,
      intensity: intensity / 100,
      duration_seconds: duration
    });
  };

  return (
    <div className="space-y-10">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {SIMULATION_TYPES.map((type) => (
          <button
            key={type.id}
            onClick={() => setSelectedType(type.id)}
            disabled={isRunning}
            className={cn(
               'p-6 rounded-3xl transition-all duration-300 text-left border border-transparent',
               selectedType === type.id 
                 ? 'nm-inset bg-slate-900 border-accent-blue/30' 
                 : 'nm-flat bg-slate-900 hover:border-slate-700',
               isRunning && 'opacity-50 cursor-not-allowed'
            )}
          >
            <div className={cn(
               'nm-flat p-3 rounded-2xl w-fit mb-4 transition-colors',
               selectedType === type.id ? 'nm-inset text-accent-blue' : 'text-slate-500'
            )}>
               <type.icon className="h-6 w-6" />
            </div>
            <h4 className={cn('text-sm font-black uppercase tracking-widest', selectedType === type.id ? 'text-white' : 'text-slate-400')}>{type.name}</h4>
            <p className="text-[10px] text-slate-500 mt-2 font-mono uppercase leading-relaxed">{type.description}</p>
          </button>
        ))}
      </div>

      <Card title="Module Parameters" icon={Settings} className="border-dashed border-slate-700">
        <div className="space-y-10 py-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div className="space-y-8">
              <div className="space-y-3">
                <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-[0.2em]">
                  <span className="text-slate-400">Intensity_Level</span>
                  <span className="text-accent-blue nm-inset px-2 rounded-lg bg-slate-950">{intensity}%</span>
                </div>
                <input
                  type="range"
                  min="10"
                  max="100"
                  step="10"
                  value={intensity}
                  onChange={(e) => setIntensity(parseInt(e.target.value))}
                  disabled={isRunning}
                  className="w-full h-2 nm-inset bg-slate-950 rounded-lg appearance-none cursor-pointer accent-accent-blue"
                />
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-[0.2em]">
                  <span className="text-slate-400">Time_Duration</span>
                  <span className="text-accent-blue nm-inset px-2 rounded-lg bg-slate-950">{duration}s</span>
                </div>
                <input
                  type="range"
                  min="10"
                  max="300"
                  step="10"
                  value={duration}
                  onChange={(e) => setDuration(parseInt(e.target.value))}
                  disabled={isRunning}
                  className="w-full h-2 nm-inset bg-slate-950 rounded-lg appearance-none cursor-pointer accent-accent-blue"
                />
              </div>
            </div>

            <div className="flex flex-col justify-center gap-4">
              {isRunning ? (
                <Button 
                  variant="danger" 
                  className="w-full h-16 rounded-2xl gap-3 shadow-[0_0_20px_rgba(239,68,68,0.2)]"
                  onClick={() => stopSimulation()}
                >
                  <Square className="h-5 w-5 fill-current" />
                  EMERGENCY_ABORT
                </Button>
              ) : (
                <Button 
                  className="w-full h-16 rounded-2xl gap-3 nm-convex bg-slate-900 border-none text-white shadow-[0_0_20px_rgba(59,130,246,0.2)]"
                  onClick={handleStart}
                >
                  <Play className="h-5 w-5 fill-current" />
                  INITIATE_BATTLE_STATION
                </Button>
              )}
            </div>
          </div>
        </div>
      </Card>

      <AnimatePresence>
        {isRunning && (
          <Motion.div
            initial={{ opacity: 0, y: 20, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="rounded-[2.5rem] nm-flat bg-slate-900 border border-accent-blue/40 p-10 relative overflow-hidden"
          >
            <div className="absolute top-0 left-0 w-2 bg-accent-blue h-full animate-pulse shadow-[0_0_15px_#3b82f6]" />
            <div className="flex items-center gap-8">
              <div className="rounded-full nm-inset p-5 bg-slate-950">
                <Loader2 className="h-10 w-10 text-accent-blue animate-spin" />
              </div>
              <div>
                <h3 className="text-2xl font-black text-white uppercase italic tracking-tighter">Stress Test Active</h3>
                <p className="text-sm text-slate-400 font-mono tracking-widest mt-2 uppercase opacity-70">
                   Neural Engine is monitoring response vectors for {selectedType.toUpperCase()}.
                </p>
              </div>
            </div>
          </Motion.div>
        )}

        {report && (
          <Motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-8"
          >
            <div className={cn(
              'p-10 rounded-[2.5rem] nm-flat bg-slate-900 border',
              report.status === 'completed' ? 'border-emerald-900/40 shadow-[0_0_20px_rgba(16,185,129,0.1)]' : 'border-red-900/40 shadow-[0_0_20px_rgba(239,68,68,0.1)]'
            )}>
              <div className="flex flex-col md:flex-row items-center justify-between mb-10 gap-6">
                <div className="flex items-center gap-6">
                  <div className={cn(
                    'nm-inset p-4 rounded-2xl bg-slate-950',
                    report.status === 'completed' ? 'text-emerald-500' : 'text-red-500'
                  )}>
                    {report.status === 'completed' ? (
                      <CheckCircle2 className="h-8 w-8" />
                    ) : (
                      <AlertTriangle className="h-8 w-8" />
                    )}
                  </div>
                  <div>
                    <h3 className="text-3xl font-black text-white uppercase tracking-tighter italic">Post-Action Report</h3>
                    <p className="text-xs text-slate-500 font-mono uppercase mt-1 tracking-widest">Simulation_Log_{report.status.toUpperCase()}</p>
                  </div>
                </div>
                <div className="flex items-center gap-6 nm-inset p-6 rounded-3xl bg-slate-950/50">
                  <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]">Resilience_IDX</span>
                  <span className={cn('text-4xl font-black font-mono drop-shadow-md',
                    report.score >= 80 ? 'text-emerald-500' : report.score >= 50 ? 'text-amber-500' : 'text-red-500'
                  )}>{report.score}</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                <div className="space-y-6">
                  <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-3">
                    <AlertTriangle className="h-4 w-4 text-amber-500" />
                    Anomaly telemetry
                  </h4>
                  <div className="space-y-3">
                    {report.anomalies_detected.length > 0 ? (
                      report.anomalies_detected.map((a, i) => (
                        <div key={i} className="text-[11px] font-mono p-4 rounded-xl nm-inset bg-slate-950 text-slate-400 border border-slate-900 leading-relaxed group">
                           <span className="text-amber-500 mr-2 opacity-50 font-bold group-hover:opacity-100 transition-opacity">{">>>"}</span>
                           {a}
                        </div>
                      ))
                    ) : (
                      <p className="text-[11px] text-slate-500 italic font-mono uppercase tracking-widest text-center py-4 bg-slate-950/30 rounded-xl border border-dashed border-slate-800">Telemetry Clean // No Abnormal Vectors</p>
                    )}
                  </div>
                </div>

                <div className="space-y-6">
                  <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-3">
                    <Zap className="h-4 w-4 text-accent-blue" />
                    Neural Actions
                  </h4>
                  <div className="space-y-3">
                    {report.response_actions.length > 0 ? (
                      report.response_actions.map((a, i) => (
                        <div key={i} className="text-[11px] font-mono p-4 rounded-xl nm-inset bg-slate-950 text-slate-400 border border-slate-900 flex justify-between items-center group">
                           <span className="flex items-center gap-2">
                              <span className="text-accent-blue font-bold opacity-50 group-hover:opacity-100 transition-opacity">#</span>
                              {a.action}
                           </span>
                           <span className="text-[9px] font-black nm-convex bg-slate-900 text-accent-blue px-3 py-1 rounded-full">{a.time}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-[11px] text-slate-500 italic font-mono uppercase tracking-widest text-center py-4 bg-slate-950/30 rounded-xl border border-dashed border-slate-800">Zero Intervention Required</p>
                    )}
                  </div>
                </div>
              </div>

              {Array.isArray(report.timeline?.transitions) && report.timeline.transitions.length > 0 && (
                <div className="mt-10 pt-10 border-t border-slate-800">
                  <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-3 mb-6">
                    <BarChart3 className="h-4 w-4 text-purple-400" />
                    Operational Timeline
                  </h4>
                  <div className="space-y-4">
                    {report.timeline.transitions.map((t, idx) => (
                      <div key={idx} className="flex items-start gap-4 group">
                        <div className="mt-1.5 h-2 w-2 rounded-full bg-accent-blue group-hover:shadow-[0_0_8px_#3b82f6] transition-all" />
                        <div className="flex-1">
                          <span className="text-[10px] font-black text-white uppercase tracking-widest block">{t.state || t.phase || 'Event_Pulse'}</span>
                          {t.message && <span className="text-[10px] text-slate-500 font-mono italic mt-1 block group-hover:text-slate-400 transition-colors">DECODED: {t.message}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
