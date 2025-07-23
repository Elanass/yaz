"""
Provenance API - Data traceability and lineage tracking endpoints.
"""

import logging
from typing import Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import get_current_user, get_db
from ..db.models import User
from ..schemas.provenance import (
    ProvenanceRecord,
    ProvenanceCreate,
    ProvenanceQuery,
    LineageGraph,
    ProvenanceTrail,
    ImmutableSnapshot,
    DataQualityMetrics,
    ProvenanceExport,
    ProvenanceImport,
    ProvenanceVisualization,
    ProvenanceVerification,
    ClinicalProvenanceTemplate,
    ProvenanceStats,
)
from ..services.provenance_service import ProvenanceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/provenance", tags=["Provenance"])
provenance_service = ProvenanceService()


@router.post("/records", response_model=ProvenanceRecord)
async def create_provenance_record(
    provenance_data: ProvenanceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new provenance record."""
    try:
        record = await provenance_service.create_provenance_record(
            db, current_user.id, provenance_data
        )
        return record
    except Exception as e:
        logger.error(f"Failed to create provenance record: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to create provenance record"
        )


@router.get("/records", response_model=List[ProvenanceRecord])
async def query_provenance_records(
    entity_id: str = Query(None, description="Entity ID to search for"),
    entity_type: str = Query(None, description="Entity type filter"),
    activity_type: str = Query(None, description="Activity type filter"),
    agent_id: str = Query(None, description="Agent ID filter"),
    bundle_id: str = Query(None, description="Bundle ID filter"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results offset"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Query provenance records based on criteria."""
    try:
        query = ProvenanceQuery(
            entity_id=entity_id,
            entity_type=entity_type,
            activity_type=activity_type,
            agent_id=agent_id,
            bundle_id=bundle_id,
            limit=limit,
            offset=offset,
        )
        
        records = await provenance_service.query_provenance(db, query)
        return records
    except Exception as e:
        logger.error(f"Failed to query provenance records: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to query provenance records"
        )


@router.get("/records/{record_id}", response_model=ProvenanceRecord)
async def get_provenance_record(
    record_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific provenance record."""
    try:
        # Implementation would fetch record from database
        # For now, return not found
        raise HTTPException(status_code=404, detail="Provenance record not found")
    except Exception as e:
        logger.error(f"Failed to get provenance record: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to get provenance record"
        )


@router.get("/lineage/{entity_id}", response_model=LineageGraph)
async def get_lineage_graph(
    entity_id: UUID,
    depth: int = Query(5, ge=1, le=20, description="Lineage depth"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get data lineage graph for an entity."""
    try:
        graph = await provenance_service.get_lineage_graph(db, entity_id, depth)
        return graph
    except Exception as e:
        logger.error(f"Failed to get lineage graph: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get lineage graph")


@router.get("/trail", response_model=ProvenanceTrail)
async def get_provenance_trail(
    start_entity: UUID = Query(..., description="Start entity ID"),
    end_entity: UUID = Query(..., description="End entity ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get provenance trail between two entities."""
    try:
        trail = await provenance_service.create_provenance_trail(
            db, start_entity, end_entity
        )
        return trail
    except Exception as e:
        logger.error(f"Failed to get provenance trail: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get provenance trail")


@router.post("/decisions/{decision_id}", response_model=ProvenanceRecord)
async def track_decision_provenance(
    decision_id: UUID,
    input_data: Dict,
    model_info: Dict,
    output_data: Dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Track provenance for a clinical decision."""
    try:
        record = await provenance_service.track_decision_provenance(
            db, decision_id, current_user.id, input_data, model_info, output_data
        )
        return record
    except Exception as e:
        logger.error(f"Failed to track decision provenance: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to track decision provenance"
        )


@router.get("/snapshots/{ipfs_hash}/verify", response_model=ProvenanceVerification)
async def verify_immutable_snapshot(
    ipfs_hash: str,
    current_user: User = Depends(get_current_user),
):
    """Verify immutable snapshot integrity."""
    try:
        is_valid, details = await provenance_service.verify_immutable_snapshot(
            ipfs_hash
        )
        
        verification = ProvenanceVerification(
            is_valid=is_valid,
            verification_time=details.get("verified_at"),
            errors=[details.get("error")] if not is_valid else [],
            warnings=[],
            signature_valid=is_valid,
            hash_matches=is_valid,
            ipfs_accessible=is_valid,
        )
        
        return verification
    except Exception as e:
        logger.error(f"Failed to verify immutable snapshot: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to verify immutable snapshot"
        )


@router.get("/quality/{entity_id}", response_model=DataQualityMetrics)
async def get_data_quality_metrics(
    entity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get data quality metrics for an entity."""
    try:
        metrics = await provenance_service.get_data_quality_metrics(db, entity_id)
        return DataQualityMetrics(**metrics)
    except Exception as e:
        logger.error(f"Failed to get data quality metrics: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to get data quality metrics"
        )


@router.get("/export/{bundle_id}", response_model=ProvenanceExport)
async def export_provenance_bundle(
    bundle_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export a provenance bundle."""
    try:
        bundle = await provenance_service.export_provenance_bundle(db, bundle_id)
        return ProvenanceExport(**bundle)
    except Exception as e:
        logger.error(f"Failed to export provenance bundle: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to export provenance bundle"
        )


@router.post("/import")
async def import_provenance_bundle(
    import_data: ProvenanceImport,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Import a provenance bundle."""
    try:
        imported_records = await provenance_service.import_provenance_bundle(
            db, import_data.bundle_data, current_user.id
        )
        
        return {
            "message": "Provenance bundle imported successfully",
            "imported_records": imported_records,
            "total_imported": len(imported_records),
        }
    except Exception as e:
        logger.error(f"Failed to import provenance bundle: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to import provenance bundle"
        )


@router.get("/templates", response_model=List[ClinicalProvenanceTemplate])
async def get_provenance_templates():
    """Get clinical provenance templates."""
    try:
        templates = [
            ClinicalProvenanceTemplate(
                template_id="clinical_decision",
                name="Clinical Decision",
                description="Template for tracking clinical decision provenance",
                entity_templates=[
                    {"type": "patient_data", "required": True},
                    {"type": "clinical_protocol", "required": True},
                    {"type": "decision_result", "required": True},
                    {"type": "ai_model", "required": False},
                ],
                activity_templates=[
                    {"type": "decision_generation", "required": True},
                    {"type": "data_validation", "required": False},
                ],
                agent_templates=[
                    {"type": "person", "required": True},
                    {"type": "software_agent", "required": False},
                ],
                required_fields=["patient_id", "protocol_id", "decision_result"],
            ),
            ClinicalProvenanceTemplate(
                template_id="treatment_plan",
                name="Treatment Plan",
                description="Template for tracking treatment plan provenance",
                entity_templates=[
                    {"type": "patient_data", "required": True},
                    {"type": "diagnosis", "required": True},
                    {"type": "treatment_plan", "required": True},
                    {"type": "evidence_record", "required": False},
                ],
                activity_templates=[
                    {"type": "treatment_planning", "required": True},
                    {"type": "evidence_synthesis", "required": False},
                ],
                agent_templates=[
                    {"type": "person", "required": True},
                    {"type": "organization", "required": False},
                ],
                required_fields=["patient_id", "diagnosis_id", "treatment_plan_id"],
            ),
            ClinicalProvenanceTemplate(
                template_id="risk_assessment",
                name="Risk Assessment",
                description="Template for tracking risk assessment provenance",
                entity_templates=[
                    {"type": "patient_data", "required": True},
                    {"type": "risk_factors", "required": True},
                    {"type": "risk_score", "required": True},
                ],
                activity_templates=[
                    {"type": "risk_assessment", "required": True},
                    {"type": "model_inference", "required": False},
                ],
                agent_templates=[
                    {"type": "person", "required": True},
                    {"type": "ai_model", "required": False},
                ],
                required_fields=["patient_id", "risk_factors", "risk_score"],
            ),
        ]
        return templates
    except Exception as e:
        logger.error(f"Failed to get provenance templates: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to get provenance templates"
        )


@router.get("/visualization/{record_id}")
async def get_provenance_visualization(
    record_id: UUID,
    graph_type: str = Query("directed", description="Graph type"),
    layout: str = Query("hierarchical", description="Layout algorithm"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get provenance visualization configuration."""
    try:
        # Implementation would generate visualization data
        # For now, return basic configuration
        
        visualization = ProvenanceVisualization(
            graph_type=graph_type,
            layout_algorithm=layout,
            node_styling={
                "entity": {"color": "#4CAF50", "shape": "ellipse"},
                "activity": {"color": "#2196F3", "shape": "rectangle"},
                "agent": {"color": "#FF9800", "shape": "triangle"},
            },
            edge_styling={
                "used": {"color": "#666", "style": "solid"},
                "generated": {"color": "#333", "style": "solid"},
                "associated": {"color": "#999", "style": "dashed"},
            },
            filters={
                "show_entities": True,
                "show_activities": True,
                "show_agents": True,
                "time_range": None,
            },
        )
        
        return visualization
    except Exception as e:
        logger.error(f"Failed to get provenance visualization: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to get provenance visualization"
        )


@router.get("/stats", response_model=ProvenanceStats)
async def get_provenance_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get provenance system statistics."""
    try:
        # Implementation would calculate real statistics
        # For now, return mock data
        
        stats = ProvenanceStats(
            total_records=0,
            total_entities=0,
            total_activities=0,
            total_agents=0,
            immutable_snapshots=0,
            average_lineage_depth=0.0,
            data_quality_score=0.95,
            verification_rate=1.0,
            storage_efficiency=0.85,
            last_updated="2024-01-01T00:00:00Z",
        )
        
        return stats
    except Exception as e:
        logger.error(f"Failed to get provenance stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get provenance stats")


@router.post("/validate")
async def validate_provenance_record(
    record_data: ProvenanceCreate,
    current_user: User = Depends(get_current_user),
):
    """Validate a provenance record without storing it."""
    try:
        # Implementation would validate the record structure
        # Check for required fields, valid relationships, etc.
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
        }
        
        # Basic validation
        if not record_data.entities:
            validation_result["errors"].append("At least one entity is required")
            validation_result["is_valid"] = False
        
        if not record_data.activities:
            validation_result["warnings"].append("No activities specified")
        
        if not record_data.agents:
            validation_result["warnings"].append("No agents specified")
        
        return validation_result
    except Exception as e:
        logger.error(f"Failed to validate provenance record: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to validate provenance record"
        )


@router.get("/search")
async def search_provenance(
    q: str = Query(..., description="Search query"),
    type_filter: str = Query(None, description="Filter by type"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search provenance records using full-text search."""
    try:
        # Implementation would perform full-text search across provenance records
        # For now, return empty results
        
        results = {
            "query": q,
            "total_results": 0,
            "results": [],
            "facets": {
                "entity_types": {},
                "activity_types": {},
                "agent_types": {},
                "time_periods": {},
            },
        }
        
        return results
    except Exception as e:
        logger.error(f"Failed to search provenance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search provenance")
