import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Gamepad2, 
  Battery, 
  Zap, 
  Cpu, 
  Activity, 
  ShieldAlert, 
  RefreshCcw, 
  Lock,
  Target,
  Wifi,
  Database
} from 'lucide-react';

const presetConfig = {
  gaming_boost: {
    name: 'COMBAT_MODE_INIT',
    color: 'red',
    icon: Gamepad2,
    terms: ["VEC_PRIORITY_BOOST", "RESOURCE_STARVATION_INIT", "CLOCK_SPEED_LOCK", "KERNEL_OVERRIDE"],
    accent: '#ef4444'
  },
  battery_saver: {
    name: 'STEALTH_ENGAGED',
    color: 'emerald',
    icon: Battery,
    terms: ["IDLE_THREAD_INJECTION", "VOLTAGE_THROTTLE", "HIBERNATION_PROTOCOL", "SYNC_SUSPENSION"],
    accent: '#10b981'
  },
  performance_boost: {
    name: 'NEURAL_SYNC_LINK',
    color: 'amber',
    icon: Zap,
    terms: ["DATA_NODE_MAPPING", "THROTTLE_ADAPTATION", "NEURAL_LINK_ESTABLISHED", "PATTERN_NORMALIZATION"],
    accent: '#f59e0b'
  },
  clean_ram: {
    name: 'MEMORY_PURGE',
    color: 'blue',
    icon: Cpu,
    terms: ["WORKING_SET_TRIM", "SECTOR_CLEANUP", "CACHE_FLUSH_RECURSIVE", "LEAK_ISOLATION"],
    accent: '#3b82f6'
  }
};

export function TweakExecutionAnimation({ tweakId, isOpen }) {
  const config = presetConfig[tweakId] || presetConfig.performance_boost;
  const [logLines, setLogLines] = useState([]);
  const [phase, setPhase] = useState('entering');

  useEffect(() => {
    if (isOpen) {
      setLogLines([config.terms[0]]);
      const timer = setInterval(() => {
        setLogLines(prev => {
          const next = [config.terms[Math.floor(Math.random() * config.terms.length)], ...prev];
          return next.slice(0, 6);
        });
      }, 300);
      return () => clearInterval(timer);
    }
  }, [isOpen, config.terms]);

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/80 backdrop-blur-xl"
    >
      <div className="max-w-4xl w-full relative">
        {/* Cinematic Scan Line */}
        <motion.div 
          animate={{ y: [-100, 600] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
          className="absolute inset-0 z-10 pointer-events-none"
        >
          <div style={{ backgroundColor: config.accent }} className="w-full h-[2px] opacity-40 blur-sm shadow-[0_0_20px_currentColor]" />
        </motion.div>

        <div className="nm-flat bg-slate-900 rounded-[3rem] border border-slate-800 p-16 overflow-hidden relative">
          {/* Animated Background Grid */}
          <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ 
            backgroundImage: `linear-gradient(to right, ${config.accent} 1px, transparent 1px), linear-gradient(to bottom, ${config.accent} 1px, transparent 1px)`, 
            backgroundSize: '30px 30px' 
          }} />

          <div className="relative z-20 flex flex-col items-center">
            {/* Main Icon Sequence */}
            <motion.div
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              key="main-icon"
              className="relative mb-12"
            >
              <div className={`nm-inset p-10 rounded-[2.5rem] bg-slate-950 border border-${config.color}-500/20 shadow-[0_0_50px_rgba(var(--accent-rgb),0.2)]`}>
                <config.icon className={`h-24 w-24 text-${config.color}-400 drop-shadow-[0_0_15px_currentColor]`} />
              </div>

              {/* HUD Rings */}
              <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                className={`absolute inset-[-20px] rounded-full border border-${config.color}-500/20 border-t-${config.color}-500/60`}
              />
              <motion.div 
                animate={{ rotate: -360 }}
                transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
                className={`absolute inset-[-40px] rounded-full border border-slate-700/50 border-b-${config.color}-500/40`}
              />
            </motion.div>

            {/* Protocol Identity */}
            <div className="text-center mb-12">
              <motion.h2 
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 0.5, repeat: Infinity }}
                className="text-4xl font-black text-white italic tracking-tighter uppercase mb-2"
              >
                {config.name}
              </motion.h2>
              <div className={`text-[10px] font-mono text-${config.color}-500 uppercase tracking-[0.5em]`}>
                {">> Deploying_System_Mutations_In_Sequence"}
              </div>
            </div>

            {/* Telemetry Log */}
            <div className="w-full max-w-lg nm-inset bg-slate-950/80 rounded-2xl p-8 border border-slate-800 relative overflow-hidden h-40">
              <div className="absolute top-0 right-0 p-4">
                <Activity className={`h-4 w-4 text-${config.color}-500/50 animate-pulse`} />
              </div>
              <div className="space-y-2">
                <AnimatePresence mode="popLayout">
                  {logLines.map((line, i) => (
                    <motion.div
                      key={`${line}-${i}`}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1 - i * 0.15, x: 0 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      className="flex items-center gap-4 text-[10px] font-mono tracking-widest uppercase italic"
                    >
                      <span className={`text-${config.color}-600 font-bold`}>[DEPLOYED]</span>
                      <span className="text-slate-400">{line}</span>
                      <span className={`ml-auto text-${config.color}-900`}>{Math.random().toString(16).substring(2, 8)}</span>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>

            {/* Progress Visualization */}
            <div className="mt-12 w-full max-w-md">
              <div className="flex justify-between items-center mb-4">
                <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Protocol_Integrity</span>
                <span className={`text-[10px] font-black text-${config.color}-500 uppercase tracking-widest animate-pulse`}>Optimizing...</span>
              </div>
              <div className="h-2 w-full bg-slate-950 rounded-full nm-inset overflow-hidden">
                <motion.div 
                  initial={{ width: "0%" }}
                  animate={{ width: "100%" }}
                  transition={{ duration: 2.5, ease: "easeInOut" }}
                  className={`h-full bg-gradient-to-r from-transparent via-${config.color}-500 to-${config.color}-400 shadow-[0_0_15px_currentColor]`}
                />
              </div>
            </div>
          </div>

          {/* Corner Elements */}
          <div className={`absolute top-12 left-12 h-20 w-20 border-t-2 border-l-2 border-${config.color}-500/30 rounded-tl-3xl`} />
          <div className={`absolute bottom-12 right-12 h-20 w-20 border-b-2 border-r-2 border-${config.color}-500/30 rounded-br-3xl`} />
        </div>
        
        {/* Cinematic Warnings */}
        <div className="mt-8 flex justify-center gap-6">
          <div className="flex items-center gap-3 px-6 py-3 nm-flat bg-slate-900 rounded-full border border-slate-800">
            <Lock className="h-4 w-4 text-emerald-500" />
            <span className="text-[10px] font-black text-slate-400 tracking-widest uppercase">Admin_Authorized</span>
          </div>
          <div className="flex items-center gap-3 px-6 py-3 nm-flat bg-slate-900 rounded-full border border-slate-800">
            <Target className={`h-4 w-4 text-${config.color}-500`} />
            <span className="text-[10px] font-black text-slate-400 tracking-widest uppercase">Nodes_Locked</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
