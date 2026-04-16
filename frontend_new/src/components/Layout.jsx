import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  Activity,
  HardDrive,
  Settings2,
  History,
  Terminal,
  Shield,
  BrainCircuit,
  Minus,
  XOctagon,
  XCircle
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
  { name: 'Security', href: '/security', icon: Shield },
  { name: 'Intelligence', href: '/intelligence', icon: BrainCircuit },
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
      <div className="relative flex h-screen text-slate-300 overflow-hidden p-4 gap-4 bg-[#080B12]">
        <DynamicBackground />

        {/* Sidebar - Clean Engineering Panel */}
        <aside className="relative w-72 rounded-xl bg-zinc-900/80 backdrop-blur-xl flex flex-col z-30 overflow-hidden border border-white/5 shadow-2xl">
          {/* Top Logo Area */}
          <div className="p-8 border-b border-white/5">
            <div className="flex items-center gap-4">
              {/* Custom Hexagon SVG */}
              <svg width="40" height="40" viewBox="0 0 100 100" className="drop-shadow-[0_0_12px_rgba(0,229,255,0.4)]">
                <path
                  d="M50 5 L90 27.5 L90 72.5 L50 95 L10 72.5 L10 27.5 Z"
                  fill="none"
                  stroke="#00E5FF"
                  strokeWidth="6"
                />
                <path d="M50 25 L70 37.5 L70 62.5 L50 75 L30 62.5 L30 37.5 Z" fill="#00E5FF" />
              </svg>
              <div>
                <h1 className="text-4xl font-extrabold text-white leading-none tracking-tight">JOC</h1>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="mt-8 flex-1 space-y-2">
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
                      'group relative flex items-center px-8 py-5 text-[11px] font-bold uppercase tracking-widest transition-all duration-300',
                      isActive
                        ? 'bg-accent-blue/5 text-accent-blue border-r-4 border-accent-blue'
                        : 'text-slate-500 hover:text-white border-r-4 border-transparent'
                    )
                  }
                >
                  <item.icon className={cn('mr-4 h-5 w-5 transition-colors', 'group-hover:text-accent-blue')} />
                  <span className="flex-1">{item.name}</span>

                  {item.isLive && (
                    <div className="flex items-center gap-2 px-2 py-0.5 rounded bg-red-500/10 border border-red-500/20">
                      <span className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse shadow-[0_0_5px_red]" />
                      <span className="text-[8px] text-red-500 font-bold tracking-widest uppercase">Live</span>
                    </div>
                  )}
                </NavLink>
              </motion.div>
            ))}
          </nav>

          {/* Bottom Status Panel */}
          <div className="p-6 bg-black/40 border-t border-white/5">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-[#00FF94] shadow-[0_0_10px_#00FF94]" />
                  <span className="text-[10px] font-bold text-[#00FF94] tracking-widest uppercase">System Connected</span>
                </div>
                <Terminal className="h-3 w-3 text-slate-600" />
              </div>

              <div className="p-3 bg-zinc-950/50 rounded-lg border border-white/5">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[8px] text-slate-500 uppercase font-bold tracking-widest">Host Proxy</span>
                  <span className="text-[9px] text-slate-400 font-medium">localhost:8000</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[8px] text-slate-500 uppercase font-bold tracking-widest">Node Time</span>
                  <span className="text-[9px] text-accent-blue tabular-nums font-bold uppercase">
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
          <header className="h-12 rounded-xl bg-zinc-900/60 backdrop-blur-xl border border-white/5 flex items-center justify-between px-8">
            <div className="flex items-center gap-3">
              <div className="h-1.5 w-1.5 rounded-full bg-accent-blue shadow-[0_0_8px_rgba(0,229,255,0.4)]" />
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">JOC Sentinel</span>
            </div>
            <div className="flex items-center gap-4">
              <Minus className="h-3 w-3 text-slate-600 hover:text-[#00E5FF] cursor-pointer transition-colors" />
              <XOctagon className="h-2.5 w-2.5 text-slate-600 hover:text-[#00E5FF] cursor-pointer transition-colors" />
              <XCircle className="h-3.5 w-3.5 text-slate-600 hover:text-[#FF3D57] cursor-pointer transition-colors" />
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