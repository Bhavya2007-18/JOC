import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  Activity,
  HardDrive,
  Settings2,
  History,
  Terminal, // Added missing icon
  Minus,
  Square,
  X
} from 'lucide-react';
import { cn } from '../utils/cn';
import { SystemModeProvider } from '../context/SystemModeContext';
import { DynamicBackground } from './DynamicBackground/DynamicBackground';

const navSpring = { type: "spring", stiffness: 400, damping: 30 };

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard, isLive: true },
  { name: 'System', href: '/system', icon: Activity },
  { name: 'Storage', href: '/storage', icon: HardDrive },
  { name: 'Tweaks', href: '/tweaks', icon: Settings2 },
  { name: 'History', href: '/history', icon: History },
];

export function Layout() {
  // Fix: Initialize the 'time' state
  const [time, setTime] = useState(new Date().toLocaleTimeString());

  // Fix: Set up the interval to update the clock every second
  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <SystemModeProvider>
      <div className="relative flex h-screen text-slate-300 font-mono overflow-hidden p-4 gap-4 bg-[#080B12]">
        <DynamicBackground />

        {/* Sidebar - Cyber Terminal Panel */}
        <aside className="relative w-64 rounded-xl bg-[#0A0D17]/80 backdrop-blur-md flex flex-col z-30 overflow-hidden border border-[rgba(0,229,255,0.1)]">
          {/* Subtle Scanline Effect Overlay */}
          <div
            className="pointer-events-none absolute inset-0 z-50 opacity-[0.03]"
            style={{ background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, #00E5FF 3px)' }}
          />

          {/* Top Logo Area */}
          <div className="p-8 border-b border-[rgba(0,229,255,0.1)]">
            <div className="flex items-center gap-4">
              {/* Custom Hexagon SVG */}
              <svg width="40" height="40" viewBox="0 0 100 100" className="drop-shadow-[0_0_8px_rgba(0,229,255,0.6)]">
                <path
                  d="M50 5 L90 27.5 L90 72.5 L50 95 L10 72.5 L10 27.5 Z"
                  fill="none"
                  stroke="#00E5FF"
                  strokeWidth="6"
                />
                <path d="M50 25 L70 37.5 L70 62.5 L50 75 L30 62.5 L30 37.5 Z" fill="#00E5FF" />
              </svg>
              <div>
                <h1 className="text-4xl font-black text-white leading-none tracking-tighter italic font-heading">JOC</h1>              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="mt-6 flex-1 space-y-1">
            {navigation.map((item) => (
              <motion.div
                key={item.name}
                whileHover={{ x: 4 }}
                transition={navSpring}
              >
                <NavLink
                  to={item.href}
                  className={({ isActive }) =>
                    cn(
                      'group relative flex items-center px-6 py-4 text-xs font-bold uppercase tracking-[0.2em] transition-all duration-300',
                      isActive
                        ? 'bg-[#00E5FF]/5 text-[#00E5FF] border-l-4 border-[#00E5FF]'
                        : 'text-slate-500 hover:text-white border-l-4 border-transparent'
                    )
                  }
                >
                  <item.icon className={cn('mr-4 h-5 w-5 transition-colors', 'group-hover:text-[#00E5FF]')} />
                  <span className="flex-1">{item.name}</span>

                  {item.isLive && (
                    <div className="flex items-center gap-2 px-2 py-0.5 rounded bg-red-500/10 border border-red-500/20">
                      <span className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse shadow-[0_0_5px_red]" />
                      <span className="text-[8px] text-red-500 font-black tracking-widest">LIVE</span>
                    </div>
                  )}
                </NavLink>
              </motion.div>
            ))}
          </nav>

          {/* Bottom Status Panel */}
          <div className="p-4 bg-black/40 border-t border-[rgba(0,229,255,0.1)]">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-[#00FF94] shadow-[0_0_8px_#00FF94] animate-pulse" />
                  <span className="text-[10px] font-black text-[#00FF94] tracking-widest">CONNECTED</span>
                </div>
                <Terminal className="h-3 w-3 text-slate-600" />
              </div>

              <div className="p-2 bg-slate-900/50 rounded border border-slate-800">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[8px] text-slate-500 uppercase font-bold">Host_Proxy</span>
                  <span className="text-[9px] text-slate-300 font-mono">localhost:8000</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[8px] text-slate-500 uppercase font-bold">Node_Time</span>
                  <span className="text-[9px] text-[#00E5FF] font-mono tabular-nums font-bold uppercase tracking-tighter">
                    {time}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col gap-4 min-w-0">
          {/* Mock Window Title Bar */}
          <header className="h-10 rounded-xl bg-[#0A0D17]/60 backdrop-blur-md border border-[rgba(0,229,255,0.1)] flex items-center justify-between px-6">
            <div className="flex items-center gap-3">
              <div className="h-1.5 w-1.5 rounded-full bg-[#00E5FF] shadow-[0_0_5px_#00E5FF]" />
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-[0.3em]">JOC</span>
            </div>
            <div className="flex items-center gap-4">
              <Minus className="h-3 w-3 text-slate-600 hover:text-[#00E5FF] cursor-pointer transition-colors" />
              <Square className="h-2.5 w-2.5 text-slate-600 hover:text-[#00E5FF] cursor-pointer transition-colors" />
              <X className="h-3.5 w-3.5 text-slate-600 hover:text-[#FF3D57] cursor-pointer transition-colors" />
            </div>
          </header>

          {/* Dynamic Content */}
          <main className="flex-1 bg-black/20 rounded-2xl overflow-y-auto p-8 scrollbar-thin">
            <div className="mx-auto max-w-7xl">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </SystemModeProvider>
  );
}