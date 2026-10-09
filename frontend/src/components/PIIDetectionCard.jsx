import React, { useState } from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  Lock, 
  EyeOff, 
  Sparkles, 
  FileCheck, 
  Key, 
  CreditCard,
  Mail,
  Phone,
  User,
  Copy,
  Check
} from 'lucide-react';
import { apiService } from '../services/api';

export default function PIIDetectionCard() {
  const [inputText, setInputText] = useState(
    "Employee Jonathan Vance (SSN: 987-65-4321, Aadhaar: 5489 2314 9081) has submitted his PAN: ABCDE1234F. " +
    "Contact him via email jonathan.vance@company.com or phone +1-415-555-8821. " +
    "Payment processed on Visa card 4532-8891-0021-4242."
  );
  const [redactedResult, setRedactedResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [copied, setCopied] = useState(false);

  const supportedEntities = [
    { name: 'SSN (Social Security)', icon: Lock, example: '987-65-4321', risk: 'HIGH' },
    { name: 'Aadhaar UID', icon: User, example: '5489 2314 9081', risk: 'HIGH' },
    { name: 'PAN Card Number', icon: Key, example: 'ABCDE1234F', risk: 'HIGH' },
    { name: 'Credit / Debit Cards', icon: CreditCard, example: '4532-8891-0021-4242', risk: 'HIGH' },
    { name: 'Email Addresses', icon: Mail, example: 'john.doe@domain.com', risk: 'MEDIUM' },
    { name: 'Phone Numbers', icon: Phone, example: '+1-555-019-2834', risk: 'MEDIUM' },
  ];

  const handleRunRedaction = async () => {
    try {
      setIsProcessing(true);
      const res = await apiService.redactText(inputText);
      setRedactedResult(res);
    } catch (err) {
      console.error('Redaction error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const copySanitized = () => {
    if (redactedResult?.sanitized_text) {
      navigator.clipboard.writeText(redactedResult.sanitized_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">
              PII Detection & Visual Masking Engine
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Automated entity detection and masking for GDPR, HIPAA, and DPDP regulatory compliance.
          </p>
        </div>
      </div>

      {/* Supported PII Types Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {supportedEntities.map((ent, idx) => {
          const Icon = ent.icon;
          return (
            <div key={idx} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <div className="p-1.5 rounded-lg bg-teal-500/10 text-teal-400">
                  <Icon className="w-4 h-4" />
                </div>
                <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded ${
                  ent.risk === 'HIGH' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'
                }`}>
                  {ent.risk}
                </span>
              </div>
              <div>
                <div className="text-xs font-semibold text-slate-200">{ent.name}</div>
                <div className="text-[10px] text-slate-500 font-mono mt-0.5">{ent.example}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Interactive PII Sandbox */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-teal-400" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wide">
              Live PII Sanitization Sandbox
            </h3>
          </div>
          <button
            onClick={handleRunRedaction}
            disabled={isProcessing}
            className="px-4 py-1.5 rounded-lg bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs shadow-md shadow-teal-500/20 disabled:opacity-50 cursor-pointer"
          >
            {isProcessing ? 'Analyzing...' : 'Scan & Redact PII'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Input Text Box */}
          <div className="space-y-2">
            <label className="block text-xs font-semibold text-slate-400">
              Input Raw Document Text
            </label>
            <textarea
              rows={6}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-teal-500"
            />
          </div>

          {/* Sanitized Text Box */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="block text-xs font-semibold text-slate-400">
                Masked & Sanitized Output
              </label>
              {redactedResult && (
                <button
                  onClick={copySanitized}
                  className="text-[11px] text-teal-400 hover:text-teal-300 flex items-center space-x-1"
                >
                  {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              )}
            </div>
            <div className="w-full bg-slate-950/80 border border-teal-500/30 rounded-xl p-3 text-xs text-teal-300 font-mono min-h-[135px] whitespace-pre-wrap">
              {redactedResult ? redactedResult.sanitized_text : 'Click "Scan & Redact PII" to view masked output...'}
            </div>
          </div>
        </div>

        {/* Detected Entities List */}
        {redactedResult && (
          <div className="pt-3 border-t border-slate-800 space-y-3">
            <div className="text-xs font-semibold text-slate-300">
              Flagged Entities ({redactedResult.entities_found.length} Matches Found):
            </div>
            <div className="flex flex-wrap gap-2">
              {redactedResult.entities_found.map((ent, i) => (
                <div
                  key={i}
                  className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 flex items-center space-x-2 text-xs"
                >
                  <span className="font-bold text-amber-400">{ent.entity_type}</span>
                  <span className="text-slate-500 font-mono line-through">{ent.raw_value}</span>
                  <span className="text-teal-300 font-mono font-medium">→ {ent.masked_value}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
