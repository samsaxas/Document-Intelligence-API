import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
SAMPLES_DIR = BASE_DIR.parent / "sample_documents"
MODEL_WEIGHTS_DIR = DATA_DIR / "models"

for directory in [DATA_DIR, UPLOADS_DIR, PROCESSED_DIR, SAMPLES_DIR, MODEL_WEIGHTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    PROJECT_NAME: str = "Document Intelligence API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'doc_intel.db'}"
    
    # Confidence Thresholds for Human-In-The-Loop Triage
    CLASSIFICATION_CONFIDENCE_THRESHOLD: float = 0.85
    EXTRACTION_CONFIDENCE_THRESHOLD: float = 0.80
    
    # Document Classes
    DOCUMENT_CLASSES: list[str] = [
        "INVOICE",
        "RECEIPT",
        "EMPLOYMENT_CONTRACT",
        "IDENTITY_DOCUMENT",
        "RESUME",
        "BANK_STATEMENT",
        "TAX_FORM"
    ]
    
    # Key Extraction Fields per Class
    EXTRACTION_FIELDS: dict[str, list[str]] = {
        "INVOICE": ["vendor_name", "invoice_number", "invoice_date", "due_date", "total_amount", "tax_amount", "customer_name"],
        "RECEIPT": ["merchant_name", "receipt_number", "date", "total_amount", "payment_method", "tax_amount"],
        "EMPLOYMENT_CONTRACT": ["employer_name", "employee_name", "job_title", "salary", "start_date", "notice_period"],
        "IDENTITY_DOCUMENT": ["full_name", "id_number", "id_type", "date_of_birth", "issue_date", "expiry_date", "nationality"],
        "RESUME": ["candidate_name", "email", "phone", "education", "experience_years", "primary_skills"],
        "BANK_STATEMENT": ["bank_name", "account_holder", "account_number", "statement_period", "closing_balance"],
        "TAX_FORM": ["taxpayer_name", "tax_id", "tax_year", "gross_income", "tax_payable"]
    }

settings = Settings()
