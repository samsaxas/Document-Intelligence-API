from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.config import settings
from app.models.db_models import DocumentRecord
from app.models.schemas import ReviewSubmission

class ReviewQueueService:
    def evaluate_triage_status(
        self,
        classification_confidence: float,
        extracted_fields: Dict[str, Dict[str, Any]],
        has_sensitive_pii: bool
    ) -> str:
        """
        Determines if document should be automatically approved or routed to
        Human-in-the-Loop (HITL) Manual Review queue.
        """
        # 1. Classification confidence check
        if classification_confidence < settings.CLASSIFICATION_CONFIDENCE_THRESHOLD:
            return "NEEDS_REVIEW"

        # 2. Key fields confidence check
        for field_name, field_info in extracted_fields.items():
            if field_info.get("confidence", 1.0) < settings.EXTRACTION_CONFIDENCE_THRESHOLD:
                return "NEEDS_REVIEW"

        # 3. High-risk unredacted PII check
        if has_sensitive_pii:
            return "NEEDS_REVIEW"

        return "PROCESSED"

    def get_review_items(
        self,
        db: Session,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[DocumentRecord]:
        """Fetch documents from the review queue with optional status filtering."""
        query = db.query(DocumentRecord)
        if status and status.upper() != "ALL":
            query = query.filter(DocumentRecord.status == status.upper())
        return query.order_by(DocumentRecord.created_at.desc()).offset(offset).limit(limit).all()

    def process_review_decision(
        self,
        doc_id: str,
        submission: ReviewSubmission,
        db: Session
    ) -> Optional[DocumentRecord]:
        """Applies reviewer corrections, updates status to APPROVED/REJECTED, and records audit trail."""
        doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
        if not doc:
            return None

        doc.status = submission.status.upper()
        doc.reviewed_at = datetime.utcnow()
        doc.reviewed_by = submission.reviewer_name
        doc.review_notes = submission.reviewer_notes

        if submission.final_document_class:
            doc.final_document_class = submission.final_document_class

        if submission.corrected_fields:
            doc.corrected_fields = submission.corrected_fields
            # Also merge into extracted_fields with 'manual_edit' source
            current_fields = doc.extracted_fields or {}
            for k, v in submission.corrected_fields.items():
                current_fields[k] = {
                    "value": v,
                    "confidence": 1.0,
                    "source": "manual_edit"
                }
            doc.extracted_fields = current_fields

        db.commit()
        db.refresh(doc)
        return doc

review_queue_service = ReviewQueueService()
