from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from app.config import SAMPLES_DIR

def generate_sample_document_image(doc_type: str, filename: str) -> Path:
    """Generates high quality synthetic scanned document images for instant testing."""
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SAMPLES_DIR / filename
    
    # 850 x 1100 (Standard Letter/A4 aspect ratio)
    img = Image.new("RGB", (850, 1100), color=(252, 252, 252))
    draw = ImageDraw.Draw(img)
    
    # Outer border
    draw.rectangle([(20, 20), (830, 1080)], outline=(210, 215, 220), width=2)
    
    if doc_type == "INVOICE":
        # Header
        draw.rectangle([(20, 20), (830, 90)], fill=(30, 41, 59))
        draw.text((45, 42), "ACME GLOBAL CORPORATION - TAX INVOICE", fill=(255, 255, 255))
        
        draw.text((45, 120), "Invoice Number: INV-2024-8892", fill=(30, 30, 30))
        draw.text((45, 150), "Invoice Date: 2024-10-15", fill=(30, 30, 30))
        draw.text((45, 180), "Due Date: 2024-11-15", fill=(30, 30, 30))
        
        draw.text((500, 120), "Billed To: Apex Solutions LLC", fill=(30, 30, 30))
        draw.text((500, 150), "Customer ID: CUST-99281", fill=(30, 30, 30))
        draw.text((500, 180), "Contact: accounts@apextech.com", fill=(30, 30, 30))
        
        # Table Header
        draw.rectangle([(45, 240), (805, 275)], fill=(241, 245, 249))
        draw.text((60, 250), "Description", fill=(51, 65, 85))
        draw.text((400, 250), "Qty", fill=(51, 65, 85))
        draw.text((520, 250), "Unit Price", fill=(51, 65, 85))
        draw.text((680, 250), "Amount", fill=(51, 65, 85))
        
        # Items
        items = [
            ("Enterprise Cloud Infrastructure", "1", "$4,200.00", "$4,200.00"),
            ("Advanced Security & Compliance Support", "1", "$1,500.00", "$1,500.00"),
            ("Dedicated Account Management Tier", "1", "$470.25", "$470.25")
        ]
        y = 295
        for desc, qty, rate, amt in items:
            draw.text((60, y), desc, fill=(40, 40, 40))
            draw.text((410, y), qty, fill=(40, 40, 40))
            draw.text((520, y), rate, fill=(40, 40, 40))
            draw.text((680, y), amt, fill=(40, 40, 40))
            draw.line([(45, y+25), (805, y+25)], fill=(230, 230, 230), width=1)
            y += 40

        # Totals
        draw.text((520, 460), "Subtotal:", fill=(50, 50, 50))
        draw.text((680, 460), "$5,700.00", fill=(50, 50, 50))
        draw.text((520, 490), "Tax (8.25%):", fill=(50, 50, 50))
        draw.text((680, 490), "$470.25", fill=(50, 50, 50))
        
        draw.rectangle([(500, 530), (805, 575)], fill=(240, 253, 244), outline=(134, 239, 172))
        draw.text((520, 545), "TOTAL DUE: $6,170.25", fill=(21, 128, 61))
        
        # Footer notes with PII
        draw.text((45, 650), "Payment Remittance Instructions:", fill=(30, 30, 30))
        draw.text((45, 680), "Wire Bank: Silicon Valley Commercial Bank", fill=(70, 70, 70))
        draw.text((45, 705), "Account Number: 8839-4402-1192", fill=(70, 70, 70))
        draw.text((45, 730), "Tax ID / SSN Reference: 334-90-8812", fill=(70, 70, 70))
        draw.text((45, 755), "Support Email: billing@acmeglobal.com | Phone: +1-800-555-0199", fill=(70, 70, 70))

    elif doc_type == "RECEIPT":
        # Narrow receipt style inside page
        draw.rectangle([(200, 40), (650, 950)], fill=(255, 255, 255), outline=(200, 200, 200), width=2)
        draw.text((320, 70), "STARBUCKS COFFEE", fill=(20, 20, 20))
        draw.text((310, 95), "Store #10492 - New York, NY", fill=(60, 60, 60))
        draw.text((330, 120), "Tel: 212-555-0144", fill=(60, 60, 60))
        draw.line([(220, 150), (630, 150)], fill=(180, 180, 180), width=1)
        
        draw.text((230, 170), "Receipt #: RCT-77291", fill=(40, 40, 40))
        draw.text((230, 195), "Date: 2024-10-12 14:32:00", fill=(40, 40, 40))
        draw.text((230, 220), "Cashier: Jennifer M.", fill=(40, 40, 40))
        
        draw.line([(220, 250), (630, 250)], fill=(180, 180, 180), width=1)
        draw.text((230, 270), "1x Caffe Latte (Venti)", fill=(40, 40, 40))
        draw.text((560, 270), "$5.45", fill=(40, 40, 40))
        draw.text((230, 305), "1x Chocolate Croissant", fill=(40, 40, 40))
        draw.text((560, 305), "$4.25", fill=(40, 40, 40))
        
        draw.line([(220, 350), (630, 350)], fill=(180, 180, 180), width=1)
        draw.text((230, 370), "Subtotal:", fill=(50, 50, 50))
        draw.text((560, 370), "$9.70", fill=(50, 50, 50))
        draw.text((230, 395), "Tax (8.875%):", fill=(50, 50, 50))
        draw.text((560, 395), "$0.86", fill=(50, 50, 50))
        draw.text((230, 430), "TOTAL AMOUNT:", fill=(10, 10, 10))
        draw.text((550, 430), "$10.56", fill=(10, 10, 10))
        
        draw.line([(220, 470), (630, 470)], fill=(180, 180, 180), width=1)
        draw.text((230, 490), "Payment Method: Visa Card", fill=(40, 40, 40))
        draw.text((230, 515), "Card Number: ****-****-****-4242", fill=(40, 40, 40))
        draw.text((230, 540), "Auth Code: 092812", fill=(40, 40, 40))
        draw.text((310, 600), "THANK YOU FOR YOUR VISIT!", fill=(60, 60, 60))

    elif doc_type == "EMPLOYMENT_CONTRACT":
        draw.rectangle([(20, 20), (830, 90)], fill=(15, 23, 42))
        draw.text((45, 42), "NOVATECH ENTERPRISES - EMPLOYMENT AGREEMENT", fill=(255, 255, 255))
        
        draw.text((45, 120), "THIS EMPLOYMENT AGREEMENT is entered into as of November 1, 2024,", fill=(40, 40, 40))
        draw.text((45, 145), "by and between NovaTech Enterprises ('Employer') and Jonathan Vance ('Employee').", fill=(40, 40, 40))
        
        draw.text((45, 190), "1. POSITION AND RESPONSIBILITIES", fill=(20, 20, 20))
        draw.text((45, 215), "The Employee shall serve in the position of Principal Solutions Architect,", fill=(50, 50, 50))
        draw.text((45, 240), "reporting directly to the Chief Technology Officer.", fill=(50, 50, 50))
        
        draw.text((45, 285), "2. COMPENSATION & SALARY", fill=(20, 20, 20))
        draw.text((45, 310), "The Employer shall pay the Employee a base annual salary of $185,000,", fill=(50, 50, 50))
        draw.text((45, 335), "payable in semi-monthly installments subject to standard deductions.", fill=(50, 50, 50))
        
        draw.text((45, 380), "3. TERM & TERMINATION", fill=(20, 20, 20))
        draw.text((45, 405), "Employment shall commence on 2024-11-01. Either party may terminate with 60 Days", fill=(50, 50, 50))
        draw.text((45, 430), "advance written notice.", fill=(50, 50, 50))
        
        draw.text((45, 480), "4. CONFIDENTIALITY & PERSONAL DATA", fill=(20, 20, 20))
        draw.text((45, 505), "Employee Social Security Number (SSN): 987-65-4321", fill=(50, 50, 50))
        draw.text((45, 530), "Employee PAN / Tax Ref: ABCDE1234F", fill=(50, 50, 50))
        draw.text((45, 555), "Emergency Contact: sarah.vance@gmail.com | +1-415-555-8821", fill=(50, 50, 50))

    elif doc_type == "IDENTITY_DOCUMENT":
        # ID Card card style
        draw.rectangle([(100, 100), (750, 550)], fill=(248, 250, 252), outline=(30, 41, 59), width=3)
        draw.rectangle([(100, 100), (750, 170)], fill=(30, 58, 138))
        draw.text((130, 125), "NATIONAL IDENTIFICATION & PASSPORT AUTHORITY", fill=(255, 255, 255))
        
        # Photo box
        draw.rectangle([(130, 200), (280, 400)], fill=(226, 232, 240), outline=(148, 163, 184), width=2)
        draw.text((170, 290), "[ PHOTO ]", fill=(100, 116, 139))
        
        draw.text((310, 200), "Full Name: Sarah Elizabeth Jenkins", fill=(15, 23, 42))
        draw.text((310, 235), "ID / Aadhaar Number: 5489 2314 9081", fill=(15, 23, 42))
        draw.text((310, 270), "Date of Birth: 1992-05-18", fill=(51, 65, 85))
        draw.text((310, 305), "Nationality: United States", fill=(51, 65, 85))
        draw.text((310, 340), "Issue Date: 2021-06-10", fill=(51, 65, 85))
        draw.text((310, 375), "Expiry Date: 2031-06-09", fill=(51, 65, 85))
        
        draw.text((130, 430), "Address: 742 Evergreen Terrace, Springfield, OR", fill=(71, 85, 105))
        draw.text((130, 465), "Emergency Contact Phone: +1-555-019-2834", fill=(71, 85, 105))
        draw.text((130, 500), "Tax ID: 450-12-7890", fill=(71, 85, 105))

    else:
        # Default Business Document
        draw.rectangle([(20, 20), (830, 90)], fill=(51, 65, 85))
        draw.text((45, 42), f"BUSINESS DOCUMENT - {doc_type}", fill=(255, 255, 255))
        draw.text((45, 130), f"Document Title: Sample {doc_type.title()} Record", fill=(30, 30, 30))
        draw.text((45, 165), "Vendor: Acme Corporation | Customer: Global Enterprises", fill=(50, 50, 50))
        draw.text((45, 200), "Total Amount: $4,500.00 | Date: 2024-10-15", fill=(50, 50, 50))
        draw.text((45, 235), "Reference SSN: 334-90-8812 | Email: contact@acme.com", fill=(50, 50, 50))

    img.save(out_path, "PNG")
    return out_path

def generate_all_sample_presets():
    """Generates all preset documents ready for immediate testing."""
    presets = [
        ("INVOICE", "sample_invoice.png"),
        ("RECEIPT", "sample_receipt.png"),
        ("EMPLOYMENT_CONTRACT", "sample_contract.png"),
        ("IDENTITY_DOCUMENT", "sample_id_card.png")
    ]
    created = []
    for doc_type, fname in presets:
        p = generate_sample_document_image(doc_type, fname)
        created.append(p)
    return created
