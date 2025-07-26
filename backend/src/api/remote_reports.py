"""
Remote Report Access API Endpoints
"""
from fastapi import APIRouter, HTTPException
from ..schemas.remote_reports import RemoteReportRequest, NormalizedReportResponse
from ..services.remote_report_service import RemoteReportService
from ..services.provenance_service import ProvenanceService
from ..db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/remote-reports", tags=["remote-reports"])

@router.post("/process", response_model=NormalizedReportResponse)
async def process_remote_report(
    request: RemoteReportRequest,
    db: Session = Depends(get_db)
):
    """Fetch, normalize, and evaluate remote clinical reports"""
    provenance_service = ProvenanceService(db)
    service = RemoteReportService(provenance_service)

    try:
        # Fetch raw report
        if request.report_format == "rest":
            raw = await service.fetch_rest_report(request.url, request.headers)
        elif request.report_format == "fhir":
            if not request.token:
                raise HTTPException(status_code=400, detail="FHIR token required for fhir format")
            raw = await service.fetch_fhir_json(request.url, request.token)
        elif request.report_format == "csv":
            raw = await service.fetch_csv_data(request.url)
        else:
            raise HTTPException(status_code=400, detail="Unsupported report format")

        # Process report and trigger agents
        normalized = await service.process_remote_report(
            source=request.source,
            raw_report=raw,
            report_type=request.report_type,
            patient_id=request.patient_id,
            timestamp=request.timestamp
        )

        return NormalizedReportResponse(**normalized)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
