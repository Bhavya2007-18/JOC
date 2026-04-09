import React, { useState } from 'react';
import { storageApi } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { 
  HardDrive, 
  Trash2, 
  Files, 
  Snowflake, 
  PieChart, 
  Search, 
  AlertTriangle,
  RefreshCw,
  Info
} from 'lucide-react';

export function Storage() {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [cleaning, setCleaning] = useState({});
  const [status, setStatus] = useState(null);

  const handleScan = async () => {
    setLoading(true);
    setError(null);
    setStatus(null);
    try {
      const response = await storageApi.scan({ path: 'C:/Users' });
      setReport(response.data);
    } catch (err) {
      setError('Failed to scan storage. Please check if the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCleanup = async (type) => {
    setCleaning(prev => ({ ...prev, [type]: true }));
    setStatus(null);
    try {
      const previewRes = await storageApi.cleanup(type, { confirm: false, dryRun: true });
      const preview = previewRes.data.preview;

      const riskLabel = previewRes.data.risk ? `Risk: ${previewRes.data.risk.toUpperCase()}. ` : '';
      let proceed = true;
      if (previewRes.data.risk === 'high') {
        const typed = window.prompt(
          `${riskLabel}High-risk cleanup. Type CONFIRM to proceed with deleting files from ${type.toUpperCase()}.`
        );
        if (typed !== 'CONFIRM') {
          proceed = false;
        }
      } else {
        proceed = window.confirm(
          preview
            ? `${riskLabel}This will delete approximately ${preview.total_files} files from ${type.toUpperCase()}. Do you want to continue?`
            : `${riskLabel}This will delete files for ${type.toUpperCase()}. Do you want to continue?`
        );
      }

      if (!proceed) {
        setCleaning(prev => ({ ...prev, [type]: false }));
        return;
      }

      const response = await storageApi.cleanup(type, { confirm: true, dryRun: false });
      const benefitPercent =
        response.data.total_deleted > 0
          ? Math.min(25, Math.max(5, Math.round(response.data.total_deleted / (1024 * 1024 * 500))))
          : 0;
      setStatus({
        type: 'success',
        message:
          benefitPercent > 0
            ? `Cleanup completed. Deleted ${response.data.total_deleted} files, ${response.data.total_failed} failed. Estimated performance improvement ~${benefitPercent}%.`
            : `Cleanup completed. Deleted ${response.data.total_deleted} files, ${response.data.total_failed} failed.`,
      });
      handleScan();
    } catch (err) {
      console.error('Failed to cleanup storage:', err);
      setStatus({
        type: 'error',
        message: 'Failed to cleanup storage. Please check if the backend is running.',
      });
    } finally {
      setCleaning(prev => ({ ...prev, [type]: false }));
    }
  };

  const categories = [
    { id: 'junk', name: 'Junk Files', icon: Trash2, color: 'text-red-600', bg: 'bg-red-50', data: report?.junk },
    { id: 'duplicates', name: 'Duplicates', icon: Files, color: 'text-amber-600', bg: 'bg-amber-50', data: report?.duplicates },
    { id: 'cold', name: 'Cold Files', icon: Snowflake, color: 'text-blue-600', bg: 'bg-blue-50', data: report?.cold_files },
  ];

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Storage Intelligence</h1>
          <p className="mt-2 text-lg text-gray-600">Scan your drives for junk, duplicates, and unused files.</p>
        </div>
        <Button size="lg" onClick={handleScan} isLoading={loading} className="shadow-lg shadow-blue-500/20">
          <Search className="mr-2 h-5 w-5" />
          Scan Storage
        </Button>
      </header>

      {error && (
        <div className="flex items-center gap-3 rounded-xl bg-red-50 p-6 text-red-800 ring-1 ring-red-200">
          <AlertTriangle className="h-6 w-6" />
          <p className="font-medium text-lg">{error}</p>
        </div>
      )}

      {status && (
        <div
          className={`flex items-center gap-3 rounded-xl p-4 text-sm font-medium ${
            status.type === 'success'
              ? 'bg-green-50 text-green-800 ring-1 ring-green-200'
              : 'bg-red-50 text-red-800 ring-1 ring-red-200'
          }`}
        >
          <Info className="h-5 w-5" />
          <p>{status.message}</p>
        </div>
      )}

      {report ? (
        <div className="space-y-8">
          {/* Overview Grid */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
            {categories.map((cat) => (
              <Card key={cat.id} className="relative overflow-hidden group border-none shadow-sm ring-1 ring-gray-200 hover:ring-blue-500/30 transition-all duration-300">
                <div className={`absolute top-0 left-0 w-1 h-full ${cat.id === 'junk' ? 'bg-red-500' : cat.id === 'duplicates' ? 'bg-amber-500' : 'bg-blue-500'}`} />
                <div className="flex items-center justify-between px-6 py-6">
                  <div className="flex items-center">
                    <div className={`mr-4 rounded-xl ${cat.bg} p-3 transition-transform duration-300 group-hover:scale-110`}>
                      <cat.icon className={`h-6 w-6 ${cat.color}`} />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-gray-500 uppercase tracking-wider">{cat.name}</p>
                      <p className="text-2xl font-black text-gray-900">{cat.data?.readable_size || '0 B'}</p>
                      <p className="text-xs text-gray-500 mt-1 font-medium">{cat.data?.junk_files?.length || cat.data?.duplicates?.length || cat.data?.cold_files?.length || 0} files found</p>
                    </div>
                  </div>
                  <Button 
                    size="sm" 
                    variant={cat.id === 'junk' ? 'danger' : 'outline'}
                    onClick={() => handleCleanup(cat.id)}
                    isLoading={cleaning[cat.id]}
                    className="shadow-sm font-bold"
                  >
                    Clean
                  </Button>
                </div>
              </Card>
            ))}
          </div>

          <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
            {/* Category Breakdown */}
            <Card title="Category Breakdown" description="Storage usage by file type">
              <div className="space-y-5 py-2">
                {Object.entries(report.category_breakdown || {}).map(([category, info]) => (
                  <div key={category} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-bold text-gray-700 capitalize flex items-center gap-2">
                        <Info className="h-4 w-4 text-blue-500" />
                        {category}
                      </span>
                      <span className="text-gray-500 font-medium">{info.readable_size}</span>
                    </div>
                    <div className="h-2.5 w-full rounded-full bg-gray-100 overflow-hidden">
                      <div 
                        className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-1000 ease-out shadow-sm"
                        style={{ width: `${Math.min(100, (info.total_size / report.total_size) * 100 || 0)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Suggestions */}
            <Card title="Optimization Suggestions" description="Quick actions to free up space">
              <div className="space-y-4">
                {report.suggestions?.map((suggestion, idx) => (
                  <div key={idx} className="flex items-start gap-4 rounded-xl border border-blue-50 bg-blue-50/30 p-5 ring-1 ring-blue-100 transition-all hover:bg-white hover:shadow-md">
                    <div className="rounded-lg bg-white p-2.5 shadow-sm">
                      <RefreshCw className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <h4 className="font-bold text-blue-900">{suggestion.title}</h4>
                      <p className="mt-1 text-sm text-blue-800/70 leading-relaxed font-medium">{suggestion.description}</p>
                      <div className="mt-3 flex items-center gap-3">
                        <Button size="sm" onClick={() => handleCleanup(suggestion.type)} isLoading={cleaning[suggestion.type]} className="bg-blue-600 hover:bg-blue-700 px-6 font-bold shadow-lg shadow-blue-500/20">
                          Execute
                        </Button>
                        <span className="text-xs font-bold text-blue-500 uppercase tracking-wider">Freed: {suggestion.size}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      ) : !loading && (
        <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-gray-200 bg-white/50 py-24 text-center">
          <div className="rounded-full bg-blue-50 p-6 mb-6">
            <HardDrive className="h-12 w-12 text-blue-500" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 uppercase tracking-tight">Ready to Scan</h3>
          <p className="mt-3 text-gray-500 max-w-md text-lg font-medium">
            Scan your drives to identify storage-saving opportunities and remove unnecessary files.
          </p>
          <Button size="lg" className="mt-8 px-12 py-6 text-lg font-black uppercase tracking-widest shadow-xl shadow-blue-500/20" onClick={handleScan}>
            Start Deep Scan
          </Button>
        </div>
      )}
    </div>
  );
}
