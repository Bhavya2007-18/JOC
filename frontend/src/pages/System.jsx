import React, { useState, useMemo } from 'react';
import { systemApi, optimizerApi } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { useSystemData } from '../hooks/useSystemData';
import { SimulationPanel } from '../components/SimulationPanel';
import { motion, AnimatePresence } from 'framer-motion';
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
  
  const { stats, processes, loading: statsLoading, error: statsError, refresh } = useSystemData(5000);
  
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [fixing, setFixing] = useState({});

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await systemApi.analyze();
      setReport(response.data);
    } catch (err) {
      setError('Failed to analyze system. Please check if the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleProcessAction = async (pid, action, priority = null) => {
    setFixing(prev => ({ ...prev, [pid]: true }));
    try {
      if (action === 'kill') await optimizerApi.processAction.kill(pid);
      if (action === 'suspend') await optimizerApi.processAction.suspend(pid);
      if (action === 'resume') await optimizerApi.processAction.resume(pid);
      if (action === 'priority') await optimizerApi.processAction.priority(pid, priority);
      refresh();
    } catch (err) {
      console.error(`Failed to ${action} process ${pid}:`, err);
    } finally {
      setFixing(prev => ({ ...prev, [pid]: false }));
    }
  };

  const handleFix = async (issue) => {
    const issueId = issue.id || issue.target;
    setFixing(prev => ({ ...prev, [issueId]: true }));
    try {
      const action = issue.action || 'kill_process';
      const target = issue.target;
      await systemApi.fix(action, target);
      handleAnalyze();
    } catch (err) {
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
          <motion.div
            key="analysis"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-8"
          >
            {report ? (
              <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
                <Card title="Resource Snapshot" icon={ShieldAlert} className="lg:col-span-1 border-t-4 border-t-blue-500">
                  <div className="space-y-6 py-2">
                    <div className="flex items-center justify-between border-b border-gray-100 pb-4">
                      <span className="text-gray-600 flex items-center gap-2"><Cpu className="h-4 w-4" /> CPU</span>
                      <span className="font-bold text-gray-900">{report.summary?.cpu_usage}%</span>
                    </div>
                    <div className="flex items-center justify-between border-b border-gray-100 pb-4">
                      <span className="text-gray-600 flex items-center gap-2"><Database className="h-4 w-4" /> RAM</span>
                      <span className="font-bold text-gray-900">{report.summary?.ram_usage}%</span>
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
                                <p className="mt-1 text-gray-600 leading-relaxed">{issue.description}</p>
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
          </motion.div>
        )}

        {activeTab === 'processes' && (
          <motion.div
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
                            <span className="font-bold text-gray-900 truncate max-w-[150px]">{proc.name}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 font-mono text-sm text-gray-500">{proc.pid}</td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                             <div className="w-12 bg-gray-100 rounded-full h-1.5 overflow-hidden">
                                <div className="bg-blue-500 h-full" style={{ width: `${Math.min(100, proc.cpu_percent)}%` }} />
                             </div>
                             <span className="text-sm font-bold text-gray-700">{proc.cpu_percent}%</span>
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
                                onClick={() => handleProcessAction(proc.pid, 'suspend')}
                                disabled={fixing[proc.pid]}
                              >
                                <Pause className="h-3.5 w-3.5" />
                              </Button>
                              <Button 
                                variant="outline" 
                                size="sm" 
                                className="h-8 w-8 p-0" 
                                title="Kill"
                                onClick={() => handleProcessAction(proc.pid, 'kill')}
                                disabled={fixing[proc.pid]}
                              >
                                <XOctagon className="h-3.5 w-3.5 text-red-500" />
                              </Button>
                              <div className="flex flex-col gap-0.5 ml-1">
                                 <button 
                                   onClick={() => handleProcessAction(proc.pid, 'priority', 'high')}
                                   className="p-0.5 hover:bg-gray-100 rounded"
                                 >
                                    <ChevronUp className="h-3 w-3" />
                                 </button>
                                 <button 
                                   onClick={() => handleProcessAction(proc.pid, 'priority', 'low')}
                                   className="p-0.5 hover:bg-gray-100 rounded"
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
          </motion.div>
        )}

        {activeTab === 'simulation' && (
          <motion.div
            key="simulation"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <SimulationPanel />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
