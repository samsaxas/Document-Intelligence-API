from fastapi import APIRouter
from app.models.schemas import PIIRedactRequest, PIIRedactResponse
from app.services.pii_detector import pii_detector_service

router = APIRouter(prefix="/pii", tags=["PII Detection & Redaction"])

@router.post("/redact", response_model=PIIRedactResponse)
def redact_text_pii(payload: PIIRedactRequest):
    """
    Scans arbitrary text for sensitive identifiers (SSN, Aadhaar, PAN, Cards, Emails, Phone numbers)
    and returns detected entities with sanitized text.
    """
    entities, sanitized_text = pii_detector_service.detect_pii(payload.text)
    return PIIRedactResponse(
        original_text=payload.text,
        sanitized_text=sanitized_text,
        entities_found=entities
    )
