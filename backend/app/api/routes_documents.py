import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings, UPLOADS_DIR, PROCESSED_DIR, SAMPLES_DIR
from app.database import get_db
from app.models.db_models import DocumentRecord
from app.models.schemas import DocumentResponse, DocumentClassificationResult, ExtractedField, PIIEntity, BoundingBox
from app.services.ocr_service import ocr_service
from app.services.classifier import classifier_service
from app.services.extractor import extractor_service
from app.services.pii_detector import pii_detector_service
from app.services.review_queue import review_queue_service
from app.services.sample_docs_generator import generate_all_sample_presets, generate_sample_document_image

router = APIRouter(prefix="/documents", tags=["Documents"])

def _build_doc_response(doc: DocumentRecord) -> DocumentResponse:
    classification = None
    if doc.pytorch_predicted_class or doc.tfidf_predicted_class:
        classification = DocumentClassificationResult(
            pytorch_class=doc.pytorch_predicted_class or "UNKNOWN",
            pytorch_confidence=doc.pytorch_confidence or 0.0,
            tfidf_class=doc.tfidf_predicted_class or "UNKNOWN",
            tfidf_confidence=doc.tfidf_confidence or 0.0,
            final_class=doc.final_document_class or "UNKNOWN"
        )
    
    extracted_fields = None
    if doc.extracted_fields:
        extracted_fields = {
            k: ExtractedField(
                value=v.get("value", "") if isinstance(v, dict) else v,
                confidence=v.get("confidence", 1.0) if isinstance(v, dict) else 1.0,
                source=v.get("source", "transformer_ner") if isinstance(v, dict) else "transformer_ner"
            )
            for k, v in doc.extracted_fields.items()
        }

    pii_entities = None
    if doc.pii_entities_detected:
        pii_entities = [PIIEntity(**e) for e in doc.pii_entities_detected]

    word_boxes = None
    if doc.ocr_word_boxes:
        word_boxes = [BoundingBox(**b) for b in doc.ocr_word_boxes]

    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size_bytes=doc.file_size_bytes,
        created_at=doc.created_at,
        status=doc.status,
        classification=classification,
        ocr_raw_text=doc.ocr_raw_text,
        ocr_word_boxes=word_boxes,
        extracted_fields=extracted_fields,
        pii_entities=pii_entities,
        has_sensitive_pii=doc.has_sensitive_pii,
        redacted_image_url=f"/api/documents/{doc.id}/redacted-image" if doc.redacted_image_path else None,
        document_image_url=f"/api/documents/{doc.id}/image",
        review_notes=doc.review_notes,
        reviewed_at=doc.reviewed_at,
        reviewed_by=doc.reviewed_by,
        corrected_fields=doc.corrected_fields
    )

def _process_file_pipeline(file_path: Path, filename: str, db: Session) -> DocumentRecord:
    doc_id = str(uuid.uuid4())
    file_ext = file_path.suffix.lower()
    file_size = file_path.stat().st_size

    # 1. OCR & Spatial Layout Extraction
    ocr_res = ocr_service.extract_text_and_boxes(str(file_path))
    
    # Save preview image if generated
    preview_img_path = PROCESSED_DIR / f"{doc_id}_preview.png"
    ocr_res.preview_image.save(preview_img_path, "PNG")

    # 2. Document Classification (PyTorch vs TF-IDF Baseline)
    clf_res = classifier_service.classify_document(ocr_res.raw_text)

    # 3. Key Field Information Extraction
    extracted = extractor_service.extract_fields(
        doc_class=clf_res["final_class"],
        text=ocr_res.raw_text,
        word_boxes=ocr_res.word_boxes
    )

    # 4. PII Detection & Visual Redaction
    pii_entities, sanitized_text = pii_detector_service.detect_pii(ocr_res.raw_text)
    has_pii = len(pii_entities) > 0
    
    redacted_img_path = PROCESSED_DIR / f"{doc_id}_redacted.png"
    if has_pii:
        pii_detector_service.create_redacted_image(
            image_path=str(preview_img_path),
            output_path=str(redacted_img_path),
            word_boxes=ocr_res.word_boxes,
            pii_entities=pii_entities
        )
        saved_redacted_path = str(redacted_img_path)
    else:
        saved_redacted_path = None

    # 5. Human-in-the-Loop Triage Decision
    triage_status = review_queue_service.evaluate_triage_status(
        classification_confidence=clf_res["final_confidence"],
        extracted_fields=extracted,
        has_sensitive_pii=has_pii
    )

    # Convert PII entities to json serializable dict
    pii_entities_json = [e.model_dump() for e in pii_entities]

    # 6. Persist to DB
    doc_record = DocumentRecord(
        id=doc_id,
        filename=filename,
        file_path=str(preview_img_path),
        file_type=file_ext,
        file_size_bytes=file_size,
        status=triage_status,
        pytorch_predicted_class=clf_res["pytorch_class"],
        pytorch_confidence=clf_res["pytorch_confidence"],
        tfidf_predicted_class=clf_res["tfidf_class"],
        tfidf_confidence=clf_res["tfidf_confidence"],
        final_document_class=clf_res["final_class"],
        ocr_raw_text=ocr_res.raw_text,
        ocr_word_boxes=ocr_res.word_boxes,
        extracted_fields=extracted,
        pii_entities_detected=pii_entities_json,
        has_sensitive_pii=has_pii,
        redacted_image_path=saved_redacted_path
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)
    return doc_record

@router.post("/process", response_model=DocumentResponse)
async def process_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a scanned document (PDF, PNG, JPG, TIFF) to run the full Document Intelligence pipeline."""
    temp_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_path = UPLOADS_DIR / temp_filename
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        doc_record = _process_file_pipeline(temp_path, file.filename, db)
        return _build_doc_response(doc_record)
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass

@router.post("/process-preset/{preset_name}", response_model=DocumentResponse)
def process_preset(
    preset_name: str,
    db: Session = Depends(get_db)
):
    """Processes a pre-built sample document (INVOICE, RECEIPT, EMPLOYMENT_CONTRACT, IDENTITY_DOCUMENT)."""
    preset_upper = preset_name.upper()
    fname = f"sample_{preset_name.lower()}.png"
    sample_file = SAMPLES_DIR / fname
    
    if not sample_file.exists():
        sample_file = generate_sample_document_image(preset_upper, fname)

    doc_record = _process_file_pipeline(sample_file, fname, db)
    return _build_doc_response(doc_record)

@router.get("", response_model=List[DocumentResponse])
def list_documents(
    status: Optional[str] = Query(None, description="Filter by status: PENDING, PROCESSED, NEEDS_REVIEW, APPROVED, REJECTED"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List all processed documents with filtering and pagination."""
    query = db.query(DocumentRecord)
    if status and status.upper() != "ALL":
        query = query.filter(DocumentRecord.status == status.upper())
    docs = query.order_by(DocumentRecord.created_at.desc()).offset(offset).limit(limit).all()
    return [_build_doc_response(d) for d in docs]

@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    """Retrieve details, extracted fields, bounding boxes, and classification for a single document."""
    doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _build_doc_response(doc)

@router.get("/{doc_id}/image")
def get_document_image(doc_id: str, db: Session = Depends(get_db)):
    """Get the rendered image preview for a document."""
    doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not doc or not Path(doc.file_path).exists():
        raise HTTPException(status_code=404, detail="Document image not found")
    return FileResponse(doc.file_path, media_type="image/png")

@router.get("/{doc_id}/redacted-image")
def get_redacted_image(doc_id: str, db: Session = Depends(get_db)):
    """Get the visually redacted image for a document."""
    doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
    if not doc or not doc.redacted_image_path or not Path(doc.redacted_image_path).exists():
        # If no redacted image, return standard preview image
        if doc and Path(doc.file_path).exists():
            return FileResponse(doc.file_path, media_type="image/png")
        raise HTTPException(status_code=404, detail="Redacted image not found")
    return FileResponse(doc.redacted_image_path, media_type="image/png")

@router.post("/seed-samples")
def seed_sample_documents(db: Session = Depends(get_db)):
    """Generates all preset documents and seeds them into the database."""
    created_presets = generate_all_sample_presets()
    processed_ids = []
    
    # Check if we already have records
    count = db.query(DocumentRecord).count()
    if count == 0:
        for p in created_presets:
            doc = _process_file_pipeline(p, p.name, db)
            processed_ids.append(doc.id)
    return {"message": "Sample documents seeded", "count": len(processed_ids), "ids": processed_ids}
