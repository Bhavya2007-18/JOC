import React, { useState, useEffect } from 'react';
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
  Settings,
  History,
  Target,
  Shield,
  Swords,
} from 'lucide-react';
import { BattleStationAnimation } from './BattleStationAnimation';
import { cn } from '../utils/cn';
import { autonomyApi } from '../api/client';

const SIMULATION_TYPES = [
  { id: 'cpu_spike', name: 'CPU Stress', icon: Flame, description: 'Simulate high CPU load across all cores', color: 'text-orange-500' },
  { id: 'memory_stress', name: 'Memory Leak', icon: Zap, description: 'Simulate rapid memory consumption', color: 'text-yellow-500' },
  { id: 'network_burst', name: 'Network Burst', icon: Network, description: 'Simulate high network traffic', color: 'text-cyan-500' },
];

const DIFFICULTIES = [
  { id: 'easy', label: 'Easy', color: 'text-emerald-500' },
  { id: 'medium', label: 'Medium', color: 'text-amber-500' },
  { id: 'hard', label: 'Hard', color: 'text-red-500' },
  { id: 'auto', label: 'Auto (ML)', color: 'text-accent-blue' },
];

export function SimulationPanel() {
  const { isRunning, report, history, error, runSimulation, stopSimulation, fetchHistory } = useSimulation();
  const [selectedType, setSelectedType] = useState('cpu_spike');
  const [intensity, setIntensity] = useState(50);
  const [duration, setDuration] = useState(30);
  const [difficulty, setDifficulty] = useState('auto');
  const [showHistory, setShowHistory] = useState(false);
  const [auditLogs, setAuditLogs] = useState([]);
  const [showAudit, setShowAudit] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const fetchAudit = async () => {
    try {
      const res = await autonomyApi.getAuditHistory();
      if (res.data?.audit) {
        setAuditLogs(res.data.audit);
      }
    } catch (err) {
      console.error('Failed to fetch audit logic:', err);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchAudit();
  }, [isRunning]);

  // Refresh history when a simulation completes
  useEffect(() => {
    if (report && (report.status === 'completed' || report.status === 'failed')) {
      fetchHistory();
      // eslint-disable-next-line react-hooks/exhaustive-deps
      // eslint-disable-next-line react-hooks/set-state-in-effect
      fetchAudit();
    }
  }, [report, fetchHistory]);

  const handleStart = () => {
    runSimulation({
      simulation_type: selectedType,
      parameters: {
        intensity: intensity / 100,
        duration_seconds: duration,
      },
      difficulty: difficulty,
      observation_window_seconds: Math.min(duration, 30),
    });
  };

  return (
    <div className="space-y-10">
      {/* Error bar */}
      <AnimatePresence>
        {error && (
          <Motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-center gap-4 rounded-2xl nm-flat bg-red-950/20 p-6 text-red-400 border border-red-900/30"
          >
            <AlertTriangle className="h-5 w-5 shrink-0" />
            <p className="text-xs font-black uppercase tracking-widest">{error}</p>
          </Motion.div>
        )}
      </AnimatePresence>

      {/* Simulation Type Selector */}
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

      {/* Module Parameters */}
      <Card title="Module Parameters" icon={Settings} className="border-dashed border-slate-700">
        <div className="space-y-10 py-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div className="space-y-8">
              {/* Intensity */}
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

              {/* Duration */}
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

              {/* Difficulty Selector */}
              <div className="space-y-3">
                <div className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">
                  Difficulty_Protocol
                </div>
                <div className="flex gap-2">
                  {DIFFICULTIES.map((d) => (
                    <button
                      key={d.id}
                      onClick={() => setDifficulty(d.id)}
                      disabled={isRunning}
                      className={cn(
                        'flex-1 py-2 rounded-xl text-[9px] font-black uppercase tracking-[0.15em] transition-all border',
                        difficulty === d.id
                          ? `nm-inset bg-slate-950 ${d.color} border-slate-700`
                          : 'nm-flat bg-slate-900 text-slate-500 border-transparent hover:border-slate-700',
                        isRunning && 'opacity-50 cursor-not-allowed'
                      )}
                    >
                      {d.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Launch / Stop Button */}
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

              {/* Summary info */}
              <div className="nm-inset rounded-2xl bg-slate-950 p-4 space-y-2">
                <div className="flex justify-between text-[9px] font-black text-slate-500 uppercase tracking-widest">
                  <span>Attack Vector</span>
                  <span className="text-white">{SIMULATION_TYPES.find(t => t.id === selectedType)?.name || selectedType}</span>
                </div>
                <div className="flex justify-between text-[9px] font-black text-slate-500 uppercase tracking-widest">
                  <span>Difficulty</span>
                  <span className={DIFFICULTIES.find(d => d.id === difficulty)?.color || 'text-white'}>{difficulty.toUpperCase()}</span>
                </div>
                <div className="flex justify-between text-[9px] font-black text-slate-500 uppercase tracking-widest">
                  <span>Duration</span>
                  <span className="text-white">{duration}s</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Running State Indicator */}
      <AnimatePresence>
        {isRunning && (
          <Motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
          >
            <BattleStationAnimation intensity={intensity} type={selectedType} />
          </Motion.div>
        )}

        {/* Completed Report */}
        {report && !isRunning && (
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
                    <p className="text-xs text-slate-500 font-mono uppercase mt-1 tracking-widest">Simulation_Log_{report.status?.toUpperCase()}</p>
                  </div>
                </div>
                <div className="flex items-center gap-6 nm-inset p-6 rounded-3xl bg-slate-950/50">
                  <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]">Resilience_IDX</span>
                  <span className={cn('text-4xl font-black font-mono drop-shadow-md',
                    report.score >= 80 ? 'text-emerald-500' : report.score >= 50 ? 'text-amber-500' : 'text-red-500'
                  )}>{report.score}</span>
                </div>
              </div>

              {/* Evaluation Breakdown */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
                {[
                  { label: 'Detection', value: report.detection_score, max: 40 },
                  { label: 'Decision', value: report.decision_score, max: 30 },
                  { label: 'Time', value: report.time_score, max: 30 },
                  { label: 'Verdict', value: report.verdict?.toUpperCase(), isText: true },
                ].map((item, i) => (
                  <div key={i} className="nm-inset rounded-2xl bg-slate-950 p-4 text-center">
                    <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2">{item.label}</p>
                    <p className={cn(
                      'text-xl font-black font-mono',
                      item.isText
                        ? item.value === 'EFFECTIVE' ? 'text-emerald-500' : item.value === 'PARTIAL' ? 'text-amber-500' : 'text-red-500'
                        : 'text-white'
                    )}>
                      {item.isText ? item.value : `${item.value}/${item.max}`}
                    </p>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                <div className="space-y-6">
                  <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-3">
                    <AlertTriangle className="h-4 w-4 text-amber-500" />
                    Anomaly telemetry
                  </h4>
                  <div className="space-y-3">
                    {report.anomalies_detected?.length > 0 ? (
                      report.anomalies_detected.map((a, i) => (
                        <div key={i} className="text-[11px] font-mono p-4 rounded-xl nm-inset bg-slate-950 text-slate-400 border border-slate-900 leading-relaxed group">
                           <span className="text-amber-500 mr-2 opacity-50 font-bold group-hover:opacity-100 transition-opacity">{">>>"}</span>
                           {typeof a === 'string' ? a : a.message || JSON.stringify(a)}
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
                    {report.response_actions?.length > 0 ? (
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

              {/* Attack Plan (Red Team) */}
              {report.attack_plan && (
                <div className="mt-10 pt-10 border-t border-slate-800">
                  <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-3 mb-6">
                    <Swords className="h-4 w-4 text-red-400" />
                    Red Team Attack Plan
                  </h4>
                  <div className="nm-inset rounded-2xl bg-slate-950 p-6">
                    <p className="text-xs font-mono text-slate-400">
                      Strategy: <span className="text-red-400 font-black">{report.attack_plan.strategy || 'auto'}</span>
                      {report.attack_plan.multi_vector && <span className="ml-4 text-amber-500"> | Multi-Vector</span>}
                    </p>
                  </div>
                </div>
              )}

              {/* Feedback (Blue Team) */}
              {report.feedback && Object.keys(report.feedback).length > 0 && (
                <div className="mt-6 pt-6 border-t border-slate-800">
                  <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-3 mb-6">
                    <Shield className="h-4 w-4 text-blue-400" />
                    Blue Team Feedback
                  </h4>
                  <div className="nm-inset rounded-2xl bg-slate-950 p-6">
                    <p className="text-xs font-mono text-slate-400">
                      {report.feedback.recommendation || report.feedback.message || 'Feedback recorded for learning loop.'}
                    </p>
                  </div>
                </div>
              )}

              {/* Timeline */}
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

      {/* Simulation History */}
      <Card
        title="Mission Archive"
        description="Historical simulation records"
        icon={History}
      >
        <div className="mt-6">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="text-[10px] font-black text-accent-blue uppercase tracking-[0.2em] hover:text-white transition-colors"
          >
            {showHistory ? 'COLLAPSE_ARCHIVE' : `EXPAND_ARCHIVE (${history.length} Records)`}
          </button>

          <AnimatePresence>
            {showHistory && (
              <Motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="space-y-4 mt-6">
                  {history.length > 0 ? (
                    history.slice(0, 10).map((h, idx) => (
                      <div key={idx} className="flex items-center justify-between nm-flat bg-slate-900 rounded-2xl p-5 border border-slate-800 hover:nm-convex transition-all">
                        <div className="flex items-center gap-4">
                          <div className={cn(
                            'nm-inset p-2 rounded-xl bg-slate-950',
                            h.status === 'completed' ? 'text-emerald-500' : 'text-red-500'
                          )}>
                            <Target className="h-4 w-4" />
                          </div>
                          <div>
                            <p className="text-xs font-black text-white uppercase tracking-tight">
                              {h.simulation_type?.replace(/_/g, ' ')}
                            </p>
                            <p className="text-[9px] text-slate-500 font-mono mt-1">
                              {h.simulation_id?.slice(0, 8)}... | {h.status?.toUpperCase()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className={cn(
                            'text-lg font-black font-mono',
                            h.score >= 80 ? 'text-emerald-500' : h.score >= 50 ? 'text-amber-500' : 'text-red-500'
                          )}>
                            {h.score}
                          </span>
                          <span className={cn(
                            'text-[8px] font-black uppercase tracking-widest nm-inset px-2 py-1 rounded-lg bg-slate-950',
                            h.verdict === 'effective' ? 'text-emerald-500' : h.verdict === 'partial' ? 'text-amber-500' : 'text-red-500'
                          )}>
                            {h.verdict}
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-[11px] text-slate-500 italic font-mono uppercase tracking-widest text-center py-8 bg-slate-950/30 rounded-xl border border-dashed border-slate-800">
                      No historical records. Execute a simulation to begin.
                    </p>
                  )}
                </div>
              </Motion.div>
            )}
          </AnimatePresence>
        </div>
      </Card>

      {/* Determinisitc Audit Log DVR */}
      <Card
        title="Autonomy Audit Trail"
        description="Deterministic decision replayer"
        icon={Shield}
      >
        <div className="mt-6">
          <button
            onClick={() => {
              setShowAudit(!showAudit);
              fetchAudit();
            }}
            className="text-[10px] font-black text-emerald-500 uppercase tracking-[0.2em] hover:text-white transition-colors"
          >
            {showAudit ? 'HIDE_AUDIT_LOG' : `SHOW_AUDIT_LOG (${auditLogs.length} Ticks)`}
          </button>
          
          <AnimatePresence>
            {showAudit && (
              <Motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden mt-6"
              >
                <div className="space-y-4 max-h-[500px] overflow-y-auto scrollbar-thin pr-2">
                  {auditLogs.length > 0 ? (
                    [...auditLogs].reverse().map((log, idx) => (
                      <div key={idx} className="nm-flat bg-slate-900 rounded-2xl p-5 border border-slate-800 flex justify-between gap-4">
                        <div>
                          <div className="flex gap-4 items-center">
                            <span className="text-[10px] nm-inset bg-slate-950 px-2 py-1 rounded text-slate-500 font-mono">
                              {new Date(log.timestamp * 1000).toLocaleTimeString()}
                            </span>
                            <span className="text-xs font-black uppercase tracking-widest text-emerald-500 text-shadow-[0_0_5px_rgba(16,185,129,0.5)]">
                              {log.decision?.action || 'NO_ACTION'}
                            </span>
                          </div>
                          {log.decision?.target && (
                            <p className="mt-2 text-xs text-slate-400 font-mono">
                              TARGET: {log.decision.target}
                            </p>
                          )}
                        </div>
                        <div className="text-right">
                          <p className="text-[9px] text-slate-500 font-black uppercase tracking-[0.2em]">Sys_State</p>
                          <p className="text-xs font-mono text-slate-400 mt-1">CPU: {log.state_snapshot?.cpu?.toFixed(0)}% | THREAT: {log.state_snapshot?.threat}</p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-[11px] text-slate-500 italic font-mono uppercase tracking-widest text-center py-8 bg-slate-950/30 rounded-xl border border-dashed border-slate-800">
                      No deterministic ticks logged from the Orchestrator loop.
                    </p>
                  )}
                </div>
              </Motion.div>
            )}
          </AnimatePresence>
        </div>
      </Card>
    </div>
  );
}
