import React, { useState, useEffect } from 'react';
import { optimizerApi, systemApi } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { 
  Zap, 
  Gamepad2, 
  Battery, 
  Cpu,
  Monitor,
  CheckCircle2,
  AlertTriangle,
  Info,
  ChevronRight,
  Eye,
  Shield,
  X,
  Target,
  Sparkles,
  Undo2,
  RefreshCcw,
  ZapOff,
  Activity
} from 'lucide-react';
import { motion as Motion, AnimatePresence } from 'framer-motion';
import { cn } from '../utils/cn';

export function Tweaks() {
  const [executing, setExecuting] = useState({});
  const [previewing, setPreviewing] = useState({});
  const [preview, setPreview] = useState(null);
  const [status, setStatus] = useState(null);
  const [suggestion, setSuggestion] = useState(null);
  const [lastActionId, setLastActionId] = useState(null);
  const [reverting, setReverting] = useState(false);

  const tweaks = [
    { 
      id: 'gaming_boost', 
      name: 'Combat Mode', 
      description: 'Maximum performance protocol. Boosts foreground app priority and locks ultimate power vectors.', 
      icon: Gamepad2, 
      color: 'text-purple-400', 
      impact: 'HIGH_STRESS',
      type: 'PERFORMANCE',
      actions: [
        'PURGE: Non-essential background services',
        'OVERRIDE: Power vector High Performance',
        'ESCALE: Foreground process to HIGH priority',
        'STARVE: Background thread resource allocation',
      ],
      details: "Aggressively redirects all system resources to your active task. Perfect for gaming, rendering, or heavy compilation. Note: May cause higher temperatures and battery drain."
    },
    { 
      id: 'battery_saver', 
      name: 'Stealth Mode', 
      description: 'Efficiency protocol. Hibernates background sync and engages ultra-low power states.', 
      icon: Battery, 
      color: 'text-emerald-400', 
      impact: 'MODERATE',
      type: 'ECONOMY',
      actions: [
        'HIBERNATE: Background sync protocols',
        'OVERRIDE: Power vector Ultra Efficiency',
        'THROTTLE: Windows Update & background services',
        'DOWNCLOCK: Non-active processing threads',
      ],
      details: "Maximizes operational longevity by quieting the system. Ideal for travel or low-power situations. Some notifications may be delayed."
    },
    { 
      id: 'performance_boost', 
      name: 'Neural Sync', 
      description: 'Intelligent real-time optimization. Throttles runaway processes and protects stability.', 
      icon: Zap, 
      color: 'text-amber-400', 
      impact: 'MODERATE',
      type: 'STABILITY',
      actions: [
        'ANALYSIS: Real-time telemetry monitoring',
        'THROTTLE: Runaway background resource hogs',
        'SHIELD: Critical system kernel nodes',
        'BALANCE: Dynamic task redistribution',
      ],
      details: "A smart balancing act that keeps the system smooth during heavy multitasking. Uses pattern matching to identify and normalize anomalous resource spikes."
    },
    { 
      id: 'clean_ram', 
      name: 'Memory Flush', 
      description: 'Deep sector memory recovery. Clears standby caches and inactive segments.', 
      icon: Cpu, 
      color: 'text-accent-blue', 
      impact: 'LOW_RISK',
      type: 'RESOURCES',
      actions: [
        'PURGE: Flush inactive WorkingSet segments',
        'RECLAIM: Clear Windows Standby memory list',
        'DEFRAGMENT: Sector-level memory recovery',
        'FLUSH: System file cache optimization',
      ],
      details: "Refreshes the system by forcing applications to release held memory that isn't actively being used. Great for 'unjamming' a sluggish OS."
    },
  ];

  useEffect(() => {
    fetchSuggestion();
  }, []);

  const resolveResult = (payload) => payload?.result || payload || {};

  const mapPreviewData = (tweak, result) => {
    const effects = result.effects || {};
    const raw = effects.raw || {};
    return {
      tweakId: tweak.id,
      tweakName: tweak.name,
      result,
      details: effects.details || raw.details || tweak.actions,
      dryRun: result.simulated ?? result.dry_run ?? true,
      summary: result.summary,
      processesAffected:
        effects.targets ||
        raw.processes_killed ||
        raw.processes_suspended ||
        raw.processes_lowered ||
        raw.processes_cleaned ||
        [],
      powerPlan: effects.power_plan ?? raw.power_plan,
      memoryBefore: raw.memory_before_percent,
      memoryAfter: raw.memory_after_percent,
      freedMb: effects.memory_freed ?? raw.freed_mb,
      guard: result.meta?.guard || null,
    };
  };

  const fetchSuggestion = async () => {
    try {
      const response = await optimizerApi.suggestTweak();
      if (response.data && response.data.recommended) {
        setSuggestion(response.data);
      }
    } catch (err) {
      console.error("Suggestion link failure", err);
    }
  };

  const handlePreview = async (tweak) => {
    setPreviewing(prev => ({ ...prev, [tweak.id]: true }));
    setStatus(null);
    try {
      const response = await optimizerApi.executeTweak(tweak.id, { dryRun: true });
      const res = resolveResult(response.data);
      setPreview(mapPreviewData(tweak, res));
    } catch (err) {
      setStatus({ 
        type: 'error', 
        message: `LINK FAILURE: Could not retrieve telemetric preview.` 
      });
    } finally {
      setPreviewing(prev => ({ ...prev, [tweak.id]: false }));
    }
  };

  const handleExecute = async (tweak, options = {}) => {
    const { confirmHighRisk = false } = options;
    setExecuting(prev => ({ ...prev, [tweak.id]: true }));
    setStatus(null);
    setPreview(null);
    try {
      const response = await optimizerApi.executeTweak(tweak.id, { dryRun: false, confirmHighRisk });
      const data = response.data;
      const res = resolveResult(data);
      
      if (res.status === 'failed' || res.status === 'error') {
        setStatus({ type: 'error', message: res.message || 'PROTOCOL_REJECTED: Target node denied deployment.' });
        return;
      }

      if (res.status === 'blocked') {
        const reasons = res.meta?.guard?.reasons || [];
        if (reasons.includes('high_risk_unconfirmed') && !confirmHighRisk) {
          const approved = window.confirm(
            'High-risk execution requires explicit confirmation. Proceed with Combat Mode?'
          );
          if (approved) {
            await handleExecute(tweak, { confirmHighRisk: true });
            return;
          }
        }
        setStatus({
          type: 'warning',
          message: res.summary || res.message || 'EXECUTION BLOCKED BY SAFETY GUARD.',
        });
        return;
      }

      const warnings = res.meta?.guard?.warnings || [];
      const msg = res.summary || res.message || `PROTOCOL EXECUTED: ${tweak.name} successfully deployed.`;
      const statusType = res.status === 'partial' ? 'warning' : 'success';
      setStatus({
        type: statusType,
        message: warnings.length ? `${msg} | WARN: ${warnings[0]}` : msg,
      });
      if (data.action_id) {
        setLastActionId(data.action_id);
      }
    } catch (err) {
      const errorMsg = err.response?.data?.message || err.message || 'EXECUTION_ERROR: Protocol failed to deploy to target nodes.';
      setStatus({ 
        type: 'error', 
        message: errorMsg
      });
      console.error(err);
    } finally {
      setExecuting(prev => ({ ...prev, [tweak.id]: false }));
    }
  };

  const handleUndo = async () => {
    if (!lastActionId) return;
    setReverting(true);
    try {
      const response = await optimizerApi.revertAction(lastActionId);
      const res = resolveResult(response.data);
      const msg = res.summary || res.message || 'PROTOCOL REVERTED: System states restored.';
      setStatus({ type: 'success', message: msg });
      setLastActionId(null);
    } catch (err) {
      setStatus({ type: 'error', message: 'REVERSION_ERROR: Failed to undo protocol changes.' });
    } finally {
      setReverting(false);
    }
  };

  return (
    <div className="space-y-10 pb-20">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic">System Tweaks</h1>
          <p className="mt-2 text-slate-400 font-mono text-sm tracking-widest uppercase opacity-70">Parameter Overrides // Neural Optimization Matrix</p>
        </div>
        {lastActionId && (
          <Button 
            onClick={handleUndo} 
            isLoading={reverting}
            variant="outline"
            className="nm-flat bg-slate-900 border-yellow-500/30 text-yellow-500 hover:bg-yellow-500/10 px-6 h-12 uppercase font-black italic tracking-widest text-[10px]"
          >
            <Undo2 className="mr-2 h-4 w-4" /> Undo Last Protocol
          </Button>
        )}
      </header>

      {/* Smart Suggestion Banner */}
      <AnimatePresence>
        {suggestion && (
          <Motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="nm-flat bg-indigo-950/20 border border-indigo-500/30 rounded-[2rem] p-8 relative overflow-hidden group mb-10"
          >
            <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
              <Zap className="h-20 w-20 text-indigo-400" />
            </div>
            <div className="flex flex-col md:flex-row items-center gap-8 relative z-10">
              <div className="nm-inset p-5 rounded-2xl bg-indigo-950/40">
                <Sparkles className="h-8 w-8 text-indigo-400" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <h3 className="text-xl font-black text-indigo-400 uppercase italic">Intelligence Recommendation</h3>
                  <span className="bg-indigo-500/20 text-indigo-400 text-[10px] px-2 py-0.5 rounded-full font-bold border border-indigo-500/30 font-mono">
                    CONFIDENCE: {(suggestion.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-slate-300 mt-2 font-mono text-sm uppercase leading-relaxed opacity-80 italic">
                  {suggestion.reason}
                </p>
                {suggestion.decision && (
                  <p className="text-[10px] mt-2 text-indigo-300/80 font-mono uppercase tracking-widest">
                    Engine: {suggestion.decision.engine} | Auto-Trigger Candidate: {String(suggestion.decision.auto_trigger_candidate)}
                  </p>
                )}
              </div>
              <Button 
                onClick={() => {
                  const candidate = tweaks.find(t => t.id === suggestion.recommended);
                  if (candidate) handleExecute(candidate);
                }}
                className="nm-convex bg-indigo-600 border-none text-white px-8 h-12 uppercase font-black italic tracking-widest text-[10px]"
              >
                DEPLOY RECOMMENDED
              </Button>
              <button onClick={() => setSuggestion(null)} className="text-slate-500 hover:text-slate-300 p-2">
                <X className="h-5 w-5" />
              </button>
            </div>
          </Motion.div>
        )}
      </AnimatePresence>

      {status && (
        <Motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn(
            "flex items-center gap-6 rounded-3xl p-8 font-black uppercase tracking-[0.2em] italic",
            status.type === 'success'
              ? 'nm-flat bg-emerald-950/20 text-emerald-400 border border-emerald-900/30 font-mono'
              : status.type === 'warning'
                ? 'nm-flat bg-amber-950/20 text-amber-400 border border-amber-900/30 font-mono'
                : 'nm-flat bg-red-950/20 text-red-400 border border-red-900/30 font-mono'
          )}
        >
          {status.type === 'success' ? <CheckCircle2 className="h-8 w-8" /> : <AlertTriangle className="h-8 w-8" />}
          <p className="text-lg">{status.message}</p>
        </Motion.div>
      )}

      {/* Preview Modal */}
      <AnimatePresence>
        {preview && (
          <Motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm"
          >
            <Motion.div className="rounded-[2.5rem] nm-flat bg-slate-900 border border-accent-blue/40 p-10 shadow-[0_0_80px_rgba(59,130,246,0.25)] relative overflow-hidden max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="absolute top-0 left-0 w-2 bg-accent-blue h-full opacity-50 shadow-[0_0_15px_#3b82f6]" />
              <div className="flex items-center justify-between mb-10">
                <div className="flex items-center gap-6">
                  <div className="nm-inset p-4 rounded-2xl bg-slate-950">
                    <Eye className="h-8 w-8 text-accent-blue shadow-[0_0_15px_#3b82f6]" />
                  </div>
                  <div>
                    <h3 className="text-3xl font-black text-white uppercase italic tracking-tighter">
                      Telemetric_Preview: {preview.tweakName}
                    </h3>
                    <p className="text-[11px] font-black text-accent-blue uppercase font-mono tracking-[0.3em] mt-1">
                      {preview.dryRun ? '>> SIMULATION_ONLY -- NO_STATE_CHANGE' : '>> LIVE_DEPLOYMENT_FEEDBACK'}
                    </p>
                  </div>
                </div>
                <button 
                  onClick={() => setPreview(null)} 
                  className="nm-flat p-3 rounded-xl bg-slate-800 text-slate-400 hover:text-white transition-all hover:nm-inset"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              {preview.summary && (
                <div className="mb-10 p-6 nm-inset bg-slate-950/50 rounded-2xl border border-slate-800/50">
                   <p className="text-lg text-white font-mono uppercase italic tracking-wider leading-relaxed">
                     <RefreshCcw className="inline mr-3 h-5 w-5 text-accent-blue animate-spin-slow" />
                     {preview.summary}
                   </p>
                </div>
              )}
              {preview.guard?.warnings?.length > 0 && (
                <div className="mb-8 p-4 rounded-2xl border border-amber-500/30 bg-amber-500/10">
                  <p className="text-amber-300 font-mono text-xs uppercase tracking-wider">
                    Guard Notice: {preview.guard.warnings[0]}
                  </p>
                </div>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                <div className="space-y-8">
                  <div className="space-y-4">
                    <h4 className="text-[11px] font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2">
                       <Target className="h-4 w-4" /> Protocol Vectors
                    </h4>
                    <ul className="space-y-3">
                      {(preview.details || []).map((detail, idx) => (
                        <li key={idx} className="flex items-start gap-4 text-[11px] font-mono p-4 rounded-xl nm-inset bg-slate-950 border border-slate-900 leading-relaxed text-slate-400 italic group">
                          <span className="text-accent-blue group-hover:shadow-[0_0_5px_#3b82f6]">#</span> {detail}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {preview.powerPlan && (
                    <div className="space-y-4">
                       <h4 className="text-[11px] font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2">
                         <ZapOff className="h-4 w-4" /> Power State Override
                       </h4>
                       <div className="p-4 rounded-xl nm-inset bg-indigo-950/20 border border-indigo-500/20 text-indigo-400 font-black text-xs uppercase tracking-widest italic">
                         {preview.powerPlan}
                       </div>
                    </div>
                  )}
                </div>

                <div className="space-y-8">
                  {preview.processesAffected.length > 0 && (
                    <div className="space-y-4">
                      <h4 className="text-[11px] font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2">
                         <Cpu className="h-4 w-4" /> Targets_Acquired
                      </h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[250px] overflow-y-auto pr-2 custom-scrollbar">
                        {preview.processesAffected.map((p, idx) => (
                          <div key={idx} className="flex items-center justify-between bg-slate-950/50 rounded-xl px-4 py-3 nm-inset border border-slate-900 group">
                            <span className="font-black text-[10px] text-white uppercase truncate">{p.name}</span>
                            <span className="text-[9px] font-bold text-slate-600 font-mono">ID_{p.pid}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {preview.memoryBefore !== undefined && (
                    <div className="space-y-4">
                      <h4 className="text-[11px] font-black text-slate-500 uppercase tracking-[0.3em] flex items-center gap-2">
                         <Activity className="h-4 w-4" /> RAM Consumption Evolution
                      </h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="nm-inset p-4 rounded-xl bg-slate-950 text-center">
                          <div className="text-[10px] text-slate-500 uppercase mb-1">Before</div>
                          <div className="text-xl font-black text-white italic">{preview.memoryBefore}%</div>
                        </div>
                        <div className="nm-inset p-4 rounded-xl bg-slate-950 text-center border border-emerald-500/20">
                          <div className="text-[10px] text-emerald-500 uppercase mb-1">After</div>
                          <div className="text-xl font-black text-emerald-400 italic">{preview.memoryAfter}%</div>
                        </div>
                      </div>
                      {preview.freedMb > 0 && (
                        <div className="text-center font-black text-[10px] text-emerald-400 uppercase tracking-[0.4em] bg-emerald-500/10 py-2 rounded-lg border border-emerald-500/20">
                          TOTAL_RECOVERED: {preview.freedMb} MB
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
              <div className="mt-12 flex justify-end gap-6">
                 <button 
                  onClick={() => setPreview(null)}
                  className="px-10 h-14 uppercase tracking-[0.3em] font-black italic text-slate-500 hover:text-white transition-colors"
                 >
                    CANCEL
                 </button>
                 <Button onClick={() => handleExecute(tweaks.find(t => t.id === preview.tweakId))} className="nm-convex bg-slate-900 border-none text-white px-10 h-14 uppercase tracking-[0.3em] font-black italic shadow-[0_0_20px_rgba(59,130,246,0.3)]">
                    AUTHORIZE_DEPLOYMENT
                 </Button>
              </div>
            </Motion.div>
          </Motion.div>
        )}
      </AnimatePresence>

      <div className="grid grid-cols-1 gap-10 lg:grid-cols-2">
        {tweaks.map((tweak) => (
          <div key={tweak.id} className="nm-flat bg-slate-900 rounded-[2.5rem] p-10 border border-slate-800 hover:nm-convex transition-all duration-500 group relative overflow-hidden flex flex-col">
            <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity pointer-events-none">
               <tweak.icon className="h-48 w-48" />
            </div>
            <div className="relative z-10 flex flex-col h-full">
              <div className="flex items-start justify-between mb-8">
                <div className="flex items-center gap-6">
                  <div className={cn("nm-inset p-5 rounded-[1.5rem] bg-slate-950 transition-transform duration-500 group-hover:scale-110")}>
                    <tweak.icon className={cn('h-10 w-10', tweak.color)} />
                  </div>
                  <div>
                    <h3 className="text-2xl font-black text-white uppercase italic tracking-tighter">{tweak.name}</h3>
                    <div className="flex gap-3 mt-3">
                      <span className="text-[9px] font-black uppercase tracking-widest px-3 py-1 rounded-full bg-slate-950 text-slate-500 nm-inset border border-slate-800">
                        {tweak.type}
                      </span>
                      <span className={cn('text-[9px] font-black uppercase tracking-widest px-3 py-1 rounded-full nm-inset border-none shadow-[0_0_10px_currentColor]',
                        tweak.impact === 'HIGH_STRESS' ? 'text-red-500' : 
                        tweak.impact === 'MODERATE' ? 'text-amber-400' :
                        tweak.impact === 'LOW_RISK' ? 'text-emerald-400' : 'text-accent-blue'
                      )}>
                        IMPACT: {tweak.impact}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <p className="text-slate-400 leading-relaxed font-mono uppercase text-xs opacity-80 mb-6 grow">
                {tweak.description}
              </p>

              <div className="mb-8 space-y-3">
                {tweak.actions.map((action, idx) => (
                  <div key={idx} className="flex items-center gap-4 text-[10px] font-black text-slate-600 uppercase tracking-widest group-hover:text-slate-400 transition-colors">
                    <span className="h-1.5 w-1.5 rounded-full bg-accent-blue group-hover:shadow-[0_0_5px_#3b82f6]" />
                    {action}
                  </div>
                ))}
              </div>

              {/* Expanded details on hover or hidden by default */}
              <div className="mt-auto pt-8 border-t border-slate-800/50 flex flex-col gap-6">
                <div className="text-[10px] text-slate-500 italic font-mono leading-relaxed opacity-0 group-hover:opacity-100 transition-opacity duration-500 h-0 group-hover:h-auto overflow-hidden">
                   {tweak.details}
                </div>
                
                <div className="flex items-center justify-between gap-6">
                  <Button 
                    size="md"
                    variant="outline"
                    onClick={() => handlePreview(tweak)} 
                    isLoading={previewing[tweak.id]}
                    className="px-8 h-12 nm-flat bg-slate-900 border-none rounded-xl text-[10px] font-black uppercase tracking-[0.2em] hover:text-white"
                  >
                    <Eye className="mr-3 h-4 w-4" />
                    PREVIEW
                  </Button>
                  <Button 
                    onClick={() => handleExecute(tweak)} 
                    isLoading={executing[tweak.id]}
                    className="flex-1 h-14 nm-convex bg-slate-900 border-none rounded-xl text-[10px] font-black uppercase tracking-[0.3em] font-mono text-white shadow-[0_0_20px_rgba(59,130,246,0.1)]"
                  >
                    EXECUTE PROTOCOL <ChevronRight className="ml-3 h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="nm-flat bg-slate-900 border border-slate-800 rounded-[3rem] p-10 relative overflow-hidden group">
        <div className="absolute top-0 right-0 p-10 opacity-5 group-hover:opacity-10 transition-opacity">
           <Sparkles className="h-40 w-40 text-accent-blue" />
        </div>
        <div className="relative z-10 flex flex-col md:flex-row items-center gap-10">
          <div className="nm-inset p-8 rounded-[2rem] bg-slate-950 backdrop-blur-md">
            <Monitor className="h-16 w-16 text-accent-blue drop-shadow-[0_0_15px_#3b82f6]" />
          </div>
          <div>
            <h3 className="text-3xl font-black text-white uppercase italic tracking-tighter">Smart Engine Neural Matrix</h3>
            <p className="mt-4 text-slate-400 font-mono text-sm uppercase tracking-widest max-w-2xl leading-relaxed opacity-70 italic">
              The JOC Neural Engine uses cross-vector telemetry and pattern matching to derive optimal system states. Suggestions are calculated based on CPU bottlenecks, memory pressure, and battery cycle health.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
