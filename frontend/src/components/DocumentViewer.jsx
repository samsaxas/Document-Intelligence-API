import React, { useState } from 'react';
import { 
  Eye, 
  EyeOff, 
  Scan, 
  Maximize2, 
  ShieldCheck, 
  ShieldAlert,
  Info,
  ZoomIn,
  ZoomOut
} from 'lucide-react';

export default function DocumentViewer({ document }) {
  const [showBoxes, setShowBoxes] = useState(true);
  const [showRedacted, setShowRedacted] = useState(false);
  const [hoveredBox, setHoveredBox] = useState(null);
  const [zoomLevel, setZoomLevel] = useState(1);

  if (!document) {
    return (
      <div className="h-full min-h-[500px] flex flex-col items-center justify-center p-8 rounded-2xl glass-panel text-center">
        <div className="w-16 h-16 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center mb-4">
          <Scan className="w-8 h-8 text-slate-600" />
        </div>
        <h3 className="text-base font-semibold text-slate-300">No Document Selected</h3>
        <p className="text-xs text-slate-500 max-w-sm mt-1">
          Upload a document or choose a sample preset to view high-resolution OCR bounding boxes and PII redactions.
        </p>
      </div>
    );
  }

  const imageUrl = showRedacted && document.redacted_image_url
    ? document.redacted_image_url
    : document.document_image_url;

  return (
    <div className="flex flex-col h-full rounded-2xl glass-panel overflow-hidden border border-slate-800">
      {/* Viewer Header Toolbar */}
      <div className="p-4 border-b border-slate-800 bg-slate-950/60 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <span className="text-sm font-semibold text-white truncate max-w-[220px]">
            {document.filename}
          </span>
          <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full uppercase tracking-wider ${
            document.status === 'PROCESSED'
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
              : document.status === 'NEEDS_REVIEW'
              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              : 'bg-teal-500/10 text-teal-400 border border-teal-500/20'
          }`}>
            {document.status}
          </span>
        </div>

        {/* View Controls */}
        <div className="flex items-center space-x-2">
          {/* Toggle OCR Bounding Boxes */}
          <button
            onClick={() => setShowBoxes(!showBoxes)}
            className={`px-2.5 py-1.5 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition-all ${
              showBoxes
                ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <Scan className="w-3.5 h-3.5" />
            <span>OCR Boxes</span>
          </button>

          {/* Toggle PII Redaction View */}
          {document.has_sensitive_pii && (
            <button
              onClick={() => setShowRedacted(!showRedacted)}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition-all ${
                showRedacted
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                  : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {showRedacted ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
              <span>{showRedacted ? 'Redacted View' : 'Original View'}</span>
            </button>
          )}

          {/* Zoom Controls */}
          <div className="flex items-center bg-slate-900 rounded-lg border border-slate-800 p-0.5">
            <button
              onClick={() => setZoomLevel(Math.max(0.7, zoomLevel - 0.15))}
              className="p-1 hover:text-white text-slate-400"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-[10px] font-mono px-1.5 text-slate-400">
              {Math.round(zoomLevel * 100)}%
            </span>
            <button
              onClick={() => setZoomLevel(Math.min(1.8, zoomLevel + 0.15))}
              className="p-1 hover:text-white text-slate-400"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Canvas Viewport */}
      <div className="relative flex-1 p-4 bg-slate-950/40 overflow-auto flex items-center justify-center min-h-[500px]">
        <div 
          className="relative inline-block rounded-lg shadow-2xl overflow-hidden border border-slate-800 transition-transform duration-200"
          style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'top center' }}
        >
          <img
            src={imageUrl}
            alt="Scanned Document"
            className="max-w-full h-auto object-contain block select-none"
            style={{ maxHeight: '720px' }}
          />

          {/* Bounding Box Overlays */}
          {showBoxes && !showRedacted && document.ocr_word_boxes?.map((box, idx) => {
            const [ymin, xmin, ymax, xmax] = box.bbox; // 0-1000 normalized
            const top = `${ymin / 10}%`;
            const left = `${xmin / 10}%`;
            const height = `${(ymax - ymin) / 10}%`;
            const width = `${(xmax - xmin) / 10}%`;

            return (
              <div
                key={idx}
                onMouseEnter={() => setHoveredBox(box)}
                onMouseLeave={() => setHoveredBox(null)}
                style={{ top, left, height, width }}
                className="absolute border border-teal-400/40 hover:border-teal-300 hover:bg-teal-400/20 cursor-crosshair transition-colors duration-150 group"
              />
            );
          })}
        </div>

        {/* Hover Tooltip for Word Box */}
        {hoveredBox && (
          <div className="absolute bottom-6 left-6 z-20 px-3 py-2 rounded-lg bg-slate-900/95 border border-teal-500/40 text-xs shadow-xl backdrop-blur-md flex items-center space-x-3">
            <span className="font-semibold text-white">OCR Token:</span>
            <span className="font-mono text-teal-300 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800">
              "{hoveredBox.text}"
            </span>
            <span className="text-slate-400">
              Conf: <span className="text-emerald-400 font-mono font-medium">{(hoveredBox.confidence * 100).toFixed(1)}%</span>
            </span>
          </div>
        )}
      </div>

      {/* Footer Info Banner */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center space-x-4 font-mono text-[11px]">
          <span>Size: {(document.file_size_bytes / 1024).toFixed(1)} KB</span>
          <span>•</span>
          <span>OCR Words: {document.ocr_word_boxes?.length || 0}</span>
          <span>•</span>
          <span>Class: {document.classification?.final_class || 'N/A'}</span>
        </div>
        {document.has_sensitive_pii && (
          <div className="flex items-center space-x-1.5 text-amber-400 font-medium">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>PII Detected ({document.pii_entities?.length || 0} entities)</span>
          </div>
        )}
      </div>
    </div>
  );
}
