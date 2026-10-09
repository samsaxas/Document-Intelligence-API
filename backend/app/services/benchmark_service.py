import time
import numpy as np
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from app.config import settings
from app.services.classifier import classifier_service, TRAINING_CORPUS
from app.models.db_models import BenchmarkRecord
from app.models.schemas import BenchmarkComparisonResponse, BenchmarkMetrics

# Evaluation / Test Dataset
EVAL_DATASET = [
    # INVOICE
    ("INVOICE #99824 Date: 2024-09-15 Vendor: Atlas Solutions Client: Meta Corp Total: $9,400.00 Net 30 days due wire transfer", "INVOICE"),
    ("Commercial Bill of Supply #8821 Billed To: Global Supply Inc Total Amount: $3,210.50 Tax $240.00 Remittance details", "INVOICE"),
    ("INVOICE INV-2024-5501 Date: 2024-10-01 Seller: CloudFlow Technologies Total Payable: $14,900.00 Payment due on receipt", "INVOICE"),
    
    # RECEIPT
    ("RECEIPT Chipotle Mexican Grill Store #441 Burrito Bowl $11.50 Chips & Guac $4.25 Subtotal $15.75 Tax $1.34 Total $17.09 Card payment", "RECEIPT"),
    ("Store Receipt Best Buy Purchase Order HDMI Cable $19.99 USB Drive $24.99 Total $44.98 Apple Pay Approved", "RECEIPT"),
    ("Shell Gas Station Fuel Receipt 12.4 Gal Regular Unleaded Total $48.25 Paid Visa ending 8812", "RECEIPT"),

    # EMPLOYMENT_CONTRACT
    ("EMPLOYMENT AGREEMENT between OmniTech Inc and Michael Scott. Position: Regional Director. Annual Salary: $160,000. Start Date: Jan 1 2025. 60 days notice.", "EMPLOYMENT_CONTRACT"),
    ("OFFER OF EMPLOYMENT Dear Jennifer, Welcome to Apex Systems as Principal Architect. Base Compensation $195,000 per annum plus bonus.", "EMPLOYMENT_CONTRACT"),

    # IDENTITY_DOCUMENT
    ("PASSPORT United States of America Surname: SMITH Given Names: ALEXANDER Passport No: D8829104 DOB: 1985-07-22 Nationality: USA", "IDENTITY_DOCUMENT"),
    ("UNIQUE IDENTIFICATION AUTHORITY OF INDIA Aadhaar Card No: 8829 1102 9931 Name: Priya Sharma DOB: 15/03/1991 Female Address: Bangalore", "IDENTITY_DOCUMENT"),

    # RESUME
    ("RESUME - DAVID K. CHEN Senior Full Stack Developer. 8+ years building enterprise React and Python web applications. Education: UCLA BS Computer Science.", "RESUME"),
    ("CURRICULUM VITAE Dr. Emily Watson NLP Research Scientist. Publications in NeurIPS, ACL. Skills: PyTorch, Transformers, LLMs, Vector DBs.", "RESUME"),

    # BANK_STATEMENT
    ("WELLS FARGO MONTHLY STATEMENT Account Holder: Sarah Jenkins Account No: 8892-1102-3310 Total Deposits $6,400 Total Debits $4,100 Ending Balance $11,920.00", "BANK_STATEMENT"),
    ("BANK OF AMERICA CHECKING STATEMENT Customer: Robert Miller Period Ending 10/31/2024 Available Balance $8,420.50", "BANK_STATEMENT"),

    # TAX_FORM
    ("IRS FORM W-2 Wage and Tax Statement 2024 Employee: Jonathan Vance SSN: 987-65-4321 Wages: $145,000 Federal Tax Withheld: $28,900", "TAX_FORM"),
    ("FORM 1040 U.S. Individual Tax Return 2024 Taxpayer: Alexandra Chen SSN: 334-90-8812 Adjusted Gross Income: $180,000 Total Tax: $34,200", "TAX_FORM")
]

class BenchmarkService:
    def run_benchmark(self, db: Session = None) -> BenchmarkComparisonResponse:
        """
        Runs comprehensive benchmark comparing PyTorch Deep Neural Model against TF-IDF Baseline.
        Computes Accuracy, Macro F1, Precision, Recall, Confusion Matrix, and Average Latency.
        """
        classes = settings.DOCUMENT_CLASSES
        class_to_idx = {c: i for i, c in enumerate(classes)}
        
        texts = [item[0] for item in EVAL_DATASET]
        y_true = [item[1] for item in EVAL_DATASET]
        y_true_indices = [class_to_idx.get(c, 0) for c in y_true]

        # 1. Benchmark PyTorch Model
        pyt_preds = []
        pyt_latencies = []
        for text in texts:
            t0 = time.perf_counter()
            pred_class, conf, _ = classifier_service.classify_pytorch(text)
            lat = (time.perf_counter() - t0) * 1000.0
            pyt_preds.append(pred_class)
            pyt_latencies.append(lat)

        pyt_pred_indices = [class_to_idx.get(c, 0) for c in pyt_preds]
        pyt_acc = float(accuracy_score(y_true_indices, pyt_pred_indices))
        pyt_p, pyt_r, pyt_f1, _ = precision_recall_fscore_support(y_true_indices, pyt_pred_indices, average='macro', zero_division=0)
        
        # Per-class F1
        _, _, pyt_per_class_f1_arr, _ = precision_recall_fscore_support(y_true_indices, pyt_pred_indices, labels=list(range(len(classes))), average=None, zero_division=0)
        pyt_per_class_f1 = {classes[i]: round(float(pyt_per_class_f1_arr[i]), 3) for i in range(len(classes))}
        pyt_cm = confusion_matrix(y_true_indices, pyt_pred_indices, labels=list(range(len(classes)))).tolist()

        # 2. Benchmark TF-IDF Baseline
        tfidf_preds = []
        tfidf_latencies = []
        for text in texts:
            t0 = time.perf_counter()
            pred_class, conf, _ = classifier_service.classify_tfidf(text)
            lat = (time.perf_counter() - t0) * 1000.0
            tfidf_preds.append(pred_class)
            tfidf_latencies.append(lat)

        tfidf_pred_indices = [class_to_idx.get(c, 0) for c in tfidf_preds]
        tfidf_acc = float(accuracy_score(y_true_indices, tfidf_pred_indices))
        tfidf_p, tfidf_r, tfidf_f1, _ = precision_recall_fscore_support(y_true_indices, tfidf_pred_indices, average='macro', zero_division=0)
        
        _, _, tfidf_per_class_f1_arr, _ = precision_recall_fscore_support(y_true_indices, tfidf_pred_indices, labels=list(range(len(classes))), average=None, zero_division=0)
        tfidf_per_class_f1 = {classes[i]: round(float(tfidf_per_class_f1_arr[i]), 3) for i in range(len(classes))}
        tfidf_cm = confusion_matrix(y_true_indices, tfidf_pred_indices, labels=list(range(len(classes)))).tolist()

        # Build response
        pyt_metrics = BenchmarkMetrics(
            model_name="PyTorch Deep Neural Network",
            accuracy=round(pyt_acc, 4),
            macro_f1=round(float(pyt_f1), 4),
            avg_latency_ms=round(float(np.mean(pyt_latencies)), 2),
            precision_macro=round(float(pyt_p), 4),
            recall_macro=round(float(pyt_r), 4),
            per_class_f1=pyt_per_class_f1
        )

        tfidf_metrics = BenchmarkMetrics(
            model_name="TF-IDF + Logistic Regression Baseline",
            accuracy=round(tfidf_acc, 4),
            macro_f1=round(float(tfidf_f1), 4),
            avg_latency_ms=round(float(np.mean(tfidf_latencies)), 2),
            precision_macro=round(float(tfidf_p), 4),
            recall_macro=round(float(tfidf_r), 4),
            per_class_f1=tfidf_per_class_f1
        )

        # Save to DB if session provided
        if db:
            record = BenchmarkRecord(
                total_samples=len(texts),
                pytorch_accuracy=pyt_metrics.accuracy,
                pytorch_macro_f1=pyt_metrics.macro_f1,
                pytorch_avg_latency_ms=pyt_metrics.avg_latency_ms,
                tfidf_accuracy=tfidf_metrics.accuracy,
                tfidf_macro_f1=tfidf_metrics.macro_f1,
                tfidf_avg_latency_ms=tfidf_metrics.avg_latency_ms,
                confusion_matrices={"pytorch": pyt_cm, "tfidf": tfidf_cm},
                per_class_metrics={"pytorch": pyt_per_class_f1, "tfidf": tfidf_per_class_f1}
            )
            db.add(record)
            db.commit()

        return BenchmarkComparisonResponse(
            total_samples=len(texts),
            pytorch_metrics=pyt_metrics,
            tfidf_metrics=tfidf_metrics,
            confusion_matrices={"pytorch": pyt_cm, "tfidf": tfidf_cm},
            classes=classes
        )

benchmark_service = BenchmarkService()
