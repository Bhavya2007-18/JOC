import React, { useState } from 'react';
import { systemApi, optimizerApi } from '../api/client';
import { useSystemMode } from '../context/SystemModeContext';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { useSystemData } from '../hooks/useSystemData';
import { SimulationPanel } from '../components/SimulationPanel';
import { DeepScanAnimation } from '../components/DeepScanAnimation';
import { motion as Motion, AnimatePresence } from 'framer-motion';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Settings,
  Cpu,
  Database,
  ListFilter,
  Terminal,
  ShieldAlert,
  Pause,
  XOctagon,
  ChevronUp,
  ChevronDown
} from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { cn } from '../utils/cn';

export function System() {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'analysis';

  const { stats, processes, refresh, causalGraph } = useSystemData(5000);
  const { systemMode } = useSystemMode();

  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [fixing, setFixing] = useState({});
  const [actionPreview, setActionPreview] = useState(null);
  const [actionStatus, setActionStatus] = useState(null);
  const [optimizationPreview, setOptimizationPreview] = useState(null);
  const [optimizing, setOptimizing] = useState(false);

  const classifyUsage = (value) => {
    if (value < 50) return { label: 'OPTIMAL', tone: 'text-emerald-500', badge: 'nm-inset text-emerald-500 bg-slate-900 border-emerald-900/30' };
    if (value < 80) return { label: 'WARNING', tone: 'text-amber-500', badge: 'nm-inset text-amber-500 bg-slate-900 border-amber-900/30' };
    return { label: 'CRITICAL', tone: 'text-red-500', badge: 'nm-inset text-red-500 bg-slate-900 border-red-900/30' };
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setReport(null); // Clear previous report to show animation
    setError(null);
    setActionStatus(null);
    
    // Ensure animation plays for at least 3.5 seconds for visual weight
    const minTimePromise = new Promise(resolve => setTimeout(resolve, 3500));
    
    try {
      const [response] = await Promise.all([
        systemApi.safeAnalyze(),
        minTimePromise
      ]);
      
      if (response.status === 'success') {
        setReport(response.data);
      } else {
        setError(response.message || 'Analysis Node Failure: Backend Unreachable');
      }
    } catch (err) {
      setError('Analysis Node Failure: Internal Link Severed');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const requestProcessAction = async (proc, action, priority = null) => {
    if (stats && (stats.cpu.usage_percent > 95 || stats.memory.percent > 95)) {
      setActionStatus({
        type: 'error',
        message: 'Action Blocked: System Stress detected. Authorization restricted.',
      });
      return;
    }
    if (proc.protected && action !== 'resume') {
      setActionStatus({
        type: 'error',
        message: `Security Override: ${proc.name} is a protected core process.`,
      });
      return;
    }

    setFixing(prev => ({ ...prev, [proc.pid]: true }));
    setActionStatus(null);
    try {
      let preview;
      if (action === 'kill') {
        const res = await optimizerApi.processAction.kill(proc.pid, true);
        preview = res.data;
      } else if (action === 'suspend') {
        const res = await optimizerApi.processAction.suspend(proc.pid, true);
        preview = res.data;
      } else if (action === 'resume') {
        const res = await optimizerApi.processAction.resume(proc.pid, true);
        preview = res.data;
      } else if (action === 'priority') {
        const res = await optimizerApi.processAction.priority(proc.pid, priority, true);
        preview = res.data;
      }

      setActionPreview({
        proc,
        action,
        priority,
        preview,
      });
    } catch (err) {
      console.error(`Link failure during ${action} preview:`, err);
      setActionStatus({
        type: 'error',
        message: 'Protocol Preview Error: Failed to simulate outcome.',
      });
      setFixing(prev => ({ ...prev, [proc.pid]: false }));
    }
  };

  const confirmProcessAction = async () => {
    if (!actionPreview) return;
    const { proc, action, priority } = actionPreview;

    const risk = actionPreview.preview?.risk;
    if (risk === 'medium') {
      const ok = window.confirm('DANGER: Medium-risk protocol requested. Authorization required. Continue?');
      if (!ok) {
        setActionPreview(null);
        setFixing(prev => ({ ...prev, [proc.pid]: false }));
        return;
      }
    }
    if (risk === 'high') {
      const typed = window.prompt('CRITICAL THREAT: High-risk action. Type CONFIRM_EXECUTION to bypass safety interlinks.');
      if (typed !== 'CONFIRM_EXECUTION') {
        setActionStatus({
          type: 'error',
          message: 'Protocol Aborted: Authorization Phrase Mismatch.',
        });
        setActionPreview(null);
        setFixing(prev => ({ ...prev, [proc.pid]: false }));
        return;
      }
    }

    try {
      let res;
      if (action === 'kill') {
        res = await optimizerApi.processAction.kill(proc.pid, false);
      } else if (action === 'suspend') {
        res = await optimizerApi.processAction.suspend(proc.pid, false);
      } else if (action === 'resume') {
        res = await optimizerApi.processAction.resume(proc.pid, false);
      } else if (action === 'priority') {
        res = await optimizerApi.processAction.priority(proc.pid, priority, false);
      }

      const result = res?.data;
      if (result?.success || result?.dry_run) {
        setActionStatus({
          type: 'success',
          message: result?.dry_run
            ? `Simulated action (DRY RUN): ${action} on ${proc.name} (PID ${proc.pid}).`
            : `Action ${action} applied to ${proc.name} (PID ${proc.pid}).`,
        });
        refresh();
      } else {
        setActionStatus({
          type: 'error',
          message: result?.message || `PROTOCOL_FAILURE: Target ${proc.name} resisted intervention.`,
        });
      }
    } catch (err) {
      console.error(`Unexpected process error:`, err);
      setActionStatus({
        type: 'error',
        message: 'PROTOCOL_CRASH: Unexpected feedback loop during execution.',
      });
    } finally {
      setFixing(prev => ({ ...prev, [proc.pid]: false }));
      setActionPreview(null);
    }
  };

  const cancelProcessAction = () => {
    if (actionPreview?.proc) {
      setFixing(prev => ({ ...prev, [actionPreview.proc.pid]: false }));
    }
    setActionPreview(null);
  };

  const handleFix = async (issue) => {
    const issueId = issue.id || issue.target;
    setFixing(prev => ({ ...prev, [issueId]: true }));
    try {
      const action = issue.best_action?.action_type || issue.action || 'kill_process';
      const target = issue.best_action?.target || issue.target;
      const pid =
        issue.best_action?.pid ??
        issue.pid ??
        issue.target_pid ??
        issue.evidence?.fix_action?.pid;

      if (action === 'kill_process' && !pid) {
        throw new Error('PID required for safe process termination');
      }

      const res = await systemApi.fix(action, target, pid);

      if (res?.data?.success || res?.data?.dry_run) {
        setActionStatus({
          type: 'success',
          message: res?.data?.dry_run
            ? `Simulated fix applied (DRY RUN): ${action}`
            : `Fix applied successfully: ${action}`,
        });
      } else {
        setActionStatus({
          type: 'error',
          message: res?.data?.message || 'Failed to apply fix',
        });
      }

      handleAnalyze();
    } catch (err) {
      setActionStatus({
        type: 'error',
        message: 'Failed to apply fix',
      });
      console.error('Failed to fix issue:', err);
    } finally {
      setFixing(prev => ({ ...prev, [issueId]: false }));
    }
  };

  const tabs = [
    { id: 'analysis', label: 'Analysis Node', icon: Activity },
    { id: 'processes', label: 'Process Control', icon: ListFilter },
    { id: 'simulation', label: 'Battle Station', icon: Terminal },
  ];

  return (
    <div className="space-y-10 pb-20">
      <header className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic">System_Command</h1>
          <p className="mt-2 text-slate-400 font-mono text-sm tracking-widest uppercase opacity-70">Deep Integration Hub // Neural_Net_Sync</p>
        </div>
      </header>

      {error && (
        <div className="flex items-center gap-4 rounded-2xl nm-flat bg-red-950/20 p-6 text-red-400 border border-red-900/30">
          <XCircle className="h-6 w-6" />
          <p className="text-sm font-black tracking-widest uppercase">{error}</p>
        </div>
      )}

      {actionStatus && (
        <div
          className={cn(
            'flex items-center justify-between rounded-2xl px-6 py-4 text-xs font-black uppercase tracking-[0.2em]',
            actionStatus.type === 'success'
              ? 'nm-flat bg-emerald-950/20 text-emerald-400 border border-emerald-900/30'
              : 'nm-flat bg-red-950/20 text-red-400 border border-red-900/30'
          )}
        >
          <span>{actionStatus.message}</span>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex p-2 nm-inset bg-slate-900 border border-slate-800 rounded-3xl w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setSearchParams({ tab: tab.id })}
            className={cn(
              'flex items-center gap-4 px-8 py-3 rounded-2xl text-[10px] font-black uppercase tracking-[0.3em] transition-all duration-300',
              activeTab === tab.id
                ? 'nm-convex text-accent-blue bg-slate-800'
                : 'text-slate-500 hover:text-slate-300'
            )}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'analysis' && (
          <Motion.div
            key="analysis"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.02 }}
            className="space-y-10"
          >
            {report ? (
              <>
                <div className="grid grid-cols-1 gap-10 lg:grid-cols-3">
                  <Card title="Telemetry Snapshot" icon={ShieldAlert} className="lg:col-span-1 border-t-2 border-t-accent-blue">
                    <div className="space-y-8 py-4">
                      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
                        <span className="text-slate-400 font-mono uppercase text-xs flex items-center gap-3"><Cpu className="h-4 w-4 text-accent-blue" /> CPU_LOAD</span>
                        <div className="text-right">
                          <span className="font-black text-white font-mono text-xl block">{(report.summary?.cpu_percent ?? 0)}%</span>
                          {typeof (report.summary?.cpu_percent ?? 0) === 'number' && (
                            <span className={`mt-2 inline-flex rounded-xl px-3 py-1 text-[9px] font-black tracking-widest uppercase ${classifyUsage((report.summary?.cpu_percent ?? 0)).badge}`}>
                              {classifyUsage((report.summary?.cpu_percent ?? 0)).label}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
                        <span className="text-slate-400 font-mono uppercase text-xs flex items-center gap-3"><Database className="h-4 w-4 text-purple-400" /> MEM_ADDR</span>
                        <div className="text-right">
                          <span className="font-black text-white font-mono text-xl block">{(report.summary?.memory_percent ?? 0)}%</span>
                          {typeof (report.summary?.memory_percent ?? 0) === 'number' && (
                            <span className={`mt-2 inline-flex rounded-xl px-3 py-1 text-[9px] font-black tracking-widest uppercase ${classifyUsage((report.summary?.memory_percent ?? 0)).badge}`}>
                              {classifyUsage((report.summary?.memory_percent ?? 0)).label}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400 font-mono uppercase text-xs">DECODED_ISSUES</span>
                        <span className={cn('font-black font-mono text-xl', report.issues?.length > 0 ? 'text-amber-500' : 'text-emerald-500')}>
                          {report.issues?.length || 0}
                        </span>
                      </div>
                    </div>
                  </Card>

                  <Card title="Neural Recommendations" description="Automated protocols for engine stability" className="lg:col-span-2">
                  <Motion.div 
                    initial="hidden"
                    animate="visible"
                    variants={{
                      visible: { transition: { staggerChildren: 0.15 } }
                    }}
                    className="space-y-6 mt-6"
                  >
                    {report.issues?.length > 0 ? (
                      report.issues.map((issue, idx) => (
                        <Motion.div 
                          key={idx} 
                          variants={{
                            hidden: { opacity: 0, y: 20, scale: 0.98 },
                            visible: { opacity: 1, y: 0, scale: 1 }
                          }}
                          whileHover={{ y: -4, scale: 1.01 }}
                          transition={{ type: "spring", stiffness: 400, damping: 25 }}
                          className="nm-flat bg-slate-900 border border-slate-800 rounded-3xl p-8 hover:nm-convex transition-all group relative overflow-hidden"
                        >
                          {issue.severity === 'high' && (
                            <div className="absolute top-0 left-0 w-1 h-full bg-red-500/40 animate-pulse" />
                          )}
                          <div className="flex items-start justify-between relative z-10">
                            <div className="flex items-start gap-6">
                              <div className={cn(
                                'mt-1 nm-inset rounded-2xl p-4 bg-slate-950 transition-colors duration-500', 
                                issue.severity === 'high' ? 'text-red-500 group-hover:text-red-400' : 'text-amber-400 group-hover:text-amber-300'
                              )}>
                                <AlertTriangle className="h-6 w-6" />
                              </div>
                              <div>
                                <h4 className="text-lg font-black tracking-tight text-white uppercase">{issue.title || issue.issue_type}</h4>
                                <p className="mt-2 text-slate-400 text-sm leading-relaxed italic">{issue.explanation || issue.description}</p>
                                {issue.best_action && (
                                  <div className="mt-4 text-xs font-black tracking-widest uppercase text-accent-blue nm-inset bg-slate-900 w-fit px-3 py-1.5 rounded-lg">
                                    🔥 STRATEGY: {issue.best_action.action_type} → {issue.best_action.target}
                                  </div>
                                )}
                              </div>
                            </div>
                            <span className={cn('px-3 py-1 rounded-xl text-[9px] font-black uppercase tracking-[0.2em]',
                              issue.severity === 'high' ? 'nm-inset bg-red-950 text-red-500 border border-red-900/50' : 'nm-inset bg-amber-950 text-amber-500 border border-amber-900/50'
                            )}>
                              SEV_{issue.severity || 'MED'}
                            </span>
                          </div>
                          <div className="flex justify-end mt-8 relative z-10">
                            <Button size="sm" onClick={() => handleFix(issue)} isLoading={fixing[issue.id || issue.target]} className="nm-convex bg-slate-900 text-emerald-500 border-none hover:text-emerald-400">
                              EXECUTE_FIX_PROTOCOL
                            </Button>
                          </div>
                        </Motion.div>
                      ))
                    ) : (
                      <Motion.div 
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="py-20 text-center nm-inset bg-slate-900/30 rounded-3xl border border-slate-800 flex flex-col items-center"
                      >
                        <div className="nm-flat p-6 rounded-full bg-slate-900 mb-6">
                          <CheckCircle2 className="h-12 w-12 text-emerald-500 drop-shadow-[0_0_8px_#10b981]" />
                        </div>
                        <h3 className="text-2xl font-black text-white uppercase tracking-tighter">Engine Optimized</h3>
                        <p className="text-slate-500 font-mono text-xs mt-2 uppercase tracking-widest">No critical latency vectors detected</p>
                      </Motion.div>
                    )}
                  </Motion.div>
                  </Card>
                </div>
                
                {causalGraph && causalGraph.edges && causalGraph.edges.length > 0 && (
                  <Card title="Causal Topological Graph" description="Root cause relationship tracker" className="mt-8 border-l-2 border-l-purple-500">
                    <div className="flex flex-wrap gap-4 mt-6">
                      {causalGraph.edges.map((edge, i) => (
                        <div key={i} className="flex items-center gap-3 nm-flat bg-slate-900 px-4 py-2 rounded-2xl">
                          <span className="font-mono text-xs text-white bg-slate-800 px-2 py-1 rounded truncate max-w-[150px]">{edge.from}</span>
                          <span className="text-slate-500 text-[10px] uppercase font-black tracking-widest flex items-center gap-1">
                             —[ {(edge.weight * 100).toFixed(0)}% ]→
                          </span>
                          <span className="font-mono text-xs text-purple-400 bg-purple-900/20 border border-purple-900/50 px-2 py-1 rounded">{edge.to}</span>
                        </div>
                      ))}
                    </div>
                    {causalGraph.root_cause_node && (
                      <div className="mt-6 text-sm text-slate-400 font-mono italic">
                        <Database className="h-4 w-4 inline mr-2 text-red-500"/>
                        Topological Root Cause Isolated: <span className="text-white font-black">{causalGraph.root_cause_node}</span>
                      </div>
                    )}
                  </Card>
                )}
              </>
            ) : loading ? (
              <DeepScanAnimation />
            ) : (
              <div className="flex flex-col items-center justify-center py-32 nm-flat bg-slate-900 rounded-[3rem] border border-slate-800">
                <div className="nm-inset p-10 rounded-full bg-slate-950 mb-10 group cursor-pointer hover:nm-flat transition-all" onClick={handleAnalyze}>
                  <Motion.div 
                    whileHover={{ scale: 1.1, rotate: 180 }}
                    transition={{ type: "spring", stiffness: 200 }}
                  >
                    <Activity className="h-20 w-20 text-accent-blue" />
                  </Motion.div>
                </div>
                <h3 className="text-4xl font-black text-white uppercase italic tracking-tighter">Deep Scan Required</h3>
                <p className="mt-4 text-slate-500 font-mono text-sm uppercase tracking-[0.3em] max-w-md text-center opacity-60">Initialize Neural Diagnostics to identify performance bottlenecks and security leaks.</p>
                <Button size="lg" onClick={handleAnalyze} isLoading={loading} className="mt-12 px-16 h-16 text-xl tracking-[0.4em] nm-convex bg-slate-900 border-none text-white">
                  RUN_SCAN
                </Button>
              </div>
            )}
          </Motion.div>
        )}

        {activeTab === 'processes' && (
          <Motion.div
            key="processes"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.02 }}
          >
            <Card title="Active Threads" description="Real-time resource allocation telemetry" icon={ListFilter}>
              <div className="mt-8 overflow-hidden rounded-[2rem] nm-inset bg-slate-950 border border-slate-900">
                <table className="w-full text-left border-collapse">
                  <thead className="bg-slate-900 border-b border-slate-800">
                    <tr>
                      <th className="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Target_Process</th>
                      <th className="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">PID</th>
                      <th className="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">CPU_LOAD</th>
                      <th className="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">RAM_ALLOC</th>
                      <th className="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">Interrupts</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {processes.map((proc) => (
                      <tr key={proc.pid} className="group hover:bg-slate-900/30 transition-all">
                        <td className="px-8 py-5">
                          <div className="flex items-center gap-4">
                            <div className="h-10 w-10 nm-flat rounded-xl bg-slate-900 flex items-center justify-center text-slate-500 group-hover:text-accent-blue transition-colors">
                              <Settings className="h-5 w-5" />
                            </div>
                            <div className="flex flex-col">
                              <span className="font-black text-white truncate max-w-[200px] text-sm uppercase tracking-tight">
                                {proc.name}
                              </span>
                              {proc.protected ? (
                                <span className="mt-1 inline-flex items-center rounded-lg nm-inset bg-slate-900 px-2 py-0.5 text-[8px] font-black uppercase tracking-widest text-slate-500">
                                  CORE_PROTECT
                                </span>
                              ) : proc.cpu_percent >= 70 ? (
                                <span className="mt-1 inline-flex items-center rounded-lg nm-inset bg-red-950 px-2 py-0.5 text-[8px] font-black uppercase tracking-widest text-red-500">
                                  HIGH_INTERRUPT
                                </span>
                              ) : (
                                <span className="mt-1 inline-flex items-center rounded-lg nm-inset bg-emerald-950 px-2 py-0.5 text-[8px] font-black uppercase tracking-widest text-emerald-500">
                                  STABLE_NODE
                                </span>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="px-8 py-5 font-mono text-xs text-slate-500 tracking-tighter">[{proc.pid}]</td>
                        <td className="px-8 py-5">
                          <div className="flex items-center gap-4">
                            <div className="w-20 nm-inset bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
                              <div className="bg-accent-blue h-full shadow-[0_0_8px_#3b82f6]" style={{ width: `${Math.min(100, proc.cpu_percent)}%` }} />
                            </div>
                            <span className="text-xs font-black text-white font-mono">
                              {proc.cpu_percent}%{' '}
                              {proc.trend === 'up' ? '▲' : proc.trend === 'down' ? '▼' : '▬'}
                            </span>
                          </div>
                        </td>
                        <td className="px-8 py-5 text-xs font-black text-slate-400 font-mono">{proc.memory_percent}%</td>
                        <td className="px-8 py-5 text-right">
                          <div className="flex items-center justify-end gap-3">
                            <Button
                              variant="outline"
                              size="sm"
                              className="h-10 w-10 p-0 nm-flat bg-slate-900 rounded-xl"
                              title="Suspend Thread"
                              onClick={() => requestProcessAction(proc, 'suspend')}
                              disabled={fixing[proc.pid] || proc.protected}
                            >
                              <Pause className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              className="h-10 w-10 p-0 nm-flat bg-slate-900 rounded-xl group/kill"
                              title="Terminate Thread"
                              onClick={() => requestProcessAction(proc, 'kill')}
                              disabled={fixing[proc.pid] || proc.protected}
                            >
                              <XOctagon className="h-4 w-4 text-red-700 group-hover/kill:text-red-500" />
                            </Button>
                            <div className="flex flex-col gap-1 ml-2">
                              <button
                                onClick={() => requestProcessAction(proc, 'priority', 'high')}
                                className="nm-convex bg-slate-900 p-1 hover:text-accent-blue rounded text-slate-600 transition-colors"
                                disabled={fixing[proc.pid] || proc.protected}
                              >
                                <ChevronUp className="h-3 w-3" />
                              </button>
                              <button
                                onClick={() => requestProcessAction(proc, 'priority', 'low')}
                                className="nm-convex bg-slate-900 p-1 hover:text-accent-blue rounded text-slate-600 transition-colors"
                                disabled={fixing[proc.pid] || proc.protected}
                              >
                                <ChevronDown className="h-3 w-3" />
                              </button>
                            </div>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
            {actionPreview && (
              <div className="mt-10 rounded-[2rem] nm-flat bg-slate-900 border border-accent-blue/40 p-10 flex flex-col md:flex-row items-center justify-between gap-10">
                <div className="flex-1">
                  <p className="text-[10px] font-black uppercase tracking-[0.4em] text-accent-blue inline-block nm-inset px-4 py-1 rounded-full mb-4">
                    Neural_Simulation_Link
                  </p>
                  <p className="text-xl font-bold text-white tracking-tight leading-relaxed">
                    {actionPreview.preview?.message || 'Protocol outcome verified. Authorization required for state mutation.'}
                  </p>
                  <p className="mt-4 text-xs font-mono text-slate-500 uppercase">
                    Target_Entity: <span className="text-white">{actionPreview.proc.name}</span> // PID: <span className="text-white">{actionPreview.proc.pid}</span>
                  </p>
                </div>
                <div className="flex gap-4">
                  <Button size="md" variant="secondary" onClick={cancelProcessAction}>
                    ABORT_COMMAND
                  </Button>
                  <Button size="md" onClick={confirmProcessAction} className="bg-accent-blue text-white nm-convex border-none">
                    CONFIRM_EXECUTION
                  </Button>
                </div>
              </div>
            )}
          </Motion.div>
        )}

        {activeTab === 'simulation' && (
          <Motion.div
            key="simulation"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.02 }}
          >
            <SimulationPanel />
          </Motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
