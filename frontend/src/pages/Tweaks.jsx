import React, { useState } from 'react';
import { optimizerApi } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { 
  Zap, 
  Gamepad2, 
  Battery, 
  Cpu,
  Monitor,
  CheckCircle2,
  AlertTriangle,
  Info,
  ChevronRight,
  Eye,
  Shield,
  X
} from 'lucide-react';

export function Tweaks() {
  const [executing, setExecuting] = useState({});
  const [previewing, setPreviewing] = useState({});
  const [preview, setPreview] = useState(null);
  const [status, setStatus] = useState(null);

  const tweaks = [
    { 
      id: 'gaming_boost', 
      name: 'Gaming Boost', 
      description: 'Kill background apps (OneDrive, Search, Edge, Teams, Discord, Spotify) and activate High Performance power plan for maximum FPS.', 
      icon: Gamepad2, 
      color: 'text-purple-600', 
      bg: 'bg-purple-50',
      impact: 'High',
      type: 'Performance',
      actions: [
        'Kill: OneDrive, SearchIndexer, Teams, Discord, Spotify, Edge updates',
        'Power Plan: Switch to High Performance',
        'Priority: Boost foreground game processes',
      ]
    },
    { 
      id: 'battery_saver', 
      name: 'Battery Saver', 
      description: 'Suspend heavy background apps and activate Power Saver plan to extend battery life.', 
      icon: Battery, 
      color: 'text-green-600', 
      bg: 'bg-green-50',
      impact: 'Medium',
      type: 'Power',
      actions: [
        'Suspend: OneDrive, Teams, Discord, Spotify, Steam',
        'Power Plan: Switch to Power Saver',
        'CPU: Reduce background thread activity',
      ]
    },
    { 
      id: 'performance_boost', 
      name: 'Performance Boost', 
      description: 'Lower priority of CPU-heavy background processes so your active apps run smoother.', 
      icon: Zap, 
      color: 'text-amber-600', 
      bg: 'bg-amber-50',
      impact: 'Medium',
      type: 'Performance',
      actions: [
        'Reprioritize: Lower priority of processes using >20% CPU',
        'Skip: All protected/critical system processes',
        'Result: More CPU headroom for active apps',
      ]
    },
    { 
      id: 'clean_ram', 
      name: 'Clean RAM', 
      description: 'Clear inactive memory pages from all non-critical processes using Windows EmptyWorkingSet API.', 
      icon: Cpu, 
      color: 'text-blue-600', 
      bg: 'bg-blue-50',
      impact: 'Low',
      type: 'Memory',
      actions: [
        'Clear: Inactive memory pages via EmptyWorkingSet',
        'Skip: All critical system processes',
        'Result: Immediate RAM freed for active use',
      ]
    },
  ];

  const handlePreview = async (tweak) => {
    setPreviewing(prev => ({ ...prev, [tweak.id]: true }));
    setStatus(null);
    try {
      const response = await optimizerApi.executeTweak(tweak.id);
      const data = response.data;
      setPreview({
        tweakId: tweak.id,
        tweakName: tweak.name,
        result: data.result || data,
        details: data.result?.details || tweak.actions,
        dryRun: data.result?.dry_run ?? true,
        processesAffected: data.result?.processes_killed || data.result?.processes_suspended || data.result?.processes_lowered || [],
      });
    } catch (err) {
      setStatus({ 
        type: 'error', 
        message: `Failed to preview ${tweak.name}. Backend might be offline.` 
      });
    } finally {
      setPreviewing(prev => ({ ...prev, [tweak.id]: false }));
    }
  };

  const handleExecute = async (tweak) => {
    setExecuting(prev => ({ ...prev, [tweak.id]: true }));
    setStatus(null);
    setPreview(null);
    try {
      const response = await optimizerApi.executeTweak(tweak.id);
      const data = response.data;
      const msg = data.result?.message || data.message || `Successfully executed ${tweak.name}`;
      setStatus({ type: 'success', message: msg });
    } catch (err) {
      setStatus({ 
        type: 'error', 
        message: `Failed to execute ${tweak.name}. Please check if the backend is running.` 
      });
      console.error(err);
    } finally {
      setExecuting(prev => ({ ...prev, [tweak.id]: false }));
    }
  };

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">System Tweaks</h1>
        <p className="mt-2 text-lg text-gray-600 font-medium">Fine-tune your system performance with specialized optimizations.</p>
      </header>

      {status && (
        <div className={`flex items-center gap-4 rounded-xl p-6 shadow-sm ring-1 ring-inset ${
          status.type === 'success' 
            ? 'bg-green-50 text-green-800 ring-green-200' 
            : 'bg-red-50 text-red-800 ring-red-200'
        }`}>
          {status.type === 'success' ? <CheckCircle2 className="h-6 w-6" /> : <AlertTriangle className="h-6 w-6" />}
          <p className="font-bold text-lg">{status.message}</p>
        </div>
      )}

      {/* Preview Modal */}
      {preview && (
        <div className="rounded-2xl bg-white shadow-xl ring-1 ring-gray-200 overflow-hidden">
          <div className="flex items-center justify-between bg-gray-50 px-6 py-4 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-amber-100 p-2">
                <Eye className="h-5 w-5 text-amber-600" />
              </div>
              <div>
                <h3 className="text-lg font-black text-gray-900 uppercase tracking-tight">
                  Preview: {preview.tweakName}
                </h3>
                <p className="text-xs font-bold text-amber-600 uppercase tracking-widest">
                  {preview.dryRun ? '🛡️ DRY RUN — No changes made yet' : '⚡ Live execution result'}
                </p>
              </div>
            </div>
            <button onClick={() => setPreview(null)} className="rounded-lg p-2 hover:bg-gray-200 transition-colors">
              <X className="h-5 w-5 text-gray-500" />
            </button>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <h4 className="text-xs font-black text-gray-500 uppercase tracking-widest mb-3">What will happen:</h4>
              <ul className="space-y-2">
                {(preview.details || []).map((detail, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-sm">
                    <Shield className="h-4 w-4 mt-0.5 text-blue-500 flex-shrink-0" />
                    <span className="text-gray-700 font-medium">{detail}</span>
                  </li>
                ))}
              </ul>
            </div>
            {preview.processesAffected.length > 0 && (
              <div>
                <h4 className="text-xs font-black text-gray-500 uppercase tracking-widest mb-3">Processes affected:</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {preview.processesAffected.map((p, idx) => (
                    <div key={idx} className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2 text-xs">
                      <span className="font-bold text-gray-900">{p.name}</span>
                      <span className="text-gray-400">PID {p.pid}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        {tweaks.map((tweak) => (
          <Card key={tweak.id} className="relative group overflow-hidden border-none shadow-sm ring-1 ring-gray-200 hover:ring-blue-500/30 transition-all duration-300">
            <div className="flex flex-col h-full p-2">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className={`mr-4 rounded-2xl ${tweak.bg} p-4 transition-transform duration-300 group-hover:scale-110 shadow-sm`}>
                    <tweak.icon className={`h-8 w-8 ${tweak.color}`} />
                  </div>
                  <div>
                    <h3 className="text-xl font-black text-gray-900 uppercase tracking-tight">{tweak.name}</h3>
                    <div className="flex gap-2 mt-1">
                      <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full bg-gray-100 text-gray-500 ring-1 ring-gray-200">
                        {tweak.type}
                      </span>
                      <span className={`text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full ring-1 ring-inset ${
                        tweak.impact === 'High' ? 'bg-red-50 text-red-600 ring-red-200' : 'bg-blue-50 text-blue-600 ring-blue-200'
                      }`}>
                        Impact: {tweak.impact}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              <p className="text-gray-600 leading-relaxed font-medium mb-4 grow">
                {tweak.description}
              </p>

              {/* Action details */}
              <div className="mb-4 space-y-1.5">
                {tweak.actions.map((action, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs text-gray-500">
                    <span className="text-blue-400 mt-0.5">›</span>
                    <span className="font-medium">{action}</span>
                  </div>
                ))}
              </div>

              <div className="pt-4 border-t border-gray-100/50 flex items-center justify-between gap-2">
                <Button 
                  size="sm"
                  variant="outline"
                  onClick={() => handlePreview(tweak)} 
                  isLoading={previewing[tweak.id]}
                  className="px-4 font-bold uppercase tracking-widest text-xs"
                >
                  <Eye className="mr-1.5 h-3.5 w-3.5" />
                  Preview
                </Button>
                <Button 
                  onClick={() => handleExecute(tweak)} 
                  isLoading={executing[tweak.id]}
                  className="px-6 font-black uppercase tracking-widest shadow-lg shadow-blue-500/20"
                >
                  Execute <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-700 p-8 text-white shadow-xl">
        <div className="flex items-center gap-6">
          <div className="rounded-2xl bg-white/20 p-4 backdrop-blur-sm">
            <Monitor className="h-10 w-10" />
          </div>
          <div>
            <h3 className="text-2xl font-black uppercase tracking-tight">Smart Optimization</h3>
            <p className="mt-1 text-blue-100 font-medium max-w-2xl leading-relaxed">
              JOC Engine automatically learns from your usage patterns to suggest the best tweaks for your specific hardware configuration.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
