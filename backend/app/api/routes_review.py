from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import DocumentResponse, ReviewSubmission
from app.services.review_queue import review_queue_service
from app.api.routes_documents import _build_doc_response

router = APIRouter(prefix="/review-queue", tags=["Manual Review Queue"])

@router.get("", response_model=List[DocumentResponse])
def get_review_queue(
    status: Optional[str] = Query("NEEDS_REVIEW", description="Filter: NEEDS_REVIEW, APPROVED, REJECTED, ALL"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Retrieve documents requiring Human-in-the-Loop manual verification and correction."""
    docs = review_queue_service.get_review_items(db, status=status, limit=limit, offset=offset)
    return [_build_doc_response(d) for d in docs]

@router.post("/{doc_id}/submit", response_model=DocumentResponse)
def submit_review_decision(
    doc_id: str,
    submission: ReviewSubmission,
    db: Session = Depends(get_db)
):
    """
    Submit a reviewer's decision (Approve / Reject) with field corrections,
    overridden document class, and auditor notes.
    """
    updated_doc = review_queue_service.process_review_decision(doc_id, submission, db)
    if not updated_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _build_doc_response(updated_doc)
