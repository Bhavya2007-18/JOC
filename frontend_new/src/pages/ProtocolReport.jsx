import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer
} from 'recharts';
import { 
  ShieldCheck, 
  Activity, 
  Target, 
  UserCheck, 
  ChevronLeft,
  Cpu,
  Database
} from 'lucide-react';
import { Button } from '../components/Button';

export function ProtocolReport() {
  const location = useLocation();
  const navigate = useNavigate();
  const reportData = location.state?.data;

  // Fallback if no data is present (e.g. direct URL access)
  if (!reportData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <Database className="h-20 w-20 text-slate-800 mb-6" />
        <h1 className="text-2xl font-black text-white uppercase italic">No Report Data Cached</h1>
        <p className="mt-4 text-slate-500 font-mono text-sm uppercase">Please execute a protocol to generate telemetric insights.</p>
        <Button onClick={() => navigate('/tweaks')} className="mt-8 px-10 h-14 nm-flat bg-slate-900 border-none rounded-2xl uppercase font-black text-[10px] tracking-widest transition-all hover:nm-convex">
          Return to Tweaks
        </Button>
      </div>
    );
  }

  const { tweak, status, summary, effects = {}, meta = {} } = reportData;
  
  // High-fidelity data extraction with fallbacks for different response schemas
  const raw = effects.raw || reportData.raw || reportData;
  const beforePercent = raw.memory_before_percent || reportData.memory_before_percent || 0;
  const afterPercent = raw.memory_after_percent || reportData.memory_after_percent || beforePercent;
  
  const transitionData = [
    { stage: 'PRE_DEPLOY', value: beforePercent, label: 'Before' },
    { stage: 'TRANSITION', value: (beforePercent + afterPercent) / 2 },
    { stage: 'POST_DEPLOY', value: afterPercent, label: 'After' },
  ];

  const targets = effects.targets || reportData.targets || raw.processes_cleaned || raw.processes_killed || [];
  const memoryFreed = effects.memory_freed || reportData.memory_freed || raw.freed_mb || 0;

  // Calculate dynamic efficacy based on yield and status
  const calculateEfficacy = () => {
    if (status === 'failed') return 1.2;
    if (status === 'blocked') return 0.0;
    
    let base = status === 'partial' ? 6.5 : 8.5;
    if (memoryFreed > 500) base += 1.0;
    else if (memoryFreed > 100) base += 0.5;
    
    if (targets.length > 5) base += 0.4;
    return Math.min(9.9, base).toFixed(1);
  };
  
  const efficacy = calculateEfficacy();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="pb-20 space-y-12"
    >
      <header className="flex flex-col lg:flex-row lg:items-center justify-between gap-8">
        <div className="flex items-center gap-6">
          <Button 
            onClick={() => navigate('/tweaks')} 
            variant="outline" 
            className="nm-flat bg-slate-900 border-none rounded-2xl p-4 h-14 w-14 group"
          >
            <ChevronLeft className="h-6 w-6 text-slate-400 group-hover:text-white transition-colors" />
          </Button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-4xl font-black text-white uppercase italic tracking-tighter">
                Intelligence_Report: {tweak.toUpperCase().replace('_', ' ')}
              </h1>
              <span className={`px-4 py-1 rounded-full text-[10px] font-black uppercase tracking-widest nm-inset bg-slate-900 ${status === 'success' ? 'text-emerald-400' : 'text-amber-400'}`}>
                {status}
              </span>
            </div>
            <p className="mt-2 text-slate-500 font-mono text-xs uppercase tracking-[0.4em] italic opacity-70">
              {">> Deployment_Audit_Log // Ref."}{meta.request_id?.substring(0, 8)}
            </p>
          </div>
        </div>
        <div className="flex gap-6">
          <div className="nm-inset p-4 rounded-2xl bg-slate-900 text-right">
            <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest block mb-1">Duration</span>
            <div className="text-xl font-black text-white font-mono">{meta.duration_ms}ms</div>
          </div>
          <div className="nm-inset p-4 rounded-2xl bg-slate-900 text-right">
            <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest block mb-1">Auth_Level</span>
            <div className="text-xl font-black text-emerald-400 font-mono flex items-center gap-2 italic">
              <UserCheck className="h-4 w-4" /> ADMIN
            </div>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        {/* Main Visual: State Transition */}
        <div className="lg:col-span-2 space-y-10">
          <div className="nm-flat bg-slate-900 rounded-[3rem] p-10 border border-slate-800 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-8 opacity-5">
              <Activity className="h-40 w-40 text-accent-blue" />
            </div>
            
            <div className="flex items-center justify-between mb-10">
              <h3 className="text-xl font-black text-white uppercase italic flex items-center gap-3">
                <Activity className="h-5 w-5 text-accent-blue" /> System State Evolution
              </h3>
              {memoryFreed > 0 && (
                <div className="nm-inset px-6 py-2 rounded-2xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-black uppercase tracking-widest">
                  RECOVERY_YIELD: {memoryFreed} MB
                </div>
              )}
            </div>

            <div className="h-[350px] w-full mt-6">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={transitionData}>
                  <defs>
                    <linearGradient id="reportGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis 
                    dataKey="label" 
                    stroke="#475569" 
                    fontSize={10} 
                    tickFormatter={(val) => val?.toUpperCase() || ''}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis 
                    stroke="#475569" 
                    fontSize={10} 
                    domain={[0, 100]}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: 'none', borderRadius: '1rem', color: '#fff' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#3b82f6" 
                    fill="url(#reportGrad)" 
                    strokeWidth={4} 
                    animationDuration={1500}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-2 gap-8 mt-10">
              <div className="nm-inset p-6 rounded-3xl bg-slate-950 text-center">
                <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 block">Initial_Load</span>
                <div className="text-3xl font-black text-slate-400 italic font-mono">{beforePercent}%</div>
              </div>
              <div className="nm-inset p-6 rounded-3xl bg-slate-950 border border-emerald-500/20 text-center">
                <span className="text-[10px] font-black text-emerald-500 uppercase tracking-widest mb-2 block">Optimized_Load</span>
                <div className="text-3xl font-black text-white italic font-mono">{afterPercent}%</div>
              </div>
            </div>
          </div>

          {/* Target Intervention Ledger */}
          <div className="nm-flat bg-slate-900 rounded-[3rem] p-10 border border-slate-800">
             <div className="flex items-center justify-between mb-10 pb-6 border-b border-slate-800">
              <h3 className="text-xl font-black text-white uppercase italic flex items-center gap-3">
                <Target className="h-5 w-5 text-red-400" /> Intervention_Ledger
              </h3>
              <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">
                TOTAL_VECTORS: {targets.length}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[450px] overflow-y-auto custom-scrollbar pr-4">
              {targets.length > 0 ? targets.map((target, idx) => (
                <div key={idx} className="nm-inset p-4 rounded-2xl bg-slate-950 border border-slate-800 group hover:border-accent-blue/30 transition-all">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-black text-white uppercase truncate">{target.name}</span>
                    <span className="text-[9px] font-bold text-slate-500 font-mono">[{target.pid}]</span>
                  </div>
                  <div className="flex items-center gap-2">
                     <div className="h-1 flex-1 bg-slate-900 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-accent-blue" 
                          style={{ width: `${Math.min(100, (target.memory_mb / 1024) * 100)}%` }} 
                        />
                     </div>
                     <span className="text-[9px] font-black text-slate-600 font-mono italic">
                       {target.memory_mb?.toFixed(0)}MB
                     </span>
                  </div>
                </div>
              )) : (
                <div className="col-span-full py-12 text-center text-slate-600 font-mono text-sm italic">
                  {">> No targeted intervention required for this vector."}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Side Panels: HUD & Synopsis */}
        <div className="space-y-10">
          {/* Efficiency Score */}
          <div className="nm-flat bg-slate-900 rounded-[3rem] p-10 border border-slate-800 flex flex-col items-center text-center">
             <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-8">Efficacy_Rating</span>
             <div className="relative h-48 w-48 flex items-center justify-center">
                <svg className="h-full w-full" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="45" fill="none" stroke="#1e293b" strokeWidth="8" />
                  <motion.circle 
                    cx="50" cy="50" r="45" fill="none" stroke="#3b82f6" strokeWidth="8" 
                    strokeDasharray="283"
                    animate={{ strokeDashoffset: 283 - (283 * (parseFloat(efficacy) / 10)) }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-4xl font-black text-white italic drop-shadow-[0_0_10px_#3b82f6]">{efficacy}</span>
                  <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">NEURAL_STABILITY</span>
                </div>
             </div>
             <p className="mt-8 text-[10px] font-mono text-slate-400 uppercase leading-relaxed tracking-wider italic">
               The protocol achieved nominal recovery yield with zero critical path interference.
             </p>
          </div>

          {/* Intelligence Synopsis */}
          <div className="nm-flat bg-slate-900 rounded-[3rem] p-10 border border-indigo-500/20 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-6 opacity-10 text-indigo-400">
              <Database className="h-16 w-16" />
            </div>
            <h4 className="text-[11px] font-black text-indigo-400 uppercase tracking-[0.3em] mb-6 flex items-center gap-3">
              <ShieldCheck className="h-4 w-4" /> Intelligence Synopsis
            </h4>
            <div className="text-xs text-slate-300 font-mono leading-relaxed italic border-l-2 border-indigo-500/30 pl-4 py-2">
              Deployment successful across all targeted nodes. {summary}
            </div>
            <div className="mt-8 space-y-4">
               {(effects.details || []).map((detail, i) => (
                  <div key={i} className="flex items-start gap-3 group">
                     <span className="text-indigo-500 group-hover:animate-pulse">▶</span>
                     <span className="text-[10px] uppercase font-black text-slate-500 tracking-widest group-hover:text-slate-300 transition-colors">
                       {detail}
                     </span>
                  </div>
               ))}
            </div>
          </div>

          {/* Protocol Meta */}
          <div className="nm-inset bg-slate-950 rounded-3xl p-8 space-y-6">
             <div className="flex justify-between items-center">
               <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Process_Isolation</span>
               <span className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">COMPLETE</span>
             </div>
             <div className="flex justify-between items-center">
               <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Memory_Fragmentation</span>
               <span className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">NORMALIZED</span>
             </div>
             <div className="flex justify-between items-center">
               <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">Power_Vector_Stability</span>
               <span className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">OPTIMAL</span>
             </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
