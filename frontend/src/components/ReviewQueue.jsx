import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Clock, 
  UserCheck, 
  FileText, 
  Edit3, 
  Eye, 
  Filter,
  Check,
  ShieldAlert,
  Send
} from 'lucide-react';
import { apiService } from '../services/api';
import DocumentViewer from './DocumentViewer';

export default function ReviewQueue({ onReviewActionCompleted }) {
  const [reviews, setReviews] = useState([]);
  const [filterStatus, setFilterStatus] = useState('NEEDS_REVIEW');
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [correctedFields, setCorrectedFields] = useState({});
  const [reviewerNotes, setReviewerNotes] = useState('');
  const [overrideClass, setOverrideClass] = useState('');

  const docClasses = [
    "INVOICE",
    "RECEIPT",
    "EMPLOYMENT_CONTRACT",
    "IDENTITY_DOCUMENT",
    "RESUME",
    "BANK_STATEMENT",
    "TAX_FORM"
  ];

  useEffect(() => {
    loadReviewQueue();
  }, [filterStatus]);

  const loadReviewQueue = async () => {
    try {
      setIsLoading(true);
      const data = await apiService.getReviewQueue(filterStatus);
      setReviews(data);
      if (data.length > 0 && !selectedDoc) {
        selectDocumentForReview(data[0]);
      } else if (data.length === 0) {
        setSelectedDoc(null);
      }
    } catch (err) {
      console.error('Failed to load review queue:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const selectDocumentForReview = (doc) => {
    setSelectedDoc(doc);
    setReviewerNotes(doc.review_notes || '');
    setOverrideClass(doc.classification?.final_class || doc.final_document_class || 'INVOICE');
    
    // Initialize editable fields
    const initialFields = {};
    if (doc.extracted_fields) {
      Object.entries(doc.extracted_fields).forEach(([k, v]) => {
        initialFields[k] = typeof v === 'object' ? v.value : v;
      });
    }
    setCorrectedFields(initialFields);
  };

  const handleFieldChange = (key, val) => {
    setCorrectedFields((prev) => ({
      ...prev,
      [key]: val
    }));
  };

  const handleSubmitDecision = async (status) => {
    if (!selectedDoc) return;
    try {
      setIsLoading(true);
      const submission = {
        status: status, // 'APPROVED' or 'REJECTED'
        corrected_fields: correctedFields,
        final_document_class: overrideClass,
        reviewer_notes: reviewerNotes,
        reviewer_name: 'Compliance Auditor'
      };

      await apiService.submitReviewDecision(selectedDoc.id, submission);
      if (onReviewActionCompleted) onReviewActionCompleted();
      await loadReviewQueue();
    } catch (err) {
      alert('Failed to submit review decision: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Review Queue Header */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <UserCheck className="w-5 h-5 text-teal-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              Human-In-The-Loop (HITL) Manual Review Queue
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Audit low-confidence classifications, correct extracted metadata, verify PII compliance, and approve documents.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex bg-slate-900 rounded-xl p-1 border border-slate-800 text-xs">
          {['NEEDS_REVIEW', 'APPROVED', 'REJECTED', 'ALL'].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                filterStatus === st
                  ? 'bg-teal-500 text-slate-950 shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {st.replace(/_/g, ' ')}
            </button>
          ))}
        </div>
      </div>

      {reviews.length === 0 && !isLoading ? (
        <div className="p-12 rounded-2xl glass-panel text-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-teal-500/10 text-teal-400 flex items-center justify-center mx-auto">
            <Check className="w-6 h-6" />
          </div>
          <h3 className="text-base font-semibold text-white">Queue is Clear!</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            No documents matching status "{filterStatus}". New low-confidence documents will automatically appear here.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Review Item List */}
          <div className="lg:col-span-4 space-y-3 max-h-[750px] overflow-y-auto pr-1">
            {reviews.map((doc) => {
              const isSelected = selectedDoc?.id === doc.id;
              return (
                <div
                  key={doc.id}
                  onClick={() => selectDocumentForReview(doc)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-teal-950/40 border-teal-500/60 shadow-lg shadow-teal-500/10'
                      : 'bg-slate-900/60 hover:bg-slate-900 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-start justify-between mb-1.5">
                    <div className="flex items-center space-x-2">
                      <FileText className={`w-4 h-4 ${isSelected ? 'text-teal-400' : 'text-slate-400'}`} />
                      <span className="text-xs font-semibold text-white truncate max-w-[160px]">
                        {doc.filename}
                      </span>
                    </div>
                    <span className={`px-2 py-0.2 text-[9px] font-bold rounded-full uppercase ${
                      doc.status === 'APPROVED'
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : doc.status === 'REJECTED'
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    }`}>
                      {doc.status}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2">
                    <span>Class: <strong className="text-slate-200">{doc.classification?.final_class}</strong></span>
                    <span className="font-mono text-teal-400">
                      Conf: {doc.classification ? Math.round(doc.classification.pytorch_confidence * 100) : 0}%
                    </span>
                  </div>

                  {doc.has_sensitive_pii && (
                    <div className="mt-2 flex items-center space-x-1 text-[10px] text-amber-400 font-medium">
                      <ShieldAlert className="w-3 h-3" />
                      <span>Contains Sensitive PII</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Right Column: Review & Correction Workbench */}
          {selectedDoc && (
            <div className="lg:col-span-8 space-y-6">
              {/* Document Image Viewer */}
              <div className="h-[450px]">
                <DocumentViewer document={selectedDoc} />
              </div>

              {/* Correction Workbench Form */}
              <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-5">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div className="flex items-center space-x-2">
                    <Edit3 className="w-4 h-4 text-teal-400" />
                    <h3 className="text-sm font-bold text-white uppercase tracking-wide">
                      Review & Field Correction Workbench
                    </h3>
                  </div>
                  <span className="text-xs text-slate-400 font-mono">
                    ID: {selectedDoc.id.substring(0, 8)}...
                  </span>
                </div>

                {/* Document Class Override */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Assigned Document Type
                  </label>
                  <select
                    value={overrideClass}
                    onChange={(e) => setOverrideClass(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-teal-500 font-medium"
                  >
                    {docClasses.map((c) => (
                      <option key={c} value={c}>
                        {c.replace(/_/g, ' ')}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Key Field Value Inputs */}
                <div className="space-y-3">
                  <label className="block text-xs font-semibold text-slate-300">
                    Verify & Correct Extracted Fields
                  </label>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {Object.entries(correctedFields).map(([key, val]) => (
                      <div key={key} className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                        <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                          {key.replace(/_/g, ' ')}
                        </label>
                        <input
                          type="text"
                          value={val || ''}
                          onChange={(e) => handleFieldChange(key, e.target.value)}
                          className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-teal-500 font-mono"
                        />
                      </div>
                    ))}
                  </div>
                </div>

                {/* Reviewer Notes */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Auditor Review Notes
                  </label>
                  <textarea
                    rows={2}
                    value={reviewerNotes}
                    onChange={(e) => setReviewerNotes(e.target.value)}
                    placeholder="Add audit notes, reason for override, or exception flags..."
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
                  />
                </div>

                {/* Action Buttons */}
                <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
                  <button
                    onClick={() => handleSubmitDecision('REJECTED')}
                    disabled={isLoading}
                    className="px-4 py-2.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-bold flex items-center space-x-2 transition-all cursor-pointer"
                  >
                    <XCircle className="w-4 h-4" />
                    <span>Reject Document</span>
                  </button>

                  <button
                    onClick={() => handleSubmitDecision('APPROVED')}
                    disabled={isLoading}
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-xs flex items-center space-x-2 shadow-lg shadow-emerald-500/20 transition-all cursor-pointer"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Approve & Save Corrections</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
