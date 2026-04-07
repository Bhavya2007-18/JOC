import React, { useState } from 'react';
import { systemApi } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { 
  History as HistoryIcon, 
  RotateCcw, 
  CheckCircle2, 
  Clock, 
  Search,
  AlertTriangle,
  Info,
  Calendar
} from 'lucide-react';

export function History() {
  const [reverting, setReverting] = useState({});
  const [status, setStatus] = useState(null);

  // Mock history for now as backend might not have a GET /history endpoint
  const [history, setHistory] = useState([
    { id: 'act_1', action: 'Kill Process', target: 'chrome.exe', timestamp: '2026-04-07 14:30', status: 'Completed', revertible: true },
    { id: 'act_2', action: 'Clean Junk', target: 'Temp Files', timestamp: '2026-04-07 12:15', status: 'Completed', revertible: false },
    { id: 'act_3', action: 'Tweak Execute', target: 'Gaming Boost', timestamp: '2026-04-07 10:00', status: 'Completed', revertible: true },
  ]);

  const handleRevert = async (actionId) => {
    setReverting(prev => ({ ...prev, [actionId]: true }));
    setStatus(null);
    try {
      const response = await systemApi.revertAction(actionId);
      setStatus({ 
        type: 'success', 
        message: response.data.message || `Successfully reverted action ${actionId}` 
      });
      // Optionally update history status
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
    <div className="space-y-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 uppercase tracking-tight">Action History</h1>
          <p className="mt-2 text-lg text-gray-600 font-medium">Track and manage recent system modifications.</p>
        </div>
        <div className="relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 group-hover:text-blue-500 transition-colors" />
          <input 
            type="text" 
            placeholder="Search history..." 
            className="pl-10 pr-4 py-2 rounded-xl border border-gray-200 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-medium"
          />
        </div>
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

      <Card className="overflow-hidden border-none shadow-sm ring-1 ring-gray-200">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50/50">
                <th className="px-6 py-4 text-xs font-black uppercase tracking-widest text-gray-500">Action</th>
                <th className="px-6 py-4 text-xs font-black uppercase tracking-widest text-gray-500">Target</th>
                <th className="px-6 py-4 text-xs font-black uppercase tracking-widest text-gray-500">Timestamp</th>
                <th className="px-6 py-4 text-xs font-black uppercase tracking-widest text-gray-500">Status</th>
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
                  <td className="px-6 py-5">
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-green-50 px-2.5 py-0.5 text-xs font-black uppercase tracking-widest text-green-700 ring-1 ring-inset ring-green-600/20">
                      <CheckCircle2 className="h-3 w-3" />
                      {item.status}
                    </span>
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

      <div className="flex items-center gap-4 rounded-xl border border-blue-100 bg-blue-50/30 p-6 ring-1 ring-blue-100">
        <Info className="h-6 w-6 text-blue-500" />
        <p className="text-sm font-medium text-blue-900 leading-relaxed max-w-3xl">
          History is stored locally and shows actions performed by JOC Engine during this session. Reverting an action attempts to restore the previous state, but some changes (like file deletions) are permanent.
        </p>
      </div>
    </div>
  );
}
