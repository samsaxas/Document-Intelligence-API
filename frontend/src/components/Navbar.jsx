import React from 'react';
import { 
  FileText, 
  CheckCircle2, 
  BarChart3, 
  ShieldAlert, 
  Activity, 
  Cpu,
  Layers
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, stats, isOnline }) {
  const navItems = [
    { id: 'process', label: 'Document Studio', icon: FileText },
    { id: 'review', label: 'HITL Review Queue', icon: CheckCircle2, badge: stats?.needs_review },
    { id: 'benchmark', label: 'Model Benchmark (PyTorch vs TF-IDF)', icon: BarChart3 },
    { id: 'pii', label: 'PII & Redaction Hub', icon: ShieldAlert, badge: stats?.pii_flagged },
    { id: 'analytics', label: 'Pipeline Analytics', icon: Activity },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800 bg-slate-950/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-teal-500/20">
              <Layers className="w-6 h-6 text-slate-950" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-teal-400 bg-clip-text text-transparent">
                  DocuIntel AI
                </span>
                <span className="px-2 py-0.5 text-[10px] font-semibold bg-teal-500/10 text-teal-400 border border-teal-500/20 rounded-full">
                  v1.0.0
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                PyTorch • Transformers • Multi-Backend OCR • HITL
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex space-x-1 lg:space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs md:text-sm font-medium transition-all duration-200 relative ${
                    isActive
                      ? 'bg-teal-500/15 text-teal-300 border border-teal-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-teal-400' : 'text-slate-500'}`} />
                  <span className="hidden md:inline">{item.label}</span>
                  {item.badge > 0 && (
                    <span className="px-1.5 py-0.2 text-[10px] font-bold rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Live Status Indicator */}
          <div className="flex items-center space-x-3">
            <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800">
              <Cpu className="w-4 h-4 text-teal-400" />
              <div className="text-xs">
                <span className="text-slate-400">FastAPI & PyTorch: </span>
                <span className="text-emerald-400 font-medium">Ready</span>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <span className={`w-2.5 h-2.5 rounded-full ${isOnline ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]' : 'bg-rose-500'}`} />
              <span className="text-xs text-slate-400 hidden sm:inline">
                {isOnline ? 'Connected' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
