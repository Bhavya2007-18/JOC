import React, { useState, useEffect } from 'react';
// Added missing LineChart, Line, and ReferenceLine imports
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  ReferenceLine 
} from 'recharts';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { SystemHealthScore } from '../components/SystemHealthScore';
import { EventStream } from '../components/EventStream';
import { useSystemData } from '../hooks/useSystemData';
import { systemApi, optimizerApi } from '../api/client';
import { useSystemMode } from '../context/SystemModeContext';
import { AnimatePresence, motion as Motion } from 'framer-motion'; // Consistent alias
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
  Loader2,
  CheckCircle2,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '../utils/cn';
import { StatCardBg } from '../components/StatCardBg';
import { ModeCardBg } from '../components/ModeCardBg';
import { ProtocolBg } from '../components/ProtocolBg';

export function Dashboard() {
  const { stats, processes, anomalies, decisions, health, loading, error, events, forecast, addEvent } = useSystemData(3000);
  const { systemMode, setSystemMode } = useSystemMode();
  const [chartData, setChartData] = useState([]);
  const [modeLoading, setModeLoading] = useState(false);
  const [boostLoading, setBoostLoading] = useState(false);
  const [flushLoading, setFlushLoading] = useState(false);
  const [protocolStatus, setProtocolStatus] = useState(null);

  useEffect(() => {
    if (!stats) return;
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
  }, [stats]);

  const quickStats = [
    { 
      name: 'CPU Usage', 
      value: stats?.cpu?.usage_percent || 0, 
      icon: Cpu, 
      color: 'text-accent-blue',
      chartData: chartData.map(d => ({ value: d.cpu })) 
    },
    { 
      name: 'Memory', 
      value: stats?.memory?.percent || 0, 
      icon: Activity, 
      color: 'text-purple-400',
      chartData: chartData.map(d => ({ value: d.memory }))
    },
    { 
      name: 'Disk Usage', 
      value: stats?.disk?.percent || 0, 
      icon: HardDrive, 
      color: 'text-emerald-400',
      chartData: [] 
    },
    { 
      name: 'Network', 
      value: 'Active', 
      icon: Monitor, 
      color: 'text-cyan-400',
      chartData: [] 
    },
  ];

  const modes = [
    { id: 'chill', label: 'Chill', icon: Clock, color: 'text-blue-400', desc: 'Power saving' },
    { id: 'smart', label: 'Smart', icon: BrainCircuit, color: 'text-purple-400', desc: 'Balanced' },
    { id: 'beast', label: 'Beast', icon: Zap, color: 'text-amber-400', desc: 'Max performance' },
  ];

  useEffect(() => {
    if (!protocolStatus) return;
    const timer = setTimeout(() => setProtocolStatus(null), 5000);
    return () => clearTimeout(timer);
  }, [protocolStatus]);

  const handleModeChange = async (modeId) => {
    if (modeLoading) return;
    setModeLoading(true);
    try {
      await setSystemMode(modeId);
      addEvent(`Mode switched to ${modeId.toUpperCase()}`, 'config');
      setProtocolStatus({ type: 'success', message: `Mode set to ${modeId.toUpperCase()}` });
    } catch (err) {
      setProtocolStatus({ type: 'error', message: `Failed to switch mode` });
    } finally {
      setModeLoading(false);
    }
  };

  const handleSystemBoost = async () => {
    if (boostLoading) return;
    setBoostLoading(true);
    try {
      const res = await optimizerApi.boost({ cpu_threshold: 30, max_processes: 10 });
      setProtocolStatus({ type: 'success', message: `Boost complete: ${res.data.processes?.length || 0} optimized` });
    } catch (err) {
      setProtocolStatus({ type: 'error', message: 'Boost protocol failed' });
    } finally {
      setBoostLoading(false);
    }
  };

  const handleCacheFlush = async () => {
    if (flushLoading) return;
    setFlushLoading(true);
    try {
      const res = await optimizerApi.cleanup({});
      const freedMB = (res.data.total_bytes_freed / (1024 * 1024)).toFixed(2);
      setProtocolStatus({ type: 'success', message: `Cache flushed: ${freedMB} MB recovered` });
    } catch (err) {
      setProtocolStatus({ type: 'error', message: 'Flush failed' });
    } finally {
      setFlushLoading(false);
    }
  };

  const handleFix = async (issue) => {
    if (!issue.best_action) return;
    try {
      await systemApi.fix(issue.best_action.action_type, issue.best_action.target, issue.best_action.pid);
      addEvent(`Applied fix: ${issue.best_action.target}`, 'success');
    } catch (err) {
      addEvent(`Fix failed`, 'error');
    }
  };

  return (
    <div className="space-y-8 pb-12">
      <Motion.header initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-black tracking-tighter text-white flex items-center gap-3 uppercase italic">
              <div className="nm-flat p-3 rounded-2xl bg-slate-900">
                <ShieldCheck className="h-10 w-10 text-accent-blue" />
              </div>
              Intelligence Center
            </h1>
          </div>
          <div className="nm-flat p-4 rounded-3xl bg-slate-900 border border-slate-800">
            <SystemHealthScore score={health || 100} />
          </div>
        </div>
      </Motion.header>

      <AnimatePresence>
        {protocolStatus && (
          <Motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={cn(
              'flex items-center gap-4 rounded-2xl px-6 py-4 text-xs font-black uppercase tracking-[0.15em] border',
              protocolStatus.type === 'success' ? 'bg-emerald-950/20 text-emerald-400 border-emerald-900/30' : 'bg-red-950/20 text-red-400 border-red-900/30'
            )}
          >
            {protocolStatus.type === 'success' ? <CheckCircle2 size={20} /> : <AlertTriangle size={20} />}
            <span>{protocolStatus.message}</span>
          </Motion.div>
        )}
      </AnimatePresence>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {quickStats.map((stat, idx) => {
          const value = typeof stat.value === 'number' ? stat.value : 0;
          const radius = 45;
          const circumference = 2 * Math.PI * radius;
          const offset = circumference - (value / 100) * circumference;

          const getStrokeColor = (v) => {
            if (v < 50) return '#10b981';
            if (v < 80) return '#FFB300';
            return '#FF3D57';
          };

          return (
            <Motion.div
              key={stat.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="relative overflow-hidden rounded-2xl bg-[#0A0D14]/80 border border-white/5 p-6 group cursor-pointer hover:border-cyan-500/30"
            >
              <StatCardBg type={stat.name} />
              <div className="relative z-10 flex flex-col items-center">
                <div className="w-full flex justify-between items-start mb-4">
                  <div className="p-2 rounded-lg bg-slate-900/50 border border-slate-800">
                    <stat.icon className={cn("h-4 w-4", stat.color)} />
                  </div>
                  <span className="text-[10px] font-mono font-bold text-slate-500 uppercase">{stat.name}</span>
                </div>
                <div className="relative h-32 w-32 flex items-center justify-center">
                  <svg className="absolute inset-0 h-full w-full -rotate-90">
                    <circle cx="64" cy="64" r={radius} stroke="#1e293b" strokeWidth="6" fill="transparent" />
                    <Motion.circle
                      cx="64" cy="64" r={radius}
                      stroke={getStrokeColor(value)}
                      strokeWidth="6" fill="transparent"
                      strokeDasharray={circumference}
                      animate={{ strokeDashoffset: offset }}
                      strokeLinecap="round"
                    />
                  </svg>
                  <span className="text-4xl font-black text-white font-mono">{Math.round(value)}%</span>
                </div>
                <div className="w-full h-12 mt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={stat.chartData}>
                      <Line type="monotone" dataKey="value" stroke={getStrokeColor(value)} strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </Motion.div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 gap-10 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-10">
          <Card title="Telemetric Analysis" description="Live system resource overhead" icon={Activity}>
            <div className="relative h-[400px] w-full mt-6 bg-[#080B12] rounded-xl p-6 border border-white/5 overflow-hidden">
              <div className="absolute top-8 right-8 z-20 flex flex-col gap-2 bg-black/60 p-3 border border-slate-800 font-mono text-[10px]">
                <div className="flex items-center gap-3"><div className="h-2 w-2 rounded-full bg-[#00E5FF]" />CPU_LOAD</div>
                <div className="flex items-center gap-3"><div className="h-2 w-2 rounded-full bg-[#BF5FFF]" />MEM_ALLOC</div>
              </div>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="cyberCpu" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00E5FF" stopOpacity={0.4} /><stop offset="95%" stopColor="#00E5FF" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="cyberMem" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#BF5FFF" stopOpacity={0.4} /><stop offset="95%" stopColor="#BF5FFF" stopOpacity={0} />
                    </linearGradient>
                    <pattern id="dotGrid" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="0.5" fill="#334155" opacity="0.5" /></pattern>
                  </defs>
                  <rect width="100%" height="100%" fill="url(#dotGrid)" />
                  <XAxis dataKey="time" hide />
                  <YAxis domain={[0, 100]} stroke="#475569" fontSize={10} axisLine={false} tickLine={false} />
                  <Tooltip content={({ active, payload }) => active && payload ? (
                    <div className="bg-[#0D1117] border border-slate-700 p-4 font-mono text-[11px]">
                      <p className="text-[#00E5FF]">CPU: {payload[0].value?.toFixed(1)}%</p>
                      <p className="text-[#BF5FFF]">MEM: {payload[1].value?.toFixed(1)}%</p>
                    </div>
                  ) : null} />
                  <ReferenceLine y={80} stroke="#FFB300" strokeDasharray="4 4" />
                  <ReferenceLine y={95} stroke="#FF3D57" strokeDasharray="4 4" />
                  <Area type="monotone" dataKey="cpu" stroke="#00E5FF" fill="url(#cyberCpu)" strokeWidth={3} isAnimationActive={false} />
                  <Area type="monotone" dataKey="memory" stroke="#BF5FFF" fill="url(#cyberMem)" strokeWidth={3} isAnimationActive={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card title="Anomaly Detection" icon={BrainCircuit}>
            <div className="space-y-4 mt-6">
              <AnimatePresence mode="popLayout">
                {decisions.length > 0 ? decisions.map((issue, idx) => {
                  const severityColor = issue.confidence >= 0.8 ? '#00E676' : issue.confidence >= 0.5 ? '#FFB300' : '#FF3D57';
                  return (
                    <Motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      style={{ borderLeft: `4px solid ${severityColor}` }}
                      className="relative rounded-r-xl bg-[#0D1117] p-5 border border-white/5"
                    >
                      <ProtocolBg type="anomaly" />
                      <div className="relative z-10">
                        <div className="flex justify-between items-center mb-3">
                          <h4 className="font-bold text-white text-sm uppercase">{issue.title}</h4>
                          <span className="font-mono text-[10px]" style={{ color: severityColor }}>CONFIDENCE: {Math.round(issue.confidence * 100)}%</span>
                        </div>
                        <div className="bg-black/40 p-3 font-mono text-[11px] text-slate-400 border border-white/5">
                          <span style={{ color: severityColor }}>&gt;</span> {issue.cause}
                        </div>
                        {issue.best_action && (
                          <button onClick={() => handleFix(issue)} className="mt-4 px-4 py-2 rounded-full text-[10px] font-black bg-white/5 border border-white/10 hover:bg-white/10 transition-all uppercase tracking-widest">
                            Execute Fix →
                          </button>
                        )}
                      </div>
                    </Motion.div>
                  );
                }) : (
                  <Motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="py-16 flex flex-col items-center border border-dashed border-white/10 rounded-2xl">
                    <div className="h-2 w-2 rounded-full bg-[#00E676] animate-ping mb-4" />
                    <p className="text-[#00E676] font-mono text-xs uppercase tracking-widest">All Systems Nominal</p>
                  </Motion.div>
                )}
              </AnimatePresence>
            </div>
          </Card>
        </div>

        <div className="space-y-10">
          <Card title="System Mode" icon={Settings2}>
            <div className="grid gap-4 mt-6">
              {modes.map((mode) => (
                <Motion.button
                  key={mode.id}
                  onClick={() => handleModeChange(mode.id)}
                  className={cn(
                    'flex items-center gap-5 p-5 rounded-2xl border transition-all relative overflow-hidden',
                    systemMode === mode.id ? 'bg-slate-900 border-cyan-500/30' : 'bg-slate-900 border-transparent hover:border-slate-700'
                  )}
                >
                  <ModeCardBg type={mode.id} />
                  <div className={cn('p-3 rounded-xl', systemMode === mode.id ? 'text-accent-blue' : 'text-slate-500')}>
                    <mode.icon size={24} />
                  </div>
                  <div className="text-left z-10">
                    <span className="block font-black uppercase text-sm">{mode.label}</span>
                    <span className="text-[10px] text-slate-500 uppercase">{mode.desc}</span>
                  </div>
                </Motion.button>
              ))}
            </div>
          </Card>

          <Card title="Direct Protocols" icon={Zap}>
            <div className="grid grid-cols-2 gap-5 mt-6">
              <Button variant="outline" className="flex-col h-28 bg-slate-900 border-slate-800 hover:border-amber-500/50 relative overflow-hidden" onClick={handleSystemBoost}>
                <ProtocolBg type="boost" />
                <Zap size={24} className="text-amber-500 mb-2" />
                <span className="text-[10px] font-black uppercase tracking-widest">Boost</span>
              </Button>
              <Button variant="outline" className="flex-col h-28 bg-slate-900 border-slate-800 hover:border-emerald-500/50 relative overflow-hidden" onClick={handleCacheFlush}>
                <ProtocolBg type="flush" />
                <Trash2 size={24} className="text-emerald-500 mb-2" />
                <span className="text-[10px] font-black uppercase tracking-widest">Flush</span>
              </Button>
            </div>
          </Card>

          <EventStream events={events} />
        </div>
      </div>
    </div>
  );
}