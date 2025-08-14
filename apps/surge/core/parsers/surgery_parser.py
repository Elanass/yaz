"""Surgery Domain Parser.

Handles parsing of surgical case data, patient information,
procedures, and surgical outcomes.
"""

import logging
from typing import Any

import pandas as pd

from . import BaseParser


logger = logging.getLogger(__name__)


class SurgeryParser(BaseParser):
    """Parser for surgical domain data."""

    def get_schema_patterns(self) -> list[str]:
        """Surgery-specific header patterns."""
        return [
            "surgery",
            "surgical",
            "procedure",
            "operation",
            "patient",
            "diagnosis",
            "surgeon",
            "anesthesia",
            "case",
            "outcome",
            "preop",
            "postop",
            "complication",
            "asa_score",
            "los",
        ]

    def parse(self, data: Any) -> dict[str, Any]:
        """Parse surgical data."""
        try:
            if isinstance(data, pd.DataFrame):
                return self._parse_dataframe(data)
            if isinstance(data, dict):
                return self._parse_dict(data)
            if isinstance(data, str):
                return self._parse_text(data)
            if isinstance(data, list):
                return self._parse_image_list(data)
            return {"error": f"Unsupported data type: {type(data)}"}
        except Exception as e:
            logger.exception(f"Error parsing surgery data: {e}")
            return {"error": str(e)}

    def _parse_dataframe(self, df: pd.DataFrame) -> dict[str, Any]:
        """Parse surgical DataFrame."""
        result = {
            "domain": "surgery",
            "data_type": "dataframe",
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "summary": {},
        }

        # Surgery-specific analysis
        surgery_columns = self._identify_surgery_columns(df)

        if surgery_columns.get("procedure"):
            result["summary"]["procedures"] = (
                df[surgery_columns["procedure"]].value_counts().to_dict()
            )

        if surgery_columns.get("outcome"):
            result["summary"]["outcomes"] = (
                df[surgery_columns["outcome"]].value_counts().to_dict()
            )

        if surgery_columns.get("los"):  # Length of stay
            los_col = surgery_columns["los"]
            if pd.api.types.is_numeric_dtype(df[los_col]):
                result["summary"]["avg_length_of_stay"] = float(df[los_col].mean())

        if surgery_columns.get("asa_score"):
            result["summary"]["asa_distribution"] = (
                df[surgery_columns["asa_score"]].value_counts().to_dict()
            )

        return result

    def _parse_dict(self, data: dict) -> dict[str, Any]:
        """Parse surgical dictionary data."""
        return {
            "domain": "surgery",
            "data_type": "dictionary",
            "keys": list(data.keys()),
            "case_data": data,
            "summary": {
                "fields_identified": len(data),
                "has_patient_info": any(
                    key in data for key in ["patient_id", "patient_name", "mrn"]
                ),
                "has_procedure_info": any(
                    key in data for key in ["procedure", "surgery_type", "operation"]
                ),
                "has_outcome_info": any(
                    key in data for key in ["outcome", "result", "status"]
                ),
            },
        }

    def _parse_text(self, text: str) -> dict[str, Any]:
        """Parse surgical text data with enhanced medical context analysis."""
        surgical_keywords = [
            "surgery",
            "operation",
            "procedure",
            "patient",
            "diagnosis",
            "anesthesia",
            "laparoscopic",
            "robotic",
            "open",
            "complication",
            "resection",
            "anastomosis",
            "dissection",
            "incision",
            "closure",
        ]

        # Enhanced medical terminology detection
        gastric_keywords = [
            "gastric",
            "stomach",
            "gastrectomy",
            "flot",
            "adenocarcinoma",
        ]
        clinical_keywords = [
            "preoperative",
            "postoperative",
            "intraoperative",
            "albumin",
            "hemoglobin",
            "asa",
        ]
        staging_keywords = [
            "tnm",
            "t1",
            "t2",
            "t3",
            "t4",
            "n0",
            "n1",
            "n2",
            "m0",
            "m1",
            "stage",
        ]

        found_surgical = [kw for kw in surgical_keywords if kw.lower() in text.lower()]
        found_gastric = [kw for kw in gastric_keywords if kw.lower() in text.lower()]
        found_clinical = [kw for kw in clinical_keywords if kw.lower() in text.lower()]
        found_staging = [kw for kw in staging_keywords if kw.lower() in text.lower()]

        # Basic keyword detection
        [kw for kw in surgical_keywords if kw.lower() in text.lower()]

        # Extract potential medical entities (simple pattern matching)
        import re

        # Look for medication names (capitalized words ending in common suffixes)
        medication_pattern = r"\b[A-Z][a-z]+(?:cillin|mycin|zole|pril|lol|ide|ine)\b"
        medications = re.findall(medication_pattern, text)

        # Look for measurements and lab values
        measurement_pattern = (
            r"\b\d+\.?\d*\s*(?:mg|ml|cc|units?|mmHg|bpm|°C|°F|kg|lbs?)\b"
        )
        measurements = re.findall(measurement_pattern, text)

        # Look for anatomical references
        anatomy_keywords = [
            "heart",
            "lung",
            "liver",
            "kidney",
            "stomach",
            "colon",
            "brain",
            "spine",
        ]
        anatomy_found = [
            word for word in anatomy_keywords if word.lower() in text.lower()
        ]

        # Look for time references
        time_pattern = r"\b\d+\s*(?:days?|weeks?|months?|years?|hours?|minutes?)\b"
        time_references = re.findall(time_pattern, text)

        # Assess text type
        if (
            any(word in text.lower() for word in ["operative", "surgery", "procedure"])
            or any(
                word in text.lower() for word in ["pathology", "biopsy", "histology"]
            )
            or any(word in text.lower() for word in ["discharge", "summary", "follow"])
            or any(word in text.lower() for word in ["assessment", "plan", "diagnosis"])
        ):
            pass

        return {
            "domain": "surgery",
            "data_type": "text",
            "text_length": len(text),
            "surgical_keywords_found": found_surgical,
            "gastric_keywords_found": found_gastric,
            "clinical_keywords_found": found_clinical,
            "staging_keywords_found": found_staging,
            "likely_surgery_text": len(found_surgical) > 0,
            "medical_specialty": self._detect_medical_specialty(text),
            "clinical_entities": {
                "medications": medications,
                "measurements": measurements,
                "anatomy": anatomy_found,
                "time_references": time_references,
            },
            "text_complexity": {
                "word_count": len(text.split()),
                "sentence_count": len([s for s in text.split(".") if s.strip()]),
                "medical_density": len(found_surgical + found_gastric + found_clinical)
                / max(len(text.split()), 1),
            },
        }

    def _parse_image_list(self, images: list[str]) -> dict[str, Any]:
        """Parse surgery-related image list."""
        surgery_image_types = {
            "ct_scan": ["ct", "computed_tomography", "scan"],
            "mri": ["mri", "magnetic_resonance"],
            "xray": ["xray", "x-ray", "radiograph"],
            "ultrasound": ["ultrasound", "us", "sonogram"],
            "endoscopy": ["endoscopy", "endoscopic", "scope"],
            "pathology": ["pathology", "histology", "biopsy", "slide"],
            "surgical_photo": ["surgical", "operative", "procedure", "surgery"],
            "wound": ["wound", "incision", "scar", "healing"],
        }

        categorized_images = {category: [] for category in surgery_image_types}
        valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".tiff", ".dcm", ".dicom"}
        valid_images = []

        for img_path in images:
            # Check if valid image extension
            if any(img_path.lower().endswith(ext) for ext in valid_extensions):
                valid_images.append(img_path)

                # Categorize by content
                img_lower = img_path.lower()
                for category, keywords in surgery_image_types.items():
                    if any(keyword in img_lower for keyword in keywords):
                        categorized_images[category].append(img_path)
                        break

        return {
            "domain": "surgery",
            "data_type": "image_list",
            "total_images": len(images),
            "valid_image_count": len(valid_images),
            "valid_images": valid_images,
            "categorized_images": categorized_images,
            "image_types_detected": [
                cat for cat, imgs in categorized_images.items() if imgs
            ],
            "medical_imaging_ratio": len(
                [
                    img
                    for img in valid_images
                    if any(
                        keyword in img.lower()
                        for keyword in ["ct", "mri", "xray", "ultrasound", "scan"]
                    )
                ]
            )
            / max(len(valid_images), 1),
        }

    def _detect_medical_specialty(self, text: str) -> str:
        """Detect medical specialty from text content."""
        specialty_keywords = {
            "gastric_surgery": [
                "gastric",
                "stomach",
                "gastrectomy",
                "flot",
                "gastroenterology",
            ],
            "cardiac_surgery": [
                "cardiac",
                "heart",
                "coronary",
                "bypass",
                "valve",
                "cardiology",
            ],
            "orthopedic_surgery": [
                "orthopedic",
                "bone",
                "joint",
                "fracture",
                "spine",
                "hip",
                "knee",
            ],
            "neurosurgery": ["neuro", "brain", "spine", "cranial", "tumor", "aneurysm"],
            "general_surgery": [
                "appendix",
                "gallbladder",
                "hernia",
                "colon",
                "intestine",
            ],
        }

        text_lower = text.lower()
        specialty_scores = {}

        for specialty, keywords in specialty_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                specialty_scores[specialty] = score

        if specialty_scores:
            return max(specialty_scores.items(), key=lambda x: x[1])[0]
        return "general_surgery"
