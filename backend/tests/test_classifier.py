import pytest
from app.services.classifier import classifier_service

def test_classifier_initialization():
    assert classifier_service.is_trained == True
    assert classifier_service.tfidf_classifier is not None

def test_tfidf_classification():
    text = "TAX INVOICE INV-2024-001 Acme Corp Total Due $500.00 Billed to Client"
    pred_class, conf, probs = classifier_service.classify_tfidf(text)
    assert pred_class == "INVOICE"
    assert conf > 0.3
    assert "INVOICE" in probs

def test_pytorch_classification():
    text = "STARBUCKS COFFEE Receipt 1x Latte $5.50 Subtotal $9.25 Total $10.05 Paid by Visa"
    pred_class, conf, probs = classifier_service.classify_pytorch(text)
    assert pred_class == "RECEIPT"
    assert conf > 0.3

def test_document_classification_pipeline():
    text = "EMPLOYMENT AGREEMENT between NovaTech and Employee Base Salary $150,000 Start Date Nov 1"
    res = classifier_service.classify_document(text)
    assert res["final_class"] == "EMPLOYMENT_CONTRACT"
    assert "pytorch_class" in res
    assert "tfidf_class" in res
    assert "agreement" in res
