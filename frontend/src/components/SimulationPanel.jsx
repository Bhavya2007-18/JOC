import React, { useState } from 'react';
import { useSimulation } from '../hooks/useSimulation';
import { Button } from './Button';
import { Card } from './Card';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Square, 
  AlertTriangle, 
  CheckCircle2, 
  Loader2, 
  BarChart3,
  Flame,
  Zap,
  Network
} from 'lucide-react';

const SIMULATION_TYPES = [
  { id: 'cpu_spike', name: 'CPU Stress', icon: Flame, description: 'Simulate high CPU load across all cores' },
  { id: 'memory_stress', name: 'Memory Leak', icon: Zap, description: 'Simulate rapid memory consumption' },
  { id: 'network_burst', name: 'Network Burst', icon: Network, description: 'Simulate high network traffic' },
];

export function SimulationPanel() {
  const { isRunning, report, runSimulation, stopSimulation } = useSimulation();
  const [selectedType, setSelectedType] = useState('cpu_spike');
  const [intensity, setIntensity] = useState(50);
  const [duration, setDuration] = useState(30);

  const handleStart = () => {
    runSimulation({
      simulation_type: selectedType,
      intensity: intensity / 100,
      duration_seconds: duration
    });
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {SIMULATION_TYPES.map((type) => (
          <button
            key={type.id}
            onClick={() => setSelectedType(type.id)}
            disabled={isRunning}
            className={`p-4 rounded-xl border-2 transition-all text-left ${
              selectedType === type.id 
                ? 'border-blue-500 bg-blue-50/50' 
                : 'border-gray-100 bg-white hover:border-gray-200'
            } ${isRunning ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <type.icon className={`h-6 w-6 mb-2 ${selectedType === type.id ? 'text-blue-600' : 'text-gray-400'}`} />
            <h4 className="font-bold text-gray-900">{type.name}</h4>
            <p className="text-xs text-gray-500 mt-1">{type.description}</p>
          </button>
        ))}
      </div>

      <Card>
        <div className="space-y-6 p-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <label className="block">
                <span className="text-sm font-semibold text-gray-700 flex justify-between">
                  Intensity
                  <span className="text-blue-600">{intensity}%</span>
                </span>
                <input
                  type="range"
                  min="10"
                  max="100"
                  step="10"
                  value={intensity}
                  onChange={(e) => setIntensity(parseInt(e.target.value))}
                  disabled={isRunning}
                  className="mt-2 w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </label>

              <label className="block">
                <span className="text-sm font-semibold text-gray-700 flex justify-between">
                  Duration (seconds)
                  <span className="text-blue-600">{duration}s</span>
                </span>
                <input
                  type="range"
                  min="10"
                  max="300"
                  step="10"
                  value={duration}
                  onChange={(e) => setDuration(parseInt(e.target.value))}
                  disabled={isRunning}
                  className="mt-2 w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </label>
            </div>

            <div className="flex flex-col justify-end gap-3">
              {isRunning ? (
                <Button 
                  variant="outline" 
                  className="w-full h-12 border-red-200 text-red-600 hover:bg-red-50 gap-2"
                  onClick={() => stopSimulation()}
                >
                  <Square className="h-4 w-4 fill-current" />
                  Terminate Simulation
                </Button>
              ) : (
                <Button 
                  className="w-full h-12 bg-blue-600 hover:bg-blue-700 text-white gap-2 shadow-lg shadow-blue-200"
                  onClick={handleStart}
                >
                  <Play className="h-4 w-4 fill-current" />
                  Initiate Stress Test
                </Button>
              )}
            </div>
          </div>
        </div>
      </Card>

      <AnimatePresence>
        {isRunning && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="rounded-2xl border border-blue-100 bg-blue-50/30 p-6 relative overflow-hidden"
          >
            <div className="absolute top-0 left-0 w-1 bg-blue-500 h-full animate-pulse" />
            <div className="flex items-center gap-4">
              <div className="rounded-full bg-blue-100 p-3 animate-spin">
                <Loader2 className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-blue-900">Simulation in Progress</h3>
                <p className="text-sm text-blue-700/80">The JOC engine is currently monitoring system response to the {selectedType} event.</p>
              </div>
            </div>
          </motion.div>
        )}

        {report && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className={`p-6 rounded-2xl border ${
              report.status === 'completed' ? 'border-green-100 bg-green-50/30' : 'border-red-100 bg-red-50/30'
            }`}>
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  {report.status === 'completed' ? (
                    <CheckCircle2 className="h-6 w-6 text-green-600" />
                  ) : (
                    <AlertTriangle className="h-6 w-6 text-red-600" />
                  )}
                  <h3 className="text-xl font-bold text-gray-900">Simulation Report</h3>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-500 uppercase tracking-wider">Score:</span>
                  <span className={`text-2xl font-black ${
                    report.score >= 80 ? 'text-green-600' : report.score >= 50 ? 'text-amber-600' : 'text-red-600'
                  }`}>{report.score}</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="text-sm font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    Anomalies Detected
                  </h4>
                  <div className="space-y-2">
                    {report.anomalies_detected.length > 0 ? (
                      report.anomalies_detected.map((a, i) => (
                        <div key={i} className="text-sm p-3 rounded-lg bg-white border border-gray-100 shadow-sm">
                          {a}
                        </div>
                      ))
                    ) : (
                      <p className="text-sm text-gray-500 italic">No anomalies detected during run.</p>
                    )}
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="text-sm font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                    <Zap className="h-4 w-4" />
                    Response Actions
                  </h4>
                  <div className="space-y-2">
                    {report.response_actions.length > 0 ? (
                      report.response_actions.map((a, i) => (
                        <div key={i} className="text-sm p-3 rounded-lg bg-white border border-gray-100 shadow-sm flex justify-between items-center">
                          <span>{a.action}</span>
                          <span className="text-[10px] font-bold bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">{a.time}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-sm text-gray-500 italic">No autonomous actions were required.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
