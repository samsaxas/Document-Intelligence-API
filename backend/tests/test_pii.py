import pytest
from app.services.pii_detector import pii_detector_service

def test_pii_detection():
    sample_text = "Employee SSN: 987-65-4321, Aadhaar: 5489 2314 9081, Email: test@example.com, PAN: ABCDE1234F"
    entities, sanitized = pii_detector_service.detect_pii(sample_text)
    
    types = [e.entity_type for e in entities]
    assert "SSN" in types
    assert "AADHAAR" in types
    assert "EMAIL" in types
    assert "PAN" in types
    
    # Verify sanitized text does not leak raw SSN
    assert "987-65-4321" not in sanitized
    assert "***-**-4321" in sanitized
