import React, { useState, useEffect, useMemo } from 'react';
import { storageApi } from '../api/client';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import {
  HardDrive, Trash2, Files, Snowflake, Search,
  AlertTriangle, RefreshCw, Info, Database, X, Terminal
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip } from 'recharts';
import { cn } from '../utils/cn';

export function Storage() {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [cleaning, setCleaning] = useState({});
  const [toast, setToast] = useState(null);
  const [hexScroll, setHexScroll] = useState([]);

  // Simulated HEX scroll for the scan overlay
  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => {
        const hex = Array.from({ length: 10 }, () =>
          Math.floor(Math.random() * 0xffffff).toString(16).toUpperCase().padStart(6, '0')
        );
        setHexScroll(hex);
      }, 100);
      return () => clearInterval(interval);
    }
  }, [loading]);

  const handleScan = async () => {
    setLoading(true);
    setError(null);
    setReport(null);

    try {
      const minTimePromise = new Promise(resolve => setTimeout(resolve, 4000));
      const [response] = await Promise.all([
        storageApi.scan({ path: 'C:/Users' }),
        minTimePromise
      ]);
      setReport(response.data);
    } catch (err) {
      setError('Telemetric scan failed. Primary link severed.');
    } finally {
      setLoading(false);
    }
  };

  const handleCleanup = async (type) => {
    setCleaning(prev => ({ ...prev, [type]: true }));
    try {
      const previewRes = await storageApi.cleanup(type, { confirm: false, dryRun: true });
      const { total_files, risk } = previewRes.data.preview || {};

      const proceed = window.confirm(
        `[DRY_RUN_WARNING]\nType: ${type.toUpperCase()}\nRisk: ${risk || 'MODERATE'}\nAction: Delete ${total_files || 0} objects.\n\nContinue with purge?`
      );

      if (!proceed) return;

      const response = await storageApi.cleanup(type, { confirm: true, dryRun: false });
      setToast({
        type: 'success',
        message: `DELETED: ${response.data.total_deleted} units. Sector ${type} stabilized.`
      });
      setTimeout(() => setToast(null), 5000);
      handleScan();
    } catch (err) {
      setToast({ type: 'error', message: 'PURGE_FAILURE: Resistance detected.' });
    } finally {
      setCleaning(prev => ({ ...prev, [type]: false }));
    }
  };

  const pieData = useMemo(() => {
    if (!report) return [];
    return [
      { name: 'Junk', value: report.junk?.total_junk_size || 0, color: '#FF3D57' },
      { name: 'Cold', value: report.cold_files?.total_cold_size || 0, color: '#00E5FF' },
      { name: 'Redundant', value: report.duplicates?.total_duplicate_size || 0, color: '#FFB300' },
      { name: 'Used', value: (report.summary?.total_files ? 100000000 : 0), color: '#1E293B' }, // Stub Used
    ];
  }, [report]);

  return (
    <div className="relative min-h-screen pb-20">
      {/* 1. INITIAL STATE: Launch Button */}
      {!loading && !report && (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="relative group cursor-pointer" onClick={handleScan}>
            {/* Rotating Outer Rings */}
            <div className="absolute inset-[-20px] rounded-full border border-cyan-500/20 animate-[spin_10s_linear_infinite]" />
            <div className="absolute inset-[-40px] rounded-full border border-cyan-500/10 animate-[spin_15s_linear_infinite_reverse]" />

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="relative h-64 w-64 rounded-full bg-[#080B12] border-2 border-cyan-500/50 shadow-[0_0_50px_rgba(0,229,255,0.2)] flex flex-col items-center justify-center gap-2 group-hover:border-cyan-400 group-hover:shadow-[0_0_70px_rgba(0,229,255,0.4)] transition-all"
            >
              <Search className="h-12 w-12 text-cyan-400" />
              <span className="text-sm font-black tracking-[0.4em] text-cyan-400">INIT DEEP SCAN</span>
            </motion.button>
          </div>
          <p className="mt-16 font-mono text-xs text-slate-500 tracking-[0.5em] uppercase animate-pulse">
            Awaiting Command: Select sector for telemetric audit
          </p>
        </div>
      )}

      {/* 2. LOADING STATE: Full Screen Scan Line Overlay */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] bg-[#080B12] flex flex-col items-center justify-center"
          >
            {/* Vertical Scan Line */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              <div className="w-full h-[2px] bg-cyan-500/50 shadow-[0_0_20px_cyan] animate-[scan_2s_ease-in-out_infinite] absolute top-0" />
            </div>

            <div className="z-10 text-center space-y-6">
              <div className="flex gap-4 mb-8">
                {hexScroll.map((hex, i) => (
                  <span key={i} className="text-[10px] font-mono text-cyan-900">{hex}</span>
                ))}
              </div>
              <h2 className="text-4xl font-black italic tracking-tighter text-white animate-pulse">SCANNING SUBSPACE</h2>
              <div className="font-mono text-xs text-cyan-500/60 tracking-widest">
                AUDITING FILE SYSTEM NODES... [OK]<br />
                MAP VIRTUAL SECTORS... [ACTIVE]
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 3. REPORT STATE: Results */}
      {report && !loading && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
          <div className="flex justify-between items-end">
            <div>
              <h1 className="text-4xl font-black italic tracking-tighter text-white uppercase">Sector Report</h1>
              <p className="font-mono text-xs text-slate-500 uppercase tracking-widest mt-2">Analysis complete: Redundancy isolated</p>
            </div>
            <Button onClick={handleScan} variant="outline" className="border-cyan-500/20 text-cyan-500 font-mono text-[10px] tracking-widest">
              RE SCAN SECTOR
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { id: 'junk', label: 'JUNK_DEBRIS', icon: Trash2, color: '#FF3D57', data: report.junk, sizeKey: 'total_junk_size', fileKey: 'junk_files' },
              { id: 'cold', label: 'DEEP_FREEZE', icon: Snowflake, color: '#00E5FF', data: report.cold_files, sizeKey: 'total_cold_size', fileKey: 'cold_files' },
              { id: 'duplicates', label: 'REDUNDANCY', icon: Files, color: '#FFB300', data: report.duplicates, sizeKey: 'total_duplicate_size', fileKey: 'duplicates' },
            ].map((cat) => (
              <div key={cat.id} className="glass-card p-6 border-l-4" style={{ borderLeftColor: cat.color }}>
                <div className="flex justify-between items-start mb-6">
                  <cat.icon size={20} style={{ color: cat.color }} />
                  <span className="font-mono text-[10px] text-slate-500 tracking-tighter uppercase">{cat.label}</span>
                </div>
                <div className="mb-8">
                  <h3 className="text-3xl font-black font-mono text-white">{((cat.data?.[cat.sizeKey] || 0) / (1024 * 1024)).toFixed(1)}<span className="text-sm ml-1 opacity-40">MB</span></h3>
                  <p className="text-[10px] font-mono text-slate-400 uppercase mt-1">OBJECTS: {cat.data?.[cat.fileKey]?.length || 0}</p>
                </div>
                <Button
                  onClick={() => handleCleanup(cat.id)}
                  isLoading={cleaning[cat.id]}
                  className="w-full font-black text-[10px] tracking-widest py-4"
                  style={{ backgroundColor: `${cat.color}15`, color: cat.color, border: `1px solid ${cat.color}30` }}
                >
                  INIT_PURGE
                </Button>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card title="Distribution_Map" icon={Database}>
              <div className="h-[300px] w-full mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                      stroke="none"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip
                      contentStyle={{ backgroundColor: '#080B12', border: '1px solid #1E293B', borderRadius: '8px' }}
                      itemStyle={{ color: '#00E5FF', fontFamily: 'Space Mono', fontSize: '10px' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card title="Optimization_Nodes" icon={Terminal}>
              <div className="space-y-4 mt-4">
                {report.junk?.junk_files?.slice(0, 4).map((f, i) => (
                  <div key={i} className="flex justify-between items-center p-3 bg-white/5 rounded font-mono text-[10px]">
                    <span className="text-slate-400 truncate max-w-[200px]">&gt; {f.path?.split('/').pop()}</span>
                    <span className="text-red-400">{(f.size / 1024).toFixed(0)}KB</span>
                  </div>
                ))}
                <div className="p-4 border border-dashed border-slate-800 rounded text-center">
                  <p className="text-[9px] font-mono text-slate-600 uppercase tracking-widest">Awaiting further sector clearance...</p>
                </div>
              </div>
            </Card>
          </div>
        </motion.div>
      )}

      {/* 4. TOAST NOTIFICATIONS */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 50, x: 0 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className={cn(
              "fixed bottom-8 right-8 z-[200] px-6 py-4 rounded-xl border font-mono text-xs font-bold uppercase tracking-widest flex items-center gap-4 shadow-2xl",
              toast.type === 'success' ? "bg-emerald-950/90 border-emerald-500 text-emerald-400" : "bg-red-950/90 border-red-500 text-red-400"
            )}
          >
            {toast.type === 'success' ? <Info size={16} /> : <AlertTriangle size={16} />}
            {toast.message}
            <X size={14} className="ml-4 cursor-pointer opacity-50 hover:opacity-100" onClick={() => setToast(null)} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}