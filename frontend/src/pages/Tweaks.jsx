import React, { useState } from 'react';
import { systemApi } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { 
  Zap, 
  Settings2, 
  Gamepad2, 
  Battery, 
  Cpu,
  Monitor,
  CheckCircle2,
  AlertTriangle,
  Info,
  ChevronRight
} from 'lucide-react';

export function Tweaks() {
  const [executing, setExecuting] = useState({});
  const [status, setStatus] = useState(null);

  const tweaks = [
    { 
      id: 'gaming_boost', 
      name: 'Gaming Boost', 
      description: 'Prioritize game processes and disable background services for maximum FPS.', 
      icon: Gamepad2, 
      color: 'text-purple-600', 
      bg: 'bg-purple-50',
      impact: 'High',
      type: 'Performance'
    },
    { 
      id: 'battery_saver', 
      name: 'Battery Saver', 
      description: 'Reduce CPU performance and screen brightness to extend battery life.', 
      icon: Battery, 
      color: 'text-green-600', 
      bg: 'bg-green-50',
      impact: 'Medium',
      type: 'Power'
    },
    { 
      id: 'performance_boost', 
      name: 'Performance Boost', 
      description: 'Clear system caches and optimize memory allocation for smoother operation.', 
      icon: Zap, 
      color: 'text-amber-600', 
      bg: 'bg-amber-50',
      impact: 'Medium',
      type: 'Performance'
    },
    { 
      id: 'clean_ram', 
      name: 'Clean RAM', 
      description: 'Forcefully clear inactive memory pages to free up resources.', 
      icon: Cpu, 
      color: 'text-blue-600', 
      bg: 'bg-blue-50',
      impact: 'Low',
      type: 'Memory'
    },
  ];

  const handleExecute = async (tweak) => {
    setExecuting(prev => ({ ...prev, [tweak.id]: true }));
    setStatus(null);
    try {
      const response = await systemApi.executeTweak(tweak.id);
      setStatus({ 
        type: 'success', 
        message: response.data.message || `Successfully executed ${tweak.name}` 
      });
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

      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        {tweaks.map((tweak) => (
          <Card key={tweak.id} className="relative group overflow-hidden border-none shadow-sm ring-1 ring-gray-200 hover:ring-blue-500/30 transition-all duration-300">
            <div className="flex flex-col h-full p-2">
              <div className="flex items-start justify-between mb-6">
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
              <p className="text-gray-600 leading-relaxed font-medium mb-8 grow">
                {tweak.description}
              </p>
              <div className="pt-6 border-t border-gray-100/50 flex items-center justify-between">
                <div className="flex items-center text-xs font-bold text-gray-400 uppercase tracking-widest">
                  <Info className="h-3.5 w-3.5 mr-1.5" />
                  One-click optimize
                </div>
                <Button 
                  onClick={() => handleExecute(tweak)} 
                  isLoading={executing[tweak.id]}
                  className="px-8 font-black uppercase tracking-widest shadow-lg shadow-blue-500/20"
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
