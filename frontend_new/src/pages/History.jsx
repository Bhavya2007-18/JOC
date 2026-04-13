import React, { useState, useEffect } from 'react';
import { systemApi, intelligenceApi, autonomyApi } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { useSimulation } from '../hooks/useSimulation';
import { 
  History as HistoryIcon, 
  RotateCcw, 
  CheckCircle2, 
  Clock, 
  AlertTriangle,
  Calendar,
  Terminal,
  Activity,
  FileText,
  BrainCircuit,
  Database
} from 'lucide-react';
import { motion as Motion, AnimatePresence } from 'framer-motion';
import { cn } from '../utils/cn';

export function History() {
  const [reverting, setReverting] = useState({});
  const [status, setStatus] = useState(null);
  const { history: simHistory, fetchHistory: fetchSimHistory } = useSimulation();
  const [activeTab, setActiveTab] = useState('actions');

  const [history, setHistory] = useState([]);
  const [behavior, setBehavior] = useState(null);
  const [autonomyLog, setAutonomyLog] = useState([]);

  useEffect(() => {
    let mounted = true;
    autonomyApi.getAuditHistory().then((res) => {
      if (mounted) setAutonomyLog(res.data?.audit || []);
    }).catch(() => {});
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    let mounted = true;
    systemApi.getActionHistory().then((res) => {
      if (!mounted) return;
      const actions = (res.data?.actions || []).map((a) => ({
        id: a.id,
        action: a.action,
        target: a.target,
        timestamp: new Date(a.timestamp * 1000).toLocaleString(),
        status: a.status,
        revertible: a.reversible,
      }));
      setHistory(actions);
    }).catch(() => {});
    return () => { mounted = false; };
  }, []);

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
        message: response.data.message || `PROTOCOL_REVERTED: State restored for ${actionId}` 
      });
    } catch (err) {
      setStatus({ 
        type: 'error', 
        message: `LINK_FAILURE: Could not initiate state reversal.` 
      });
      console.error(err);
    } finally {
      setReverting(prev => ({ ...prev, [actionId]: false }));
    }
  };

  const tabs = [
    { id: 'actions', label: 'System Protocols', icon: Activity },
    { id: 'simulations', label: 'Engagement History', icon: Terminal },
    { id: 'autonomy', label: 'Autonomy Audit', icon: BrainCircuit },
  ];

  return (
    <div className="space-y-10 pb-20">
      <header className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic">Operation Logs</h1>
          <p className="mt-2 text-slate-400 font-mono text-sm tracking-widest uppercase opacity-70">Decoded Audit Trail // State Mutation Record</p>
        </div>
      </header>

      {behavior && (
        <div className="nm-flat bg-slate-900 border border-accent-blue/20 rounded-[2.5rem] p-10 flex flex-col md:flex-row items-center justify-between gap-10 shadow-[0_0_30px_rgba(59,130,246,0.1)] relative overflow-hidden group hover:nm-convex transition-all duration-500">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
             <BrainCircuit className="h-40 w-40 text-accent-blue" />
          </div>
          <div className="relative z-10 flex flex-col md:flex-row items-center gap-10 text-center md:text-left">
            <div className="nm-inset p-6 rounded-[2rem] bg-slate-950">
               <Activity className="h-10 w-10 text-accent-blue drop-shadow-[0_0_8px_#3b82f6]" />
            </div>
            <div>
              <h2 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em] mb-4">Baseline Behavior Analysis</h2>
              <p className="text-xl font-bold text-white tracking-tight leading-relaxed max-w-xl italic">
                Telemetry verify baseline at <span className="text-accent-blue font-mono">{behavior.avgCpu?.toFixed(1) ?? 0}%</span> CPU and <span className="text-purple-400 font-mono">{behavior.avgMem?.toFixed(1) ?? 0}%</span> RAM.
              </p>
            </div>
          </div>
          {behavior.peakHours.length > 0 && (
            <div className="relative z-10 nm-inset p-6 rounded-3xl bg-slate-950/50 flex flex-col items-center">
              <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Peak Hours</span>
              <div className="text-2xl font-black text-white font-mono">
                {behavior.peakHours[0].hour}:00
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex p-2 nm-inset bg-slate-900 border border-slate-800 rounded-3xl w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
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

      {status && (
        <Motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn(
            "flex items-center gap-6 rounded-3xl p-8 font-black uppercase tracking-[0.2em] italic",
            status.type === 'success' ? 'nm-flat bg-emerald-950/20 text-emerald-400 border border-emerald-900/30 font-mono' : 'nm-flat bg-red-950/20 text-red-400 border border-red-900/30 font-mono'
          )}
        >
          {status.type === 'success' ? <CheckCircle2 className="h-8 w-8" /> : <AlertTriangle className="h-8 w-8" />}
          <p className="text-lg">{status.message}</p>
        </Motion.div>
      )}

      <AnimatePresence mode="wait">
        {activeTab === 'actions' && (
          <Motion.div
            key="actions"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.02 }}
          >
            <Card title="Protocol Record" icon={Database} className="border-t-2 border-accent-blue">
              <div className="mt-8 overflow-hidden rounded-[2rem] nm-inset bg-slate-950 border border-slate-900">
                <table className="w-full text-left border-collapse">
                  <thead className="bg-slate-900 border-b border-slate-800">
                    <tr>
                      <th className="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Mutation Protocol</th>
                      <th className="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Target ID</th>
                      <th className="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Temporal Marker</th>
                      <th className="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">Intervention</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {history.map((item) => (
                      <tr key={item.id} className="group hover:bg-slate-900/30 transition-all duration-300">
                        <td className="px-8 py-5">
                          <div className="flex items-center gap-4">
                            <div className="nm-flat h-10 w-10 rounded-xl bg-slate-900 flex items-center justify-center text-slate-500 group-hover:text-accent-blue transition-all group-hover:nm-inset">
                              <HistoryIcon className="h-5 w-5" />
                            </div>
                            <span className="font-black text-white text-sm uppercase tracking-tight italic">{item.action}</span>
                          </div>
                        </td>
                        <td className="px-8 py-5">
                          <span className="text-xs font-mono font-black text-slate-500 group-hover:text-accent-blue transition-colors">[{item.target}]</span>
                        </td>
                        <td className="px-8 py-5">
                          <div className="flex flex-col gap-1">
                            <span className="text-[10px] font-black text-white flex items-center gap-2 font-mono">
                              <Calendar className="h-3 w-3 text-slate-600" />
                              {item.timestamp.split(' ')[0]}
                            </span>
                            <span className="text-[9px] font-black text-slate-500 flex items-center gap-2 font-mono uppercase">
                              <Clock className="h-3 w-3" />
                              {item.timestamp.split(' ')[1]}
                            </span>
                          </div>
                        </td>
                        <td className="px-8 py-5 text-right">
                          {item.revertible && (
                            <Button 
                              size="sm" 
                              variant="outline" 
                              onClick={() => handleRevert(item.id)}
                              isLoading={reverting[item.id]}
                              className="px-6 h-10 nm-flat bg-slate-900 border-none rounded-xl text-[10px] font-black uppercase tracking-[0.2em] hover:text-white"
                            >
                              <RotateCcw className="mr-2 h-3.5 w-3.5" />
                              Restore
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </Motion.div>
        )}
        
        {activeTab === 'simulations' && (
          <Motion.div
            key="simulations"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.02 }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-10"
          >
            {simHistory.length > 0 ? (
              simHistory.map((report, idx) => (
                <Card key={idx} title={`SIM_CORE_RUN_${simHistory.length - idx}`} icon={Terminal} className="hover:nm-convex transition-all group">
                   <div className="flex justify-between items-center mb-10 py-4 border-b border-slate-800">
                      <div className="flex flex-col">
                         <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em] mb-2">Protocol_Type</span>
                         <span className="text-lg font-black text-white italic uppercase">{report.simulation_type}</span>
                      </div>
                      <div className="text-right nm-inset p-4 rounded-2xl bg-slate-950">
                         <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest block mb-1">Resilience</span>
                         <div className={cn('text-2xl font-black font-mono',
                           report.score >= 80 ? 'text-emerald-500' : report.score >= 50 ? 'text-amber-500' : 'text-red-500'
                         )}>{report.score}</div>
                      </div>
                   </div>
                   <div className="grid grid-cols-2 gap-6 mb-8">
                      <div className="nm-inset p-4 rounded-2xl bg-slate-950/30 flex flex-col items-center">
                         <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2 text-center">ANOMALIES_DECODED</span>
                         <span className="font-mono text-xl text-white font-black">{report.anomalies_detected.length}</span>
                      </div>
                      <div className="nm-inset p-4 rounded-2xl bg-slate-950/30 flex flex-col items-center">
                         <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2 text-center">NEURAL_RESPONSES</span>
                         <span className="font-mono text-xl text-white font-black">{report.response_actions.length}</span>
                      </div>
                   </div>
                   <Button variant="outline" size="md" className="w-full text-[10px] font-black uppercase tracking-[0.4em] nm-flat bg-slate-900 border-none rounded-xl h-12">
                      <FileText className="h-4 w-4 mr-3 text-accent-blue" />
                      View_Telemetry_Log
                   </Button>
                </Card>
              ))
            ) : (
              <div className="col-span-2 py-32 text-center nm-flat bg-slate-900 rounded-[3rem] border border-slate-800 flex flex-col items-center">
                 <div className="nm-inset p-10 rounded-full bg-slate-950 mb-10">
                    <Terminal className="h-20 w-20 text-slate-700" />
                 </div>
                 <h3 className="text-4xl font-black text-white uppercase italic tracking-tighter">Engagement History Null</h3>
                 <p className="mt-4 text-slate-500 font-mono text-sm uppercase tracking-[0.3em] max-w-md opacity-60">Run localized stress simulations to populate battle station logs.</p>
              </div>
            )}
          </Motion.div>
        )}

        {activeTab === 'autonomy' && (
          <Motion.div
            key="autonomy"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.02 }}
          >
            <Card title="Autonomy Audit Trail" icon={BrainCircuit} className="border-t-2 border-purple-500">
              <div className="mt-8 overflow-hidden rounded-[2rem] nm-inset bg-slate-950 border border-slate-900">
                <table className="w-full text-left border-collapse">
                  <thead className="bg-slate-900 border-b border-slate-800">
                    <tr>
                      <th className="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Temporal Marker</th>
                      <th className="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Event Subtype</th>
                      <th className="px-8 py-5 text-[10px] font-black text-slate-500 uppercase tracking-widest">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {autonomyLog.map((logItem, idx) => (
                      <tr key={idx} className="group hover:bg-slate-900/30 transition-all duration-300">
                        <td className="px-8 py-5">
                          <span className="text-[10px] font-black text-slate-400 font-mono">
                            {logItem.timestamp ? new Date(logItem.timestamp * 1000).toLocaleString() : 'N/A'}
                          </span>
                        </td>
                        <td className="px-8 py-5">
                          <span className="text-[10px] font-black text-purple-400 nm-inset bg-purple-950/20 px-3 py-1.5 rounded-lg border border-purple-900/30 font-mono uppercase">
                            {logItem.decision_type || logItem.event_type || 'SYS_EVENT'}
                          </span>
                        </td>
                        <td className="px-8 py-5 text-xs text-slate-300">
                          {logItem.action_taken || logItem.reasoning || JSON.stringify(logItem)}
                        </td>
                      </tr>
                    ))}
                    {autonomyLog.length === 0 && (
                      <tr>
                        <td colSpan="3" className="px-8 py-10 text-center text-slate-500 font-mono text-sm">
                          No autonomy events recorded.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </Card>
          </Motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
