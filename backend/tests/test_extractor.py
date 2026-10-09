import pytest
from app.services.extractor import extractor_service

def test_invoice_field_extraction():
    text = "TAX INVOICE Acme Global Corp Invoice Number: INV-2024-998 Date: 2024-10-15 Total Amount: $4,500.00 Tax: $350.00 Customer: Vertex Inc"
    fields = extractor_service.extract_fields("INVOICE", text)
    assert "invoice_number" in fields
    assert "total_amount" in fields
    assert "vendor_name" in fields
    assert fields["invoice_number"]["value"] == "INV-2024-998"
    assert "$4,500.00" in fields["total_amount"]["value"]

def test_receipt_field_extraction():
    text = "STARBUCKS STORE Receipt #: RCT-8819 Date: 2024-10-12 Total Amount: $14.50 Paid by Visa"
    fields = extractor_service.extract_fields("RECEIPT", text)
    assert "merchant_name" in fields
    assert "receipt_number" in fields
    assert "total_amount" in fields
    assert fields["receipt_number"]["value"] == "RCT-8819"
