import React, { useState, useEffect } from 'react';
import { FileText, Download, Activity, Cpu, Shield, BrainCircuit, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { reportApi } from '../api/client';

export default function Report() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReport();
  }, []);

  const fetchReport = async () => {
    try {
      const res = await reportApi.getSessionReport();
      setReport(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center p-8 bg-black">
        <div className="text-center space-y-4">
          <FileText className="h-12 w-12 text-blue-500 animate-pulse mx-auto" />
          <h2 className="text-xl font-medium text-white tracking-widest">GENERATING REPORT...</h2>
          <p className="text-zinc-500 font-mono text-sm">Compiling intelligence telemetry and XAI narratives</p>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="p-8">
        <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-lg flex items-center gap-3">
          <AlertTriangle className="text-red-400" />
          <p className="text-red-400">Failed to load session report.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-zinc-300 p-8 space-y-8 font-sans">
      
      {/* Header */}
      <div className="flex justify-between items-start border-b border-zinc-800 pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <FileText className="h-8 w-8 text-blue-400" />
            <h1 className="text-3xl font-bold tracking-tight text-white">Session Intelligence Report</h1>
          </div>
          <p className="text-zinc-500 font-mono text-sm">
            TID: {report.timestamp_iso} | AUTONOMY: {report.autonomy_mode}
          </p>
        </div>
        <button 
          onClick={reportApi.exportReport}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded font-medium transition-colors"
        >
          <Download className="h-4 w-4" />
          Export JSON
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: XAI Narrative */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
              <BrainCircuit className="h-5 w-5 text-purple-400" />
              Cognitive Summary
            </h2>
            
            <div className="space-y-6">
              <div className="border-l-2 border-blue-500 pl-4 py-1">
                <h3 className="text-xs uppercase tracking-wider text-zinc-500 mb-1">Current State</h3>
                <p className="text-zinc-200">{report.narrative.summary}</p>
              </div>

              <div className="border-l-2 border-orange-500 pl-4 py-1">
                <h3 className="text-xs uppercase tracking-wider text-zinc-500 mb-1">Causal Chain</h3>
                <p className="text-zinc-200">{report.narrative.cause}</p>
              </div>

              <div className="border-l-2 border-red-500 pl-4 py-1">
                <h3 className="text-xs uppercase tracking-wider text-zinc-500 mb-1">Impact & Trajectory</h3>
                <p className="text-zinc-200">{report.narrative.impact} {report.narrative.prediction}</p>
              </div>

              <div className="border-l-2 border-emerald-500 pl-4 py-1">
                <h3 className="text-xs uppercase tracking-wider text-zinc-500 mb-1">Autonomy Rationale</h3>
                <p className="text-zinc-200">{report.narrative.autonomy_context}</p>
              </div>
            </div>
          </div>
          
          {/* Decision Trace */}
          <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
              <Activity className="h-5 w-5 text-emerald-400" />
              Recent Decisions
            </h2>
            
            {report.recent_decisions.length === 0 ? (
              <p className="text-zinc-500 italic">No autonomous decisions recorded yet.</p>
            ) : (
              <div className="space-y-3">
                {report.recent_decisions.map((trace, i) => (
                  <div key={i} className="bg-black/40 border border-zinc-800 p-3 rounded flex justify-between items-center group hover:border-zinc-700 transition-colors">
                    <div>
                      <span className="text-xs font-mono text-zinc-500 block mb-1">
                        {new Date(trace.timestamp * 1000).toLocaleTimeString()}
                      </span>
                      <span className="text-sm font-medium text-zinc-300">
                        → Action: <span className="text-blue-400">{trace.final_decision}</span>
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-xs block text-zinc-400">Reason: {trace.override_reason}</span>
                      <span className="text-xs block text-emerald-500/70">Conf: {(trace.confidence * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Key Metrics */}
        <div className="space-y-6">
          <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Shield className="h-4 w-4 text-zinc-400" />
              Global State
            </h2>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center py-2 border-b border-zinc-800">
                <span className="text-zinc-400">Threat Level</span>
                <span className={`font-mono font-medium ${
                  report.threat_state === 'CRITICAL' ? 'text-red-500' :
                  report.threat_state === 'THREAT' ? 'text-orange-500' :
                  'text-emerald-500'
                }`}>{report.threat_state}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-zinc-800">
                <span className="text-zinc-400">Autopilot</span>
                <span className={report.autonomy_mode === "ACTIVE" ? 'text-emerald-400' : 'text-zinc-500'}>
                  {report.autonomy_mode}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Cpu className="h-4 w-4 text-zinc-400" />
              Learning Memory
            </h2>
            <div className="mb-4">
              <span className="text-3xl font-light text-white">{report.intelligence_memory.total_patterns_learned}</span>
              <span className="text-zinc-500 text-sm ml-2 font-mono">patterns</span>
            </div>
            
            <h3 className="text-xs uppercase text-zinc-500 mb-2 font-medium tracking-wider">Recent Lessons</h3>
            <div className="space-y-2">
              {report.intelligence_memory.recent_lessons.map((lesson, i) => (
                <div key={i} className="text-xs font-mono bg-black/50 px-2 py-1.5 rounded flex justify-between items-center">
                  <span className="text-zinc-400 truncate max-w-[100px]">{lesson.scenario}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-blue-400/80">{lesson.action}</span>
                    <span className="text-emerald-500">+{lesson.impact_score.toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
        </div>

      </div>

    </div>
  );
}
