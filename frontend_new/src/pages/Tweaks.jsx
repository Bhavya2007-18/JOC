import React, { useState } from 'react';
import { optimizerApi } from '../api/client';
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
  Sparkles
} from 'lucide-react';
import { motion as Motion, AnimatePresence } from 'framer-motion';
import { cn } from '../utils/cn';

export function Tweaks() {
  const [executing, setExecuting] = useState({});
  const [previewing, setPreviewing] = useState({});
  const [preview, setPreview] = useState(null);
  const [status, setStatus] = useState(null);

  const tweaks = [
    { 
      id: 'gaming_boost', 
      name: 'Combat Mode', 
      description: 'Purge background services (OneDrive, Search, Edge, Teams) and lock power vectors to maximum performance.', 
      icon: Gamepad2, 
      color: 'text-purple-400', 
      impact: 'HIGH_STRESS',
      type: 'PERFORMANCE',
      actions: [
        'PURGE: Non-essential background services',
        'OVERRIDE: Power vector High Performance',
        'PRIORITY: Foreground focus escalation',
      ]
    },
    { 
      id: 'battery_saver', 
      name: 'Stealth Mode', 
      description: 'Hibernate heavy background protocols and engage ultra-efficiency power state.', 
      icon: Battery, 
      color: 'text-emerald-400', 
      impact: 'MODERATE',
      type: 'ECONOMY',
      actions: [
        'RESTRICT: High-drain background sync',
        'OVERRIDE: Power vector Ultra Efficiency',
        'FREQ: Downclock non-active threads',
      ]
    },
    { 
      id: 'performance_boost', 
      name: 'Neural Sync', 
      description: 'Dynamic reprioritization of system resources based on active process telemetry.', 
      icon: Zap, 
      color: 'text-amber-400', 
      impact: 'MODERATE',
      type: 'STABILITY',
      actions: [
        'ANALYSIS: Identifying CPU-heavy vectors',
        'ISOLATE: Shielding critical system nodes',
        'FLOW: Optimizing task distribution',
      ]
    },
    { 
      id: 'clean_ram', 
      name: 'Memory Flush', 
      description: 'Deep sector purge of inactive memory segments using advanced Windows Memory APIs.', 
      icon: Cpu, 
      color: 'text-accent-blue', 
      impact: 'LOW_RISK',
      type: 'RESOURCES',
      actions: [
        'PURGE: Flush WorkingSet segments',
        'PROTECT: Bypass kernel-reserved nodes',
        'RECOVERY: Immediate capacity expansion',
      ]
    },
  ];

  const handlePreview = async (tweak) => {
    setPreviewing(prev => ({ ...prev, [tweak.id]: true }));
    setStatus(null);
    try {
      const response = await optimizerApi.executeTweak(tweak.id);
      const data = response.data;
      setPreview({
        tweakId: tweak.id,
        tweakName: tweak.name,
        result: data.result || data,
        details: data.result?.details || tweak.actions,
        dryRun: data.result?.dry_run ?? true,
        processesAffected: data.result?.processes_killed || data.result?.processes_suspended || data.result?.processes_lowered || [],
      });
    } catch (err) {
      setStatus({ 
        type: 'error', 
        message: `LINK FAILURE: Could not retrieve telemetric preview.` 
      });
    } finally {
      setPreviewing(prev => ({ ...prev, [tweak.id]: false }));
    }
  };

  const handleExecute = async (tweak) => {
    setExecuting(prev => ({ ...prev, [tweak.id]: true }));
    setStatus(null);
    setPreview(null);
    try {
      const response = await optimizerApi.executeTweak(tweak.id);
      const data = response.data;
      const msg = data.result?.message || data.message || `PROTOCOL EXECUTED: ${tweak.name} successfully deployed.`;
      setStatus({ type: 'success', message: msg });
    } catch (err) {
      setStatus({ 
        type: 'error', 
        message: `EXECUTION_ERROR: Protocol failed to deploy to target nodes.` 
      });
      console.error(err);
    } finally {
      setExecuting(prev => ({ ...prev, [tweak.id]: false }));
    }
  };

  return (
    <div className="space-y-10 pb-20">
      <header>
        <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic">System Tweaks</h1>
        <p className="mt-2 text-slate-400 font-mono text-sm tracking-widest uppercase opacity-70">Parameter Overrides // Neural Optimization Matrix</p>
      </header>

      {status && (
        <Motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn(
            "flex items-center gap-6 rounded-3xl p-8 font-black uppercase tracking-[0.2em] italic",
            status.type === 'success' ? 'nm-flat bg-emerald-950/20 text-emerald-400 border border-emerald-900/30 font-mono' : 'nm-flat bg-red-950/20 text-red-400 border border-red-900/30 font-mono'
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
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="rounded-[2.5rem] nm-flat bg-slate-900 border border-accent-blue/40 p-8 shadow-[0_0_50px_rgba(59,130,246,0.15)] relative overflow-hidden"
          >
            <div className="absolute top-0 left-0 w-2 bg-accent-blue h-full opacity-50 shadow-[0_0_15px_#3b82f6]" />
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-6">
                <div className="nm-inset p-4 rounded-2xl bg-slate-950">
                  <Eye className="h-6 w-6 text-accent-blue" />
                </div>
                <div>
                  <h3 className="text-2xl font-black text-white uppercase italic tracking-tighter">
                    Telemetric_Preview: {preview.tweakName}
                  </h3>
                  <p className="text-[10px] font-black text-accent-blue uppercase font-mono tracking-[0.3em] mt-1">
                    {preview.dryRun ? '>> SIMULATION_ONLY -- NO_STATE_CHANGE' : '>> LIVE_DEPLOYMENT_FEEDBACK'}
                  </p>
                </div>
              </div>
              <button 
                onClick={() => setPreview(null)} 
                className="nm-flat p-3 rounded-xl bg-slate-800 text-slate-400 hover:text-white transition-all hover:nm-inset"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
              <div className="space-y-6">
                <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                   <Target className="h-3 w-3" /> Predicted Impact
                </h4>
                <ul className="space-y-3">
                  {(preview.details || []).map((detail, idx) => (
                    <li key={idx} className="flex items-start gap-4 text-[11px] font-mono p-4 rounded-xl nm-inset bg-slate-950 border border-slate-900 leading-relaxed text-slate-400 italic">
                      <span className="text-accent-blue">#</span> {detail}
                    </li>
                  ))}
                </ul>
              </div>
              {preview.processesAffected.length > 0 && (
                <div className="space-y-6">
                  <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                     <Cpu className="h-3 w-3" /> Targets_Acquired
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {preview.processesAffected.map((p, idx) => (
                      <div key={idx} className="flex items-center justify-between bg-slate-950/50 rounded-xl px-4 py-3 nm-inset border border-slate-900 group">
                        <span className="font-black text-[10px] text-white uppercase truncate">{p.name}</span>
                        <span className="text-[9px] font-bold text-slate-600 font-mono">ID_{p.pid}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <div className="mt-10 flex justify-end">
               <Button onClick={() => handleExecute(tweaks.find(t => t.id === preview.tweakId))} className="nm-convex bg-slate-900 border-none text-white px-10 h-14 uppercase tracking-[0.3em] font-black italic">
                  AUTHORIZE_DEPLOYMENT
               </Button>
            </div>
          </Motion.div>
        )}
      </AnimatePresence>

      <div className="grid grid-cols-1 gap-10 lg:grid-cols-2">
        {tweaks.map((tweak) => (
          <div key={tweak.id} className="nm-flat bg-slate-900 rounded-[2.5rem] p-10 border border-slate-800 hover:nm-convex transition-all duration-500 group relative overflow-hidden">
            <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
               <tweak.icon className="h-40 w-40" />
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
                        tweak.impact === 'HIGH_STRESS' ? 'text-red-500' : 'text-accent-blue'
                      )}>
                        IMPACT: {tweak.impact}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <p className="text-slate-400 leading-relaxed font-mono uppercase text-xs opacity-80 mb-8 grow">
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

              <div className="pt-8 border-t border-slate-800/50 flex items-center justify-between gap-6">
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
              JOC Engine telemetric analysis detected localized hardware clusters. Suggestions are derived from pattern-matching against 144 nodes of successful optimization states.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
