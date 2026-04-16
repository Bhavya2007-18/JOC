import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  BrainCircuit, 
  Activity, 
  Zap, 
  Database, 
  Terminal as TerminalIcon, 
  Cpu, 
  HardDrive, 
  Layers,
  History,
  TrendingUp,
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';
import { cn } from '../utils/cn';
import { intelligenceApi } from '../api/client';

const POLL_INTERVAL = 5000;

export function Cognition() {
  const [pattern, setPattern] = useState(null);
  const [learning, setLearning] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const eventEndRef = useRef(null);

  useEffect(() => {
    let mounted = true;
    const fetchData = async () => {
      try {
        const [patRes, learnRes, etwRes] = await Promise.all([
          intelligenceApi.getPattern(),
          intelligenceApi.getLearning(),
          intelligenceApi.getETW()
        ]);

        if (!mounted) return;

        if (patRes?.data) setPattern(patRes.data);
        if (learnRes?.data) setLearning(learnRes.data);
        if (etwRes?.data?.events) {
          setEvents(prev => {
            const newEvents = etwRes.data.events.filter(e => 
              !prev.find(p => p.timestamp === e.timestamp && p.pid === e.pid)
            );
            return [...prev, ...newEvents].slice(-50);
          });
        }
        setLoading(false);
      } catch (err) {
        console.error("Intelligence Fetch Error:", err);
        if (mounted) {
          setError(err.message);
          setLoading(false);
        }
      }
    };

    fetchData();
    const interval = setInterval(fetchData, POLL_INTERVAL);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    if (events.length > 0) {
      eventEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [events]);

  if (error) {
    return (
      <div className="flex flex-col h-[60vh] items-center justify-center text-center p-8">
        <AlertTriangle className="h-12 w-12 text-red-500 mb-4" />
        <h3 className="text-lg font-bold text-white uppercase tracking-widest">Neural Layer Offline</h3>
        <p className="text-slate-500 text-xs mt-2 max-w-md font-mono">FAULT: {error}.<br/>Please ensure the JOC Backend is running on port 8000.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-6">
          <div className="relative">
            <div className="absolute inset-0 bg-accent-blue/20 blur-xl rounded-full animate-pulse" />
            <BrainCircuit className="h-16 w-16 text-accent-blue animate-pulse relative z-10" />
          </div>
          <div className="space-y-2 text-center">
            <span className="text-[10px] font-black text-white uppercase tracking-[0.3em] block">Synchronizing Neural Layer</span>
            <div className="flex gap-1 justify-center">
              {[0, 1, 2].map(i => (
                <motion.div 
                  key={i}
                  animate={{ opacity: [0, 1, 0] }}
                  transition={{ repeat: Infinity, duration: 1, delay: i * 0.2 }}
                  className="h-1 w-1 rounded-full bg-accent-blue"
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const pType = pattern?.pattern_type || 'STABLE';
  const pConfidence = pattern?.confidence ?? 0;
  const pIntensity = pattern?.intensity ?? 0;
  const pResource = pattern?.resource || 'NONE';
  const pDerivative = pattern?.derivative ?? 0;

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* Header Info */}
      <header className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-black text-white tracking-tighter uppercase italic drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]">
            Intelligence <span className="text-accent-blue">Cognition</span>
          </h2>
          <div className="flex items-center gap-2 mt-1">
            <div className="h-1.5 w-1.5 rounded-full bg-[#00FF94] shadow-[0_0_8px_#00FF94]" />
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Cross-Scenario Pattern Memory Active</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="px-4 py-2 bg-zinc-900 border border-white/5 rounded-xl text-[10px] font-bold text-slate-400 uppercase tracking-widest">
            Uptime: <span className="text-white">{(events.length > 0 ? "LIVE" : "SYNCING")}</span>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left/Middle Column */}
        <div className="lg:col-span-2 space-y-8">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Pattern Analysis Card */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-zinc-900/60 backdrop-blur-xl border border-white/5 rounded-3xl p-8 relative overflow-hidden group shadow-2xl"
            >
              <div className="absolute top-0 right-0 p-10 opacity-[0.03] scale-[5] pointer-events-none group-hover:text-accent-blue transition-colors duration-500">
                <Activity />
              </div>

              <div className="relative z-10 space-y-8">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-accent-blue/10 rounded-2xl border border-accent-blue/20">
                    <Activity className="h-5 w-5 text-accent-blue" />
                  </div>
                  <div>
                    <h3 className="text-[11px] font-black text-white uppercase tracking-widest">Pattern Matrix</h3>
                    <p className="text-[9px] text-slate-500 font-bold uppercase">Dynamic Resource Topology</p>
                  </div>
                </div>

                <div className="flex justify-between items-end">
                  <div className="space-y-1">
                    <div className="text-[9px] font-bold text-slate-600 uppercase tracking-widest">Active State</div>
                    <div className={cn(
                      "text-4xl font-black italic uppercase italic tracking-tighter",
                      pType === 'stable' ? "text-[#00FF94]" : "text-amber-400"
                    )}>
                      {pType}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-[9px] font-bold text-slate-600 uppercase tracking-widest">Confidence</div>
                    <div className="text-2xl font-black text-white tabular-nums tracking-tighter">
                      {(pConfidence * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between text-[9px] font-black text-slate-400 uppercase tracking-widest">
                    <span>Stress Intensity</span>
                    <span className="text-accent-blue">{(pIntensity * 100).toFixed(1)}%</span>
                  </div>
                  <div className="h-2 bg-black/40 rounded-full border border-white/5 p-0.5">
                    <motion.div 
                      className="h-full bg-accent-blue rounded-full shadow-[0_0_15px_rgba(0,229,255,0.5)]"
                      animate={{ width: `${Math.max(5, pIntensity * 100)}%` }}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-6 border-t border-white/5">
                  <div className="p-4 bg-black/40 rounded-2xl border border-white/5">
                    <div className="text-[8px] font-black text-slate-600 uppercase mb-2">Resource Host</div>
                    <div className="flex items-center gap-2">
                       {pResource === 'cpu' ? <Cpu className="h-4 w-4 text-accent-blue" /> : <HardDrive className="h-4 w-4 text-purple-400" />}
                       <span className="text-xs font-black text-white uppercase">{pResource}</span>
                    </div>
                  </div>
                  <div className="p-4 bg-black/40 rounded-2xl border border-white/5">
                    <div className="text-[8px] font-black text-slate-600 uppercase mb-2">Trend Velocity</div>
                    <div className="flex items-center gap-2">
                       <TrendingUp className={cn("h-4 w-4", pDerivative > 0 ? "text-red-400" : "text-[#00FF94]")} />
                       <span className="text-xs font-black text-white">{pDerivative.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Suggested Action Card */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="bg-[#0A0D14] border border-white/5 rounded-3xl p-8 shadow-2xl flex flex-col justify-between"
            >
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-amber-400/10 rounded-2xl border border-amber-400/20">
                  <Zap className="h-5 w-5 text-amber-400" />
                </div>
                <div>
                  <h3 className="text-[11px] font-black text-white uppercase tracking-widest">Neural Proposal</h3>
                  <p className="text-[9px] text-slate-500 font-bold uppercase">Optimal Mitigation Path</p>
                </div>
              </div>

              <div className="py-12 text-center space-y-6">
                 {learning?.current_pattern_id ? (
                    <>
                      <div className="relative inline-block">
                        <div className="absolute inset-0 bg-amber-400/20 blur-2xl rounded-full" />
                        <Zap className="h-12 w-12 text-amber-400 relative z-10 animate-bounce" />
                      </div>
                      <div className="space-y-2">
                        <div className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Protocol Identified</div>
                        <div className="text-2xl font-black text-white italic uppercase tracking-tighter">
                          {learning.top_patterns?.find(p => p.pattern_id === learning.current_pattern_id)?.response || 'AUTH_PENDING'}
                        </div>
                      </div>
                    </>
                 ) : (
                    <>
                      <Layers className="h-12 w-12 text-slate-800 mx-auto" />
                      <div className="text-[10px] font-black text-slate-700 uppercase tracking-widest">Waiting for Pattern Deviation</div>
                    </>
                 )}
              </div>

              <div className="px-4 py-3 bg-white/[0.02] border border-white/5 rounded-2xl text-center">
                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-tight">Strategy based on {learning?.total_patterns || 0} synaptic memory clusters.</span>
              </div>
            </motion.div>
          </div>

          {/* Learning Ledger */}
          <motion.div 
             initial={{ opacity: 0, y: 20 }}
             animate={{ opacity: 1, y: 0 }}
             transition={{ delay: 0.2 }}
             className="bg-zinc-900/40 border border-white/5 rounded-3xl p-8"
          >
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-white/5 rounded-2xl border border-white/10">
                  <Database className="h-5 w-5 text-accent-blue" />
                </div>
                <div>
                   <h3 className="text-sm font-black text-white uppercase tracking-widest">Synaptic Ledger</h3>
                   <p className="text-[10px] text-slate-500 font-bold uppercase">Persistent Success Metrics (SQLite)</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-[10px] font-black text-slate-600 uppercase mb-1">Total Signals</div>
                <div className="text-3xl font-black text-white tabular-nums tracking-tighter">{learning?.total_patterns || 0}</div>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {learning?.top_patterns?.length > 0 ? (
                learning.top_patterns.map((item, idx) => (
                  <div key={item.pattern_id} className="relative bg-black/40 border border-white/5 p-6 rounded-2xl flex items-center justify-between group hover:border-accent-blue/30 transition-all duration-300">
                    <div className="flex items-center gap-6">
                       <div className="text-lg font-black text-slate-800 italic group-hover:text-accent-blue/20 transition-colors">#{idx + 1}</div>
                       <div>
                          <div className="flex items-center gap-3">
                             <span className="text-sm font-black text-white uppercase italic tracking-tight">{item.pattern_type}</span>
                             <span className="px-2 py-0.5 bg-accent-blue/10 text-accent-blue text-[8px] font-black uppercase rounded border border-accent-blue/20">{item.resource}</span>
                          </div>
                          <div className="text-[10px] font-bold text-slate-500 uppercase mt-1">Suggested Fix: <span className="text-white">{item.response}</span></div>
                       </div>
                    </div>
                    <div className="flex items-center gap-10">
                       <div className="text-right">
                          <div className="text-[9px] font-bold text-slate-600 uppercase mb-1">Success Rating</div>
                          <div className="text-lg font-black text-[#00FF94] tabular-nums tracking-tighter">{(item.success_score * 100).toFixed(0)}%</div>
                       </div>
                       <div className="w-32 space-y-2">
                          <div className="flex justify-between text-[8px] font-black text-slate-600 uppercase tracking-widest">
                             <span>Learning Weight</span>
                             <span>{item.executions} exe</span>
                          </div>
                          <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                             <div className="h-full bg-accent-blue" style={{ width: `${item.success_score * 100}%` }} />
                          </div>
                       </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="py-20 text-center border-2 border-dashed border-white/5 rounded-3xl">
                  <Layers className="h-10 w-10 text-slate-800 mx-auto mb-4" />
                  <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest">No Patterns Localized Yet</p>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Right Column: Event Stream */}
        <div className="space-y-8">
           <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-black border border-white/5 rounded-3xl overflow-hidden flex flex-col h-[calc(100vh-280px)] shadow-2xl"
          >
            <div className="p-5 bg-zinc-900 border-b border-white/5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                 <TerminalIcon className="h-4 w-4 text-accent-blue" />
                 <span className="text-[11px] font-black text-white uppercase tracking-widest">Kernel Event Stream</span>
              </div>
              <div className="px-2 py-0.5 rounded bg-[#00FF94]/10 border border-[#00FF94]/30 text-[8px] font-black text-[#00FF94] uppercase animate-pulse">Live Feed</div>
            </div>

            <div className="flex-1 p-6 font-mono overflow-y-auto scrollbar-none space-y-2">
               {events.length > 0 ? events.map((evt, i) => (
                 <div key={i} className="text-[10px] flex gap-3 leading-relaxed border-b border-white/[0.02] pb-1 group">
                    <span className="text-slate-700 min-w-[70px]">[{new Date(evt.timestamp * 1000).toLocaleTimeString([], { hour12: false })}]</span>
                    <span className={cn("font-black min-w-[30px]", evt.type === 'process_start' ? "text-emerald-400" : "text-amber-500")}>
                      {evt.type === 'process_start' ? '+++' : '---'}
                    </span>
                    <span className="text-white font-bold group-hover:text-accent-blue transition-colors cursor-crosshair truncate max-w-[120px]">{evt.name}</span>
                    <span className="text-slate-600 text-[9px] uppercase font-bold italic">({evt.metadata?.source || 'sys'})</span>
                 </div>
               )) : (
                 <div className="h-full flex flex-col items-center justify-center opacity-20 italic text-[10px] text-slate-500 text-center px-10 gap-3">
                    <Activity className="h-8 w-8 animate-pulse" />
                    Listening for process IOCTL signals...
                 </div>
               )}
               <div ref={eventEndRef} />
            </div>

            <div className="p-4 bg-zinc-900/80 border-t border-white/5">
                <div className="flex items-center justify-between">
                  <div className="text-[8px] font-black text-slate-600 uppercase">Architecture: <span className="text-slate-400">X64_NT_HOOK</span></div>
                  <div className="text-[8px] font-black text-slate-600 uppercase">Buffer: <span className="text-slate-400">{events.length}/50</span></div>
                </div>
            </div>
          </motion.div>

          {/* Policy Card */}
          <motion.div 
             initial={{ opacity: 0, x: 20 }}
             animate={{ opacity: 1, x: 0 }}
             transition={{ delay: 0.1 }}
             className="bg-accent-blue/5 border border-accent-blue/20 rounded-3xl p-8 space-y-6 relative overflow-hidden group shadow-xl"
          >
            <div className="absolute -bottom-4 -right-4 italic font-black text-[80px] text-white/[0.02] rotate-12 pointer-events-none group-hover:text-accent-blue/5 transition-colors">OS</div>
            <div className="w-14 h-14 bg-accent-blue/10 border border-accent-blue/20 rounded-2xl flex items-center justify-center">
              <Layers className="h-7 w-7 text-accent-blue" />
            </div>
            <div className="space-y-4 relative z-10">
              <h4 className="text-xs font-black text-white uppercase tracking-[0.2em]">Autonomous Cognitive Policy</h4>
              <p className="text-[10px] text-slate-400 font-bold leading-relaxed uppercase tracking-tight">
                Sentinel OS is now utilizing an <span className="text-white">Intelligence-First</span> execution policy. High-confidence patterns override static rules.
              </p>
            </div>
          </motion.div>
        </div>

      </div>
    </div>
  );
}
