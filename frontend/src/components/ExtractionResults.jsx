import React, { useState } from 'react';
import { 
  CheckCircle2, 
  AlertCircle, 
  ShieldAlert, 
  Edit3, 
  Save, 
  Cpu, 
  Zap, 
  Database,
  Tag,
  Copy,
  Check
} from 'lucide-react';

export default function ExtractionResults({ document, onFieldUpdated }) {
  const [editingField, setEditingField] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [copiedField, setCopiedField] = useState(null);

  if (!document) return null;

  const { classification, extracted_fields, pii_entities, status } = document;

  const handleStartEdit = (key, currentVal) => {
    setEditingField(key);
    setEditValue(currentVal);
  };

  const handleSaveEdit = (key) => {
    if (onFieldUpdated) {
      onFieldUpdated(key, editValue);
    }
    setEditingField(null);
  };

  const copyToClipboard = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedField(key);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const getConfidenceBadge = (score) => {
    const pct = Math.round(score * 100);
    if (pct >= 90) {
      return (
        <span className="px-2 py-0.5 rounded-md text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          {pct}% Conf
        </span>
      );
    } else if (pct >= 80) {
      return (
        <span className="px-2 py-0.5 rounded-md text-[10px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
          {pct}% Conf
        </span>
      );
    } else {
      return (
        <span className="px-2 py-0.5 rounded-md text-[10px] font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
          {pct}% Low
        </span>
      );
    }
  };

  return (
    <div className="space-y-5">
      {/* Classification Card (PyTorch vs TF-IDF Baseline) */}
      <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-teal-400" />
            <h3 className="text-sm font-semibold text-white tracking-wide uppercase">
              Document Classification
            </h3>
          </div>
          <span className="text-[11px] font-mono text-slate-400">
            Ensemble Decision
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {/* PyTorch Model Box */}
          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-teal-500/30 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-teal-500/5 rounded-full blur-xl pointer-events-none" />
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span className="font-semibold text-teal-400 flex items-center space-x-1">
                <Zap className="w-3.5 h-3.5" />
                <span>PyTorch Deep Model</span>
              </span>
              <span className="font-mono text-white font-bold">
                {classification ? Math.round(classification.pytorch_confidence * 100) : 0}%
              </span>
            </div>
            <div className="text-base font-bold text-white tracking-tight mt-1">
              {classification?.pytorch_class || 'Processing...'}
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-2">
              <div
                className="bg-gradient-to-r from-teal-500 to-cyan-400 h-full rounded-full transition-all duration-500"
                style={{ width: `${classification ? classification.pytorch_confidence * 100 : 0}%` }}
              />
            </div>
          </div>

          {/* TF-IDF Baseline Box */}
          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 relative overflow-hidden">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span className="font-semibold text-slate-300 flex items-center space-x-1">
                <Database className="w-3.5 h-3.5 text-slate-400" />
                <span>TF-IDF Baseline</span>
              </span>
              <span className="font-mono text-slate-300 font-bold">
                {classification ? Math.round(classification.tfidf_confidence * 100) : 0}%
              </span>
            </div>
            <div className="text-base font-bold text-slate-200 tracking-tight mt-1">
              {classification?.tfidf_class || 'Processing...'}
            </div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-2">
              <div
                className="bg-slate-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${classification ? classification.tfidf_confidence * 100 : 0}%` }}
              />
            </div>
          </div>
        </div>

        <div className="p-2.5 rounded-xl bg-teal-950/30 border border-teal-500/20 flex items-center justify-between text-xs">
          <span className="text-slate-400">Assigned Document Class:</span>
          <span className="font-bold text-teal-300 font-mono">
            {classification?.final_class || 'UNCLASSIFIED'}
          </span>
        </div>
      </div>

      {/* Extracted Key-Value Fields Card */}
      <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Tag className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-semibold text-white tracking-wide uppercase">
              Extracted Key Fields (Transformers NER)
            </h3>
          </div>
          <span className="text-[11px] text-slate-400 font-mono">
            {extracted_fields ? Object.keys(extracted_fields).length : 0} Fields Extracted
          </span>
        </div>

        <div className="space-y-2.5">
          {extracted_fields && Object.entries(extracted_fields).map(([key, fieldData]) => {
            const isEditing = editingField === key;
            const formattedKey = key.replace(/_/g, ' ').toUpperCase();

            return (
              <div
                key={key}
                className="p-3 rounded-xl bg-slate-900/70 border border-slate-800/80 hover:border-slate-700 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-2"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="text-[11px] font-semibold text-slate-400 tracking-wider">
                      {formattedKey}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono bg-slate-950 px-1.5 py-0.2 rounded border border-slate-800">
                      {fieldData.source}
                    </span>
                  </div>

                  {isEditing ? (
                    <div className="flex items-center space-x-2 mt-1.5">
                      <input
                        type="text"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        className="flex-1 bg-slate-950 border border-teal-500 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none"
                      />
                      <button
                        onClick={() => handleSaveEdit(key)}
                        className="p-1 rounded bg-teal-500 hover:bg-teal-600 text-slate-950 font-bold"
                      >
                        <Save className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ) : (
                    <div className="text-sm font-medium text-slate-100 font-mono truncate mt-0.5">
                      {fieldData.value || 'N/A'}
                    </div>
                  )}
                </div>

                <div className="flex items-center space-x-2 self-end sm:self-center">
                  {getConfidenceBadge(fieldData.confidence)}
                  
                  {!isEditing && (
                    <>
                      <button
                        onClick={() => copyToClipboard(fieldData.value, key)}
                        className="p-1.5 rounded-lg text-slate-500 hover:text-slate-200 hover:bg-slate-800 transition-colors"
                        title="Copy field value"
                      >
                        {copiedField === key ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                      </button>
                      <button
                        onClick={() => handleStartEdit(key, fieldData.value)}
                        className="p-1.5 rounded-lg text-slate-500 hover:text-teal-400 hover:bg-slate-800 transition-colors"
                        title="Edit field value"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* PII Detection Alert Card */}
      {pii_entities && pii_entities.length > 0 && (
        <div className="p-4 rounded-2xl bg-amber-950/20 border border-amber-500/30 space-y-2.5">
          <div className="flex items-center space-x-2 text-amber-400">
            <ShieldAlert className="w-4 h-4" />
            <h4 className="text-xs font-bold uppercase tracking-wider">
              Sensitive PII Detected ({pii_entities.length} Items Flagged)
            </h4>
          </div>
          <p className="text-xs text-slate-300">
            Automated visual redaction and token masking have been applied to protect confidential citizen/company data.
          </p>
          <div className="flex flex-wrap gap-1.5 pt-1">
            {pii_entities.map((p, i) => (
              <span
                key={i}
                className="px-2 py-0.5 rounded-md text-[10px] font-mono font-medium bg-slate-900 border border-amber-500/30 text-amber-300"
              >
                {p.entity_type}: {p.masked_value}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
