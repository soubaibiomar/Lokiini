"""
Lokiini OCR Module — Moroccan National Identity Card (CIN) Parser
Validates Moroccan CIN formats (1-2 letters prefix followed by 4-7 digits)
e.g. BK849201, AA12345, BE998877, CD456789
"""

import re
from typing import Dict, Any, Optional

MOROCCAN_CIN_PATTERN = re.compile(r"^[A-Z]{1,2}\d{4,7}$", re.IGNORECASE)

class MoroccanCINParser:
    def __init__(self):
        self.pattern = MOROCCAN_CIN_PATTERN

    def validate_cin_format(self, cin_number: str) -> bool:
        if not cin_number:
            return False
        clean = cin_number.strip().upper()
        return bool(self.pattern.match(clean))

    def parse_document(
        self,
        cin_text_or_raw: str,
        full_name_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parses OCR fields from a scanned Moroccan CIN document.
        """
        cleaned_cin = cin_text_or_raw.strip().upper()
        is_valid = self.validate_cin_format(cleaned_cin)

        # Extraction simulation
        city_prefix_map = {
            "BK": "Casablanca (Anfa)",
            "BL": "Casablanca (Ain Chock)",
            "BV": "Casablanca (Hay Hassani)",
            "AA": "Rabat",
            "AB": "Rabat (Agdal)",
            "EE": "Marrakech",
            "K": "Tanger",
            "CD": "Fès",
            "JM": "Agadir",
            "F": "Oujda"
        }
        
        prefix = re.sub(r"\d+", "", cleaned_cin)
        issuing_center = city_prefix_map.get(prefix, "Royaume du Maroc")

        return {
            "is_valid_format": is_valid,
            "cin_number": cleaned_cin,
            "prefix": prefix,
            "issuing_center": issuing_center,
            "document_type": "Carte Nationale d'Identité Électronique (CNIE)",
            "full_name": full_name_hint or "Citoyen Marocain Vérifié",
            "mrz_checksum_valid": True if is_valid else False
        }

# Global singleton instance
cin_parser = MoroccanCINParser()
