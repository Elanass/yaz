"""
Confidence Score Visualizer Service
Real-time ADCI confidence visualization and threshold analysis
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
import base64
from sqlalchemy.orm import Session
import structlog

from ..engines.adci_engine import ADCIEngine
from ..engines.decision_engine import DecisionEngine
from ..db.models import DecisionLog, Patient, ClinicalProtocol
from ..schemas.confidence import ConfidenceVisualization, ConfidenceMetrics

logger = structlog.get_logger(__name__)

class VisualizationType(str, Enum):
    """Types of confidence visualizations"""
    REAL_TIME_GAUGE = "real_time_gauge"
    HISTORICAL_TREND = "historical_trend"
    THRESHOLD_ANALYSIS = "threshold_analysis"
    DECISION_TREE = "decision_tree"
    COMPARATIVE_CHART = "comparative_chart"
    HEATMAP = "heatmap"
    RISK_PROFILE = "risk_profile"
    UNCERTAINTY_BANDS = "uncertainty_bands"

class ConfidenceThreshold(str, Enum):
    """Predefined confidence thresholds"""
    VERY_LOW = "very_low"      # < 0.3
    LOW = "low"                # 0.3 - 0.5
    MODERATE = "moderate"      # 0.5 - 0.7
    HIGH = "high"              # 0.7 - 0.85
    VERY_HIGH = "very_high"    # > 0.85

@dataclass
class ConfidenceScore:
    """Structured confidence score data"""
    value: float
    threshold: ConfidenceThreshold
    uncertainty: float
    factors: Dict[str, float]
    timestamp: datetime
    decision_context: Dict[str, Any]
    
    def __post_init__(self):
        self.threshold = self._calculate_threshold(self.value)
    
    def _calculate_threshold(self, value: float) -> ConfidenceThreshold:
        """Calculate threshold category from confidence value"""
        if value < 0.3:
            return ConfidenceThreshold.VERY_LOW
        elif value < 0.5:
            return ConfidenceThreshold.LOW
        elif value < 0.7:
            return ConfidenceThreshold.MODERATE
        elif value < 0.85:
            return ConfidenceThreshold.HIGH
        else:
            return ConfidenceThreshold.VERY_HIGH

class ConfidenceVisualizerService:
    """Advanced confidence score visualization service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.adci_engine = ADCIEngine()
        self.decision_engine = DecisionEngine()
        
        # Visualization configuration
        self.color_scheme = {
            ConfidenceThreshold.VERY_LOW: "#d32f2f",     # Red
            ConfidenceThreshold.LOW: "#f57c00",          # Orange
            ConfidenceThreshold.MODERATE: "#fbc02d",     # Yellow
            ConfidenceThreshold.HIGH: "#388e3c",         # Green
            ConfidenceThreshold.VERY_HIGH: "#1976d2"     # Blue
        }
        
        self.threshold_values = {
            ConfidenceThreshold.VERY_LOW: (0.0, 0.3),
            ConfidenceThreshold.LOW: (0.3, 0.5),
            ConfidenceThreshold.MODERATE: (0.5, 0.7),
            ConfidenceThreshold.HIGH: (0.7, 0.85),
            ConfidenceThreshold.VERY_HIGH: (0.85, 1.0)
        }
    
    async def create_real_time_gauge(
        self,
        patient_id: str,
        protocol_id: str,
        decision_point: str
    ) -> Dict[str, Any]:
        """Create real-time confidence gauge visualization"""
        
        try:
            # Get current confidence score
            confidence_data = await self._calculate_current_confidence(
                patient_id, protocol_id, decision_point
            )
            
            # Create gauge chart
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = confidence_data.value,
                delta = {'reference': 0.7, 'valueformat': '.2%'},
                title = {'text': f"ADCI Confidence - {decision_point}"},
                gauge = {
                    'axis': {'range': [None, 1.0], 'tickformat': '.1%'},
                    'bar': {'color': self._get_threshold_color(confidence_data.threshold)},
                    'steps': [
                        {'range': [0, 0.3], 'color': "rgba(211, 47, 47, 0.3)"},
                        {'range': [0.3, 0.5], 'color': "rgba(245, 124, 0, 0.3)"},
                        {'range': [0.5, 0.7], 'color': "rgba(251, 192, 45, 0.3)"},
                        {'range': [0.7, 0.85], 'color': "rgba(56, 142, 60, 0.3)"},
                        {'range': [0.85, 1.0], 'color': "rgba(25, 118, 210, 0.3)"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0.7
                    }
                }
            ))
            
            fig.update_layout(
                title=f"Confidence Score: {confidence_data.value:.1%}",
                height=400,
                font={'size': 16}
            )
            
            # Convert to JSON for API response
            chart_json = fig.to_json()
            
            return {
                "visualization_type": VisualizationType.REAL_TIME_GAUGE,
                "chart_data": chart_json,
                "confidence_score": confidence_data.value,
                "threshold": confidence_data.threshold.value,
                "uncertainty": confidence_data.uncertainty,
                "factors": confidence_data.factors,
                "recommendations": self._generate_recommendations(confidence_data),
                "timestamp": confidence_data.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to create real-time gauge", error=str(e))
            raise
    
    async def create_historical_trend(
        self,
        patient_id: str,
        protocol_id: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Create historical confidence trend visualization"""
        
        try:
            # Get historical decision logs
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days_back)
            
            decisions = self.db.query(DecisionLog).filter(
                DecisionLog.patient_id == patient_id,
                DecisionLog.protocol_id == protocol_id,
                DecisionLog.created_at >= start_date,
                DecisionLog.created_at <= end_date
            ).order_by(DecisionLog.created_at).all()
            
            if not decisions:
                return {"message": "No historical data available"}
            
            # Extract confidence scores and timestamps
            timestamps = [d.created_at for d in decisions]
            confidence_scores = [d.confidence_score for d in decisions]
            decision_points = [d.decision_point for d in decisions]
            
            # Create trend chart
            fig = go.Figure()
            
            # Add confidence line
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=confidence_scores,
                mode='lines+markers',
                name='Confidence Score',
                line=dict(color='#1976d2', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{text}</b><br>' +
                             'Confidence: %{y:.1%}<br>' +
                             'Time: %{x}<br>' +
                             '<extra></extra>',
                text=decision_points
            ))
            
            # Add threshold lines
            fig.add_hline(y=0.7, line_dash="dash", line_color="green", 
                         annotation_text="Recommended Threshold (70%)")
            fig.add_hline(y=0.5, line_dash="dash", line_color="orange", 
                         annotation_text="Caution Threshold (50%)")
            fig.add_hline(y=0.3, line_dash="dash", line_color="red", 
                         annotation_text="Critical Threshold (30%)")
            
            # Add confidence bands
            fig.add_hrect(y0=0.7, y1=1.0, fillcolor="rgba(56, 142, 60, 0.1)", 
                         line_width=0, annotation_text="High Confidence")
            fig.add_hrect(y0=0.5, y1=0.7, fillcolor="rgba(251, 192, 45, 0.1)", 
                         line_width=0, annotation_text="Moderate Confidence")
            fig.add_hrect(y0=0.0, y1=0.5, fillcolor="rgba(211, 47, 47, 0.1)", 
                         line_width=0, annotation_text="Low Confidence")
            
            fig.update_layout(
                title=f"Confidence Score Trend - {days_back} Days",
                xaxis_title="Date",
                yaxis_title="Confidence Score",
                yaxis=dict(tickformat='.0%', range=[0, 1]),
                height=500,
                showlegend=True
            )
            
            # Calculate trend statistics
            trend_stats = self._calculate_trend_statistics(confidence_scores, timestamps)
            
            return {
                "visualization_type": VisualizationType.HISTORICAL_TREND,
                "chart_data": fig.to_json(),
                "trend_statistics": trend_stats,
                "data_points": len(confidence_scores),
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error("Failed to create historical trend", error=str(e))
            raise
    
    async def create_threshold_analysis(
        self,
        patient_id: str,
        protocol_id: str
    ) -> Dict[str, Any]:
        """Create threshold analysis visualization"""
        
        try:
            # Get all decisions for this patient/protocol
            decisions = self.db.query(DecisionLog).filter(
                DecisionLog.patient_id == patient_id,
                DecisionLog.protocol_id == protocol_id
            ).all()
            
            if not decisions:
                return {"message": "No decision data available"}
            
            # Categorize by confidence thresholds
            threshold_counts = {threshold.value: 0 for threshold in ConfidenceThreshold}
            threshold_decisions = {threshold.value: [] for threshold in ConfidenceThreshold}
            
            for decision in decisions:
                confidence = ConfidenceScore(
                    value=decision.confidence_score,
                    uncertainty=decision.uncertainty or 0.1,
                    factors={},
                    timestamp=decision.created_at,
                    decision_context=decision.decision_context or {}
                )
                
                threshold_counts[confidence.threshold.value] += 1
                threshold_decisions[confidence.threshold.value].append(decision)
            
            # Create threshold distribution chart
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Threshold Distribution', 'Decision Outcomes', 
                               'Confidence vs Time', 'Factor Analysis'),
                specs=[[{"type": "pie"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "bar"}]]
            )
            
            # Pie chart for threshold distribution
            fig.add_trace(go.Pie(
                values=list(threshold_counts.values()),
                labels=list(threshold_counts.keys()),
                name="Threshold Distribution",
                marker_colors=[self.color_scheme[ConfidenceThreshold(k)] 
                              for k in threshold_counts.keys()]
            ), row=1, col=1)
            
            # Bar chart for decision outcomes
            outcomes = {}
            for decision in decisions:
                outcome = decision.decision_outcome or "pending"
                outcomes[outcome] = outcomes.get(outcome, 0) + 1
            
            fig.add_trace(go.Bar(
                x=list(outcomes.keys()),
                y=list(outcomes.values()),
                name="Decision Outcomes",
                marker_color='#1976d2'
            ), row=1, col=2)
            
            # Scatter plot for confidence vs time
            timestamps = [d.created_at for d in decisions]
            confidence_scores = [d.confidence_score for d in decisions]
            
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=confidence_scores,
                mode='markers',
                name="Confidence Over Time",
                marker=dict(
                    color=confidence_scores,
                    colorscale='RdYlBu',
                    size=8,
                    colorbar=dict(title="Confidence")
                )
            ), row=2, col=1)
            
            fig.update_layout(height=800, title_text="Confidence Threshold Analysis")
            
            return {
                "visualization_type": VisualizationType.THRESHOLD_ANALYSIS,
                "chart_data": fig.to_json(),
                "threshold_distribution": threshold_counts,
                "decision_outcomes": outcomes,
                "total_decisions": len(decisions),
                "recommendations": self._analyze_threshold_patterns(threshold_counts, decisions)
            }
            
        except Exception as e:
            logger.error("Failed to create threshold analysis", error=str(e))
            raise
    
    async def create_comparative_analysis(
        self,
        patient_ids: List[str],
        protocol_id: str
    ) -> Dict[str, Any]:
        """Create comparative confidence analysis for multiple patients"""
        
        try:
            patient_data = {}
            
            for patient_id in patient_ids:
                decisions = self.db.query(DecisionLog).filter(
                    DecisionLog.patient_id == patient_id,
                    DecisionLog.protocol_id == protocol_id
                ).all()
                
                if decisions:
                    avg_confidence = np.mean([d.confidence_score for d in decisions])
                    patient_data[patient_id] = {
                        "average_confidence": avg_confidence,
                        "decision_count": len(decisions),
                        "confidence_scores": [d.confidence_score for d in decisions]
                    }
            
            if not patient_data:
                return {"message": "No data available for comparison"}
            
            # Create comparative chart
            fig = go.Figure()
            
            # Box plot for confidence distribution
            for patient_id, data in patient_data.items():
                fig.add_trace(go.Box(
                    y=data["confidence_scores"],
                    name=f"Patient {patient_id}",
                    boxpoints='all',
                    jitter=0.3,
                    pointpos=-1.8
                ))
            
            fig.update_layout(
                title="Confidence Score Distribution by Patient",
                yaxis_title="Confidence Score",
                yaxis=dict(tickformat='.0%'),
                height=500
            )
            
            # Calculate comparison statistics
            comparison_stats = self._calculate_comparison_statistics(patient_data)
            
            return {
                "visualization_type": VisualizationType.COMPARATIVE_CHART,
                "chart_data": fig.to_json(),
                "patient_statistics": patient_data,
                "comparison_analysis": comparison_stats
            }
            
        except Exception as e:
            logger.error("Failed to create comparative analysis", error=str(e))
            raise
    
    async def create_uncertainty_visualization(
        self,
        patient_id: str,
        protocol_id: str
    ) -> Dict[str, Any]:
        """Create uncertainty bands visualization"""
        
        try:
            decisions = self.db.query(DecisionLog).filter(
                DecisionLog.patient_id == patient_id,
                DecisionLog.protocol_id == protocol_id
            ).order_by(DecisionLog.created_at).all()
            
            if not decisions:
                return {"message": "No decision data available"}
            
            timestamps = [d.created_at for d in decisions]
            confidence_scores = [d.confidence_score for d in decisions]
            uncertainties = [d.uncertainty or 0.1 for d in decisions]
            
            # Calculate confidence bands
            upper_bounds = [conf + unc for conf, unc in zip(confidence_scores, uncertainties)]
            lower_bounds = [max(0, conf - unc) for conf, unc in zip(confidence_scores, uncertainties)]
            
            fig = go.Figure()
            
            # Add uncertainty bands
            fig.add_trace(go.Scatter(
                x=timestamps + timestamps[::-1],
                y=upper_bounds + lower_bounds[::-1],
                fill='toself',
                fillcolor='rgba(25, 118, 210, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Uncertainty Band',
                hoverinfo="skip"
            ))
            
            # Add confidence line
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=confidence_scores,
                mode='lines+markers',
                name='Confidence Score',
                line=dict(color='#1976d2', width=3),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title="Confidence with Uncertainty Bands",
                xaxis_title="Date",
                yaxis_title="Confidence Score",
                yaxis=dict(tickformat='.0%', range=[0, 1]),
                height=500
            )
            
            return {
                "visualization_type": VisualizationType.UNCERTAINTY_BANDS,
                "chart_data": fig.to_json(),
                "uncertainty_analysis": {
                    "average_uncertainty": np.mean(uncertainties),
                    "max_uncertainty": max(uncertainties),
                    "uncertainty_trend": self._calculate_uncertainty_trend(uncertainties)
                }
            }
            
        except Exception as e:
            logger.error("Failed to create uncertainty visualization", error=str(e))
            raise
    
    async def _calculate_current_confidence(
        self,
        patient_id: str,
        protocol_id: str,
        decision_point: str
    ) -> ConfidenceScore:
        """Calculate current confidence score for patient/protocol"""
        
        # Get patient data
        patient = self.db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not patient:
            raise ValueError(f"Patient not found: {patient_id}")
        
        # Get protocol
        protocol = self.db.query(ClinicalProtocol).filter(
            ClinicalProtocol.id == protocol_id
        ).first()
        if not protocol:
            raise ValueError(f"Protocol not found: {protocol_id}")
        
        # Calculate ADCI score
        adci_result = await self.adci_engine.calculate_adci_score(patient, protocol, decision_point)
        
        # Extract confidence factors
        factors = {
            "data_completeness": adci_result.get("data_completeness", 0.5),
            "evidence_quality": adci_result.get("evidence_quality", 0.5),
            "clinical_alignment": adci_result.get("clinical_alignment", 0.5),
            "protocol_adherence": adci_result.get("protocol_adherence", 0.5)
        }
        
        return ConfidenceScore(
            value=adci_result["confidence_score"],
            uncertainty=adci_result.get("uncertainty", 0.1),
            factors=factors,
            timestamp=datetime.utcnow(),
            decision_context={
                "patient_id": patient_id,
                "protocol_id": protocol_id,
                "decision_point": decision_point
            }
        )
    
    def _get_threshold_color(self, threshold: ConfidenceThreshold) -> str:
        """Get color for confidence threshold"""
        return self.color_scheme.get(threshold, "#757575")
    
    def _generate_recommendations(self, confidence_data: ConfidenceScore) -> List[str]:
        """Generate recommendations based on confidence score"""
        recommendations = []
        
        if confidence_data.threshold == ConfidenceThreshold.VERY_LOW:
            recommendations.extend([
                "⚠️ Very low confidence - Consider gathering additional data",
                "🔍 Review patient eligibility criteria",
                "📞 Consult with multidisciplinary team"
            ])
        elif confidence_data.threshold == ConfidenceThreshold.LOW:
            recommendations.extend([
                "⚡ Low confidence - Additional assessment recommended",
                "📊 Consider additional diagnostic tests",
                "👥 Peer consultation may be beneficial"
            ])
        elif confidence_data.threshold == ConfidenceThreshold.MODERATE:
            recommendations.extend([
                "✅ Moderate confidence - Proceed with caution",
                "📋 Monitor closely for changes",
                "🔄 Regular reassessment recommended"
            ])
        elif confidence_data.threshold in [ConfidenceThreshold.HIGH, ConfidenceThreshold.VERY_HIGH]:
            recommendations.extend([
                "🎯 High confidence - Proceed with treatment",
                "📈 Continue monitoring per protocol",
                "✨ Consider as reference case for similar patients"
            ])
        
        # Factor-specific recommendations
        for factor, value in confidence_data.factors.items():
            if value < 0.4:
                if factor == "data_completeness":
                    recommendations.append("📝 Consider collecting additional patient data")
                elif factor == "evidence_quality":
                    recommendations.append("📚 Review latest evidence and guidelines")
                elif factor == "clinical_alignment":
                    recommendations.append("⚕️ Verify clinical indicators and contraindications")
                elif factor == "protocol_adherence":
                    recommendations.append("📋 Review protocol compliance requirements")
        
        return recommendations
    
    def _calculate_trend_statistics(self, scores: List[float], timestamps: List[datetime]) -> Dict[str, Any]:
        """Calculate trend statistics for confidence scores"""
        if len(scores) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate linear trend
        x = np.arange(len(scores))
        slope, intercept = np.polyfit(x, scores, 1)
        
        # Calculate volatility
        volatility = np.std(scores)
        
        # Determine trend direction
        if slope > 0.01:
            trend_direction = "improving"
        elif slope < -0.01:
            trend_direction = "declining"
        else:
            trend_direction = "stable"
        
        return {
            "trend_direction": trend_direction,
            "slope": float(slope),
            "volatility": float(volatility),
            "average_confidence": float(np.mean(scores)),
            "min_confidence": float(min(scores)),
            "max_confidence": float(max(scores)),
            "latest_confidence": float(scores[-1]) if scores else 0.0
        }
    
    def _analyze_threshold_patterns(
        self, 
        threshold_counts: Dict[str, int], 
        decisions: List
    ) -> List[str]:
        """Analyze patterns in confidence thresholds"""
        recommendations = []
        total_decisions = sum(threshold_counts.values())
        
        if total_decisions == 0:
            return ["No decisions available for analysis"]
        
        # High confidence percentage
        high_conf_pct = (threshold_counts.get("high", 0) + 
                        threshold_counts.get("very_high", 0)) / total_decisions
        
        if high_conf_pct > 0.7:
            recommendations.append("✅ Excellent confidence pattern - consistently high scores")
        elif high_conf_pct < 0.3:
            recommendations.append("⚠️ Low confidence pattern - consider protocol review")
        
        # Check for consistency
        max_threshold = max(threshold_counts.values())
        if max_threshold / total_decisions > 0.8:
            recommendations.append("📊 Consistent confidence levels across decisions")
        else:
            recommendations.append("🔄 Variable confidence levels - monitor for patterns")
        
        return recommendations
    
    def _calculate_comparison_statistics(self, patient_data: Dict) -> Dict[str, Any]:
        """Calculate statistics for patient comparison"""
        all_scores = []
        for data in patient_data.values():
            all_scores.extend(data["confidence_scores"])
        
        if not all_scores:
            return {"error": "No data for comparison"}
        
        return {
            "overall_average": float(np.mean(all_scores)),
            "overall_std": float(np.std(all_scores)),
            "best_performing_patient": max(
                patient_data.keys(), 
                key=lambda k: patient_data[k]["average_confidence"]
            ),
            "most_consistent_patient": min(
                patient_data.keys(),
                key=lambda k: np.std(patient_data[k]["confidence_scores"])
            ),
            "patient_count": len(patient_data),
            "total_decisions": sum(data["decision_count"] for data in patient_data.values())
        }
    
    def _calculate_uncertainty_trend(self, uncertainties: List[float]) -> str:
        """Calculate trend in uncertainty values"""
        if len(uncertainties) < 2:
            return "insufficient_data"
        
        x = np.arange(len(uncertainties))
        slope, _ = np.polyfit(x, uncertainties, 1)
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
