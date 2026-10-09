import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw
from app.models.schemas import PIIEntity

class PIIDetectorService:
    def __init__(self):
        # Regex patterns for high-risk PII
        self.patterns = [
            ("SSN", r'\b\d{3}-\d{2}-\d{4}\b', "HIGH", self._mask_ssn),
            ("AADHAAR", r'\b\d{4}\s\d{4}\s\d{4}\b', "HIGH", self._mask_aadhaar),
            ("PAN", r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', "HIGH", self._mask_pan),
            ("CREDIT_CARD", r'\b(?:\d{4}[-\s]?){3}\d{4}\b', "HIGH", self._mask_cc),
            ("EMAIL", r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', "MEDIUM", self._mask_email),
            ("PHONE", r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', "MEDIUM", self._mask_phone),
            ("PASSPORT", r'\b[A-PR-WY][1-9]\d\s?\d{4}[1-9]\b|\b[C-Z]\d{8}\b', "HIGH", self._mask_passport),
            ("API_KEY", r'\b(?:sk_live_|ghp_|AKIA)[A-Za-z0-9_\-]{16,40}\b', "HIGH", self._mask_secret),
        ]

    def _mask_ssn(self, val: str) -> str:
        parts = val.split("-")
        return f"***-**-{parts[-1]}" if len(parts) == 3 else "***-**-****"

    def _mask_aadhaar(self, val: str) -> str:
        parts = val.split()
        return f"XXXX XXXX {parts[-1]}" if len(parts) == 3 else "XXXX XXXX XXXX"

    def _mask_pan(self, val: str) -> str:
        return f"{val[:2]}***{val[-2:]}" if len(val) >= 5 else "XXXXX****X"

    def _mask_cc(self, val: str) -> str:
        clean = val.replace(" ", "").replace("-", "")
        return f"****-****-****-{clean[-4:]}" if len(clean) >= 4 else "****-****-****-****"

    def _mask_email(self, val: str) -> str:
        if "@" in val:
            user, domain = val.split("@", 1)
            masked_user = user[0] + "***" if len(user) > 1 else "*"
            return f"{masked_user}@{domain}"
        return "masked@email.com"

    def _mask_phone(self, val: str) -> str:
        return f"***-***-{val[-4:]}" if len(val) >= 4 else "***-***-****"

    def _mask_passport(self, val: str) -> str:
        return f"{val[:2]}*****{val[-2:]}" if len(val) >= 4 else "*******"

    def _mask_secret(self, val: str) -> str:
        return f"{val[:4]}****************"

    def detect_pii(self, text: str) -> Tuple[List[PIIEntity], str]:
        """
        Scans text for all sensitive PII entities, returning structured entity matches
        and a sanitized/redacted version of the text.
        """
        entities: List[PIIEntity] = []
        sanitized_text = text

        for entity_type, pattern, severity, mask_fn in self.patterns:
            for match in re.finditer(pattern, text):
                raw = match.group(0)
                masked = mask_fn(raw)
                
                # Check for duplicates
                if not any(e.start == match.start() and e.end == match.end() for e in entities):
                    entities.append(PIIEntity(
                        entity_type=entity_type,
                        raw_value=raw,
                        masked_value=masked,
                        start=match.start(),
                        end=match.end(),
                        severity=severity
                    ))

        # Sort entities by start index descending to safely replace in sanitized string
        entities.sort(key=lambda x: x.start, reverse=True)
        for entity in entities:
            sanitized_text = (
                sanitized_text[:entity.start] + entity.masked_value + sanitized_text[entity.end:]
            )

        # Restore original ascending order
        entities.sort(key=lambda x: x.start)
        return entities, sanitized_text

    def create_redacted_image(
        self,
        image_path: str,
        output_path: str,
        word_boxes: List[Dict[str, Any]],
        pii_entities: List[PIIEntity]
    ) -> str:
        """
        Creates a visually redacted document image by drawing solid black rectangles
        over any OCR bounding boxes that contain detected PII.
        """
        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        w, h = img.size

        # Collect raw PII values / tokens
        pii_tokens = set()
        for p in pii_entities:
            for token in re.findall(r'[A-Za-z0-9]+', p.raw_value):
                if len(token) >= 3:
                    pii_tokens.add(token.lower())

        # Check each OCR bounding box
        for box in word_boxes:
            box_text = box.get("text", "").strip()
            bbox = box.get("bbox", [0, 0, 0, 0]) # [ymin, xmin, ymax, xmax] 0-1000
            
            # Check if box text overlaps with any pii token
            clean_box = re.sub(r'[^A-Za-z0-9]', '', box_text).lower()
            if any(t in clean_box or clean_box in t for t in pii_tokens if len(t) > 2):
                ymin, xmin, ymax, xmax = bbox
                # Convert normalized coordinates to pixel dimensions
                px_xmin = int((xmin / 1000.0) * w) - 2
                px_ymin = int((ymin / 1000.0) * h) - 2
                px_xmax = int((xmax / 1000.0) * w) + 2
                px_ymax = int((ymax / 1000.0) * h) + 2
                
                # Draw solid redaction box
                draw.rectangle([(px_xmin, px_ymin), (px_xmax, px_ymax)], fill=(15, 23, 42))

        # Save redacted image
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")
        return output_path

pii_detector_service = PIIDetectorService()
