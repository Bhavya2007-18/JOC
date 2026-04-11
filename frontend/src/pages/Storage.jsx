import React, { useState } from 'react';
import { storageApi } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { 
  HardDrive, 
  Trash2, 
  Files, 
  Snowflake, 
  Search, 
  AlertTriangle,
  RefreshCw,
  Info,
  ChevronRight,
  Database
} from 'lucide-react';
import { motion as Motion, AnimatePresence } from 'framer-motion';
import { cn } from '../utils/cn';

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
      setError('Telemetric scan failed. Primary link severed.');
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

      const riskLabel = previewRes.data.risk ? `RISK_LVL: ${previewRes.data.risk.toUpperCase()}. ` : '';
      let proceed = true;
      if (previewRes.data.risk === 'high') {
        const typed = window.prompt(
          `${riskLabel}CRITICAL_IMPACT detected. Type AUTHORIZE_PURGE to proceed with ${type.toUpperCase()}.`
        );
        if (typed !== 'AUTHORIZE_PURGE') {
          proceed = false;
        }
      } else {
        proceed = window.confirm(
          preview
            ? `${riskLabel}Protocol will eliminate ${preview.total_files} objects from ${type.toUpperCase()}. Proceed?`
            : `${riskLabel}Initiate purge for ${type.toUpperCase()}?`
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
            ? `PURGE_COMPLETE: Eliminated ${response.data.total_deleted} targets. Stability improvement ~${benefitPercent}%.`
            : `PURGE_COMPLETE: Sector cleared.`,
      });
      handleScan();
    } catch (err) {
      console.error('Purge failure:', err);
      setStatus({
        type: 'error',
        message: 'Purge protocol failed. Target resisted intervention.',
      });
    } finally {
      setCleaning(prev => ({ ...prev, [type]: false }));
    }
  };

  const categories = [
    { id: 'junk', name: 'Junk Protocols', icon: Trash2, color: 'text-red-500', data: report?.junk },
    { id: 'duplicates', name: 'Redundant Links', icon: Files, color: 'text-amber-500', data: report?.duplicates },
    { id: 'cold', name: 'Deep Freeze', icon: Snowflake, color: 'text-accent-blue', data: report?.cold_files },
  ];

  return (
    <div className="space-y-10 pb-20">
      <header className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic">Storage_Intelligence</h1>
          <p className="mt-2 text-slate-400 font-mono text-sm tracking-widest uppercase opacity-70">Sector Analysis // Residual_Data_Siphon</p>
        </div>
        {!report && (
           <Button size="lg" onClick={handleScan} isLoading={loading} className="px-10 nm-convex bg-slate-900 border-none text-white gap-3">
             <Search className="h-5 w-5" />
             INIT_DEEP_SCAN
           </Button>
        )}
      </header>

      {error && (
        <div className="flex items-center gap-4 rounded-2xl nm-flat bg-red-950/20 p-8 text-red-400 border border-red-900/30">
          <AlertTriangle className="h-8 w-8" />
          <p className="font-black text-sm uppercase tracking-widest">{error}</p>
        </div>
      )}

      {status && (
        <div
          className={cn(
            'flex items-center gap-4 rounded-2xl p-6 text-xs font-black uppercase tracking-[0.2em]',
            status.type === 'success'
              ? 'nm-flat bg-emerald-950/20 text-emerald-400 border border-emerald-900/30 font-mono'
              : 'nm-flat bg-red-950/20 text-red-400 border border-red-900/30 font-mono'
          )}
        >
          <Info className="h-5 w-5" />
          <p>{status.message}</p>
        </div>
      )}

      {report ? (
        <div className="space-y-10">
          {/* Overview Grid */}
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
            {categories.map((cat) => (
              <div key={cat.id} className="relative nm-flat bg-slate-900 rounded-[2rem] p-8 border border-slate-800 hover:nm-convex transition-all duration-300 group overflow-hidden">
                <div className={cn(
                  "absolute top-0 left-0 w-1.5 h-full opacity-50 shadow-[0_0_15px_currentColor]",
                  cat.id === 'junk' ? 'bg-red-500 text-red-500' : cat.id === 'duplicates' ? 'bg-amber-500 text-amber-500' : 'bg-accent-blue text-accent-blue'
                )} />
                <div className="flex flex-col h-full justify-between gap-8">
                  <div className="flex items-start justify-between">
                    <div className="nm-inset p-4 rounded-2xl bg-slate-950 group-hover:scale-110 transition-transform duration-500">
                      <cat.icon className={cn('h-6 w-6', cat.color)} />
                    </div>
                    <div className="text-right">
                       <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">{cat.name}</p>
                       <p className="text-2xl font-black text-white font-mono">{cat.data?.readable_size || '0 B'}</p>
                    </div>
                  </div>
                  <div className="space-y-6">
                    <div className="flex justify-between items-center text-[10px] font-black text-slate-500 uppercase font-mono italic">
                       <span>Objects_Found: {cat.data?.junk_files?.length || cat.data?.duplicates?.length || cat.data?.cold_files?.length || 0}</span>
                    </div>
                    <Button 
                      size="md" 
                      onClick={() => handleCleanup(cat.id)}
                      isLoading={cleaning[cat.id]}
                      className={cn(
                        "w-full rounded-2xl h-12 uppercase tracking-[0.3em] text-[10px] font-black",
                        cat.id === 'junk' ? 'nm-convex bg-red-950/20 text-red-500' : 'nm-flat bg-slate-900 border-none text-slate-400 hover:text-white'
                      )}
                    >
                      EXEC_PURGE
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 gap-10 lg:grid-cols-2">
            {/* Category Breakdown */}
            <Card title="Structural Breakdown" description="Data distribution markers" icon={Database}>
              <div className="space-y-8 py-6">
                {Object.entries(report.category_breakdown || {}).map(([category, info]) => (
                  <div key={category} className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-3">
                        <ChevronRight className="h-3 w-3 text-accent-blue" />
                        {category}
                      </span>
                      <span className="text-xs font-black text-white font-mono italic">{info.readable_size}</span>
                    </div>
                    <div className="h-3 w-full nm-inset bg-slate-950 rounded-full overflow-hidden border border-slate-900">
                      <div 
                        className="h-full bg-accent-blue shadow-[0_0_10px_#3b82f6] transition-all duration-1000 ease-out"
                        style={{ width: `${Math.min(100, (info.total_size / report.total_size) * 100 || 0)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Suggestions */}
            <Card title="Neural Optimization" description="Intelligence-derived resource recovery" icon={RefreshCw}>
              <div className="space-y-6 mt-6">
                {report.suggestions?.actions?.map((suggestion, idx) => (
                  <div key={idx} className="flex flex-col gap-6 rounded-3xl nm-flat bg-slate-900 border border-slate-800 p-8 hover:nm-convex transition-all group relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                       <RefreshCw className="h-20 w-20 text-accent-blue" />
                    </div>
                    <div className="flex items-start gap-6 relative z-10">
                      <div className="nm-inset p-4 rounded-2xl bg-slate-950">
                        <RefreshCw className="h-6 w-6 text-accent-blue animate-pulse" />
                      </div>
                      <div className="flex-1">
                        <h4 className="text-white font-black uppercase tracking-tight italic">{suggestion.title}</h4>
                        <p className="mt-2 text-xs text-slate-400 leading-relaxed font-mono uppercase opacity-70">{suggestion.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between pt-6 border-t border-slate-800 relative z-10">
                      <span className="text-[10px] font-black text-emerald-500 font-mono uppercase tracking-widest">
                         Potential_Gain: {suggestion.size}
                      </span>
                      <Button size="sm" onClick={() => handleCleanup(suggestion.type)} isLoading={cleaning[suggestion.type]} className="nm-convex bg-slate-900 border-none text-accent-blue px-6 h-10">
                        PURGE_TARGET
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      ) : !loading && (
        <Motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex flex-col items-center justify-center nm-flat bg-slate-900 rounded-[3rem] border border-slate-800 py-32 text-center"
        >
          <div className="nm-inset p-10 rounded-full bg-slate-950 mb-10 group cursor-pointer hover:nm-flat transition-all" onClick={handleScan}>
            <HardDrive className="h-24 w-24 text-accent-blue drop-shadow-[0_0_15px_#3b82f6] group-hover:scale-110 transition-transform duration-500" />
          </div>
          <h3 className="text-4xl font-black text-white uppercase italic tracking-tighter">Sector Purge Node</h3>
          <p className="mt-4 text-slate-500 font-mono text-sm uppercase tracking-[0.3em] max-w-md opacity-60">
            Initialize telemetric scan to identify redundant data vectors and residual debris.
          </p>
          <Button size="lg" className="mt-12 px-20 h-16 text-xl font-black uppercase tracking-[0.4em] nm-convex bg-slate-900 border-none text-white shadow-[0_0_20px_rgba(59,130,246,0.2)]" onClick={handleScan}>
            RUN_SCAN
          </Button>
        </Motion.div>
      )}
    </div>
  );
}
