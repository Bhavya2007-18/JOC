import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, 
  ShieldAlert, 
  ShieldCheck, 
  Zap, 
  Activity, 
  Clock3 as Clock, 
  AlertTriangle, 
  Settings,
  Terminal,
  RefreshCcw as RefreshCw,
  Search,
  Lock,
  Target,
  XOctagon as Square,
  History,
  Info,
  ChevronRight,
  Database,
  Cpu,
  Globe,
  Activity as PulseIcon
} from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import { securityApi } from '../api/client';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { cn } from '../utils/cn';

export function Security() {
  const [health, setHealth] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [intervalValue, setIntervalValue] = useState(10);
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [healthRes, alertsRes, logsRes] = await Promise.all([
        securityApi.getHealth(),
        securityApi.getAlerts(15),
        securityApi.getLogs(30)
      ]);
      
      if (healthRes.data) {
        setHealth(healthRes.data);
        setIntervalValue(healthRes.data.interval);
      }
      if (alertsRes.data) {
        setAlerts(alertsRes.data);
      }
      if (logsRes.data) {
        setLogs(logsRes.data);
      }
    } catch (err) {
      console.error("Security link failure", err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleMonitor = async () => {
    setIsUpdating(true);
    try {
      if (health?.running) {
        await securityApi.stopMonitor();
      } else {
        await securityApi.startMonitor();
      }
      await fetchData();
    } finally {
      setIsUpdating(false);
    }
  };

  const handleIntervalChange = async (newVal) => {
    setIntervalValue(newVal);
    try {
      await securityApi.setInterval(newVal);
    } catch (err) {
      console.error("Failed to set interval", err);
    }
  };

  const formatUptime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const riskTrendData = useMemo(() => {
    return logs.map((log, i) => ({
      value: log.data?.risk_score || 0,
      id: i
    }));
  }, [logs]);

  const spm = useMemo(() => {
    if (!health?.scan_count || !health?.uptime_seconds) return 0;
    return ((health.scan_count / (health.uptime_seconds / 60))).toFixed(1);
  }, [health]);

  const StatusIcon = health?.running ? ShieldCheck : ShieldAlert;
  const statusColor = health?.running ? "text-emerald-400" : "text-red-400";
  const glowColor = health?.running ? "rgba(52, 211, 153, 0.4)" : "rgba(248, 113, 113, 0.4)";

  return (
    <div className="space-y-10 pb-20">
      {/* Header Section */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-8">
        <div className="flex items-center gap-6">
          <div className={cn(
            "p-5 rounded-3xl bg-slate-900/50 border relative group",
            health?.running ? "border-emerald-500/30" : "border-red-500/30"
          )}>
            <div className="absolute inset-0 rounded-3xl opacity-20 blur-xl transition-all duration-1000 group-hover:opacity-30" style={{ backgroundColor: glowColor }} />
            <StatusIcon className={cn("h-10 w-10 relative z-10", statusColor)} />
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-4xl font-black text-white uppercase italic tracking-tighter">Sentinel_Security_Hub</h1>
              <div className={cn(
                "px-3 py-1 rounded text-[10px] font-black uppercase tracking-widest animate-pulse",
                health?.running ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-red-500/10 text-red-400 border border-red-500/20"
              )}>
                {health?.running ? "Active_Protection" : "Offline_Standby"}
              </div>
            </div>
            <p className="mt-2 text-slate-500 font-mono text-xs uppercase tracking-[0.4em] italic opacity-70">
              &gt;&gt; autonomous_threat_detection_and_security_orchestration
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Button
            onClick={handleToggleMonitor}
            disabled={isUpdating}
            className={cn(
              "nm-convex px-10 h-14 uppercase font-black italic tracking-widest transition-all",
              health?.running 
                ? "bg-red-500/10 text-red-500 border border-red-500/30 hover:bg-red-500/20" 
                : "bg-emerald-500/10 text-emerald-500 border border-emerald-500/30 hover:bg-emerald-500/20"
            )}
          >
            {isUpdating ? (
              <RefreshCw className="h-5 w-5 animate-spin" />
            ) : health?.running ? (
              <><Square className="mr-2 h-4 w-4 fill-current" /> Terminate_Protection</>
            ) : (
              <><Activity className="mr-2 h-4 w-4 fill-current" /> Start_Monitoring_Loop</>
            )}
          </Button>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* Main Stats HUD */}
        <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="md:col-span-1 group relative overflow-visible h-full flex flex-col justify-between" glowColor="cyan">
            <div className="flex justify-between items-start mb-4">
              <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest block">System_Uptime</span>
              <Clock className="h-5 w-5 text-slate-700 group-hover:text-white transition-colors" />
            </div>
            <div>
              <div className="text-4xl font-black text-white font-mono italic tracking-tighter mb-1">
                {health?.uptime_seconds ? formatUptime(health.uptime_seconds) : "00:00:00"}
              </div>
              <div className="text-[10px] text-slate-600 font-mono uppercase tracking-widest">
                SESSION_ROOT: AUTH_MOD_JOC
              </div>
            </div>
            <div className="mt-6 pt-4 border-t border-white/5 flex items-center justify-between">
              <span className="text-[9px] text-slate-600 uppercase font-bold">Status</span>
              <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-widest italic">Stable</span>
            </div>
          </Card>

          <Card className="md:col-span-1 group relative overflow-visible h-full flex flex-col justify-between" glowColor="cyan">
            <div className="flex justify-between items-start mb-4">
              <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest block">Telemetry_Scans</span>
              <PulseIcon className="h-5 w-5 text-slate-700 group-hover:text-[#00E5FF] transition-colors" />
            </div>
            <div>
              <div className="text-4xl font-black text-[#00E5FF] font-mono italic tracking-tighter mb-1">
                {health?.scan_count?.toLocaleString() || 0}
              </div>
              <div className="text-[10px] text-slate-600 font-mono uppercase tracking-widest">
                AVG_RATE: {spm} SCANS/MIN
              </div>
            </div>
            <div className="mt-6 pt-4 border-t border-white/5 flex items-center justify-between">
              <span className="text-[9px] text-slate-600 uppercase font-bold">Skipped</span>
              <span className="text-[10px] text-slate-400 font-bold font-mono">[{health?.skipped_scans || 0}]</span>
            </div>
          </Card>

          <Card className="md:col-span-1 group relative overflow-visible h-full flex flex-col justify-between" glowColor={ (health?.last_risk_score || 0) > 40 ? "red" : "amber" }>
            <div className="flex justify-between items-start mb-4">
              <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest block">Risk_Factor</span>
              <ShieldAlert className={cn(
                "h-5 w-5 transition-colors",
                (health?.last_risk_score || 0) > 40 ? "text-red-500" : "text-slate-700 group-hover:text-white"
              )} />
            </div>
            <div className="flex-1 min-h-[50px] relative">
               <div className="absolute inset-0 z-0 opacity-20">
                 <ResponsiveContainer width="100%" height="100%">
                   <AreaChart data={riskTrendData}>
                     <Area 
                       type="monotone" 
                       dataKey="value" 
                       stroke={ (health?.last_risk_score || 0) > 40 ? "#F87171" : "#FBBF24" } 
                       fill={ (health?.last_risk_score || 0) > 40 ? "#F87171" : "#FBBF24" } 
                       fillOpacity={0.2}
                       strokeWidth={2}
                     />
                   </AreaChart>
                 </ResponsiveContainer>
               </div>
               <div className="relative z-10 text-3xl font-black font-mono italic tracking-tighter text-white">
                 {health?.last_risk_score || 0}%
               </div>
            </div>
            <div className="mt-4 h-1 w-full bg-slate-800 rounded-full overflow-hidden">
               <motion.div 
                 className={cn(
                   "h-full",
                   (health?.last_risk_score || 0) > 70 ? "bg-red-400 shadow-[0_0_8px_#F87171]" : "bg-amber-400"
                 )}
                 initial={{ width: 0 }}
                 animate={{ width: `${health?.last_risk_score || 0}%` }}
               />
            </div>
          </Card>

          {/* Redesigned Frequency Control */}
          <Card className="md:col-span-3 h-auto" glowColor="cyan">
             <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-10 py-2">
                <div className="flex items-center gap-6">
                   <div className="p-4 rounded-2xl bg-black/40 border border-white/5 flex-shrink-0">
                      <Settings className="h-6 w-6 text-accent-blue" />
                   </div>
                   <div className="min-w-0">
                      <h3 className="text-xl font-black text-white uppercase italic tracking-widest">Scanning_Frequency_Control</h3>
                      <p className="text-[10px] text-slate-500 font-mono uppercase tracking-widest mt-1">
                        Real-time security telemetry synchronization interval adjustment.
                      </p>
                   </div>
                </div>

                <div className="flex-1 xl:max-w-md w-full p-6 bg-white/5 rounded-2xl border border-white/5">
                   <div className="flex items-center justify-between mb-4">
                      <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Frequency_Vector</span>
                      <span className="text-xl font-black text-accent-blue font-mono">{intervalValue} SEC</span>
                   </div>
                   <input
                      type="range"
                      min="1"
                      max="60"
                      value={intervalValue}
                      onChange={(e) => handleIntervalChange(parseInt(e.target.value))}
                      className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-accent-blue"
                   />
                   <div className="flex justify-between text-[8px] text-slate-600 font-bold uppercase tracking-[0.2em] mt-2">
                      <span>AGGRESSIVE (1S)</span>
                      <span>NOMINAL (60S)</span>
                   </div>
                </div>
             </div>
          </Card>
        </div>

        {/* Alerts Log Section */}
        <div className="lg:col-span-1">
          <Card className="h-full group overflow-hidden" glowColor="red">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/5">
              <h3 className="text-sm font-black text-white uppercase italic tracking-widest flex items-center gap-3">
                <ShieldAlert className="h-4 w-4 text-red-500" /> Threats
              </h3>
              <div className="flex items-center gap-2">
                <div className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse" />
                <span className="text-[10px] text-red-500 font-black tracking-widest uppercase">Live</span>
              </div>
            </div>
            
            <div className="h-[500px] overflow-y-auto custom-scrollbar -mx-6 px-6">
              <AnimatePresence initial={false}>
                {alerts.length > 0 ? (
                  alerts.map((alert, i) => (
                    <motion.div 
                      key={alert.id || i}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="mb-4 p-4 rounded-lg bg-white/5 border border-white/5 hover:border-red-500/30 transition-all cursor-crosshair group relative"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className={cn(
                          "text-[8px] font-black uppercase px-2 py-0.5 rounded",
                          alert.severity === 'critical' ? 'bg-red-500 text-white' : 'bg-amber-500 text-black'
                        )}>
                          {alert.severity}
                        </span>
                        <span className="text-[8px] font-mono text-slate-500">{new Date(alert.timestamp * 1000).toLocaleTimeString([], { hour12: false })}</span>
                      </div>
                      <h4 className="text-[11px] font-bold text-slate-200 group-hover:text-white transition-colors uppercase truncate">{alert.title}</h4>
                      <p className="text-[9px] text-slate-500 font-mono mt-1 line-clamp-2 italic">{alert.message || alert.description}</p>
                    </motion.div>
                  ))
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-slate-700 opacity-30 py-10">
                    <Lock className="h-10 w-10 mb-4" />
                    <span className="text-[10px] font-black uppercase tracking-[0.3em]">No Threats Detected</span>
                  </div>
                )}
              </AnimatePresence>
            </div>
          </Card>
        </div>

        {/* Scan History Section */}
        <div className="lg:col-span-1">
          <Card className="h-full group overflow-hidden" glowColor="cyan">
             <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/5">
                <h3 className="text-sm font-black text-white uppercase italic tracking-widest flex items-center gap-3">
                  <History className="h-4 w-4 text-accent-blue" /> History
                </h3>
             </div>

             <div className="h-[500px] overflow-y-auto custom-scrollbar -mx-6 px-6">
               <AnimatePresence initial={false}>
                 {logs.length > 0 ? (
                   logs.slice().reverse().map((log, i) => (
                     <motion.div 
                       key={i}
                       initial={{ opacity: 0, x: 20 }}
                       animate={{ opacity: 1, x: 0 }}
                       className="mb-4 p-4 rounded-lg bg-white/5 border border-white/5 hover:border-accent-blue/30 transition-all cursor-pointer group"
                     >
                       <div className="flex items-center justify-between mb-2">
                          <div className={cn(
                            "text-[8px] font-black uppercase px-2 py-0.5 rounded",
                            (log.data?.risk_score || 0) > 40 ? "bg-red-500/20 text-red-500" : "bg-emerald-500/20 text-emerald-400"
                          )}>
                            RISK: {log.data?.risk_score || 0}%
                          </div>
                          <span className="text-[8px] font-mono text-slate-500">
                            {new Date(log.timestamp).toLocaleTimeString([], { hour12: false })}
                          </span>
                       </div>
                       <div className="flex items-center justify-between">
                         <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest italic">{log.data?.risk_level || 'STABLE'}</span>
                         <span className="text-[10px] text-slate-500 font-mono flex items-center gap-1">
                           <Database className="h-2.5 w-2.5" /> {log.data?.threats?.length || 0}
                         </span>
                       </div>
                     </motion.div>
                   ))
                 ) : (
                   <div className="flex flex-col items-center justify-center h-full text-slate-700 opacity-30 py-10">
                     <Terminal className="h-10 w-10 mb-4" />
                     <span className="text-[10px] font-black uppercase tracking-[0.3em]">Audit Log Initializing...</span>
                   </div>
                 )}
               </AnimatePresence>
             </div>
          </Card>
        </div>
      </div>

      {/* Advanced Diagnostics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
         {[
           { label: "Shield_Status", val: "ACTIVE", icon: Lock, color: "text-emerald-400", glow: "cyan" },
           { label: "Neural_Monitoring", val: "NOMINAL", icon: Target, color: "text-accent-blue", glow: "cyan" },
           { label: "Packet_Orchestrator", val: "0.2ms", icon: Terminal, color: "text-slate-400", glow: "purple" },
           { label: "Threat_Vectors", val: "TRACKING", icon: ShieldAlert, color: "text-amber-400", glow: "amber" }
         ].map((stat, i) => (
           <Card key={i} glowColor={stat.glow} className="group cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest block mb-1">{stat.label}</span>
                  <span className={cn("text-xs font-black uppercase tracking-[0.2em] italic", stat.color)}>{stat.val}</span>
                </div>
                <stat.icon className="h-5 w-5 text-slate-700 group-hover:text-accent-blue transition-colors" />
              </div>
           </Card>
         ))}
      </div>
    </div>
  );
}


