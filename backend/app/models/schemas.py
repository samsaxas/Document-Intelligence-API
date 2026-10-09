from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict

class BoundingBox(BaseModel):
    text: str
    bbox: list[float]  # [ymin, xmin, ymax, xmax] normalized 0-1000 or pixels
    confidence: float

class ExtractedField(BaseModel):
    value: Any
    confidence: float
    source: str = "transformer_ner"  # transformer_ner / rule_extractor / manual_edit

class PIIEntity(BaseModel):
    entity_type: str  # SSN, AADHAAR, PAN, CREDIT_CARD, EMAIL, PHONE, SECRET_KEY, PASSPORT
    raw_value: str
    masked_value: str
    start: int
    end: int
    severity: str = "HIGH"  # HIGH / MEDIUM / LOW

class DocumentClassificationResult(BaseModel):
    pytorch_class: str
    pytorch_confidence: float
    tfidf_class: str
    tfidf_confidence: float
    final_class: str

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    file_type: str
    file_size_bytes: int
    created_at: datetime
    status: str
    classification: Optional[DocumentClassificationResult] = None
    ocr_raw_text: Optional[str] = None
    ocr_word_boxes: Optional[list[BoundingBox]] = None
    extracted_fields: Optional[dict[str, ExtractedField]] = None
    pii_entities: Optional[list[PIIEntity]] = None
    has_sensitive_pii: bool = False
    redacted_image_url: Optional[str] = None
    document_image_url: Optional[str] = None
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    corrected_fields: Optional[dict[str, Any]] = None

class ReviewSubmission(BaseModel):
    status: str = Field(..., description="APPROVED, REJECTED, or NEEDS_REVIEW")
    corrected_fields: Optional[dict[str, Any]] = None
    final_document_class: Optional[str] = None
    reviewer_notes: Optional[str] = None
    reviewer_name: str = "compliance_agent"

class BenchmarkMetrics(BaseModel):
    model_name: str
    accuracy: float
    macro_f1: float
    avg_latency_ms: float
    precision_macro: float
    recall_macro: float
    per_class_f1: dict[str, float]

class BenchmarkComparisonResponse(BaseModel):
    total_samples: int
    pytorch_metrics: BenchmarkMetrics
    tfidf_metrics: BenchmarkMetrics
    confusion_matrices: dict[str, list[list[int]]]
    classes: list[str]

class PIIRedactRequest(BaseModel):
    text: str
    mask_char: str = "*"
    entity_types_to_mask: Optional[list[str]] = None

class PIIRedactResponse(BaseModel):
    original_text: str
    sanitized_text: str
    entities_found: list[PIIEntity]
