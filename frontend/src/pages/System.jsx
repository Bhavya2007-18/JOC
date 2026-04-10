import React, { useState } from 'react';
import { systemApi, optimizerApi } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { useSystemData } from '../hooks/useSystemData';
import { SimulationPanel } from '../components/SimulationPanel';
import { motion as Motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle,
  Play,
  Settings,
  Cpu,
  Database,
  ListFilter,
  Terminal,
  ShieldAlert,
  Zap,
  Trash2,
  Pause,
  PlayCircle,
  XOctagon,
  ChevronUp,
  ChevronDown
} from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

export function System() {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'analysis';
  
  const { stats, processes, refresh } = useSystemData(5000);
  
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [fixing, setFixing] = useState({});
  const [actionPreview, setActionPreview] = useState(null);
  const [actionStatus, setActionStatus] = useState(null);
  const [optimizationPreview, setOptimizationPreview] = useState(null);
  const [optimizing, setOptimizing] = useState(false);

  const classifyUsage = (value) => {
    if (value < 50) return { label: 'NORMAL', tone: 'text-green-600', badge: 'bg-green-50 text-green-700' };
    if (value < 80) return { label: 'HIGH', tone: 'text-amber-600', badge: 'bg-amber-50 text-amber-700' };
    return { label: 'CRITICAL', tone: 'text-red-600', badge: 'bg-red-50 text-red-700' };
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setActionStatus(null);
    try {
      const response = await systemApi.safeAnalyze();
      if (response.status === 'success') {
        setReport(response.data);
      } else {
        setError(response.message || 'Failed to analyze system. Please check if the backend is running.');
      }
    } catch (err) {
      setError('Failed to analyze system. Please check if the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const requestProcessAction = async (proc, action, priority = null) => {
    if (stats && (stats.cpu.usage_percent > 95 || stats.memory.percent > 95)) {
      setActionStatus({
        type: 'error',
        message: 'Action blocked: system under stress. Try again when CPU and RAM load are lower.',
      });
      return;
    }
    if (proc.protected && action !== 'resume') {
      setActionStatus({
        type: 'error',
        message: `Action blocked. ${proc.name} is a protected system process.`,
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
      console.error(`Failed to preview ${action} for process ${proc.pid}:`, err);
      setActionStatus({
        type: 'error',
        message: `Failed to preview ${action} action.`,
      });
      setFixing(prev => ({ ...prev, [proc.pid]: false }));
    }
  };

  const confirmProcessAction = async () => {
    if (!actionPreview) return;
    const { proc, action, priority } = actionPreview;

    const risk = actionPreview.preview?.risk;
    if (risk === 'medium') {
      const ok = window.confirm('This action is medium risk and may affect running applications. Continue?');
      if (!ok) {
        setActionPreview(null);
        setFixing(prev => ({ ...prev, [proc.pid]: false }));
        return;
      }
    }
    if (risk === 'high') {
      const typed = window.prompt('High-risk action. Type CONFIRM to proceed.');
      if (typed !== 'CONFIRM') {
        setActionStatus({
          type: 'error',
          message: 'Action cancelled: confirmation phrase not entered.',
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
          message: result?.message || `Failed to apply ${action} to ${proc.name}.`,
        });
      }
    } catch (err) {
      console.error(`Failed to execute ${action} for process ${proc.pid}:`, err);
      setActionStatus({
        type: 'error',
        message: `Unexpected error while applying ${action} to ${proc.name}.`,
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
    { id: 'analysis', label: 'System Analysis', icon: Activity },
    { id: 'processes', label: 'Process Control', icon: ListFilter },
    { id: 'simulation', label: 'Simulation Engine', icon: Terminal },
  ];

  return (
    <div className="space-y-8 pb-20">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">System Control</h1>
          <p className="mt-2 text-lg text-gray-600">Advanced management and automated optimization of system resources.</p>
        </div>
      </header>

      {error && (
        <div className="flex items-center gap-3 rounded-xl bg-red-50 p-4 text-red-800 ring-1 ring-red-200">
          <XCircle className="h-5 w-5" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      {actionStatus && (
        <div
          className={`flex items-center justify-between rounded-xl px-4 py-3 text-sm font-medium ${
            actionStatus.type === 'success'
              ? 'bg-green-50 text-green-800 ring-1 ring-green-200'
              : 'bg-red-50 text-red-800 ring-1 ring-red-200'
          }`}
        >
          <span>{actionStatus.message}</span>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex p-1 bg-gray-100 rounded-xl w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setSearchParams({ tab: tab.id })}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-bold transition-all ${
              activeTab === tab.id 
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
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
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-8"
          >
            {report ? (
              <>
                <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
                  <Card title="Resource Snapshot" icon={ShieldAlert} className="lg:col-span-1 border-t-4 border-t-blue-500">
                    <div className="space-y-6 py-2">
                      <div className="flex items-center justify-between border-b border-gray-100 pb-4">
                        <span className="text-gray-600 flex items-center gap-2"><Cpu className="h-4 w-4" /> CPU</span>
                        <div className="text-right">
                          <span className="font-bold text-gray-900 block">{(report.summary?.cpu_percent ?? 0)}%</span>
                          {typeof (report.summary?.cpu_percent ?? 0) === 'number' && (
                            <span className={`mt-1 inline-flex rounded-full px-2 py-0.5 text-[10px] font-bold tracking-widest uppercase ${classifyUsage((report.summary?.cpu_percent ?? 0)).badge}`}>
                              {classifyUsage((report.summary?.cpu_percent ?? 0)).label}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center justify-between border-b border-gray-100 pb-4">
                        <span className="text-gray-600 flex items-center gap-2"><Database className="h-4 w-4" /> RAM</span>
                        <div className="text-right">
                          <span className="font-bold text-gray-900 block">{(report.summary?.memory_percent ?? 0)}%</span>
                          {typeof (report.summary?.memory_percent ?? 0) === 'number' && (
                            <span className={`mt-1 inline-flex rounded-full px-2 py-0.5 text-[10px] font-bold tracking-widest uppercase ${classifyUsage((report.summary?.memory_percent ?? 0)).badge}`}>
                              {classifyUsage((report.summary?.memory_percent ?? 0)).label}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600">Anomaly Index</span>
                        <span className={`font-bold ${report.issues?.length > 0 ? 'text-amber-600' : 'text-green-600'}`}>
                          {report.issues?.length || 0}
                        </span>
                      </div>
                    </div>
                  </Card>

                  <Card title="Intelligence Recommendations" description="Automated actions to optimize system stability" className="lg:col-span-2">
                    <div className="space-y-4">
                      {report.issues?.length > 0 ? (
                        report.issues.map((issue, idx) => (
                          <div key={idx} className="flex flex-col gap-4 rounded-xl border border-gray-100 bg-gray-50/50 p-6 hover:bg-white hover:shadow-sm transition-all">
                            <div className="flex items-start justify-between">
                              <div className="flex items-start gap-4">
                                <div className={`mt-1 rounded-lg p-2 ${issue.severity === 'high' ? 'bg-red-100 text-red-600' : 'bg-amber-100 text-amber-600'}`}>
                                  <AlertTriangle className="h-5 w-5" />
                                </div>
                                <div>
                                  <h4 className="text-lg font-bold text-gray-900">{issue.title || issue.issue_type}</h4>
                                  <p className="mt-1 text-gray-600 leading-relaxed">{issue.explanation || issue.description}</p>
                                  {issue.best_action && (
                                    <div className="mt-3 text-sm font-semibold text-blue-600">
                                      🔥 Recommended: {issue.best_action.action_type} → {issue.best_action.target}
                                    </div>
                                  )}
                                </div>
                              </div>
                              <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                                issue.severity === 'high' ? 'bg-red-50 text-red-700 ring-1 ring-red-200' : 'bg-amber-50 text-amber-700 ring-1 ring-amber-200'
                              }`}>
                                {issue.severity || 'Medium'}
                              </span>
                            </div>
                            <div className="flex justify-end pt-3 border-t border-gray-100/50">
                              <Button size="sm" onClick={() => handleFix(issue)} isLoading={fixing[issue.id || issue.target]} className="bg-green-600 hover:bg-green-700">
                                Execute Resolution
                              </Button>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="py-12 text-center">
                          <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-4" />
                          <h3 className="text-lg font-bold text-gray-900">Optimal Performance</h3>
                          <p className="text-gray-500">No critical performance issues detected.</p>
                        </div>
                      )}
                    </div>
                  </Card>
                </div>

                <Card title="Optimization Engine" description="Dry-run safe optimizations before applying" className="border-dashed border-blue-200">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                      <p className="text-sm text-gray-600">
                        Run a dry-run boost and cleanup to preview the impact before committing changes.
                      </p>
                    </div>
                    <div className="flex gap-3">
                      <Button
                        size="sm"
                        variant="outline"
                        isLoading={optimizing}
                        onClick={async () => {
                          setOptimizing(true);
                          setActionStatus(null);
                          try {
                            const res = await optimizerApi.safeBoost({ cpu_threshold: 50, max_processes: 5, dry_run: true });
                            if (res.status === 'success') {
                              setOptimizationPreview(res.data);
                            } else {
                              setActionStatus({
                                type: 'error',
                                message: res.message || 'Failed to preview boost operation.',
                              });
                            }
                            setActionStatus({
                              type: 'success',
                              message: 'Dry-run boost completed. Review preview before applying.',
                            });
                          } catch (err) {
                            console.error('Failed to preview boost:', err);
                            setActionStatus({
                              type: 'error',
                              message: 'Failed to preview boost operation.',
                            });
                          } finally {
                            setOptimizing(false);
                          }
                        }}
                      >
                        Preview Boost
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        isLoading={optimizing}
                        onClick={async () => {
                          setOptimizing(true);
                          setActionStatus(null);
                          try {
                            const res = await optimizerApi.safeCleanup({ dry_run: true });
                            if (res.status === 'success') {
                              setOptimizationPreview(res.data);
                            } else {
                              setActionStatus({
                                type: 'error',
                                message: res.message || 'Failed to preview cleanup operation.',
                              });
                            }
                            setActionStatus({
                              type: 'success',
                              message: 'Dry-run cleanup completed. Review preview before applying.',
                            });
                          } catch (err) {
                            console.error('Failed to preview cleanup:', err);
                            setActionStatus({
                              type: 'error',
                              message: 'Failed to preview cleanup operation.',
                            });
                          } finally {
                            setOptimizing(false);
                          }
                        }}
                      >
                        Preview Cleanup
                      </Button>
                    </div>
                  </div>

                  {optimizationPreview && (
                    <div className="mt-4 border-t border-gray-100 pt-4 space-y-3">
                      {typeof optimizationPreview.total_bytes_freed === 'number' && (
                        <p className="text-xs text-gray-600">
                          Estimated bytes freed: <span className="font-semibold">{optimizationPreview.total_bytes_freed}</span>
                        </p>
                      )}
                      {Array.isArray(optimizationPreview.processes) && optimizationPreview.processes.length > 0 && (
                        <div className="max-h-40 overflow-y-auto text-xs text-gray-700 space-y-1">
                          {optimizationPreview.processes.map((p) => (
                            <div key={p.pid} className="flex justify-between">
                              <span className="truncate max-w-[140px]">{p.name}</span>
                              <span>
                                {p.cpu_percent?.toFixed ? p.cpu_percent.toFixed(1) : p.cpu_percent}% → priority {p.new_priority}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                      <div className="flex justify-between items-center gap-2 pt-2">
                        {typeof optimizationPreview.risk === 'string' && (
                          <span className="text-[11px] font-semibold text-gray-500">
                            Risk: <span className="uppercase">{optimizationPreview.risk}</span>{' '}
                            {typeof optimizationPreview.confidence === 'number' &&
                              `(confidence ${(optimizationPreview.confidence * 100).toFixed(0)}%)`}
                          </span>
                        )}
                        <div className="flex justify-end gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setOptimizationPreview(null)}
                          >
                            Dismiss
                          </Button>
                          <Button
                            size="sm"
                            className="bg-blue-600 text-white"
                            onClick={async () => {
                              if (!optimizationPreview) return;
                              setOptimizing(true);
                              try {
                                if (Array.isArray(optimizationPreview.processes)) {
                                  await optimizerApi.boost({ cpu_threshold: 50, max_processes: 5, dry_run: false });
                                  setActionStatus({
                                    type: 'success',
                                    message: 'Optimization boost executed successfully.',
                                  });
                                  setOptimizationPreview(null);
                                  refresh();
                                } else {
                                  const resCleanup = await optimizerApi.cleanup({ dry_run: false });
                                  setActionStatus({
                                    type: 'success',
                                    message: `Cleanup executed. Freed ${resCleanup.data.total_bytes_freed} bytes.`,
                                  });
                                  setOptimizationPreview(null);
                                }
                              } catch (err) {
                                console.error('Failed to execute optimization:', err);
                                setActionStatus({
                                  type: 'error',
                                  message: 'Failed to execute optimization.',
                                });
                              } finally {
                                setOptimizing(false);
                              }
                            }}
                          >
                            Apply
                          </Button>
                        </div>
                      </div>
                    </div>
                  )}
                </Card>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-gray-100 shadow-sm">
                <div className="bg-blue-50 p-6 rounded-full mb-6">
                   <Activity className="h-12 w-12 text-blue-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900">Run Deep Analysis</h3>
                <p className="mt-2 text-gray-500 max-w-sm text-center">Initialize the JOC engine to scan for performance bottlenecks and security anomalies.</p>
                <Button size="lg" onClick={handleAnalyze} isLoading={loading} className="mt-8 px-12 h-14 text-lg">
                   Analyze System
                </Button>
              </div>
            )}
          </Motion.div>
        )}

        {activeTab === 'processes' && (
          <Motion.div
            key="processes"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <Card title="Active Processes" description="Real-time resource allocation by application">
              <div className="mt-6 overflow-hidden rounded-xl border border-gray-100">
                <table className="w-full text-left">
                  <thead className="bg-gray-50 border-b border-gray-100">
                    <tr>
                      <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Process</th>
                      <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">PID</th>
                      <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">CPU</th>
                      <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Memory</th>
                      <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 bg-white">
                    {processes.map((proc) => (
                      <tr key={proc.pid} className="hover:bg-gray-50/50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="h-8 w-8 rounded bg-gray-100 flex items-center justify-center text-gray-500">
                               <Settings className="h-4 w-4" />
                            </div>
                            <div className="flex flex-col">
                              <span className="font-bold text-gray-900 truncate max-w-[150px]">
                                {proc.name}
                              </span>
                              {proc.protected && (
                                <span className="mt-0.5 inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest text-gray-500">
                                  System Protected
                                </span>
                              )}
                              {!proc.protected && proc.cpu_percent < 20 && proc.memory_percent < 10 && (
                                <span className="mt-0.5 inline-flex items-center rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest text-emerald-700">
                                  Safe To Kill
                                </span>
                              )}
                              {!proc.protected && proc.cpu_percent >= 70 && (
                                <span className="mt-0.5 inline-flex items-center rounded-full bg-red-50 px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest text-red-700">
                                  High Impact
                                </span>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 font-mono text-sm text-gray-500">{proc.pid}</td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                             <div className="w-12 bg-gray-100 rounded-full h-1.5 overflow-hidden">
                                <div className="bg-blue-500 h-full" style={{ width: `${Math.min(100, proc.cpu_percent)}%` }} />
                             </div>
                             <span className="text-sm font-bold text-gray-700">
                               {proc.cpu_percent}%{' '}
                               {proc.trend === 'up' ? '↑' : proc.trend === 'down' ? '↓' : '→'}
                             </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-700">{proc.memory_percent}%</td>
                        <td className="px-6 py-4 text-right">
                           <div className="flex items-center justify-end gap-1">
                              <Button 
                                variant="outline" 
                                size="sm" 
                                className="h-8 w-8 p-0" 
                                title="Suspend"
                                onClick={() => requestProcessAction(proc, 'suspend')}
                                disabled={fixing[proc.pid] || proc.protected}
                              >
                                <Pause className="h-3.5 w-3.5" />
                              </Button>
                              <Button 
                                variant="outline" 
                                size="sm" 
                                className="h-8 w-8 p-0" 
                                title="Kill"
                                onClick={() => requestProcessAction(proc, 'kill')}
                                disabled={fixing[proc.pid] || proc.protected}
                              >
                                <XOctagon className="h-3.5 w-3.5 text-red-500" />
                              </Button>
                              <div className="flex flex-col gap-0.5 ml-1">
                                 <button 
                                   onClick={() => requestProcessAction(proc, 'priority', 'high')}
                                   className="p-0.5 hover:bg-gray-100 rounded"
                                   disabled={fixing[proc.pid] || proc.protected}
                                 >
                                    <ChevronUp className="h-3 w-3" />
                                 </button>
                                 <button 
                                   onClick={() => requestProcessAction(proc, 'priority', 'low')}
                                   className="p-0.5 hover:bg-gray-100 rounded"
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
              <div className="mt-6 rounded-2xl border border-blue-100 bg-blue-50/40 p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-widest text-blue-600">
                      Dry Run Preview
                    </p>
                    <p className="mt-1 text-sm text-blue-900">
                      {actionPreview.preview?.message || 'Action would be applied to this process.'}
                    </p>
                    <p className="mt-2 text-xs text-blue-700">
                      Target: {actionPreview.proc.name} (PID {actionPreview.proc.pid})
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={cancelProcessAction}>
                      Cancel
                    </Button>
                    <Button size="sm" onClick={confirmProcessAction} className="bg-blue-600 text-white">
                      Confirm
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </Motion.div>
        )}

        {activeTab === 'simulation' && (
          <Motion.div
            key="simulation"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <SimulationPanel />
          </Motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
