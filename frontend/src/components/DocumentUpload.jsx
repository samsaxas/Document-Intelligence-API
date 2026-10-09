import React, { useState, useRef } from 'react';
import { 
  UploadCloud, 
  FileText, 
  Receipt, 
  Briefcase, 
  CreditCard, 
  Loader2, 
  Sparkles,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';

export default function DocumentUpload({ onDocumentProcessed, isProcessing, setIsProcessing }) {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const presets = [
    { id: 'INVOICE', label: 'Commercial Invoice', icon: FileText, desc: 'Vendor, Invoice #, Tax, Line totals' },
    { id: 'RECEIPT', label: 'Store Receipt', icon: Receipt, desc: 'Merchant, Payment method, Tax, Items' },
    { id: 'EMPLOYMENT_CONTRACT', label: 'Employment Contract', icon: Briefcase, desc: 'Salary, Roles, Start date, Covenants' },
    { id: 'IDENTITY_DOCUMENT', label: 'National ID / Aadhaar', icon: CreditCard, desc: 'Full Name, ID #, DOB, Address' },
  ];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleFileUpload = async (file) => {
    try {
      setIsProcessing(true);
      const { apiService } = await import('../services/api');
      const result = await apiService.processDocument(file);
      onDocumentProcessed(result);
    } catch (err) {
      console.error('Upload error:', err);
      alert('Failed to process document: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePresetClick = async (presetId) => {
    try {
      setIsProcessing(true);
      const { apiService } = await import('../services/api');
      const result = await apiService.processPreset(presetId);
      onDocumentProcessed(result);
    } catch (err) {
      console.error('Preset error:', err);
      alert('Failed to process preset: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Drag & Drop Upload Card */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative p-8 rounded-2xl border-2 border-dashed transition-all duration-300 cursor-pointer text-center group ${
          dragActive
            ? 'border-teal-400 bg-teal-500/10 scale-[1.01]'
            : 'border-slate-700 hover:border-teal-500/60 bg-slate-900/40 hover:bg-slate-900/70'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.tiff,.webp"
          onChange={handleFileInputChange}
          className="hidden"
          disabled={isProcessing}
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-teal-500/20 to-cyan-500/10 border border-teal-500/30 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
            {isProcessing ? (
              <Loader2 className="w-8 h-8 text-teal-400 animate-spin" />
            ) : (
              <UploadCloud className="w-8 h-8 text-teal-400 group-hover:text-teal-300" />
            )}
          </div>

          <div>
            <h3 className="text-lg font-semibold text-white">
              {isProcessing ? 'Analyzing Document Pipeline...' : 'Upload Scanned Document or PDF'}
            </h3>
            <p className="text-sm text-slate-400 mt-1">
              Drag and drop any PDF, PNG, or JPG document to trigger OCR, PyTorch classification & NER
            </p>
          </div>

          <div className="flex items-center space-x-3 text-xs text-slate-500 font-mono pt-1">
            <span>Max 50MB</span>
            <span>•</span>
            <span>PDF, PNG, JPG, TIFF</span>
            <span>•</span>
            <span>Auto PII Redaction</span>
          </div>
        </div>
      </div>

      {/* Preset Documents Quick Bar */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-teal-400" />
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Or Test with Sample Document Presets
            </h4>
          </div>
          <span className="text-[11px] text-slate-500">1-click instant evaluation</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {presets.map((preset) => {
            const Icon = preset.icon;
            return (
              <button
                key={preset.id}
                onClick={() => handlePresetClick(preset.id)}
                disabled={isProcessing}
                className="p-3.5 rounded-xl bg-slate-900/60 hover:bg-slate-850 border border-slate-800 hover:border-teal-500/40 text-left transition-all duration-200 group flex flex-col justify-between"
              >
                <div className="flex items-start justify-between w-full mb-2">
                  <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400 group-hover:bg-teal-500/20 transition-colors">
                    <Icon className="w-4 h-4" />
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-teal-400 group-hover:translate-x-0.5 transition-all" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-slate-200 group-hover:text-white">
                    {preset.label}
                  </div>
                  <div className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">
                    {preset.desc}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
