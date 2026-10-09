import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Zap, 
  Database, 
  Play, 
  RotateCw, 
  CheckCircle2, 
  Clock, 
  Layers, 
  Target,
  Sparkles
} from 'lucide-react';
import { apiService } from '../services/api';

export default function ModelComparison() {
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [activeMatrix, setActiveMatrix] = useState('pytorch'); // 'pytorch' | 'tfidf'

  useEffect(() => {
    loadBenchmark();
  }, []);

  const loadBenchmark = async () => {
    try {
      setIsRunning(true);
      const data = await apiService.runBenchmark();
      setBenchmarkData(data);
    } catch (err) {
      console.error('Benchmark error:', err);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Benchmark Header Banner */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-teal-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              Model Benchmark & Comparative Evaluation
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl">
            Side-by-side performance evaluation of the fine-tuned PyTorch Deep Classifier against the Scikit-Learn TF-IDF Baseline on real document datasets.
          </p>
        </div>

        <button
          onClick={loadBenchmark}
          disabled={isRunning}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-500 hover:from-teal-400 hover:to-cyan-400 text-slate-950 font-bold text-xs sm:text-sm flex items-center space-x-2 shadow-lg shadow-teal-500/20 disabled:opacity-50 transition-all cursor-pointer"
        >
          {isRunning ? (
            <RotateCw className="w-4 h-4 animate-spin" />
          ) : (
            <Play className="w-4 h-4 fill-current" />
          )}
          <span>{isRunning ? 'Running Benchmark...' : 'Run Live Benchmark'}</span>
        </button>
      </div>

      {benchmarkData && (
        <>
          {/* Key Metrics Comparison Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* PyTorch Model Card */}
            <div className="p-6 rounded-2xl bg-gradient-to-b from-teal-950/40 to-slate-900/90 border border-teal-500/40 space-y-5 relative overflow-hidden">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="p-2 rounded-xl bg-teal-500/20 text-teal-400">
                    <Zap className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">PyTorch Deep Classifier</h3>
                    <p className="text-xs text-teal-300/80">Learned Embedding Bag + Multi-Layer Perceptron</p>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-teal-500/20 text-teal-300 border border-teal-500/30">
                  Primary Model
                </span>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-center">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Accuracy</div>
                  <div className="text-2xl font-extrabold text-teal-400 font-mono mt-1">
                    {(benchmarkData.pytorch_metrics.accuracy * 100).toFixed(1)}%
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-center">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Macro F1</div>
                  <div className="text-2xl font-extrabold text-teal-400 font-mono mt-1">
                    {benchmarkData.pytorch_metrics.macro_f1.toFixed(3)}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-center">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Avg Latency</div>
                  <div className="text-2xl font-extrabold text-white font-mono mt-1">
                    {benchmarkData.pytorch_metrics.avg_latency_ms}ms
                  </div>
                </div>
              </div>

              <div className="space-y-2 pt-2 text-xs text-slate-300">
                <div className="flex justify-between">
                  <span className="text-slate-400">Macro Precision:</span>
                  <span className="font-mono font-semibold text-white">{(benchmarkData.pytorch_metrics.precision_macro * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Macro Recall:</span>
                  <span className="font-mono font-semibold text-white">{(benchmarkData.pytorch_metrics.recall_macro * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            {/* TF-IDF Baseline Card */}
            <div className="p-6 rounded-2xl bg-gradient-to-b from-slate-900/60 to-slate-950/90 border border-slate-800 space-y-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="p-2 rounded-xl bg-slate-800 text-slate-400">
                    <Database className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-200">TF-IDF Baseline</h3>
                    <p className="text-xs text-slate-500">N-gram (1,2) Vectorizer + Logistic Regression</p>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-400 border border-slate-700">
                  Baseline
                </span>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-center">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Accuracy</div>
                  <div className="text-2xl font-extrabold text-slate-200 font-mono mt-1">
                    {(benchmarkData.tfidf_metrics.accuracy * 100).toFixed(1)}%
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-center">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Macro F1</div>
                  <div className="text-2xl font-extrabold text-slate-200 font-mono mt-1">
                    {benchmarkData.tfidf_metrics.macro_f1.toFixed(3)}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-center">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Avg Latency</div>
                  <div className="text-2xl font-extrabold text-slate-200 font-mono mt-1">
                    {benchmarkData.tfidf_metrics.avg_latency_ms}ms
                  </div>
                </div>
              </div>

              <div className="space-y-2 pt-2 text-xs text-slate-300">
                <div className="flex justify-between">
                  <span className="text-slate-400">Macro Precision:</span>
                  <span className="font-mono font-semibold text-white">{(benchmarkData.tfidf_metrics.precision_macro * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Macro Recall:</span>
                  <span className="font-mono font-semibold text-white">{(benchmarkData.tfidf_metrics.recall_macro * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Per-Class F1 Score Comparison Table */}
          <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-teal-400" />
                <h3 className="text-sm font-semibold text-white uppercase tracking-wider">
                  Per-Class F1 Score Breakdown
                </h3>
              </div>
              <span className="text-xs text-slate-400 font-mono">
                {benchmarkData.total_samples} Evaluation Documents
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="py-2.5 px-3 font-semibold">Document Class</th>
                    <th className="py-2.5 px-3 font-semibold">PyTorch F1</th>
                    <th className="py-2.5 px-3 font-semibold">TF-IDF F1</th>
                    <th className="py-2.5 px-3 font-semibold">Performance Comparison</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {benchmarkData.classes.map((cls) => {
                    const pytF1 = benchmarkData.pytorch_metrics.per_class_f1[cls] || 0;
                    const tfidfF1 = benchmarkData.tfidf_metrics.per_class_f1[cls] || 0;
                    const diff = pytF1 - tfidfF1;

                    return (
                      <tr key={cls} className="hover:bg-slate-900/40 transition-colors">
                        <td className="py-3 px-3 font-medium text-slate-200">
                          {cls.replace(/_/g, ' ')}
                        </td>
                        <td className="py-3 px-3 font-mono font-bold text-teal-400">
                          {pytF1.toFixed(2)}
                        </td>
                        <td className="py-3 px-3 font-mono text-slate-400">
                          {tfidfF1.toFixed(2)}
                        </td>
                        <td className="py-3 px-3">
                          <div className="flex items-center space-x-2">
                            <div className="w-32 bg-slate-800 h-2 rounded-full overflow-hidden flex">
                              <div
                                className="bg-teal-400 h-full"
                                style={{ width: `${pytF1 * 100}%` }}
                              />
                            </div>
                            <span className={`text-[10px] font-mono font-bold ${diff >= 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {diff >= 0 ? `+${(diff * 100).toFixed(0)}%` : `${(diff * 100).toFixed(0)}%`}
                            </span>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Multi-Class Confusion Matrix */}
          <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Layers className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-semibold text-white uppercase tracking-wider">
                  Confusion Matrix ({activeMatrix === 'pytorch' ? 'PyTorch Model' : 'TF-IDF Baseline'})
                </h3>
              </div>

              <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-800 text-xs">
                <button
                  onClick={() => setActiveMatrix('pytorch')}
                  className={`px-3 py-1 rounded-md font-medium transition-all ${
                    activeMatrix === 'pytorch'
                      ? 'bg-teal-500 text-slate-950 font-bold'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  PyTorch Matrix
                </button>
                <button
                  onClick={() => setActiveMatrix('tfidf')}
                  className={`px-3 py-1 rounded-md font-medium transition-all ${
                    activeMatrix === 'tfidf'
                      ? 'bg-slate-700 text-white font-bold'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  TF-IDF Matrix
                </button>
              </div>
            </div>

            <div className="overflow-x-auto pt-2">
              <div className="min-w-[600px]">
                <div className="grid grid-cols-8 gap-1.5 text-center text-xs font-mono">
                  <div className="p-2 text-slate-500 font-bold text-left">Pred →<br/>True ↓</div>
                  {benchmarkData.classes.map((c) => (
                    <div key={c} className="p-2 text-slate-400 font-semibold truncate text-[10px]" title={c}>
                      {c.substring(0, 4)}
                    </div>
                  ))}

                  {benchmarkData.confusion_matrices[activeMatrix]?.map((row, rIdx) => (
                    <React.Fragment key={rIdx}>
                      <div className="p-2 text-slate-400 font-semibold truncate text-[10px] text-left" title={benchmarkData.classes[rIdx]}>
                        {benchmarkData.classes[rIdx].substring(0, 4)}
                      </div>
                      {row.map((val, cIdx) => {
                        const isDiag = rIdx === cIdx;
                        return (
                          <div
                            key={cIdx}
                            className={`p-3 rounded-lg border font-bold ${
                              isDiag && val > 0
                                ? 'bg-teal-500/20 text-teal-300 border-teal-500/40'
                                : val > 0
                                ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                                : 'bg-slate-900/40 text-slate-600 border-slate-800'
                            }`}
                          >
                            {val}
                          </div>
                        );
                      })}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
