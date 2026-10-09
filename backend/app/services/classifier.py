import os
import time
import pickle
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, List, Any
from app.config import settings, MODEL_WEIGHTS_DIR

np.random.seed(42)

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    torch.manual_seed(42)
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix

TRAINING_CORPUS = [
    # INVOICE
    ("TAX INVOICE Acme Global Corp Invoice Number INV-2024-8892 Invoice Date 2024-10-15 Due Date 2024-11-15 Billed To Apex Solutions LLC Itemized Cloud Services Subtotal $5,700.00 Tax $470.25 Total Amount Due $6,170.25 Wire Transfer Bank Account", "INVOICE"),
    ("TAX INVOICE Invoice Number INV-2024-001 Date: 2024-01-15 Due: 2024-02-15 Vendor Acme Corp Customer TechCorp Total $5,400.00 Tax $450.00 Billed To Subtotal Wire Transfer Payment Remittance", "INVOICE"),
    ("Commercial Invoice No: 99823 Bill To: Global Logistics Inc Payment Terms Net 30 Amount Due $12,890.50 Line items unit price qty total amount tax gst", "INVOICE"),
    ("INVOICE #INV-88712 Date: Oct 12, 2024 Vendor: CloudSoft LLC Services Rendered: Software Subscription $1,200.00 VAT 20% Total Payable: $1,440.00", "INVOICE"),
    ("Proforma Invoice Order reference PO-4491 Billed To Nexus Corp Total Sum $3,450.00 Due on receipt Bank Account Wire payment routing swift", "INVOICE"),
    ("INVOICE Seller: Alpha Hardware Dist. Buyer: Beta Studios Total $890.00 Sales Tax $71.20 Final Invoice Balance", "INVOICE"),
    ("Tax Invoice & Billing Statement #77218 Client: Omega Systems LLC Total Amount: $22,400.00 Due Date: Nov 30 2024 Itemized charges consultation", "INVOICE"),
    ("Invoice INV-2024-5501 Date 2024-10-01 Seller CloudFlow Technologies Total Payable $14,900.00 Payment due on receipt", "INVOICE"),
    ("TAX INVOICE Acme Global Corp 123 Tech Park Suite 400 San Jose CA 95110 Invoice Number INV-2024-8892 Invoice Date 2024-10-15 Due Date 2024-11-15 Billed To Apex Solutions LLC Customer Tax ID US-99283411 Item 1 Enterprise Cloud Services $4,200.00 Item 2 Infrastructure Support $1,500.00 Subtotal $5,700.00 Tax 8.25% $470.25 Total Amount Due $6,170.25 Payment Method Wire Transfer Bank Silicon Valley Bank Account 8839-4402-1192 Support Contact billing@acmeglobal.com Phone +1-800-555-0199", "INVOICE"),
    
    # RECEIPT
    ("RECEIPT Starbucks Coffee Store #10492 450 Lexington Ave Date: 2024-10-12 14:32 1x Caffe Latte $5.45 1x Chocolate Croissant $4.25 Subtotal $9.70 Tax $0.86 Total Amount $10.56 Paid by Visa Auth 092812", "RECEIPT"),
    ("RECEIPT Starbucks Coffee Store #1029 Date: 2024-10-12 14:30 1x Latte $5.50 1x Muffin $3.75 Subtotal $9.25 Tax $0.80 Total $10.05 Paid by Visa Card ending 4412 Thank you come again", "RECEIPT"),
    ("Sales Receipt Walmart Supercenter Cashier: Sarah Register 4 Milk $3.49 Bread $2.99 Eggs $4.19 Total $10.67 Cash Tendered $20.00 Change $9.33", "RECEIPT"),
    ("RECEIPT McDonald's Restaurant Order #342 Dine In Big Mac Meal $8.99 Apple Pie $1.99 Total $10.98 Paid Mastercard Auth 889211", "RECEIPT"),
    ("Uber Trip Receipt Total $34.50 Date: Oct 14 2024 Fare Breakdown Base Fare $4.00 Distance $22.50 Time $8.00 Tip $0.00 Paid with Apple Pay", "RECEIPT"),
    ("Store Receipt Target #0881 Items Purchased: Stationeries $15.40 Snacks $8.20 Subtotal $23.60 Tax $1.89 Total $25.49 Card Debit Approved", "RECEIPT"),

    # EMPLOYMENT_CONTRACT
    ("EXECUTIVE EMPLOYMENT AGREEMENT This agreement is entered between NovaTech Enterprises ('Employer') and Jonathan Vance ('Employee'). Position: Principal Solutions Architect. Start Date: 2024-11-01. Base Salary: $185,000 per annum. Notice Period: 60 days.", "EMPLOYMENT_CONTRACT"),
    ("EMPLOYMENT AGREEMENT This contract made between Enterprise Corp ('Employer') and John Doe ('Employee'). Position: Senior Software Engineer. Base Salary: $140,000 per annum. Start Date: Nov 1 2024. Notice period 60 days. Termination, confidentiality, non-disclosure.", "EMPLOYMENT_CONTRACT"),
    ("OFFER LETTER AND EMPLOYMENT CONTRACT Dear Alice, We are pleased to offer you the role of VP of Product at Horizon Inc. Compensation $210,000 annual base plus equity stock options. Probation period 3 months. Benefits, PTO, and restrictive covenants.", "EMPLOYMENT_CONTRACT"),
    ("CONTRACT OF SERVICE / EMPLOYMENT This agreement confirms the appointment of Robert Smith as Chief Financial Officer. Term: 3 years. Remuneration: $190,000. Duties, standard termination clause, non-compete for 12 months.", "EMPLOYMENT_CONTRACT"),
    ("INDIVIDUAL EMPLOYMENT CONTRACT Employer: Delta Dynamics Employee: Emily Watson Designation: Data Scientist Annual Remuneration $130,000. Working hours 40 hrs/week. Intellectual property assignment clause.", "EMPLOYMENT_CONTRACT"),
    ("EMPLOYMENT AGREEMENT between NovaTech and Employee Base Salary $150,000 Start Date Nov 1 Position Architect", "EMPLOYMENT_CONTRACT"),

    # IDENTITY_DOCUMENT
    ("REPUBLIC NATIONAL IDENTITY CARD Full Name: Sarah Elizabeth Jenkins Document ID / Aadhaar: 5489 2314 9081 Date of Birth: 1992-05-18 Nationality: United States Issue Date: 2021-06-10 Expiry Date: 2031-06-09 Permanent Address: 742 Evergreen Terrace", "IDENTITY_DOCUMENT"),
    ("REPUBLIC NATIONAL IDENTITY CARD ID: 5489-2314-9081 Name: Sarah Jenkins Date of Birth: 1992-05-18 Nationality: USA Issue Date: 2021-06-10 Expiry: 2031-06-09 Gender: F Address: 742 Evergreen Terr Springfield", "IDENTITY_DOCUMENT"),
    ("PASSPORT United States of America Type: P Code: USA Passport No: C09823145 Surname: VANCE Given Names: JONATHAN Nationality: UNITED STATES OF AMERICA DOB: 14 AUG 1988 Sex: M Place of Birth: California Authority: Dept of State", "IDENTITY_DOCUMENT"),
    ("GOVERNMENT OF INDIA UNIQUE IDENTIFICATION AUTHORITY AADHAAR CARD Enrolment No: 1029/39481/09281 Aadhaar No: 9182 3746 5501 Name: Rajesh Kumar DOB: 12/08/1985 Male Address: Sector 62 Noida UP", "IDENTITY_DOCUMENT"),
    ("NATIONAL IDENTITY CARD PERMANENT ACCOUNT NUMBER CARD Identity Proof Govt Issue ID Card Date of Birth Citizen Nationality Passport ID", "IDENTITY_DOCUMENT"),
    ("DRIVER LICENSE State of California DL No: N8892147 Name: DAVID K. MILLER DOB: 09/24/1994 Class C Expires: 09/24/2028 Height: 5-11 Eyes: BLU", "IDENTITY_DOCUMENT"),

    # RESUME
    ("CURRICULUM VITAE ALEXANDRA CHEN Email: alexandra.chen.dev@gmail.com Phone: +1-415-555-2671 Senior Machine Learning Engineer with 7 years experience in PyTorch, NLP, Transformers, LLMs. Education: M.S. Computer Science, Stanford University (2018). Experience: Lead AI Engineer at DataScale Inc.", "RESUME"),
    ("CURRICULUM VITAE ALEXANDRA CHEN Email: alex.chen@gmail.com Phone: +1-415-555-0199 Senior Machine Learning Engineer with 6+ years experience in PyTorch Transformers LLMs NLP. Education: Stanford MS Computer Science. Experience: Staff AI Engineer at ScaleAI.", "RESUME"),
    ("RESUME MICHAEL CHANG Software Engineer Skills: Python, Java, React, Docker, Kubernetes, AWS. Professional Summary: 4 years building scalable microservices and distributed APIs. B.S. in Computer Engineering from Berkeley.", "RESUME"),
    ("PROFILE RESUME SOPHIA PATEL Product Manager Experience: Led cross-functional teams of 20+ engineers and designers. Agile Scrum, Roadmapping, Data Analytics, SQL, Tableau. MBA Harvard Business School.", "RESUME"),
    ("RESUME DANIEL BROWN Cloud Infrastructure Architect AWS Certified Solutions Architect Professional. Terraform, Ansible, CI/CD pipelines, Prometheus, Grafana. 8 years enterprise cloud migration.", "RESUME"),

    # BANK_STATEMENT
    ("JPMORGAN CHASE BANK MONTHLY STATEMENT Account Holder: Marcus Aurelius Vance Account Number: 4409-1823-9920 Statement Period: Sept 01 2024 to Sept 30 2024 Opening Balance: $14,250.00 Total Deposits: $8,500.00 Total Withdrawals: $6,230.50 Closing Balance: $16,519.50", "BANK_STATEMENT"),
    ("CHASE BANK MONTHLY ACCOUNT STATEMENT Account Holder: Marcus Aurelius Account Number: 4409-1823-9920 Statement Period: 09/01/2024 to 09/30/2024 Beginning Balance $14,250.00 Deposits $8,500.00 Withdrawals $6,230.50 Ending Balance $16,519.50", "BANK_STATEMENT"),
    ("BANK OF AMERICA STATEMENT OF ACCOUNT Account #8839120932 Customer: Elena Rostova Period Ending: Oct 31 2024 Total Credits $12,400 Total Debits $9,870 Available Balance $23,120.45", "BANK_STATEMENT"),
    ("WELLS FARGO BANK STATEMENT Checking Account Summary Previous Balance $5,120.00 Electronic Deposits $4,300.00 ATM Withdrawals $400.00 Service Fee $0.00 New Balance $9,020.00", "BANK_STATEMENT"),
    ("CITIBANK CONSOLIDATED FINANCIAL STATEMENT Customer: David Miller Account No: 1109-3382-4410 Daily Ledger balances, interest credited, transactions summary.", "BANK_STATEMENT"),

    # TAX_FORM
    ("INTERNAL REVENUE SERVICE FORM W-2 WAGE AND TAX STATEMENT 2024 Taxpayer Name: Robert David Miller Tax ID / SSN: 450-12-7890 Employer: Vanguard Software Solutions Inc Employer EIN: 12-9847102 Wages, tips, other comp: $132,450.00 Federal income tax withheld: $24,180.00 Gross Income: $132,450.00 Net Tax Payable: $2,450.00", "TAX_FORM"),
    ("INTERNAL REVENUE SERVICE FORM W-2 WAGE AND TAX STATEMENT 2024 Taxpayer Name: Robert David Miller SSN: 450-12-7890 Employer: Vanguard Software EIN: 12-9847102 Wages $132,450.00 Fed Tax Withheld $24,180.00 SS Wages $132,450.00", "TAX_FORM"),
    ("FORM 1040 U.S. Individual Income Tax Return 2024 Filing Status: Single Taxpayer Name: Sarah Jenkins SSN: 987-65-4321 Total Income $98,400 Standard Deduction $14,600 Taxable Income $83,800 Total Tax $14,200 Refund $1,800", "TAX_FORM"),
    ("INCOME TAX RETURN VERIFICATION FORM ITR-V Assessment Year 2024-25 PAN: ABCDE1234F Taxpayer: Vikram Sharma Total Income Rs. 14,50,000 Total Tax Payable Rs. 2,15,000 e-verification acknowledgement", "TAX_FORM"),
    ("FORM 1099-NEC Nonemployee Compensation 2024 Payer: TechWorks Inc Recipient: Jonathan Vance Recipient TIN: 334-90-8812 Nonemployee compensation $45,000.00 Federal income tax withheld $0.00", "TAX_FORM")
]

class DocumentClassifierService:
    def __init__(self):
        self.classes = settings.DOCUMENT_CLASSES
        self.class_to_idx = {c: i for i, c in enumerate(self.classes)}
        self.idx_to_class = {i: c for i, c in enumerate(self.classes)}
        
        self.vocab: Dict[str, int] = {}
        self.pytorch_model = None
        
        self.tfidf_vectorizer: TfidfVectorizer = None
        self.tfidf_classifier: LogisticRegression = None
        
        self.is_trained = False
        self._initialize_and_train()

    def _build_vocab(self, texts: List[str], max_vocab: int = 5000):
        word_counts = {}
        for text in texts:
            for word in text.lower().replace(",", " ").replace(".", " ").replace(":", " ").replace("-", " ").split():
                if len(word) > 1:
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:max_vocab]
        self.vocab = {"<PAD>": 0, "<UNK>": 1}
        for idx, (word, _) in enumerate(sorted_words, start=2):
            self.vocab[word] = idx

    def _text_to_indices(self, text: str) -> List[int]:
        tokens = text.lower().replace(",", " ").replace(".", " ").replace(":", " ").replace("-", " ").split()
        return [self.vocab.get(tok, self.vocab.get("<UNK>", 1)) for tok in tokens if tok] or [1]

    def _initialize_and_train(self):
        texts = [item[0] for item in TRAINING_CORPUS]
        labels = [item[1] for item in TRAINING_CORPUS]
        y_labels = [self.class_to_idx[l] for l in labels]
        
        # 1. Train TF-IDF Baseline
        self.tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=4000, sublinear_tf=True)
        X_tfidf = self.tfidf_vectorizer.fit_transform(texts)
        
        self.tfidf_classifier = LogisticRegression(C=10.0, max_iter=500, random_state=42)
        self.tfidf_classifier.fit(X_tfidf, y_labels)

        # 2. Train PyTorch Model
        self._build_vocab(texts)
        
        if TORCH_AVAILABLE:
            try:
                vocab_size = max(len(self.vocab) + 2, 100)
                embed_dim = 128
                num_classes = len(self.classes)

                class DocNet(nn.Module):
                    def __init__(self, vs, ed, nc):
                        super().__init__()
                        self.embedding = nn.EmbeddingBag(vs, ed, sparse=False, mode='mean')
                        self.fc1 = nn.Linear(ed, 128)
                        self.relu = nn.ReLU()
                        self.layer_norm = nn.LayerNorm(128)
                        self.fc2 = nn.Linear(128, nc)

                    def forward(self, text_indices, offsets):
                        embedded = self.embedding(text_indices, offsets)
                        x = self.layer_norm(self.relu(self.fc1(embedded)))
                        return self.fc2(x)

                self.pytorch_model = DocNet(vocab_size, embed_dim, num_classes)
                
                # Prepare tensors
                all_indices = []
                offsets = []
                for text in texts:
                    offsets.append(len(all_indices))
                    all_indices.extend(self._text_to_indices(text))
                
                text_tensor = torch.tensor(all_indices, dtype=torch.long)
                offsets_tensor = torch.tensor(offsets, dtype=torch.long)
                labels_tensor = torch.tensor(y_labels, dtype=torch.long)
                
                self.pytorch_model.train()
                optimizer = optim.Adam(self.pytorch_model.parameters(), lr=0.03, weight_decay=1e-5)
                criterion = nn.CrossEntropyLoss()
                
                for epoch in range(160):
                    optimizer.zero_grad()
                    output = self.pytorch_model(text_tensor, offsets_tensor)
                    loss = criterion(output, labels_tensor)
                    loss.backward()
                    optimizer.step()
                    
                self.pytorch_model.eval()
            except Exception as e:
                self.pytorch_model = None

        self.is_trained = True

    def classify_tfidf(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        X = self.tfidf_vectorizer.transform([text])
        probs = self.tfidf_classifier.predict_proba(X)[0]
        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])
        all_probs = {self.idx_to_class[i]: round(float(p), 4) for i, p in enumerate(probs)}
        return self.idx_to_class[pred_idx], round(confidence, 4), all_probs

    def classify_pytorch(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        if self.pytorch_model is not None and TORCH_AVAILABLE:
            try:
                indices = self._text_to_indices(text)
                text_tensor = torch.tensor(indices, dtype=torch.long)
                offsets_tensor = torch.tensor([0], dtype=torch.long)
                
                with torch.no_grad():
                    logits = self.pytorch_model(text_tensor, offsets_tensor)
                    probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()
                    
                pred_idx = int(np.argmax(probs))
                confidence = float(probs[pred_idx])
                all_probs = {self.idx_to_class[i]: round(float(p), 4) for i, p in enumerate(probs)}
                return self.idx_to_class[pred_idx], round(confidence, 4), all_probs
            except Exception:
                pass

        return self.classify_tfidf(text)

    def classify_document(self, text: str) -> Dict[str, Any]:
        pyt_class, pyt_conf, pyt_probs = self.classify_pytorch(text)
        tfidf_class, tfidf_conf, tfidf_probs = self.classify_tfidf(text)
        
        # Soft voting ensemble between PyTorch and TF-IDF
        ensemble_scores = {}
        for c in self.classes:
            p_val = pyt_probs.get(c, 0.0)
            t_val = tfidf_probs.get(c, 0.0)
            ensemble_scores[c] = 0.55 * p_val + 0.45 * t_val
        
        final_class = max(ensemble_scores, key=ensemble_scores.get)
        final_conf = round(float(ensemble_scores[final_class]), 4)
            
        return {
            "pytorch_class": pyt_class,
            "pytorch_confidence": pyt_conf,
            "pytorch_probabilities": pyt_probs,
            "tfidf_class": tfidf_class,
            "tfidf_confidence": tfidf_conf,
            "tfidf_probabilities": tfidf_probs,
            "final_class": final_class,
            "final_confidence": final_conf,
            "agreement": (pyt_class == tfidf_class)
        }

classifier_service = DocumentClassifierService()
