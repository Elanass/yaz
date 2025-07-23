"""
Confidence Visualization API Endpoints
Real-time ADCI confidence visualization and analysis
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..core.deps import get_current_user, get_current_active_user
from ..core.rbac import RBACMatrix, Resource, Action, Role
from ..services.confidence_visualizer import ConfidenceVisualizerService
from ..services.audit_service import AuditService, AuditEvent, AuditEventType, AuditSeverity
from ..schemas.user import User
from ..schemas.confidence import (
    VisualizationType,
    VisualizationRequest,
    GaugeVisualizationRequest,
    TrendVisualizationRequest,
    ComparativeVisualizationRequest,
    GaugeVisualizationResponse,
    TrendVisualizationResponse,
    ThresholdAnalysisResponse,
    ComparativeAnalysisResponse,
    UncertaintyVisualizationResponse,
    ConfidenceDashboard,
    VisualizationExportRequest,
    VisualizationExportResponse
)

router = APIRouter(prefix="/confidence", tags=["confidence"])

# RBAC instance
rbac = RBACMatrix()

@router.post("/gauge", response_model=GaugeVisualizationResponse)
async def create_confidence_gauge(
    request: GaugeVisualizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create real-time confidence gauge visualization
    Requires READ permission on DECISION resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.DECISION,
        Action.READ,
        context={"user_id": current_user.id, "patient_id": request.patient_id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to access confidence visualization"
        )
    
    try:
        visualizer = ConfidenceVisualizerService(db)
        audit_service = AuditService(db)
        
        # Create gauge visualization
        result = await visualizer.create_real_time_gauge(
            patient_id=request.patient_id,
            protocol_id=request.protocol_id,
            decision_point=request.decision_point
        )
        
        # Log the visualization access
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=current_user.id,
                resource_type="confidence_visualization",
                resource_id=f"{request.patient_id}_{request.protocol_id}",
                action="create_confidence_gauge",
                details={
                    "visualization_type": "gauge",
                    "patient_id": request.patient_id,
                    "protocol_id": request.protocol_id,
                    "decision_point": request.decision_point,
                    "confidence_score": result.get("confidence_score")
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.LOW
            )
        )
        
        return GaugeVisualizationResponse(
            chart_data=result["chart_data"],
            confidence_score=result["confidence_score"],
            threshold=result["threshold"],
            uncertainty=result["uncertainty"],
            factors=result["factors"],
            recommendations=result["recommendations"],
            metadata={
                "patient_id": request.patient_id,
                "protocol_id": request.protocol_id,
                "decision_point": request.decision_point,
                "timestamp": result["timestamp"]
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create confidence gauge: {str(e)}"
        )

@router.post("/trend", response_model=TrendVisualizationResponse)
async def create_confidence_trend(
    request: TrendVisualizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create historical confidence trend visualization
    Requires READ permission on DECISION resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.DECISION,
        Action.READ,
        context={"user_id": current_user.id, "patient_id": request.patient_id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to access confidence trend"
        )
    
    try:
        visualizer = ConfidenceVisualizerService(db)
        audit_service = AuditService(db)
        
        # Create trend visualization
        result = await visualizer.create_historical_trend(
            patient_id=request.patient_id,
            protocol_id=request.protocol_id,
            days_back=request.days_back
        )
        
        # Log the visualization access
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=current_user.id,
                resource_type="confidence_visualization",
                resource_id=f"{request.patient_id}_{request.protocol_id}",
                action="create_confidence_trend",
                details={
                    "visualization_type": "trend",
                    "patient_id": request.patient_id,
                    "protocol_id": request.protocol_id,
                    "days_back": request.days_back,
                    "data_points": result.get("data_points", 0)
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.LOW
            )
        )
        
        if "message" in result:
            return TrendVisualizationResponse(
                chart_data={"message": result["message"]},
                trend_statistics={"trend": "no_data"},
                data_points=0,
                date_range={"start": "", "end": ""},
                metadata={"patient_id": request.patient_id, "protocol_id": request.protocol_id}
            )
        
        return TrendVisualizationResponse(
            chart_data=result["chart_data"],
            trend_statistics=result["trend_statistics"],
            data_points=result["data_points"],
            date_range=result["date_range"],
            metadata={
                "patient_id": request.patient_id,
                "protocol_id": request.protocol_id,
                "days_back": request.days_back
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create confidence trend: {str(e)}"
        )

@router.post("/threshold-analysis", response_model=ThresholdAnalysisResponse)
async def create_threshold_analysis(
    request: VisualizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create confidence threshold analysis visualization
    Requires READ permission on DECISION resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.DECISION,
        Action.READ,
        context={"user_id": current_user.id, "patient_id": request.patient_id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to access threshold analysis"
        )
    
    try:
        visualizer = ConfidenceVisualizerService(db)
        audit_service = AuditService(db)
        
        # Create threshold analysis
        result = await visualizer.create_threshold_analysis(
            patient_id=request.patient_id,
            protocol_id=request.protocol_id
        )
        
        # Log the visualization access
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=current_user.id,
                resource_type="confidence_visualization",
                resource_id=f"{request.patient_id}_{request.protocol_id}",
                action="create_threshold_analysis",
                details={
                    "visualization_type": "threshold_analysis",
                    "patient_id": request.patient_id,
                    "protocol_id": request.protocol_id,
                    "total_decisions": result.get("total_decisions", 0)
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.LOW
            )
        )
        
        if "message" in result:
            return ThresholdAnalysisResponse(
                chart_data={"message": result["message"]},
                threshold_distribution={},
                decision_outcomes={},
                total_decisions=0,
                recommendations=["No data available for analysis"],
                metadata={"patient_id": request.patient_id, "protocol_id": request.protocol_id}
            )
        
        return ThresholdAnalysisResponse(
            chart_data=result["chart_data"],
            threshold_distribution=result["threshold_distribution"],
            decision_outcomes=result["decision_outcomes"],
            total_decisions=result["total_decisions"],
            recommendations=result["recommendations"],
            metadata={
                "patient_id": request.patient_id,
                "protocol_id": request.protocol_id
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create threshold analysis: {str(e)}"
        )

@router.post("/comparative", response_model=ComparativeAnalysisResponse)
async def create_comparative_analysis(
    request: ComparativeVisualizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create comparative confidence analysis across multiple patients
    Requires READ permission on DECISION resource for all patients
    """
    
    # Check permissions for all patients
    for patient_id in request.patient_ids:
        if not rbac.has_permission(
            current_user.role,
            Resource.DECISION,
            Action.READ,
            context={"user_id": current_user.id, "patient_id": patient_id}
        ):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions to access data for patient {patient_id}"
            )
    
    try:
        visualizer = ConfidenceVisualizerService(db)
        audit_service = AuditService(db)
        
        # Create comparative analysis
        result = await visualizer.create_comparative_analysis(
            patient_ids=request.patient_ids,
            protocol_id=request.protocol_id
        )
        
        # Log the visualization access
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=current_user.id,
                resource_type="confidence_visualization",
                resource_id=f"comparative_{request.protocol_id}",
                action="create_comparative_analysis",
                details={
                    "visualization_type": "comparative",
                    "patient_ids": request.patient_ids,
                    "protocol_id": request.protocol_id,
                    "comparison_type": request.comparison_type,
                    "patient_count": len(request.patient_ids)
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.MEDIUM
            )
        )
        
        if "message" in result:
            return ComparativeAnalysisResponse(
                chart_data={"message": result["message"]},
                patient_statistics={},
                comparison_analysis={"error": result["message"]},
                metadata={
                    "patient_ids": request.patient_ids,
                    "protocol_id": request.protocol_id
                }
            )
        
        return ComparativeAnalysisResponse(
            chart_data=result["chart_data"],
            patient_statistics=result["patient_statistics"],
            comparison_analysis=result["comparison_analysis"],
            metadata={
                "patient_ids": request.patient_ids,
                "protocol_id": request.protocol_id,
                "comparison_type": request.comparison_type
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create comparative analysis: {str(e)}"
        )

@router.post("/uncertainty", response_model=UncertaintyVisualizationResponse)
async def create_uncertainty_visualization(
    request: VisualizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create uncertainty bands visualization
    Requires READ permission on DECISION resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.DECISION,
        Action.READ,
        context={"user_id": current_user.id, "patient_id": request.patient_id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to access uncertainty visualization"
        )
    
    try:
        visualizer = ConfidenceVisualizerService(db)
        audit_service = AuditService(db)
        
        # Create uncertainty visualization
        result = await visualizer.create_uncertainty_visualization(
            patient_id=request.patient_id,
            protocol_id=request.protocol_id
        )
        
        # Log the visualization access
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=current_user.id,
                resource_type="confidence_visualization",
                resource_id=f"{request.patient_id}_{request.protocol_id}",
                action="create_uncertainty_visualization",
                details={
                    "visualization_type": "uncertainty_bands",
                    "patient_id": request.patient_id,
                    "protocol_id": request.protocol_id
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.LOW
            )
        )
        
        if "message" in result:
            return UncertaintyVisualizationResponse(
                chart_data={"message": result["message"]},
                uncertainty_analysis={"error": result["message"]},
                metadata={"patient_id": request.patient_id, "protocol_id": request.protocol_id}
            )
        
        return UncertaintyVisualizationResponse(
            chart_data=result["chart_data"],
            uncertainty_analysis=result["uncertainty_analysis"],
            metadata={
                "patient_id": request.patient_id,
                "protocol_id": request.protocol_id
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create uncertainty visualization: {str(e)}"
        )

@router.get("/dashboard/{patient_id}/{protocol_id}", response_model=ConfidenceDashboard)
async def get_confidence_dashboard(
    patient_id: str,
    protocol_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive confidence dashboard for patient/protocol
    Requires READ permission on DECISION resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.DECISION,
        Action.READ,
        context={"user_id": current_user.id, "patient_id": patient_id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to access confidence dashboard"
        )
    
    try:
        visualizer = ConfidenceVisualizerService(db)
        audit_service = AuditService(db)
        
        # Get current confidence metrics
        current_confidence = await visualizer._calculate_current_confidence(
            patient_id=patient_id,
            protocol_id=protocol_id,
            decision_point="current_status"
        )
        
        # Get recent history (simplified for now)
        from ..schemas.confidence import ConfidenceMetrics, ConfidenceHistory, ConfidenceFactorBreakdown
        
        dashboard = ConfidenceDashboard(
            current_metrics=ConfidenceMetrics(
                current_score=current_confidence.value,
                threshold=current_confidence.threshold,
                uncertainty=current_confidence.uncertainty,
                factors=current_confidence.factors,
                trend="stable",  # Would calculate from historical data
                stability=0.8   # Would calculate from historical data
            ),
            recent_history=[
                ConfidenceHistory(
                    timestamp=current_confidence.timestamp,
                    confidence_score=current_confidence.value,
                    decision_point="current_status",
                    factors=current_confidence.factors,
                    uncertainty=current_confidence.uncertainty
                )
            ],
            factor_breakdown=[
                ConfidenceFactorBreakdown(
                    factor=factor,
                    value=value,
                    weight=0.25,  # Would be configured
                    description=f"Factor: {factor}",
                    impact="positive" if value > 0.5 else "negative",
                    recommendations=[]
                )
                for factor, value in current_confidence.factors.items()
            ],
            alerts=[],
            recommendations=[]
        )
        
        # Log dashboard access
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=current_user.id,
                resource_type="confidence_dashboard",
                resource_id=f"{patient_id}_{protocol_id}",
                action="view_confidence_dashboard",
                details={
                    "patient_id": patient_id,
                    "protocol_id": protocol_id,
                    "confidence_score": current_confidence.value
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.LOW
            )
        )
        
        return dashboard
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get confidence dashboard: {str(e)}"
        )

@router.post("/export", response_model=VisualizationExportResponse)
async def export_visualization(
    request: VisualizationExportRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Export confidence visualization in specified format
    Requires READ permission on DECISION resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.DECISION,
        Action.EXPORT,
        context={"user_id": current_user.id, "patient_id": request.patient_id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to export visualizations"
        )
    
    try:
        # This would implement actual export functionality
        # For now, return placeholder
        
        audit_service = AuditService(db)
        
        # Log export request
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.DATA_EXPORT,
                user_id=current_user.id,
                resource_type="confidence_visualization",
                resource_id=f"{request.patient_id}_{request.protocol_id}",
                action="export_confidence_visualization",
                details={
                    "visualization_type": request.visualization_type.value,
                    "export_format": request.export_format,
                    "patient_id": request.patient_id,
                    "protocol_id": request.protocol_id
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.MEDIUM
            )
        )
        
        return VisualizationExportResponse(
            export_url=f"https://api.example.com/exports/conf_viz_{request.patient_id}.{request.export_format}",
            file_size=1048576,  # Placeholder
            expires_at=datetime.utcnow().replace(hour=23, minute=59, second=59),
            format=request.export_format
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export visualization: {str(e)}"
        )
