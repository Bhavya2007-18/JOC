import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { SystemHealthScore } from '../components/SystemHealthScore';
import { EventStream } from '../components/EventStream';
import { IntelligenceStrip } from '../components/IntelligenceStrip';
import { DecisionTracePanel } from '../components/DecisionTracePanel';
import { useSystemData } from '../hooks/useSystemData';
import { GlassPanel } from '../components/GlassPanel';
import { AutonomyEventStream } from '../components/AutonomyEventStream';
import useSystemStore from '../store/useSystemStore';
import { systemApi, optimizerApi } from '../api/client';
import { useSystemMode } from '../context/SystemModeContext';
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
  Loader2,
  CheckCircle2,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '../utils/cn';
import { StatCardBg } from '../components/StatCardBg';
import { ModeCardBg } from '../components/ModeCardBg';
import { ProtocolBg } from '../components/ProtocolBg';

export function Dashboard() {
const {
  stats,
  processes,
  anomalies,
  decisions,
  health,
  loading,
  error,
  lastUpdated,
  events,
  prediction,
  bestAction,
  confidence,
  riskLevel,
  addEvent
} = useSystemData(3000);

const { intelligenceFeed, autonomyFeed } = useSystemStore();
  const { systemMode, setSystemMode } = useSystemMode();
  const [chartData, setChartData] = useState([]);
  const [modeLoading, setModeLoading] = useState(false);
  const [boostLoading, setBoostLoading] = useState(false);
  const [flushLoading, setFlushLoading] = useState(false);
  const [protocolStatus, setProtocolStatus] = useState(null);

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

  const modes = [
    { id: 'chill', label: 'Chill', icon: Clock, color: 'text-blue-400', desc: 'Power saving' },
    { id: 'smart', label: 'Smart', icon: BrainCircuit, color: 'text-purple-400', desc: 'Balanced' },
    { id: 'beast', label: 'Beast', icon: Zap, color: 'text-amber-400', desc: 'Max performance' },
  ];

  // Clear protocol status after 5 seconds
  useEffect(() => {
    if (!protocolStatus) return;
    const timer = setTimeout(() => setProtocolStatus(null), 5000);
    return () => clearTimeout(timer);
  }, [protocolStatus]);

  const handleModeChange = async (modeId) => {
    if (modeLoading) return;
    setModeLoading(true);
    setProtocolStatus(null);
    try {
      await setSystemMode(modeId);
      addEvent(
        `Mode switched to ${modeId.toUpperCase()} — State mutation confirmed`,
        'config'
      );
      setProtocolStatus({
        type: 'success',
        message: `Mode set to ${modeId.toUpperCase()}`,
      });
    } catch (err) {
      console.error('Mode switch failed:', err);
      addEvent(`Mode switch to ${modeId.toUpperCase()} FAILED`, 'error');
      setProtocolStatus({
        type: 'error',
        message: `Failed to switch to ${modeId.toUpperCase()} mode`,
      });
    } finally {
      setModeLoading(false);
    }
  };

  const handleSystemBoost = async () => {
    if (boostLoading) return;
    setBoostLoading(true);
    setProtocolStatus(null);
    try {
      const res = await optimizerApi.boost({ cpu_threshold: 30, max_processes: 10 });
      const data = res.data;
      const processCount = data.processes?.length || 0;
      addEvent(
        `System Boost ${data.dry_run ? '[DRY RUN] ' : ''}executed — ${processCount} processes optimized`,
        'success'
      );
      setProtocolStatus({
        type: 'success',
        message: `${data.dry_run ? '[SIMULATED] ' : ''}${data.message}. ${processCount} processes targeted.`,
      });
    } catch (err) {
      console.error('System boost failed:', err);
      addEvent('System Boost FAILED', 'error');
      setProtocolStatus({
        type: 'error',
        message: 'System Boost protocol failed. Target resisted intervention.',
      });
    } finally {
      setBoostLoading(false);
    }
  };

  const handleCacheFlush = async () => {
    if (flushLoading) return;
    setFlushLoading(true);
    setProtocolStatus(null);
    try {
      const res = await optimizerApi.cleanup({});
      const data = res.data;
      const freed = data.total_bytes_freed || 0;
      const freedMB = (freed / (1024 * 1024)).toFixed(2);
      addEvent(
        `Cache Flush ${data.dry_run ? '[DRY RUN] ' : ''}completed — ${freedMB} MB freed`,
        'success'
      );
      setProtocolStatus({
        type: 'success',
        message: `${data.dry_run ? '[SIMULATED] ' : ''}${data.message}. ${freedMB} MB recovered.`,
      });
    } catch (err) {
      console.error('Cache flush failed:', err);
      addEvent('Cache Flush FAILED', 'error');
      setProtocolStatus({
        type: 'error',
        message: 'Cache Flush protocol failed. Residual data resisted purge.',
      });
    } finally {
      setFlushLoading(false);
    }
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
    <div className="space-y-8 pb-12">
      <IntelligenceStrip
        prediction={prediction}
        bestAction={bestAction}
        confidence={confidence}
        riskLevel={riskLevel}
        lastUpdated={lastUpdated}
      />

      <Motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center justify-between">
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
        </div>
      </Motion.header>

      {/* Protocol Status Toast */}
      <AnimatePresence>
        {protocolStatus && (
          <Motion.div
            initial={{ opacity: 0, y: -10, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.98 }}
            className={cn(
              'flex items-center gap-4 rounded-2xl px-6 py-4 text-xs font-black uppercase tracking-[0.15em] border',
              protocolStatus.type === 'success'
                ? 'nm-flat bg-emerald-950/20 text-emerald-400 border-emerald-900/30'
                : 'nm-flat bg-red-950/20 text-red-400 border-red-900/30'
            )}
          >
            {protocolStatus.type === 'success' ? (
              <CheckCircle2 className="h-5 w-5 shrink-0" />
            ) : (
              <AlertTriangle className="h-5 w-5 shrink-0" />
            )}
            <span>{protocolStatus.message}</span>
          </Motion.div>
        )}
      </AnimatePresence>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
        {quickStats.map((stat, idx) => {
          return (
          <Motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.02, y: -4 }}
            whileTap={{ scale: 0.98 }}
            transition={{ 
              delay: idx * 0.1,
              type: "spring",
              stiffness: 500,
              damping: 30
            }}
            className="nm-flat rounded-3xl bg-slate-900 border border-slate-800 group relative overflow-hidden cursor-pointer"
          >
            <StatCardBg type={stat.name} />
            {/* Card content - perfectly structured layout */}
            <div className="relative z-10 flex flex-col items-center text-center p-6 h-full min-h-[180px]">
              {/* Icon - top section */}
              <div className="nm-inset p-4 rounded-2xl bg-slate-900 group-hover:scale-105 transition-transform duration-300 shrink-0">
                <stat.icon className={`h-8 w-8 ${stat.color}`} />
              </div>
              {/* Label + Value - middle section */}
              <div className="flex flex-col items-center mt-4 flex-1">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-widest leading-none">{stat.name}</p>
                <p className="text-3xl font-black text-white mt-2 font-mono leading-none tabular-nums">
                  {stat.value}
                </p>
              </div>
              {/* Forecast label - bottom section, always same height */}
              <div className="mt-3 h-5 flex items-center justify-center shrink-0">
                {stat.name === 'CPU Usage' && prediction?.predicted_cpu && (
                  <p className="text-[10px] text-accent-blue opacity-80 uppercase tracking-widest font-mono">
                    Forecast(5m): {prediction.predicted_cpu['5m']?.toFixed(1)}% {prediction.predicted_cpu.trend === 'up' ? '↗' : prediction.predicted_cpu.trend === 'down' ? '↘' : '→'}
                  </p>
                )}
                {stat.name === 'CPU Usage' && !prediction?.predicted_cpu && (
                  <p className="text-[10px] text-slate-500 font-mono">
                    Normal: {(stats?.cpu?.usage_percent || 0) > 45 ? 'High load' : 'Stable'}
                  </p>
                )}
                {stat.name === 'Memory' && prediction?.predicted_ram && (
                  <p className="text-[10px] text-accent-blue opacity-80 uppercase tracking-widest font-mono">
                    Forecast(5m): {prediction.predicted_ram['5m']?.toFixed(1)}% {prediction.predicted_ram.trend === 'up' ? '↗' : prediction.predicted_ram.trend === 'down' ? '↘' : '→'}
                  </p>
                )}
                {stat.name === 'Memory' && !prediction?.predicted_ram && (
                  <p className="text-[10px] text-slate-500 font-mono">
                    Normal: {(stats?.memory?.percent || 0) > 60 ? 'High load' : 'Stable'}
                  </p>
                )}
                {stat.name === 'Disk Usage' && (
                  <p className="text-[10px] text-slate-500 font-mono">
                    {(stats?.disk?.percent || 0) > 80 ? 'Critical' : (stats?.disk?.percent || 0) > 60 ? 'Moderate' : 'Healthy'}
                  </p>
                )}
                {stat.name === 'Network' && (
                  <p className="text-[10px] text-emerald-500 font-mono tracking-widest uppercase">
                    ● Online
                  </p>
                )}
              </div>
            </div>
          </Motion.div>
        )})}
      </div>

      <div className="grid grid-cols-1 gap-10 lg:grid-cols-3">
        {/* Real-time Graph */}
        <div className="lg:col-span-2 space-y-10">
          <GlassPanel
            title="Telemetric Analysis & Threat Intelligence"
            accentColor="blue"
          >
            <div className="flex items-center justify-between mt-2 mb-4 px-2">
              <div className="flex items-center space-x-6">
                <div>
                  <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest leading-none mb-1">Live Threat Score</p>
                  <div className="flex items-end space-x-2">
                    <span className="text-4xl font-black text-white font-mono leading-none">
                      {intelligenceFeed?.threat?.threat_score || 0}
                    </span>
                    <span className="text-xs text-accent-blue/80 font-mono italic mb-1">/ 100</span>
                  </div>
                </div>
                {/* Visual Threat Severity Bar */}
                <div className="h-2 w-32 bg-slate-800 rounded-full overflow-hidden mt-3 shadow-inner">
                  <div 
                    className="h-full rounded-full transition-all duration-500"
                    style={{ 
                      width: `${intelligenceFeed?.threat?.threat_score || 0}%`,
                      backgroundColor: (intelligenceFeed?.threat?.threat_score || 0) > 75 ? '#ef4444' : (intelligenceFeed?.threat?.threat_score || 0) > 40 ? '#f59e0b' : '#3b82f6'
                    }}
                  />
                </div>
              </div>
            </div>
            <div className="h-[300px] w-full rounded-2xl bg-slate-900/10 border border-slate-800/20 backdrop-blur-md">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.6} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorMem" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#a855f7" stopOpacity={0.6} />
                      <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" opacity={0.3} />
                  <XAxis dataKey="time" hide />
                  <YAxis domain={[0, 100]} stroke="#64748b" fontSize={10} fontStyle="italic" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(15, 23, 42, 0.8)',
                      backdropFilter: 'blur(10px)',
                      borderRadius: '16px',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
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
          </GlassPanel>

          {/* Intelligence & XAI Layer */}
          <GlassPanel
            title="XAI Narrative & Anomaly Detection"
            accentColor="emerald"
            hoverEffect={true}
          >
            <div className="space-y-6 mt-2">
              {/* XAI Stream Module */}
              {intelligenceFeed?.explanation && (
                <div className="mb-8 p-4 rounded-2xl bg-black/40 border border-emerald-900/40 relative overflow-hidden backdrop-blur-sm shadow-inner group">
                  <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500/50 group-hover:bg-emerald-400 transition-colors" />
                  <h4 className="text-[10px] font-black text-emerald-500/80 uppercase tracking-[0.2em] mb-2 flex items-center">
                    <BrainCircuit className="w-3 h-3 mr-2" /> XAI Narrative Stream
                  </h4>
                  <p className="text-sm text-emerald-50 leading-relaxed font-mono opacity-90">
                    {typeof intelligenceFeed.explanation === 'string' ? intelligenceFeed.explanation : JSON.stringify(intelligenceFeed.explanation)}
                  </p>
                  
                  {/* Predictive Vector Component */}
                  {intelligenceFeed.prediction?.threshold_breach_predicted && (
                    <div className="mt-4 p-3 rounded-xl bg-amber-950/30 border border-amber-900/50 flex">
                      <AlertTriangle className="w-4 h-4 text-amber-500 mr-3 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="text-xs text-amber-500 font-bold uppercase tracking-wider mb-1">Pre-emptive Alert</p>
                        <p className="text-xs text-amber-200/70 font-mono">
                          Statistical trend mapping predicts imminent capacity exhaustion within prediction horizon.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              <AnimatePresence mode="popLayout">
                {decisions.length > 0 ? (
                  decisions.map((issue, idx) => (
                    <Motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="p-6 rounded-3xl nm-flat bg-slate-900/60 border border-slate-700/50 hover:border-emerald-500/30 transition-all relative overflow-hidden group/anomaly backdrop-blur-md"
                    >
                      <ProtocolBg 
                        type="anomaly" 
                        color={(issue.confidence || 0) >= 0.8 ? 'text-emerald-500' : (issue.confidence || 0) >= 0.5 ? 'text-amber-500' : 'text-red-500'} 
                      />
                      <div className="relative z-10">
                        <div className="flex items-center justify-between mb-4">
                          <h4 className="font-black text-white uppercase tracking-wider">{typeof issue.title === 'string' ? issue.title : issue.decision || 'Anomaly Detected'}</h4>
                          <span className={`px-3 py-1 rounded-xl text-[10px] font-black uppercase tracking-widest bg-slate-950/80 border ${(issue.confidence || 0) >= 0.8 ? 'text-emerald-400 border-emerald-900/50' :
                              (issue.confidence || 0) >= 0.5 ? 'text-amber-400 border-amber-900/50' : 'text-red-400 border-red-900/50'
                            }`}>
                            {`${Math.round((issue.confidence || 0) * 100)}%`} CONFIDENCE
                          </span>
                        </div>
                        <p className="text-sm text-slate-300 font-medium leading-relaxed italic border-l-2 border-slate-700 pl-4 py-1">{typeof issue.cause === 'string' ? issue.cause : issue.reason || 'Complex behavioral deviation'}</p>
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
                      </div>
                    </Motion.div>
                  ))
                ) : (
                  <div className="py-12 rounded-2xl bg-slate-900/20 border border-white/5 text-center text-slate-500 font-mono text-xs uppercase tracking-widest backdrop-blur-sm">
                    Telemetry Clean: No active analytical vectors detected
                  </div>
                )}
              </AnimatePresence>
            </div>
            
            {/* Timeline Module */}
            <div className="mt-8 border-t border-slate-800/60 pt-6">
              <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4 flex items-center">
                <Clock className="w-3 h-3 mr-2 text-emerald-500/50" /> Analytical Timeline
              </h4>
              <div className="relative border-l border-slate-700/50 ml-2 space-y-5 pb-2">
                <div className="relative pl-6">
                  <div className="absolute w-2 h-2 rounded-full bg-emerald-500 left-[-4.5px] top-1.5 shadow-[0_0_8px_#10b981]" />
                  <p className="text-[10px] text-emerald-400 font-mono mb-0.5">T-0s [LIVE]</p>
                  <p className="text-xs text-slate-300">Continuous telemetry monitoring active.</p>
                </div>
                <div className="relative pl-6">
                  <div className="absolute w-2 h-2 rounded-full bg-amber-500 left-[-4.5px] top-1.5 border border-slate-900" />
                  <p className="text-[10px] text-amber-500/70 font-mono mb-0.5">T-30s [CAUSAL_GRAPH_UPDATE]</p>
                  <p className="text-xs text-slate-400">Threat predictive thresholds mapped against recent events.</p>
                </div>
                <div className="relative pl-6 opacity-60">
                  <div className="absolute w-2 h-2 rounded-full bg-slate-600 left-[-4.5px] top-1.5 border border-slate-900" />
                  <p className="text-[10px] text-slate-500 font-mono mb-0.5">T-60s [MEMORY_FEEDBACK]</p>
                  <p className="text-xs text-slate-500">Autonomous feedback cycle logged baseline.</p>
                </div>
              </div>
            </div>
          </GlassPanel>
        </div>

        {/* Sidebar Controls */}
        <div className="space-y-10">
          <GlassPanel title="System Mode" accentColor="purple">
            <div className="grid grid-cols-1 gap-4 mt-2">
              {modes.map((mode) => (
                <Motion.button
                  key={mode.id}
                  onClick={() => handleModeChange(mode.id)}
                  disabled={modeLoading}
                  whileHover={{ scale: 1.02, x: 2 }}
                  whileTap={{ scale: 0.96 }}
                  transition={{ type: "spring", stiffness: 600, damping: 25 }}
                  className={cn(
                    'flex items-center gap-5 p-5 rounded-2xl transition-all duration-300 relative overflow-hidden group/mode cursor-pointer',
                    systemMode === mode.id
                      ? 'bg-slate-800/80 border border-accent-blue/50 shadow-[0_0_15px_rgba(59,130,246,0.2)]'
                      : 'bg-slate-900/40 border border-white/5 hover:border-white/10 hover:bg-slate-800/50',
                    modeLoading && 'opacity-50 cursor-wait'
                  )}
                >
                  <ModeCardBg type={mode.id} />
                  <div className="flex items-center gap-5 relative z-10 w-full">
                    <div className={cn(
                      'p-3 rounded-xl transition-all duration-300',
                      systemMode === mode.id ? 'bg-slate-900 text-accent-blue shadow-inner' : 'text-slate-500 group-hover/mode:text-slate-300'
                    )}>
                      <mode.icon className="h-6 w-6" />
                    </div>
                    <div className="text-left">
                      <span className={cn(
                        'block font-black uppercase tracking-widest text-sm transition-colors duration-300',
                        systemMode === mode.id ? 'text-white' : 'text-slate-400 group-hover/mode:text-slate-300'
                      )}>
                        {mode.label}
                      </span>
                      <span className="text-[10px] text-slate-500 uppercase font-mono">{mode.desc}</span>
                    </div>
                  </div>
                  {modeLoading && systemMode === mode.id && (
                    <Loader2 className="h-4 w-4 text-accent-blue animate-spin ml-auto" />
                  )}
                </Motion.button>
              ))}
            </div>
          </GlassPanel>

          <Card title="Direct Protocols" icon={Zap}>
            <div className="grid grid-cols-2 gap-5 mt-6">
              <Button
                variant="outline"
                className="flex-col h-28 gap-3 nm-flat bg-slate-900 rounded-3xl border-slate-800 hover:border-accent-blue/50 group relative overflow-hidden"
                onClick={handleSystemBoost}
                disabled={boostLoading}
              >
                <ProtocolBg type="boost" />
                <div className="flex flex-col items-center gap-3 relative z-10">
                  {boostLoading ? (
                    <Loader2 className="h-6 w-6 text-amber-500 animate-spin" />
                  ) : (
                    <Zap className="h-6 w-6 text-amber-500 group-hover:scale-125 transition-transform duration-500" />
                  )}
                  <span className="text-[10px] font-black uppercase tracking-widest">
                    {boostLoading ? 'Boosting...' : 'System Boost'}
                  </span>
                </div>
              </Button>
              <Button
                variant="outline"
                className="flex-col h-28 gap-3 nm-flat bg-slate-900 rounded-3xl border-slate-800 hover:border-emerald-500/50 group relative overflow-hidden"
                onClick={handleCacheFlush}
                disabled={flushLoading}
              >
                <ProtocolBg type="flush" />
                <div className="flex flex-col items-center gap-3 relative z-10">
                  {flushLoading ? (
                    <Loader2 className="h-6 w-6 text-emerald-500 animate-spin" />
                  ) : (
                    <Trash2 className="h-6 w-6 text-emerald-500 group-hover:scale-125 transition-transform duration-500" />
                  )}
                  <span className="text-[10px] font-black uppercase tracking-widest">
                    {flushLoading ? 'Flushing...' : 'Cache Flush'}
                  </span>
                </div>
              </Button>
            </div>
          </Card>

          {/* Conditional Dual-Stream Event Telemetry */}
          <div className="space-y-6">
            <EventStream events={events} />
            {(systemMode === 'beast' || autonomyFeed) && (
              <Motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                transition={{ duration: 0.5 }}
              >
                <AutonomyEventStream autonomyFeed={autonomyFeed} />
              </Motion.div>
            )}
          </div>

          <DecisionTracePanel decisions={decisions} />

          <Card title="Stress Engine" description="Phase 4 Module" icon={Activity}>
            <div className="mt-6 space-y-6">
              <p className="text-xs text-slate-500 font-mono italic leading-relaxed uppercase">Initiate adversarial simulation to stress test autonomous response loops.</p>
              <Link to="/system?tab=simulation" className="block">
                <Button className="w-full text-accent-blue nm-convex bg-slate-900 rounded-2xl gap-3 relative overflow-hidden h-14 group/battle">
                  <ProtocolBg type="battle" />
                  <div className="flex items-center justify-center gap-3 relative z-10">
                    BATTLE_STATION_LAUNCH
                    <ArrowRight className="h-4 w-4 group-hover/battle:translate-x-1 transition-transform" />
                  </div>
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
