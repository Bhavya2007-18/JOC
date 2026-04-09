import React, { useState, useEffect } from 'react';
import { systemApi, intelligenceApi } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { useSimulation } from '../hooks/useSimulation';
import { 
  History as HistoryIcon, 
  RotateCcw, 
  CheckCircle2, 
  Clock, 
  Search,
  AlertTriangle,
  Info,
  Calendar,
  Terminal,
  Activity,
  FileText
} from 'lucide-react';
import { motion as Motion, AnimatePresence } from 'framer-motion';

export function History() {
  const [reverting, setReverting] = useState({});
  const [status, setStatus] = useState(null);
  const { history: simHistory, fetchHistory: fetchSimHistory } = useSimulation();
  const [activeTab, setActiveTab] = useState('actions');

  const [history] = useState([
    { id: 'act_1', action: 'Kill Process', target: 'chrome.exe', timestamp: '2026-04-07 14:30', status: 'Completed', revertible: true },
    { id: 'act_2', action: 'Clean Junk', target: 'Temp Files', timestamp: '2026-04-07 12:15', status: 'Completed', revertible: false },
    { id: 'act_3', action: 'Tweak Execute', target: 'Gaming Boost', timestamp: '2026-04-07 10:00', status: 'Completed', revertible: true },
  ]);

  const [behavior, setBehavior] = useState(null);

  useEffect(() => {
    fetchSimHistory();
  }, [fetchSimHistory]);

  useEffect(() => {
    let mounted = true;
    intelligenceApi.safePatterns(1440).then((res) => {
      if (!mounted || res.status !== 'success') return;
      const data = res.data;
      setBehavior({
        avgCpu: data.average_cpu_percent,
        avgMem: data.average_memory_percent,
        peakHours: data.peak_hours || [],
      });
    });
    return () => {
      mounted = false;
    };
  }, []);

  const handleRevert = async (actionId) => {
    setReverting(prev => ({ ...prev, [actionId]: true }));
    setStatus(null);
    try {
      const response = await systemApi.revertAction(actionId);
      setStatus({ 
        type: 'success', 
        message: response.data.message || `Successfully reverted action ${actionId}` 
      });
    } catch (err) {
      setStatus({ 
        type: 'error', 
        message: `Failed to revert action. Please check if the backend is running.` 
      });
      console.error(err);
    } finally {
      setReverting(prev => ({ ...prev, [actionId]: false }));
    }
  };

  return (
    <div className="space-y-8 pb-20">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Operation Logs</h1>
          <p className="mt-2 text-lg text-gray-600">Audit trail of all autonomous and manual system modifications.</p>
        </div>
      </header>

      {behavior && (
        <Card className="border-none shadow-sm ring-1 ring-blue-100 bg-blue-50/40">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h2 className="text-sm font-bold text-blue-900 uppercase tracking-widest">Behavior Insights</h2>
              <p className="mt-1 text-sm text-blue-900">
                You typically use around {behavior.avgCpu?.toFixed(1) ?? 0}% CPU and {behavior.avgMem?.toFixed(1) ?? 0}% memory across the day.
              </p>
            </div>
            {behavior.peakHours.length > 0 && (
              <div className="text-xs text-blue-900">
                Peak hours:{' '}
                {behavior.peakHours
                  .slice(0, 2)
                  .map((h) => `${h.hour}:00`)
                  .join(' – ')}
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Tab Navigation */}
      <div className="flex p-1 bg-gray-100 rounded-xl w-fit">
        <button
          onClick={() => setActiveTab('actions')}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-bold transition-all ${
            activeTab === 'actions' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <Activity className="h-4 w-4" />
          System Actions
        </button>
        <button
          onClick={() => setActiveTab('simulations')}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-bold transition-all ${
            activeTab === 'simulations' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <Terminal className="h-4 w-4" />
          Simulation History
        </button>
      </div>

      {status && (
        <Motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`flex items-center gap-4 rounded-xl p-6 shadow-sm ring-1 ring-inset ${
            status.type === 'success' ? 'bg-green-50 text-green-800 ring-green-200' : 'bg-red-50 text-red-800 ring-red-200'
          }`}
        >
          {status.type === 'success' ? <CheckCircle2 className="h-6 w-6" /> : <AlertTriangle className="h-6 w-6" />}
          <p className="font-bold text-lg">{status.message}</p>
        </Motion.div>
      )}

      <AnimatePresence mode="wait">
        {activeTab === 'actions' ? (
          <motion.div
            key="actions"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <Card className="overflow-hidden border-none shadow-sm ring-1 ring-gray-200">
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-gray-100 bg-gray-50/50">
                      <th className="px-6 py-4 text-xs font-black uppercase tracking-widest text-gray-500">Action</th>
                      <th className="px-6 py-4 text-xs font-black uppercase tracking-widest text-gray-500">Target</th>
                      <th className="px-6 py-4 text-xs font-black uppercase tracking-widest text-gray-500">Timestamp</th>
                      <th className="px-6 py-4 text-xs font-black uppercase tracking-widest text-gray-500 text-right">Operation</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {history.map((item) => (
                      <tr key={item.id} className="group hover:bg-blue-50/30 transition-all duration-200">
                        <td className="px-6 py-5">
                          <div className="flex items-center gap-3">
                            <div className="rounded-lg bg-blue-100 p-2 group-hover:bg-white shadow-sm transition-all duration-300">
                              <HistoryIcon className="h-4 w-4 text-blue-600" />
                            </div>
                            <span className="font-bold text-gray-900">{item.action}</span>
                          </div>
                        </td>
                        <td className="px-6 py-5">
                          <span className="text-sm font-bold text-gray-500 group-hover:text-blue-700 transition-colors">{item.target}</span>
                        </td>
                        <td className="px-6 py-5">
                          <div className="flex flex-col">
                            <span className="text-sm font-bold text-gray-700 flex items-center gap-1.5">
                              <Calendar className="h-3.5 w-3.5 text-gray-400" />
                              {item.timestamp.split(' ')[0]}
                            </span>
                            <span className="text-xs font-medium text-gray-400 flex items-center gap-1.5 mt-0.5">
                              <Clock className="h-3.5 w-3.5" />
                              {item.timestamp.split(' ')[1]}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-5 text-right">
                          {item.revertible && (
                            <Button 
                              size="sm" 
                              variant="outline" 
                              onClick={() => handleRevert(item.id)}
                              isLoading={reverting[item.id]}
                              className="px-4 font-black uppercase tracking-widest group-hover:bg-white group-hover:border-blue-500 group-hover:text-blue-600 shadow-sm"
                            >
                              <RotateCcw className="mr-1.5 h-3.5 w-3.5" />
                              Revert
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </motion.div>
        ) : (
          <motion.div
            key="simulations"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            {simHistory.length > 0 ? (
              simHistory.map((report, idx) => (
                <Card key={idx} title={`Run #${simHistory.length - idx}`} icon={Terminal} className="hover:shadow-md transition-shadow">
                   <div className="flex justify-between items-center mb-4">
                      <div className="flex flex-col">
                         <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Type</span>
                         <span className="text-sm font-bold text-gray-900">{report.simulation_type}</span>
                      </div>
                      <div className="text-right">
                         <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Score</span>
                         <div className={`text-xl font-black ${
                           report.score >= 80 ? 'text-green-600' : report.score >= 50 ? 'text-amber-600' : 'text-red-600'
                         }`}>{report.score}</div>
                      </div>
                   </div>
                   <div className="space-y-2 mb-4">
                      <div className="flex items-center justify-between text-xs">
                         <span className="text-gray-500">Anomalies Detected</span>
                         <span className="font-bold text-gray-900">{report.anomalies_detected.length}</span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                         <span className="text-gray-500">Response Actions</span>
                         <span className="font-bold text-gray-900">{report.response_actions.length}</span>
                      </div>
                   </div>
                   <Button variant="outline" size="sm" className="w-full text-[10px] font-bold uppercase tracking-widest">
                      <FileText className="h-3 w-3 mr-2" />
                      View Full Report
                   </Button>
                </Card>
              ))
            ) : (
              <div className="col-span-2 py-20 text-center bg-white rounded-3xl border-2 border-dashed border-gray-100">
                 <Terminal className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                 <h3 className="text-lg font-bold text-gray-900">No Simulation History</h3>
                 <p className="text-gray-500">Run a simulation from the System page to see results here.</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
