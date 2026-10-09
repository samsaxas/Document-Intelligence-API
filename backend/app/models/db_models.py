from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class DocumentRecord(Base):
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(32), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Processing state: 'PENDING', 'PROCESSED', 'NEEDS_REVIEW', 'APPROVED', 'REJECTED'
    status = Column(String(32), default="PENDING", index=True)
    
    # Classification results
    pytorch_predicted_class = Column(String(64), nullable=True)
    pytorch_confidence = Column(Float, nullable=True)
    tfidf_predicted_class = Column(String(64), nullable=True)
    tfidf_confidence = Column(Float, nullable=True)
    final_document_class = Column(String(64), nullable=True)
    
    # OCR and Extraction Output
    ocr_raw_text = Column(Text, nullable=True)
    ocr_word_boxes = Column(JSON, nullable=True)  # List of {text, bbox: [ymin, xmin, ymax, xmax], conf}
    extracted_fields = Column(JSON, nullable=True) # Dict of {field_name: {value, confidence, source}}
    
    # PII Flags and Redaction info
    pii_entities_detected = Column(JSON, nullable=True) # List of {type, raw_value, masked_value, span}
    has_sensitive_pii = Column(Boolean, default=False)
    redacted_image_path = Column(String(512), nullable=True)
    
    # Review details
    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String(64), nullable=True)
    corrected_fields = Column(JSON, nullable=True)

class BenchmarkRecord(Base):
    __tablename__ = "benchmark_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_samples = Column(Integer, nullable=False)
    
    # PyTorch Model Metrics
    pytorch_accuracy = Column(Float, nullable=False)
    pytorch_macro_f1 = Column(Float, nullable=False)
    pytorch_avg_latency_ms = Column(Float, nullable=False)
    
    # TF-IDF Baseline Metrics
    tfidf_accuracy = Column(Float, nullable=False)
    tfidf_macro_f1 = Column(Float, nullable=False)
    tfidf_avg_latency_ms = Column(Float, nullable=False)
    
    # Detailed classification report and confusion matrix
    confusion_matrices = Column(JSON, nullable=True)
    per_class_metrics = Column(JSON, nullable=True)
