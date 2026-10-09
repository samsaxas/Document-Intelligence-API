import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DocumentUpload from './components/DocumentUpload';
import DocumentViewer from './components/DocumentViewer';
import ExtractionResults from './components/ExtractionResults';
import ModelComparison from './components/ModelComparison';
import ReviewQueue from './components/ReviewQueue';
import PIIDetectionCard from './components/PIIDetectionCard';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import { apiService } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('process');
  const [currentDocument, setCurrentDocument] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [stats, setStats] = useState(null);
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    fetchStats();
    seedAndLoadFirstDoc();
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const data = await apiService.getStats();
      setStats(data);
      setIsOnline(true);
    } catch (err) {
      console.warn('Backend connection note:', err);
      setIsOnline(false);
    }
  };

  const seedAndLoadFirstDoc = async () => {
    try {
      await apiService.seedSamples();
      const docs = await apiService.listDocuments('ALL', 1);
      if (docs && docs.length > 0) {
        setCurrentDocument(docs[0]);
      }
      fetchStats();
    } catch (err) {
      console.warn('Initial seed note:', err);
    }
  };

  const handleDocumentProcessed = (doc) => {
    setCurrentDocument(doc);
    fetchStats();
  };

  const handleFieldUpdated = (key, val) => {
    if (!currentDocument) return;
    const updatedFields = { ...currentDocument.extracted_fields };
    if (updatedFields[key]) {
      updatedFields[key] = {
        ...updatedFields[key],
        value: val,
        source: 'manual_edit',
        confidence: 1.0
      };
    }
    setCurrentDocument({
      ...currentDocument,
      extracted_fields: updatedFields
    });
  };

  const handleInspectDocument = (doc) => {
    setCurrentDocument(doc);
    setActiveTab('process');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-teal-500 selection:text-slate-950">
      {/* Navigation Bar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        stats={stats}
        isOnline={isOnline}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'process' && (
          <div className="space-y-6">
            {/* Document Upload Area */}
            <DocumentUpload
              onDocumentProcessed={handleDocumentProcessed}
              isProcessing={isProcessing}
              setIsProcessing={setIsProcessing}
            />

            {/* Split Screen Workbench */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Left Column: Interactive Document Canvas */}
              <div className="lg:col-span-7 h-[700px]">
                <DocumentViewer document={currentDocument} />
              </div>

              {/* Right Column: Key Field Extraction & Classification */}
              <div className="lg:col-span-5 space-y-6 max-h-[700px] overflow-y-auto pr-1">
                {currentDocument ? (
                  <ExtractionResults
                    document={currentDocument}
                    onFieldUpdated={handleFieldUpdated}
                  />
                ) : (
                  <div className="p-8 rounded-2xl glass-panel text-center text-slate-500">
                    <p>Document metadata and extracted fields will populate here once a document is processed.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'review' && (
          <ReviewQueue
            onReviewActionCompleted={fetchStats}
          />
        )}

        {activeTab === 'benchmark' && (
          <ModelComparison />
        )}

        {activeTab === 'pii' && (
          <PIIDetectionCard />
        )}

        {activeTab === 'analytics' && (
          <AnalyticsDashboard
            stats={stats}
            onSelectDocument={handleInspectDocument}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 text-center text-xs text-slate-500">
        <p>Enterprise Document Intelligence API & Platform • Built with PyTorch, Transformers, FastAPI, Docker & AWS</p>
      </footer>
    </div>
  );
}
