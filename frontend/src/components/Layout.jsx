import { motion } from 'framer-motion';
import { NavLink, Outlet } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Activity, 
  HardDrive, 
  Settings2, 
  History, 
  ShieldCheck,
  Minus,
  Square,
  X
} from 'lucide-react';
import { cn } from '../utils/cn';
import { SystemModeProvider } from '../context/SystemModeContext';
import { DynamicBackground } from './DynamicBackground/DynamicBackground';

const navSpring = { type: "spring", stiffness: 400, damping: 30 };

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'System', href: '/system', icon: Activity },
  { name: 'Storage', href: '/storage', icon: HardDrive },
  { name: 'Tweaks', href: '/tweaks', icon: Settings2 },
  { name: 'History', href: '/history', icon: History },
];

export function Layout() {
  return (
    <SystemModeProvider>
      <div className="relative flex h-screen text-slate-200 font-sans overflow-hidden p-3 gap-3">
        <DynamicBackground />
        
        {/* Sidebar - Glassmorphism */}
        <aside className="w-64 rounded-3xl glass-card bg-slate-900/40 backdrop-blur-xl border border-slate-700/50 flex flex-col z-30">
        <div className="p-8 flex items-center gap-3">
          <div className="nm-inset p-2 rounded-xl bg-slate-900">
            <ShieldCheck className="h-6 w-6 text-accent-blue" />
          </div>
          <span className="text-xl font-black tracking-tighter text-white uppercase italic">JOC_ENGINE</span>
        </div>
        
        <nav className="mt-4 flex-1 px-4 space-y-3">
          {navigation.map((item) => (
            <motion.div
              key={item.name}
              whileHover={{ scale: 1.02, x: 5 }}
              whileTap={{ scale: 0.98 }}
              transition={navSpring}
            >
              <NavLink
                to={item.href}
                className={({ isActive }) =>
                  cn(
                    'group flex items-center rounded-2xl px-5 py-4 text-sm font-bold uppercase tracking-widest transition-all duration-300',
                    isActive
                      ? 'nm-inset text-accent-blue bg-slate-900'
                      : 'text-slate-500 hover:text-slate-200 hover:bg-slate-800/50'
                  )
                }
              >
                <item.icon className={cn('mr-4 h-5 w-5 transition-colors', 'group-hover:text-accent-blue')} />
                {item.name}
              </NavLink>
            </motion.div>
          ))}
        </nav>

        <div className="p-6">
           <div className="nm-inset rounded-2xl p-4 bg-slate-900/50 border border-slate-800">
              <p className="text-[10px] font-mono text-slate-500 uppercase">System Status</p>
              <p className="text-xs font-bold text-emerald-500 mt-1 flex items-center gap-2">
                 <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                 Secure Connection
              </p>
           </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col gap-3 min-w-0">
        {/* Mock Window Title Bar */}
        <header className="h-12 rounded-2xl nm-flat bg-slate-900/60 backdrop-blur-md border border-slate-700/30 flex items-center justify-between px-6">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-slate-700" />
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">JOC_SENTINEL_V4.2</span>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
               <Minus className="h-3.5 w-3.5 text-slate-600 hover:text-white cursor-pointer transition-colors" />
               <Square className="h-2.5 w-2.5 text-slate-600 hover:text-white cursor-pointer transition-colors" />
               <X className="h-4 w-4 text-slate-600 hover:text-red-500 cursor-pointer transition-colors" />
            </div>
          </div>
        </header>

        {/* Dynamic Content */}
        <main className="flex-1 nm-inset rounded-3xl bg-slate-900/20 overflow-y-auto p-8 scrollbar-thin">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
      </div>
    </SystemModeProvider>
  );
}
