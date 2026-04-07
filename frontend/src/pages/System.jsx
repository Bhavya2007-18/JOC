import React, { useState } from 'react';
import { systemApi } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle,
  Play,
  Settings,
  Cpu,
  Database
} from 'lucide-react';

export function System() {
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

  const handleFix = async (issue) => {
    const issueId = issue.id || issue.target;
    setFixing(prev => ({ ...prev, [issueId]: true }));
    try {
      // Assuming issue has an action and target
      const action = issue.action || 'kill_process';
      const target = issue.target;
      await systemApi.fix(action, target);
      // Refresh report after fix
      handleAnalyze();
    } catch (err) {
      console.error('Failed to fix issue:', err);
      alert('Failed to apply fix.');
    } finally {
      setFixing(prev => ({ ...prev, [issueId]: false }));
    }
  };

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">System Intelligence</h1>
          <p className="mt-2 text-lg text-gray-600">Analyze your system health and apply automated fixes.</p>
        </div>
        <Button 
          size="lg" 
          onClick={handleAnalyze} 
          isLoading={loading}
          className="shadow-lg shadow-blue-500/20"
        >
          <Activity className="mr-2 h-5 w-5" />
          Analyze System
        </Button>
      </header>

      {error && (
        <div className="flex items-center gap-3 rounded-xl bg-red-50 p-6 text-red-800 ring-1 ring-red-200">
          <XCircle className="h-6 w-6" />
          <p className="font-medium text-lg">{error}</p>
        </div>
      )}

      {report ? (
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          {/* Summary Card */}
          <Card 
            title="Analysis Summary" 
            className="lg:col-span-1 border-t-4 border-t-blue-500"
          >
            <div className="space-y-6 py-2">
              <div className="flex items-center justify-between border-b border-gray-100 pb-4">
                <span className="text-gray-600 flex items-center gap-2">
                  <Cpu className="h-4 w-4" /> CPU
                </span>
                <span className="font-bold text-gray-900">{report.summary?.cpu_usage}%</span>
              </div>
              <div className="flex items-center justify-between border-b border-gray-100 pb-4">
                <span className="text-gray-600 flex items-center gap-2">
                  <Database className="h-4 w-4" /> RAM
                </span>
                <span className="font-bold text-gray-900">{report.summary?.ram_usage}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Issues Found</span>
                <span className={`font-bold ${report.issues?.length > 0 ? 'text-amber-600' : 'text-green-600'}`}>
                  {report.issues?.length || 0}
                </span>
              </div>
            </div>
          </Card>

          {/* Issues Card */}
          <Card 
            title="Detected Issues" 
            description="Automated recommendations to improve performance"
            className="lg:col-span-2"
          >
            <div className="space-y-4">
              {report.issues?.length > 0 ? (
                report.issues.map((issue, idx) => (
                  <div key={idx} className="flex flex-col gap-4 rounded-xl border border-gray-100 bg-gray-50/50 p-6 transition-all hover:bg-white hover:shadow-sm">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div className={`mt-1 rounded-lg p-2 ${issue.severity === 'high' ? 'bg-red-100 text-red-600' : 'bg-amber-100 text-amber-600'}`}>
                          <AlertTriangle className="h-5 w-5" />
                        </div>
                        <div>
                          <h4 className="text-lg font-bold text-gray-900">{issue.title || issue.issue_type}</h4>
                          <p className="mt-1 text-gray-600 leading-relaxed">{issue.description || `Detected high resource usage for ${issue.target}`}</p>
                        </div>
                      </div>
                      <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ring-1 ring-inset ${
                        issue.severity === 'high' 
                          ? 'bg-red-50 text-red-700 ring-red-600/20' 
                          : 'bg-amber-50 text-amber-700 ring-amber-600/20'
                      }`}>
                        {issue.severity || 'Medium'}
                      </span>
                    </div>
                    <div className="flex justify-end pt-2 border-t border-gray-100/50">
                      <Button 
                        size="sm" 
                        onClick={() => handleFix(issue)}
                        isLoading={fixing[issue.id || issue.target]}
                        className="bg-green-600 hover:bg-green-700 shadow-sm"
                      >
                        <Settings className="mr-2 h-4 w-4" />
                        Apply Fix
                      </Button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <div className="rounded-full bg-green-100 p-4 mb-4">
                    <CheckCircle2 className="h-10 w-10 text-green-600" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900">System is Healthy</h3>
                  <p className="mt-2 text-gray-500 max-w-sm">No critical issues detected. Your system is running optimally.</p>
                </div>
              )}
            </div>
          </Card>
        </div>
      ) : !loading && (
        <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-gray-200 bg-white/50 py-24 text-center">
          <div className="rounded-full bg-blue-50 p-6 mb-6">
            <Activity className="h-12 w-12 text-blue-500" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">Ready to Analyze</h3>
          <p className="mt-3 text-gray-500 max-w-md text-lg">
            Start a full system analysis to discover performance bottlenecks and optimization opportunities.
          </p>
          <Button size="lg" className="mt-8 px-10" onClick={handleAnalyze}>
            Get Started
          </Button>
        </div>
      )}
    </div>
  );
}
