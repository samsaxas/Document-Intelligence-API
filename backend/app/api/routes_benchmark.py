from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import BenchmarkRecord
from app.models.schemas import BenchmarkComparisonResponse
from app.services.benchmark_service import benchmark_service

router = APIRouter(prefix="/benchmark", tags=["Model Benchmark"])

@router.post("/run", response_model=BenchmarkComparisonResponse)
def run_model_benchmark(db: Session = Depends(get_db)):
    """
    Executes real-time benchmarking comparing the PyTorch Deep Neural Network
    against the TF-IDF Baseline across accuracy, macro F1, per-class metrics,
    and inference latency.
    """
    return benchmark_service.run_benchmark(db=db)

@router.get("/history")
def get_benchmark_history(db: Session = Depends(get_db)):
    """Retrieves previous benchmark execution runs and performance progression."""
    records = db.query(BenchmarkRecord).order_by(BenchmarkRecord.timestamp.desc()).limit(10).all()
    return [
        {
            "id": r.id,
            "timestamp": r.timestamp,
            "total_samples": r.total_samples,
            "pytorch": {
                "accuracy": r.pytorch_accuracy,
                "macro_f1": r.pytorch_macro_f1,
                "latency_ms": r.pytorch_avg_latency_ms
            },
            "tfidf": {
                "accuracy": r.tfidf_accuracy,
                "macro_f1": r.tfidf_macro_f1,
                "latency_ms": r.tfidf_avg_latency_ms
            }
        }
        for r in records
    ]
