import pytest
from PIL import Image
from app.services.ocr_service import ocr_service
from app.services.sample_docs_generator import generate_sample_document_image

def test_image_preprocessing():
    img = Image.new("RGB", (200, 200), color=(100, 100, 100))
    preprocessed = ocr_service.preprocess_image(img)
    assert preprocessed is not None
    assert preprocessed.size == (200, 200)

def test_ocr_extraction_on_sample():
    sample_path = generate_sample_document_image("INVOICE", "test_inv.png")
    result = ocr_service.extract_text_and_boxes(str(sample_path))
    assert result.raw_text is not None
    assert len(result.raw_text) > 20
    assert len(result.word_boxes) > 0
    # Verify bounding box format [ymin, xmin, ymax, xmax] normalized
    box = result.word_boxes[0]
    assert "bbox" in box
    assert len(box["bbox"]) == 4
    assert 0 <= box["bbox"][0] <= 1000
