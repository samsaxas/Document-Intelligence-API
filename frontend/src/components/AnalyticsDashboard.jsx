import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  TrendingUp, 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  Cloud, 
  Server, 
  FileText,
  RefreshCw
} from 'lucide-react';
import { apiService } from '../services/api';

export default function AnalyticsDashboard({ stats, onSelectDocument }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadRecentDocs();
  }, []);

  const loadRecentDocs = async () => {
    try {
      setLoading(true);
      const data = await apiService.listDocuments('ALL', 10);
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load recent documents:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Docs */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Documents</span>
            <div className="text-3xl font-extrabold text-white font-mono mt-1">
              {stats?.total_documents || 0}
            </div>
            <span className="text-[11px] text-teal-400 font-medium">All Document Types</span>
          </div>
          <div className="p-3 rounded-2xl bg-teal-500/10 text-teal-400">
            <FileText className="w-6 h-6" />
          </div>
        </div>

        {/* Automation Rate */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">STP Automation Rate</span>
            <div className="text-3xl font-extrabold text-emerald-400 font-mono mt-1">
              {stats?.automation_rate_pct || 0}%
            </div>
            <span className="text-[11px] text-slate-400 font-medium">Straight-Through Processing</span>
          </div>
          <div className="p-3 rounded-2xl bg-emerald-500/10 text-emerald-400">
            <TrendingUp className="w-6 h-6" />
          </div>
        </div>

        {/* Review Queue */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Pending HITL Reviews</span>
            <div className="text-3xl font-extrabold text-amber-400 font-mono mt-1">
              {stats?.needs_review || 0}
            </div>
            <span className="text-[11px] text-amber-300/80 font-medium">Requires Human Triage</span>
          </div>
          <div className="p-3 rounded-2xl bg-amber-500/10 text-amber-400">
            <Clock className="w-6 h-6" />
          </div>
        </div>

        {/* PII Flagged */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">PII Masked Docs</span>
            <div className="text-3xl font-extrabold text-rose-400 font-mono mt-1">
              {stats?.pii_flagged || 0}
            </div>
            <span className="text-[11px] text-rose-300/80 font-medium">Auto Redaction Applied</span>
          </div>
          <div className="p-3 rounded-2xl bg-rose-500/10 text-rose-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Recent Processing Audit Log */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-teal-400" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wide">
              Recent Document Audit Log
            </h3>
          </div>
          <button
            onClick={loadRecentDocs}
            disabled={loading}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="py-2.5 px-3 font-semibold">Document Name</th>
                <th className="py-2.5 px-3 font-semibold">Assigned Class</th>
                <th className="py-2.5 px-3 font-semibold">Confidence</th>
                <th className="py-2.5 px-3 font-semibold">Status</th>
                <th className="py-2.5 px-3 font-semibold">PII Security</th>
                <th className="py-2.5 px-3 font-semibold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-3 px-3 font-semibold text-slate-200 truncate max-w-[200px]">
                    {doc.filename}
                  </td>
                  <td className="py-3 px-3 text-slate-300 font-mono">
                    {doc.classification?.final_class || doc.final_document_class || 'N/A'}
                  </td>
                  <td className="py-3 px-3 font-mono text-teal-400">
                    {doc.classification ? `${Math.round(doc.classification.pytorch_confidence * 100)}%` : 'N/A'}
                  </td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                      doc.status === 'PROCESSED' || doc.status === 'APPROVED'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : doc.status === 'REJECTED'
                        ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {doc.status}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    {doc.has_sensitive_pii ? (
                      <span className="text-[10px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded-full">
                        Masked
                      </span>
                    ) : (
                      <span className="text-[10px] text-slate-500 font-mono">Clean</span>
                    )}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={() => onSelectDocument(doc)}
                      className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-teal-500 hover:text-slate-950 text-slate-300 text-xs font-semibold transition-all cursor-pointer"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
