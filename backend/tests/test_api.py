import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_benchmark_endpoint():
    response = client.post("/api/benchmark/run")
    assert response.status_code == 200
    data = response.json()
    assert "pytorch_metrics" in data
    assert "tfidf_metrics" in data
    assert data["total_samples"] > 0

def test_pii_redact_endpoint():
    response = client.post("/api/pii/redact", json={"text": "Contact me at user@domain.com or call 555-123-4567"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["entities_found"]) > 0

def test_preset_process_endpoint():
    response = client.post("/api/documents/process-preset/INVOICE")
    assert response.status_code == 200
    data = response.json()
    assert data["classification"]["final_class"] == "INVOICE"
    assert "extracted_fields" in data
