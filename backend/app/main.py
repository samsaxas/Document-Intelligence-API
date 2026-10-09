import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, get_db
from app.models.db_models import DocumentRecord, BenchmarkRecord
from app.api.routes_documents import router as documents_router
from app.api.routes_review import router as review_router
from app.api.routes_benchmark import router as benchmark_router
from app.api.routes_pii import router as pii_router
from app.services.sample_docs_generator import generate_all_sample_presets

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables
    Base.metadata.create_all(bind=engine)
    # Generate presets on startup
    try:
        generate_all_sample_presets()
    except Exception as e:
        print(f"Preset generation note: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Document Intelligence API with PyTorch, Transformers, OCR, PII Masking, and HITL Review Queue.",
    lifespan=lifespan
)

# Enable CORS for modern web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(review_router, prefix=settings.API_V1_STR)
app.include_router(benchmark_router, prefix=settings.API_V1_STR)
app.include_router(pii_router, prefix=settings.API_V1_STR)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "supported_classes": settings.DOCUMENT_CLASSES
    }

@app.get("/api/stats")
def get_pipeline_statistics(db: Session = Depends(get_db)):
    """Summary statistics of processed documents, review queues, and model metrics."""
    total_docs = db.query(DocumentRecord).count()
    processed_count = db.query(DocumentRecord).filter(DocumentRecord.status == "PROCESSED").count()
    needs_review_count = db.query(DocumentRecord).filter(DocumentRecord.status == "NEEDS_REVIEW").count()
    approved_count = db.query(DocumentRecord).filter(DocumentRecord.status == "APPROVED").count()
    rejected_count = db.query(DocumentRecord).filter(DocumentRecord.status == "REJECTED").count()
    pii_flagged_count = db.query(DocumentRecord).filter(DocumentRecord.has_sensitive_pii == True).count()
    
    return {
        "total_documents": total_docs,
        "processed": processed_count,
        "needs_review": needs_review_count,
        "approved": approved_count,
        "rejected": rejected_count,
        "pii_flagged": pii_flagged_count,
        "automation_rate_pct": round(((processed_count + approved_count) / max(total_docs, 1)) * 100, 1)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
