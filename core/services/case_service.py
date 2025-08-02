"""
Unified Case Service for the Healthcare Cases PWA
Handles all case-related operations in a single, efficient service
"""

from typing import Dict, Any, List, Optional

from feature.analysis.impact_metrics import ImpactMetricsAnalyzer
from feature.decisions.adci_engine import ADCIEngine
from core.services.logger import get_logger

logger = get_logger(__name__)

class CaseService:
    """
    Unified case processing service that coordinates analysis and decision support
    """
    def __init__(self):
        self.impact_metrics = ImpactMetricsAnalyzer()
        self.decision_engine = ADCIEngine()
        logger.info("CaseService initialized with impact metrics and ADCI engine")

    def process_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unified case processing pipeline for gastric cases
        
        Args:
            case_data: Dictionary containing patient and clinical data
            
        Returns:
            Dictionary with analysis results, decisions and recommendations
        """
        # Validate input data
        if not self._validate_case_data(case_data):
            logger.error("Invalid case data format")
            return {"error": "Invalid case data format", "status": "failed"}
        
        try:
            # Process clinical data
            clinical_data = self._extract_clinical_data(case_data)
            
            # Run impact analysis
            impact_results = self.impact_metrics.analyze_surgical_outcomes(
                clinical_data, 
                procedure_type=case_data.get("procedure_type", "gastrectomy")
            )
            
            # Get decision recommendations
            adci_recommendations = self.decision_engine.generate_recommendations(clinical_data)
            
            # Calculate confidence intervals
            confidence_data = self._calculate_confidence_intervals(impact_results, adci_recommendations)
            
            # Compile the final results
            results = {
                "case_id": case_data.get("case_id", "unknown"),
                "impact_analysis": impact_results,
                "recommendations": adci_recommendations,
                "confidence": confidence_data,
                "status": "success"
            }
            
            logger.info(f"Case processed successfully: {case_data.get('case_id', 'unknown')}")
            return results
            
        except Exception as e:
            logger.error(f"Error processing case: {str(e)}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def _validate_case_data(self, case_data: Dict[str, Any]) -> bool:
        """Validate the case data format"""
        required_fields = ["patient_data", "clinical_data"]
        return all(field in case_data for field in required_fields)
    
    def _extract_clinical_data(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize clinical data"""
        patient_data = case_data.get("patient_data", {})
        clinical_data = case_data.get("clinical_data", {})
        
        # Combine patient and clinical data
        return {
            **patient_data,
            **clinical_data,
            "pre_post_data": case_data.get("pre_post_data", []),
            "cohort": case_data.get("cohort", [])
        }
    
    def _calculate_confidence_intervals(self, 
                                        impact_results: Dict[str, Any], 
                                        recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence intervals for the results"""
        # Simple implementation for MVP
        response_rate = impact_results.get("effectiveness", {}).get("response_rate", 0)
        total = impact_results.get("effectiveness", {}).get("total", 0)
        
        # Basic confidence calculation (placeholder for actual statistical CI)
        confidence_level = 0.8 if total > 20 else 0.6 if total > 10 else 0.4
        
        return {
            "confidence_level": confidence_level,
            "sample_size": total,
            "notes": "Confidence based on sample size and response consistency"
        }
