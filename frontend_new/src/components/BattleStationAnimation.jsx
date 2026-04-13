import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Swords, Target, Shield, Zap, AlertCircle } from 'lucide-react';

const statusTerms = [
  "INITIALIZING_VECTORS",
  "DEPRODUCING_KERNEL_BLOCKS",
  "STRESSING_CORTEX_LINKS",
  "BUFFER_SATURATION_PROTOCOL",
  "MAPPING_ADVERSARIAL_FLOW",
  "TRIGGERING_LATENCY_SPIKES",
  "PENETRATING_SECURITY_LAYERS"
];

export function BattleStationAnimation({ intensity = 50, type = 'cpu_spike' }) {
  const [countdown, setCountdown] = useState(3);
  const [phase, setPhase] = useState('countdown'); // countdown | active
  const [log, setLog] = useState([statusTerms[0]]);

  const intensityFactor = intensity / 100;

  useEffect(() => {
    if (phase === 'countdown') {
      const timer = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            setPhase('active');
            return 0;
          }
          return prev - 1;
        });
      }, 800);
      return () => clearInterval(timer);
    }
  }, [phase]);

  useEffect(() => {
    if (phase === 'active') {
      const logTimer = setInterval(() => {
        setLog(prev => [statusTerms[Math.floor(Math.random() * statusTerms.length)], ...prev].slice(0, 5));
      }, 500 / (0.5 + intensityFactor));
      return () => clearInterval(logTimer);
    }
  }, [phase, intensityFactor]);

  return (
    <motion.div 
      animate={phase === 'active' ? {
        x: [0, -2, 2, -1, 1, 0],
        y: [0, 1, -1, 2, -2, 0],
      } : {}}
      transition={{ 
        duration: 0.1, 
        repeat: phase === 'active' ? 5 : 0, // Quick shake on activation
        ease: "linear"
      }}
      className="relative w-full h-[550px] flex flex-col items-center justify-center nm-flat bg-slate-900 rounded-[3rem] border border-red-900/40 overflow-hidden"
    >
      {/* Red Combat Grid */}
      <div className="absolute inset-0 z-0 opacity-10" style={{ 
        backgroundImage: `linear-gradient(to right, #ef4444 1px, transparent 1px), linear-gradient(to bottom, #ef4444 1px, transparent 1px)`, 
        backgroundSize: '40px 40px' 
      }}>
        <motion.div 
          animate={{ scale: [1, 1.05, 1], opacity: [0.1, 0.2, 0.1] }}
          transition={{ duration: 0.5 / (0.5 + intensityFactor), repeat: Infinity }}
          className="w-full h-full bg-red-500/5"
        />
      </div>

      {/* Horizontal Threat Scan */}
      <motion.div
        animate={{ y: [-100, 650] }}
        transition={{ duration: 1.5 / (0.5 + intensityFactor), repeat: Infinity, ease: "linear" }}
        className="absolute w-full h-24 bg-gradient-to-b from-transparent via-red-500/20 to-transparent z-10 pointer-events-none"
      >
        <div className="w-full h-1 bg-red-500/40 blur-md shadow-[0_0_20px_rgba(239,68,68,0.8)]" />
      </motion.div>

      <AnimatePresence mode="wait">
        {phase === 'countdown' ? (
          <motion.div
            key="countdown"
            initial={{ opacity: 0, scale: 2 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.5, filter: 'blur(10px)' }}
            className="relative z-20 flex flex-col items-center"
          >
            <div className="text-[10px] font-black text-red-500 uppercase tracking-[0.5em] mb-4">Protocol_Override_Sequence</div>
            <motion.span 
              key={countdown}
              initial={{ opacity: 0, scale: 4, rotate: -10 }}
              animate={{ opacity: 1, scale: 1, rotate: 0 }}
              className="text-9xl font-black text-white italic drop-shadow-[0_0_30px_rgba(239,68,68,0.5)]"
            >
              {countdown}
            </motion.span>
            <div className="mt-8 flex gap-2">
              {[...Array(3)].map((_, i) => (
                <div key={i} className={`h-1 w-12 rounded-full ${3-i <= countdown ? 'bg-red-500 shadow-[0_0_10px_#ef4444]' : 'bg-slate-800'}`} />
              ))}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="active"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="w-full h-full flex flex-col items-center justify-center relative z-20"
          >
            {/* Tactical Crosshair */}
            <div className="relative mb-12">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                className="nm-inset p-16 rounded-full bg-slate-950 border-2 border-dashed border-red-500/30 flex items-center justify-center"
              >
                <Swords className="h-32 w-32 text-red-500" />
              </motion.div>
              
              {/* Spinning HUD rings */}
              <motion.div 
                animate={{ rotate: -360 }}
                transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                className="absolute inset-[-20px] rounded-full border border-red-500/20 border-t-red-500/60"
              />
              <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="absolute inset-[-40px] rounded-full border border-slate-700/50 border-b-red-500/40"
              />
            </div>

            {/* Combat Stats HUD */}
            <div className="flex gap-12 mb-8">
              <div className="text-center">
                <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Intensity_Flux</div>
                <div className="text-3xl font-black font-mono text-white">{intensity}%</div>
              </div>
              <div className="text-center">
                <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Vector_Type</div>
                <div className="text-3xl font-black font-mono text-red-500">{type.toUpperCase()}</div>
              </div>
              <div className="text-center">
                <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">System_Stress</div>
                <div className="text-3xl font-black font-mono text-amber-500">MAXIMIZING</div>
              </div>
            </div>

            {/* Scrolling Combat Log */}
            <div className="w-96 nm-inset bg-slate-950 p-6 rounded-2xl border border-red-900/30 h-32 overflow-hidden flex flex-col gap-2">
              <AnimatePresence>
                {log.map((line, i) => (
                  <motion.div
                    key={line + i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1 - i * 0.2, x: 0 }}
                    className="text-[10px] font-mono text-red-400 uppercase tracking-widest flex items-center gap-3"
                  >
                    <span className="text-red-600 font-bold">»</span> {line}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Warning Badges */}
      <div className="absolute top-8 left-8 flex items-center gap-3 nm-flat bg-red-950/20 px-4 py-2 rounded-xl border border-red-900/30">
        <AlertCircle className="h-4 w-4 text-red-500" />
        <span className="text-[10px] font-black text-red-500 uppercase tracking-widest">Adversarial_Lock_On</span>
      </div>

      {/* Decorative Corners */}
      <div className="absolute top-8 right-8 border-t-2 border-r-2 border-red-500/40 w-16 h-16 rounded-tr-3xl" />
      <div className="absolute bottom-8 left-8 border-b-2 border-l-2 border-red-500/40 w-16 h-16 rounded-bl-3xl" />
    </motion.div>
  );
}
