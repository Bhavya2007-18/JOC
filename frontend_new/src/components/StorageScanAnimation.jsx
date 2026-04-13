import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HardDrive, Search, Database, Zap, Trash2 } from 'lucide-react';

const paths = [
  "C:/CACHE/RESIDUAL_0XFB12",
  "D:/TEMP/SYPHON_LOG_TMP",
  "SYSTEM32/DRIVERS/DEBRIS",
  "USERS/LOCAL/DATA_DUMP",
  "APP_DATA/RESIDUE/NOMADIC",
  "KERNEL/DUMP/SECTOR_ALIVE",
  "REGISTRY/STALE/PROTOCOL",
  "MEMORY/SWAP/DECREMENT"
];

export function StorageScanAnimation() {
  const [percent, setPercent] = useState(0);
  const [sectors, setSectors] = useState([]);
  const [drift, setDrift] = useState([paths[0]]);

  useEffect(() => {
    // Generate initial sectors
    const initialSectors = Array.from({ length: 64 }, (_, i) => ({
      id: i,
      state: Math.random() > 0.7 ? (Math.random() > 0.5 ? 'junk' : 'redundant') : 'clean',
      delay: Math.random() * 2
    }));
    setSectors(initialSectors);

    const timer = setInterval(() => {
      setPercent(prev => (prev < 99 ? prev + 1 : 99));
    }, 35);

    const driftTimer = setInterval(() => {
      setDrift(prev => [paths[Math.floor(Math.random() * paths.length)], ...prev].slice(0, 4));
    }, 600);

    return () => {
      clearInterval(timer);
      clearInterval(driftTimer);
    };
  }, []);

  return (
    <div className="relative w-full h-[550px] flex flex-col items-center justify-center nm-flat bg-slate-900 rounded-[3rem] border border-slate-800 overflow-hidden">
      {/* Background Pixel Grid */}
      <div className="absolute inset-0 z-0 opacity-10 flex flex-wrap gap-1 p-4">
        {[...Array(200)].map((_, i) => (
          <div key={i} className="w-4 h-4 nm-inset bg-slate-850 rounded-sm" />
        ))}
      </div>

      {/* Vertical Scan Pulse */}
      <motion.div
        animate={{ x: [-200, 800] }}
        transition={{ duration: 2.5, repeat: Infinity, ease: "linear" }}
        className="absolute h-full w-32 bg-gradient-to-r from-transparent via-accent-blue/10 to-transparent z-10 pointer-events-none"
      >
        <div className="h-full w-0.5 bg-accent-blue/40 blur-sm" />
      </motion.div>

      {/* Main Analysis Engine */}
      <div className="relative z-20 flex flex-col items-center gap-12">
        {/* Sector Grid */}
        <div className="grid grid-cols-8 gap-2 nm-inset p-6 rounded-[2rem] bg-slate-950/50 backdrop-blur-sm border border-slate-800">
          {sectors.map((s, i) => (
            <motion.div
              key={s.id}
              initial={{ scale: 0 }}
              animate={percent > (i / 64) * 100 ? { 
                scale: 1, 
                backgroundColor: s.state === 'junk' ? '#ef4444' : s.state === 'redundant' ? '#f59e0b' : '#1e293b'
              } : { scale: 0 }}
              className={`w-4 h-4 rounded-sm shadow-sm transition-colors duration-1000`}
              style={{
                boxShadow: percent > (i / 64) * 100 && s.state !== 'clean' ? `0 0 10px ${s.state === 'junk' ? '#ef4444' : '#f59e0b'}` : 'none'
              }}
            />
          ))}
        </div>

        {/* Central Nexus */}
        <div className="relative">
          <motion.div
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="nm-inset p-10 rounded-full bg-slate-950 border border-accent-blue/20"
          >
            <HardDrive className="h-16 w-16 text-accent-blue" />
          </motion.div>
          
          {/* Data Siphon Particles */}
          <AnimatePresence>
            {percent % 5 === 0 && (
              <motion.div
                initial={{ x: (Math.random() - 0.5) * 400, y: (Math.random() - 0.5) * 400, opacity: 0, scale: 2 }}
                animate={{ x: 0, y: 0, opacity: 1, scale: 0.5 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.8, ease: "easeIn" }}
                className="absolute top-1/2 left-1/2 w-2 h-2 rounded-full bg-accent-blue/60"
              />
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* HUD Info */}
      <div className="absolute top-12 left-12 space-y-4 z-30">
        <div className="flex items-center gap-3">
          <div className="h-2 w-2 rounded-full bg-accent-blue animate-ping" />
          <span className="text-[10px] font-black text-white uppercase tracking-[0.3em]">Sector_Siphon_Active</span>
        </div>
        
        <div className="space-y-1">
          <div className="w-48 h-1 nm-inset rounded-full overflow-hidden bg-slate-950">
            <motion.div 
              style={{ width: `${percent}%` }}
              className="h-full bg-accent-blue shadow-[0_0_10px_#3b82f6]"
            />
          </div>
          <p className="text-[9px] font-mono text-slate-500 font-black">PROGRESS: {percent}% // DEPTH: 100%</p>
        </div>
      </div>

      {/* Drift Log */}
      <div className="absolute bottom-12 right-12 text-right space-y-2 z-30">
        <AnimatePresence>
          {drift.map((line, i) => (
            <motion.p
              key={line + i}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1 - i * 0.25, x: 0 }}
              exit={{ opacity: 0 }}
              className="text-[10px] font-mono text-slate-400 uppercase tracking-widest"
            >
              {line} <span className="text-accent-blue opacity-50">|| OK</span>
            </motion.p>
          ))}
        </AnimatePresence>
      </div>

      {/* Decorative Overlays */}
      <div className="absolute inset-0 border-[24px] border-slate-900/50 pointer-events-none" />
      <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-slate-700/50 to-transparent" />
      <div className="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-slate-700/50 to-transparent" />
    </div>
  );
}
