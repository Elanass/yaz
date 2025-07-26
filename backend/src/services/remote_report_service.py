import httpx
import json
import csv
from datetime import datetime
from typing import Any, Dict, Optional
from .provenance_service import ProvenanceService
from ..engines.adci_engine import AdciEngine
from ..engines.flot_engine import FlotEngine
from ..engines.gastrectomy_engine import GastrectomyEngine

class RemoteReportService:
    """Service to fetch and normalize remote clinical reports."""
    def __init__(self, provenance: ProvenanceService):
        self.provenance = provenance
        self.adci_engine = AdciEngine()
        self.flot_engine = FlotEngine()
        self.surgery_engine = GastrectomyEngine()

    async def fetch_rest_report(self, url: str, headers: Dict[str, str]) -> bytes:
        """Fetch report via REST API (PDF/HL7)"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.content

    async def fetch_fhir_json(self, endpoint: str, token: str) -> Dict[str, Any]:
        """Fetch FHIR JSON report"""
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(endpoint, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def fetch_csv_data(self, api_url: str) -> list:
        """Fetch lab data as CSV"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(api_url)
            resp.raise_for_status()
            text = resp.text
        reader = csv.DictReader(text.splitlines())
        return list(reader)

    def normalize_report(self, raw: Any, report_type: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw report into internal structured format"""
        # Placeholder: in reality use OCR, HL7 parsers, FHIR mappers
        normalized = {"type": report_type, "metadata": metadata, "data": raw}
        return normalized

    async def process_remote_report(self,
                                    source: str,
                                    raw_report: Any,
                                    report_type: str,
                                    patient_id: str,
                                    timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """Process and trigger actions based on normalized report"""
        ts = timestamp or datetime.utcnow()
        metadata = {"source": source, "patient_id": patient_id, "timestamp": ts.isoformat()}
        normalized = self.normalize_report(raw_report, report_type, metadata)

        # Log provenance
        self.provenance.log_report_ingestion(patient_id, report_type, metadata)

        # Trigger ADCI if pathology
        if report_type.lower() in ["pathology", "fhir-pathology"]:
            adci_result = self.adci_engine.evaluate(normalized)
            self.provenance.log_action(patient_id, "ADCI_EVALUATION", adci_result)

        # Trigger FLOT if lab data
        if report_type.lower() in ["lab", "csv"]:
            flot_result = self.flot_engine.evaluate(normalized)
            self.provenance.log_action(patient_id, "FLOT_EVALUATION", flot_result)

        # Trigger Surgery if imaging
        if report_type.lower() in ["dicom", "radiology"]:
            surgery_ready = self.surgery_engine.check_readiness(normalized)
            self.provenance.log_action(patient_id, "SURGERY_READINESS", surgery_ready)

        return normalized
