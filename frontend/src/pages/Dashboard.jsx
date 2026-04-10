import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { SystemHealthScore } from '../components/SystemHealthScore';
import { EventStream } from '../components/EventStream';
import { useSystemData } from '../hooks/useSystemData';
import { systemApi } from '../api/client';
import { motion as Motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  HardDrive, 
  Zap, 
  Clock, 
  AlertTriangle, 
  ArrowRight,
  Cpu,
  Monitor,
  ShieldCheck,
  BrainCircuit,
  Settings2,
  Trash2,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '../utils/cn';

export function Dashboard() {
  const { stats, processes, anomalies, decisions, health, loading, error, events, addEvent } = useSystemData(3000);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    if (!stats) return;
    const id = setTimeout(() => {
      const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      setChartData(prev => {
        const next = [
          ...prev,
          {
            time: timestamp,
            cpu: stats.cpu.usage_percent,
            memory: stats.memory.percent,
          },
        ].slice(-20);
        return next;
      });
    }, 0);
    return () => clearTimeout(id);
  }, [stats]);

  const quickStats = [
    { name: 'CPU Usage', value: `${stats?.cpu?.usage_percent || 0}%`, icon: Cpu, color: 'text-accent-blue' },
    { name: 'Memory', value: `${stats?.memory?.percent || 0}%`, icon: Activity, color: 'text-purple-400' },
    { name: 'Disk Usage', value: `${stats?.disk?.percent || 0}%`, icon: HardDrive, color: 'text-emerald-400' },
    { name: 'Network', value: 'Active', icon: Monitor, color: 'text-cyan-400' },
  ];

  const [systemMode, setSystemMode] = useState('smart');

  const modes = [
    { id: 'chill', label: 'Chill', icon: Clock, color: 'text-blue-400', desc: 'Power saving' },
    { id: 'smart', label: 'Smart', icon: BrainCircuit, color: 'text-purple-400', desc: 'Balanced' },
    { id: 'beast', label: 'Beast', icon: Zap, color: 'text-amber-400', desc: 'Max performance' },
  ];

  const handleModeChange = (modeId) => {
    setSystemMode(modeId);
    addEvent(`System mode changed to ${modeId.toUpperCase()}`, 'config');
  };

  const handleFix = async (issue) => {
    if (!issue.best_action) return;
    try {
      await systemApi.fix(
        issue.best_action.action_type,
        issue.best_action.target,
        issue.best_action.pid
      );
      addEvent(`Applied fix: ${issue.best_action.target}`, 'success');
    } catch (fixError) {
      addEvent(`Failed to apply fix: ${issue.best_action.target}`, 'error');
      console.error('Failed to apply fix:', fixError);
    }
  };

  return (
    <div className="space-y-10 pb-12">
      <AnimatePresence mode="wait">
        <Motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex flex-col md:flex-row items-center justify-between gap-6"
        >
          <div>
            <h1 className="text-4xl font-black tracking-tighter text-white flex items-center gap-3 uppercase italic">
              <div className="nm-flat p-3 rounded-2xl bg-slate-900">
                <ShieldCheck className="h-10 w-10 text-accent-blue" />
              </div>
              Intelligence Center
            </h1>
            <p className="mt-4 text-slate-400 font-mono text-sm tracking-widest uppercase">
              Autonomous Optimization Unit // OS_VER 4.2.1
            </p>
          </div>
          <div className="nm-flat p-4 rounded-3xl bg-slate-900 border border-slate-800">
             <SystemHealthScore score={health || 100} />
          </div>
        </Motion.header>
      </AnimatePresence>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
        {quickStats.map((stat, idx) => (
          <Motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="nm-flat rounded-3xl p-6 bg-slate-900 border border-slate-800 flex flex-col items-center text-center group"
          >
            <div className="nm-inset p-4 rounded-2xl bg-slate-900 mb-4 group-hover:scale-105 transition-transform">
              <stat.icon className={`h-8 w-8 ${stat.color}`} />
            </div>
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">{stat.name}</p>
            <p className="text-3xl font-black text-white mt-1 font-mono">{stat.value}</p>
          </Motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-10 lg:grid-cols-3">
        {/* Real-time Graph */}
        <div className="lg:col-span-2 space-y-10">
          <Card 
            title="Telemetric Analysis" 
            description="Live system resource overhead"
            icon={Activity}
          >
            <div className="h-[350px] w-full mt-6 nm-inset rounded-2xl bg-slate-900/50 p-4 border border-slate-800/50">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorMem" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" opacity={0.3} />
                  <XAxis dataKey="time" hide />
                  <YAxis domain={[0, 100]} stroke="#64748b" fontSize={10} fontStyle="italic" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#0f172a', 
                      borderRadius: '16px', 
                      border: '1px solid #334155', 
                      boxShadow: '10px 10px 20px #020617, -10px -10px 20px #1e293b',
                      color: '#f1f5f9'
                    }} 
                  />
                  <Area 
                    type="monotone" 
                    dataKey="cpu" 
                    stroke="#3b82f6" 
                    strokeWidth={3}
                    fillOpacity={1} 
                    fill="url(#colorCpu)" 
                    name="CPU %"
                    isAnimationActive={false}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="memory" 
                    stroke="#a855f7" 
                    strokeWidth={3}
                    fillOpacity={1} 
                    fill="url(#colorMem)" 
                    name="RAM %"
                    isAnimationActive={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Intelligence Layer */}
          <Card 
            title="Anomaly Detection" 
            description="Active autonomous decisions"
            icon={BrainCircuit}
          >
            <div className="space-y-6 mt-6">
              <AnimatePresence mode="popLayout">
                {decisions.length > 0 ? (
                  decisions.map((issue, idx) => (
                    <Motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="p-6 rounded-3xl nm-flat bg-slate-900 border border-slate-800 hover:nm-convex transition-all"
                    >
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-black text-white uppercase tracking-wider">{issue.title}</h4>
                        <span className={`px-3 py-1 rounded-xl text-[10px] font-black uppercase tracking-widest nm-inset bg-slate-900 ${
                          (issue.confidence || 0) >= 0.8 ? 'text-emerald-500' :
                          (issue.confidence || 0) >= 0.5 ? 'text-amber-500' : 'text-red-500'
                        }`}>
                          {`${Math.round((issue.confidence || 0) * 100)}%`} CONFIDENCE
                        </span>
                      </div>
                      <p className="text-sm text-slate-400 font-medium leading-relaxed italic">{issue.cause}</p>
                      <div className="mt-6 flex items-center justify-end">
                        <Button
                          size="sm"
                          variant="primary"
                          onClick={() => handleFix(issue)}
                          disabled={!issue.best_action}
                        >
                          {issue.best_action
                            ? `RUN_PROTOCOL: ${issue.best_action.target}`
                            : "NO_ACTION_REQUIRED"}
                        </Button>
                      </div>
                    </Motion.div>
                  ))
                ) : (
                  <div className="py-12 nm-inset rounded-2xl bg-slate-900/30 text-center text-slate-500 font-mono text-xs uppercase tracking-widest">
                    Telemetry Clean: No active anomalies detected
                  </div>
                )}
              </AnimatePresence>
            </div>
          </Card>
        </div>

        {/* Sidebar Controls */}
        <div className="space-y-10">
          <Card title="System Mode" icon={Settings2}>
             <div className="grid grid-cols-1 gap-4 mt-6">
                {modes.map((mode) => (
                  <button
                    key={mode.id}
                    onClick={() => handleModeChange(mode.id)}
                    className={cn(
                      'flex items-center gap-5 p-5 rounded-2xl transition-all duration-300',
                      systemMode === mode.id 
                        ? 'nm-inset bg-slate-900 border border-accent-blue/30' 
                        : 'nm-flat bg-slate-900 border border-transparent hover:border-slate-700'
                    )}
                  >
                    <div className={cn(
                      'nm-flat p-3 rounded-xl',
                      systemMode === mode.id ? 'nm-inset text-accent-blue' : 'text-slate-500'
                    )}>
                       <mode.icon className="h-6 w-6" />
                    </div>
                    <div className="text-left">
                       <span className={cn(
                         'block font-black uppercase tracking-widest text-sm',
                         systemMode === mode.id ? 'text-white' : 'text-slate-500'
                       )}>
                         {mode.label}
                       </span>
                       <span className="text-[10px] text-slate-500 uppercase font-mono">{mode.desc}</span>
                    </div>
                  </button>
                ))}
             </div>
          </Card>

          <Card title="Direct Protocols" icon={Zap}>
             <div className="grid grid-cols-2 gap-5 mt-6">
                <Button variant="outline" className="flex-col h-28 gap-3 nm-flat bg-slate-900 rounded-3xl border-slate-800 hover:border-accent-blue/50 group">
                   <Zap className="h-6 w-6 text-amber-500 group-hover:scale-125 transition-transform duration-500" />
                   <span className="text-[10px] font-black uppercase tracking-widest">System Boost</span>
                </Button>
                <Button variant="outline" className="flex-col h-28 gap-3 nm-flat bg-slate-900 rounded-3xl border-slate-800 hover:border-emerald-500/50 group">
                   <Trash2 className="h-6 w-6 text-emerald-500 group-hover:scale-125 transition-transform duration-500" />
                   <span className="text-[10px] font-black uppercase tracking-widest">Cache Flush</span>
                </Button>
             </div>
          </Card>

          <EventStream events={events} />

          <Card title="Stress Engine" description="Phase 4 Module" icon={Activity}>
             <div className="mt-6 space-y-6">
                <p className="text-xs text-slate-500 font-mono italic leading-relaxed uppercase">Initiate adversarial simulation to stress test autonomous response loops.</p>
                <Link to="/system?tab=simulation">
                  <Button className="w-full text-accent-blue nm-convex bg-slate-900 rounded-2xl gap-3">
                    BATTLE_STATION_LAUNCH
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
             </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
