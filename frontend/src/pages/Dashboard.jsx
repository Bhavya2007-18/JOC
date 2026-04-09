import React, { useMemo, useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { SystemHealthScore } from '../components/SystemHealthScore';
import { EventStream } from '../components/EventStream';
import { useSystemData } from '../hooks/useSystemData';
import { intelligenceApi } from '../api/client';
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
  ListRestart
} from 'lucide-react';
import { Link } from 'react-router-dom';

export function Dashboard() {
  const { stats, anomalies, decisions, events, addEvent } = useSystemData(3000);
  const [chartData, setChartData] = useState([]);
  const [baseline, setBaseline] = useState({ cpu: null, memory: null });

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

  useEffect(() => {
    let mounted = true;
    intelligenceApi.safePatterns(1440).then((res) => {
      if (!mounted || res.status !== 'success') return;
      const avgCpu = res.data.average_cpu_percent ?? null;
      const avgMem = res.data.average_memory_percent ?? null;
      setBaseline({ cpu: avgCpu, memory: avgMem });
    });
    return () => {
      mounted = false;
    };
  }, []);

  const systemHealth = useMemo(() => {
    if (!stats) return 100;
    let score = 100;
    if (stats.cpu.usage_percent > 80) score -= 20;
    if (stats.memory.percent > 80) score -= 20;
    if (anomalies.length > 0) score -= anomalies.length * 5;
    return Math.max(0, score);
  }, [stats, anomalies]);

  const classifyUsage = (value) => {
    if (value < 50) return { label: 'NORMAL', tone: 'text-green-600', badge: 'bg-green-50 text-green-700' };
    if (value < 80) return { label: 'HIGH', tone: 'text-amber-600', badge: 'bg-amber-50 text-amber-700' };
    return { label: 'CRITICAL', tone: 'text-red-600', badge: 'bg-red-50 text-red-700' };
  };

  const cpuUsage = stats?.cpu?.usage_percent || 0;
  const memUsage = stats?.memory?.percent || 0;

  const lastPoint = chartData[chartData.length - 1];
  const prevPoint = chartData[chartData.length - 2];
  const cpuTrendArrow =
    lastPoint && prevPoint
      ? lastPoint.cpu > prevPoint.cpu
        ? '↑'
        : lastPoint.cpu < prevPoint.cpu
        ? '↓'
        : '→'
      : '';
  const memTrendArrow =
    lastPoint && prevPoint
      ? lastPoint.memory > prevPoint.memory
        ? '↑'
        : lastPoint.memory < prevPoint.memory
        ? '↓'
        : '→'
      : '';

  const cpuState = classifyUsage(cpuUsage);
  const memState = classifyUsage(memUsage);

  const quickStats = [
    { name: 'CPU Usage', value: `${cpuUsage}%`, state: cpuState, icon: Cpu, color: 'text-blue-500', bg: 'bg-blue-50', trend: cpuTrendArrow },
    { name: 'Memory', value: `${memUsage}%`, state: memState, icon: Activity, color: 'text-purple-500', bg: 'bg-purple-50', trend: memTrendArrow },
    { name: 'Disk Free', value: `${stats?.disk?.percent_free || 0}%`, state: null, icon: HardDrive, color: 'text-emerald-500', bg: 'bg-emerald-50' },
    { name: 'Network', value: 'Active', state: null, icon: Monitor, color: 'text-amber-500', bg: 'bg-amber-50' },
  ];

  const [systemMode, setSystemMode] = useState('smart');

  const modes = [
    { id: 'chill', label: 'Chill', icon: Clock, color: 'text-blue-500', desc: 'Power saving' },
    { id: 'smart', label: 'Smart', icon: BrainCircuit, color: 'text-purple-500', desc: 'Balanced' },
    { id: 'beast', label: 'Beast', icon: Zap, color: 'text-amber-500', desc: 'Max performance' },
  ];

  const handleModeChange = (modeId) => {
    setSystemMode(modeId);
    addEvent(`System mode changed to ${modeId.toUpperCase()}`, 'config');
  };

  return (
    <div className="space-y-8 pb-12">
      <Motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-900 flex items-center gap-2">
              <ShieldCheck className="h-8 w-8 text-blue-600" />
              Intelligence Dashboard
            </h1>
            <p className="mt-2 text-lg text-gray-600">Real-time system monitoring and autonomous optimization.</p>
          </div>
          <div className="flex items-center gap-4 bg-white p-3 rounded-2xl border border-gray-100 shadow-sm">
             <SystemHealthScore score={systemHealth} />
          </div>
        </div>
      </Motion.header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {quickStats.map((stat, idx) => (
          <Motion.div
            key={stat.name}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: idx * 0.1 }}
            className="flex items-center rounded-2xl border border-gray-100 bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className={`mr-4 rounded-xl ${stat.bg} p-4`}>
              <stat.icon className={`h-6 w-6 ${stat.color}`} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">{stat.name}</p>
              <p className="text-2xl font-bold text-gray-900">
                {stat.value}
                {stat.trend && <span className="ml-1 text-xs align-middle">{stat.trend}</span>}
              </p>
              {stat.state && (
                <span className={`mt-1 inline-flex rounded-full px-2 py-0.5 text-[10px] font-bold tracking-widest uppercase ${stat.state.badge}`}>
                  {stat.state.label}
                </span>
              )}
              {stat.name === 'CPU Usage' && baseline.cpu != null && (
                <p className="mt-1 text-[11px] text-gray-500">
                  Normal for you: {baseline.cpu.toFixed(1)}%. {cpuUsage > baseline.cpu ? 'Higher than usual.' : 'Within usual range.'}
                </p>
              )}
              {stat.name === 'Memory' && baseline.memory != null && (
                <p className="mt-1 text-[11px] text-gray-500">
                  Normal for you: {baseline.memory.toFixed(1)}%. {memUsage > baseline.memory ? 'Higher than usual.' : 'Within usual range.'}
                </p>
              )}
              {stat.name === 'CPU Usage' && (
                <p className="mt-1 text-[11px] text-gray-500">
                  Sustained high CPU can cause slowdowns and input lag in active applications.
                </p>
              )}
              {stat.name === 'Memory' && (
                <p className="mt-1 text-[11px] text-gray-500">
                  High memory usage can lead to app freezes and disk swapping.
                </p>
              )}
            </div>
          </Motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Real-time Graph */}
        <div className="lg:col-span-2 space-y-8">
          <Card 
            title="System Performance" 
            description="Live CPU and Memory utilization"
            icon={Activity}
          >
            <div className="h-[300px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorMem" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#a855f7" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                  <XAxis dataKey="time" hide />
                  <YAxis domain={[0, 100]} stroke="#9ca3af" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="cpu" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#colorCpu)" 
                    name="CPU %"
                    isAnimationActive={false}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="memory" 
                    stroke="#a855f7" 
                    strokeWidth={2}
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
            title="Intelligence Layer" 
            description="Autonomous insights and decisions"
            icon={BrainCircuit}
          >
            <div className="space-y-4 mt-4">
              <AnimatePresence mode="popLayout">
                {decisions.length > 0 ? (
                  decisions.map((decision, idx) => (
                    <Motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="p-4 rounded-xl border border-gray-100 bg-gray-50/50 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-gray-900">{decision.decision}</h4>
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                          decision.confidence === 'high' ? 'bg-green-100 text-green-700' :
                          decision.confidence === 'medium' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'
                        }`}>
                          {decision.confidence} CONFIDENCE
                        </span>
                      </div>
                      <p className="mt-1 text-sm text-gray-600 leading-relaxed">{decision.reason}</p>
                      <div className="mt-2 text-[11px] text-gray-500">
                        <span className="font-semibold">Why:</span> Based on recent CPU and memory behavior and top processes.
                      </div>
                      {(decision.data_used || (decision.related_anomalies && decision.related_anomalies.length > 0)) && (
                        <div className="mt-2 text-[11px] text-gray-500">
                          {decision.data_used && (
                            <span className="block">
                              Data used: {Object.keys(decision.data_used).join(', ') || 'aggregate metrics'}.
                            </span>
                          )}
                          {decision.related_anomalies && decision.related_anomalies.length > 0 && (
                            <span className="block">
                              Related anomalies: {decision.related_anomalies.length}.
                            </span>
                          )}
                        </div>
                      )}
                      <div className="mt-3 flex items-center gap-3">
                         {decision.suggested_actions.map((action, aidx) => (
                           <Button key={aidx} size="sm" variant="outline" className="text-xs h-8">
                             Apply {action.action_type}
                           </Button>
                         ))}
                      </div>
                    </Motion.div>
                  ))
                ) : (
                  <div className="py-8 text-center text-gray-500 italic text-sm">
                    No active intelligence decisions at this time.
                  </div>
                )}
              </AnimatePresence>
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-8">
          {/* Quick Controls */}
          <Card title="System Mode" icon={Settings2}>
             <div className="flex flex-col gap-3 mt-4">
                <div className="grid grid-cols-3 gap-2">
                   {modes.map((mode) => (
                     <button
                       key={mode.id}
                       onClick={() => handleModeChange(mode.id)}
                       className={`flex flex-col items-center justify-center p-3 rounded-xl border-2 transition-all ${
                         systemMode === mode.id 
                           ? 'border-blue-500 bg-blue-50' 
                           : 'border-gray-100 bg-white hover:border-gray-200'
                       }`}
                     >
                       <mode.icon className={`h-5 w-5 mb-1 ${systemMode === mode.id ? 'text-blue-600' : 'text-gray-400'}`} />
                       <span className={`text-[10px] font-bold ${systemMode === mode.id ? 'text-blue-700' : 'text-gray-500'}`}>
                         {mode.label}
                       </span>
                     </button>
                   ))}
                </div>
                <div className="mt-2 p-3 rounded-lg bg-gray-50 text-[10px] text-gray-500 border border-gray-100">
                   Active: <span className="font-bold text-gray-700 uppercase">{systemMode}</span> - {modes.find(m => m.id === systemMode)?.desc}
                </div>
             </div>
          </Card>

          <Card title="Quick Actions" icon={Zap}>
             <div className="grid grid-cols-2 gap-3 mt-4">
                <Button variant="outline" className="flex-col h-20 gap-2 border-gray-200 hover:border-blue-200 hover:bg-blue-50 group">
                   <Zap className="h-5 w-5 text-amber-500 group-hover:scale-110 transition-transform" />
                   <span className="text-xs font-semibold">Boost</span>
                </Button>
                <Button variant="outline" className="flex-col h-20 gap-2 border-gray-200 hover:border-emerald-200 hover:bg-emerald-50 group">
                   <Trash2 className="h-5 w-5 text-emerald-500 group-hover:scale-110 transition-transform" />
                   <span className="text-xs font-semibold">Cleanup</span>
                </Button>
             </div>
          </Card>

          {/* Event Stream */}
          <EventStream events={events} />

          {/* Simulation Quick Launch */}
          <Card title="Simulation Engine" description="Phase 4 Integration" icon={Activity}>
             <div className="space-y-4 mt-4">
                <p className="text-xs text-gray-500">Test system resilience with simulated stress events.</p>
                <Link to="/system?tab=simulation">
                  <Button className="w-full bg-gray-900 hover:bg-black text-white gap-2">
                    Open Simulation Panel
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
