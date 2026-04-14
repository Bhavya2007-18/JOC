import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, ShieldAlert, Cpu, Database, Search } from 'lucide-react';

const scanTerms = [
  "SCANNING KORTEX MODULES",
  "MAPPING NEURAL SYNAPSE",
  "TRACING MEMORY LEAKS",
  "BUFFER INTEGRITY CHECK",
  "ISOLATING ADVERSARIAL NODES",
  "DECRYPTING SENTINEL LOGS",
  "CAPTURING TELEMETRY DATAFRAME",
  "VALIDATING PROTOCOL CHAINS"
];

export function DeepScanAnimation() {
  const [currentTerm, setCurrentTerm] = useState(scanTerms[0]);
  const [percent, setPercent] = useState(0);

  useEffect(() => {
    const termInterval = setInterval(() => {
      setCurrentTerm(scanTerms[Math.floor(Math.random() * scanTerms.length)]);
    }, 800);

    const percentInterval = setInterval(() => {
      setPercent(prev => (prev < 99 ? prev + Math.floor(Math.random() * 3) + 1 : 99));
    }, 100);

    return () => {
      clearInterval(termInterval);
      clearInterval(percentInterval);
    };
  }, []);

  return (
    <div className="relative w-full h-[500px] flex flex-col items-center justify-center nm-flat bg-slate-900 rounded-[3rem] border border-slate-800 overflow-hidden">
      {/* Background Grid - Scrolling */}
      <div className="absolute inset-0 z-0 opacity-20" style={{ 
        backgroundImage: 'radial-gradient(circle, #1e293b 1px, transparent 1px)', 
        backgroundSize: '30px 30px' 
      }}>
        <motion.div 
          animate={{ y: [0, 30] }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-full h-full"
        />
      </div>

      {/* Laser Scan Beam */}
      <motion.div
        animate={{ y: [-100, 600] }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        className="absolute w-full h-20 bg-gradient-to-b from-transparent via-accent-blue/20 to-transparent z-10 pointer-events-none"
      >
        <div className="w-full h-0.5 bg-accent-blue/50 blur-sm shadow-[0_0_15px_rgba(56,189,248,0.5)]" />
      </motion.div>

      {/* Central Core Pulse */}
      <div className="relative z-20 mb-12">
        <motion.div
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="nm-inset p-12 rounded-full bg-slate-950 flex items-center justify-center border border-slate-800/50"
        >
          <Activity className="h-28 w-28 text-accent-blue" />
        </motion.div>
        
        {/* Sonar Rings */}
        {[...Array(3)].map((_, i) => (
          <motion.div
            key={i}
            initial={{ scale: 0.8, opacity: 0.5 }}
            animate={{ scale: 2, opacity: 0 }}
            transition={{ 
              duration: 3, 
              repeat: Infinity, 
              delay: i * 1,
              ease: "easeOut" 
            }}
            className="absolute inset-0 rounded-full border border-accent-blue/30 -z-10"
          />
        ))}
      </div>

      {/* Telemetry Drift */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            initial={{ x: Math.random() * 800, y: 600, opacity: 0 }}
            animate={{ y: -100, opacity: [0, 0.4, 0] }}
            transition={{ 
              duration: 4 + Math.random() * 4, 
              repeat: Infinity, 
              delay: i * 0.5 
            }}
            className="text-[10px] font-mono text-slate-500 uppercase tracking-widest whitespace-nowrap"
          >
            {scanTerms[i]} || 0x{Math.floor(Math.random()*1000).toString(16).toUpperCase()}
          </motion.div>
        ))}
      </div>

      {/* Status HUD */}
      <div className="relative z-30 text-center space-y-4">
        <h3 className="text-2xl font-black text-white uppercase italic tracking-widest animate-pulse">
          Neural_Diagnostic_Mode
        </h3>
        
        <div className="flex flex-col items-center gap-2">
          <div className="w-64 h-1 nm-inset rounded-full overflow-hidden bg-slate-950">
            <motion.div 
              style={{ width: `${percent}%` }}
              className="h-full bg-accent-blue shadow-[0_0_10px_rgba(56,189,248,0.5)]"
            />
          </div>
          <div className="flex justify-between w-64 text-[10px] font-black font-mono text-slate-500 tracking-tighter uppercase">
             <span>Prog: {percent}%</span>
             <span>Link: Stable</span>
          </div>
        </div>

        <div className="nm-flat px-6 py-3 rounded-2xl bg-slate-900 border border-slate-800 min-w-[300px]">
          <AnimatePresence mode="wait">
            <motion.p
              key={currentTerm}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              className="text-xs font-mono text-accent-blue uppercase tracking-[0.2em] font-bold"
            >
              {`> ${currentTerm}...`}
            </motion.p>
          </AnimatePresence>
        </div>
      </div>

      {/* Scanning Corners */}
      <div className="absolute top-8 left-8 border-t border-l border-accent-blue/30 w-12 h-12" />
      <div className="absolute top-8 right-8 border-t border-r border-accent-blue/30 w-12 h-12" />
      <div className="absolute bottom-8 left-8 border-b border-l border-accent-blue/30 w-12 h-12" />
      <div className="absolute bottom-8 right-8 border-b border-r border-accent-blue/30 w-12 h-12" />
    </div>
  );
}
