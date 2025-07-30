"""
Integrated Surgery Analyzer Module for Decision Precision in Surgery Platform

This module provides a comprehensive surgical case analysis system that integrates:
- ADCI framework for decision confidence
- FLOT Protocol impact assessment for gastric surgery
- Surgical risk assessment
- Outcome prediction
- Quality metrics calculation
- Precision decision support

The module follows HIPAA/GDPR compliance patterns with proper audit logging
and error handling with clinical context.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

from features.protocols.flot_analyzer import FLOTAnalyzer
from features.decisions.adci_engine import ADCIEngine
from features.analysis.impact_metrics import ImpactMetricsCalculator
from core.services.logger import get_logger, audit_log
from core.models.surgery_models import SurgicalCaseModel, SurgicalAnalysisResult
from core.utils.validation import validate_surgical_case

logger = get_logger(__name__)

class SurgicalRiskCalculator:
    """Calculates multi-dimensional surgical risk assessment."""
    
    def calculate_comprehensive_risk(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Multi-dimensional surgical risk calculation"""
        risk_components = {
            'cardiac_risk': self._calculate_cardiac_risk(patient_data),
            'pulmonary_risk': self._calculate_pulmonary_risk(patient_data),
            'renal_risk': self._calculate_renal_risk(patient_data),
            'metabolic_risk': self._calculate_metabolic_risk(patient_data),
            'oncologic_risk': self._calculate_oncologic_risk(patient_data),
            'procedural_risk': self._calculate_procedural_risk(patient_data)
        }
        
        # Weighted risk aggregation
        overall_risk = self._aggregate_risks(risk_components)
        
        return {
            'overall_risk_score': overall_risk,
            'risk_components': risk_components,
            'risk_category': self._categorize_risk(overall_risk),
            'mitigation_strategies': self._suggest_mitigation(risk_components),
            'confidence_interval': self._calculate_confidence_interval(overall_risk)
        }
    
    def _calculate_cardiac_risk(self, patient_data: Dict[str, Any]) -> float:
        """Calculate cardiac risk based on patient data."""
        # MVP implementation - to be enhanced with actual risk algorithms
        risk = 0.0
        
        if patient_data.get('age', 0) > 65:
            risk += 0.2
        
        if 'hypertension' in patient_data.get('comorbidities', []):
            risk += 0.3
            
        if 'coronary_artery_disease' in patient_data.get('comorbidities', []):
            risk += 0.5
            
        return min(risk, 1.0)  # Normalize to 0-1 scale
    
    def _calculate_pulmonary_risk(self, patient_data: Dict[str, Any]) -> float:
        """Calculate pulmonary risk based on patient data."""
        # MVP implementation - to be enhanced with actual risk algorithms
        risk = 0.0
        
        if patient_data.get('smoking_status') == 'current':
            risk += 0.4
            
        if 'copd' in patient_data.get('comorbidities', []):
            risk += 0.5
            
        if patient_data.get('fev1_fvc', 1.0) < 0.7:
            risk += 0.3
            
        return min(risk, 1.0)  # Normalize to 0-1 scale
    
    def _calculate_renal_risk(self, patient_data: Dict[str, Any]) -> float:
        """Calculate renal risk based on patient data."""
        # MVP implementation - to be enhanced with actual risk algorithms
        risk = 0.0
        
        creatinine = patient_data.get('lab_values', {}).get('creatinine', 1.0)
        if creatinine > 1.5:
            risk += 0.3
            
        if 'chronic_kidney_disease' in patient_data.get('comorbidities', []):
            risk += 0.4
            
        return min(risk, 1.0)  # Normalize to 0-1 scale
    
    def _calculate_metabolic_risk(self, patient_data: Dict[str, Any]) -> float:
        """Calculate metabolic risk based on patient data."""
        # MVP implementation - to be enhanced with actual risk algorithms
        risk = 0.0
        
        if patient_data.get('bmi', 25) > 30:
            risk += 0.2
            
        if 'diabetes' in patient_data.get('comorbidities', []):
            risk += 0.3
            
        return min(risk, 1.0)  # Normalize to 0-1 scale
    
    def _calculate_oncologic_risk(self, patient_data: Dict[str, Any]) -> float:
        """Calculate oncologic risk based on patient data."""
        # MVP implementation - to be enhanced with actual risk algorithms
        risk = 0.0
        
        tumor_stage = patient_data.get('tumor_stage', '')
        
        if 'T3' in tumor_stage or 'T4' in tumor_stage:
            risk += 0.3
            
        if 'N1' in tumor_stage or 'N2' in tumor_stage:
            risk += 0.3
            
        if 'M1' in tumor_stage:
            risk += 0.4
            
        return min(risk, 1.0)  # Normalize to 0-1 scale
    
    def _calculate_procedural_risk(self, patient_data: Dict[str, Any]) -> float:
        """Calculate procedure-specific risk based on surgery type."""
        # MVP implementation - to be enhanced with actual risk algorithms
        risk = 0.0
        
        if patient_data.get('surgical_approach') == 'open':
            risk += 0.2
            
        if patient_data.get('urgency') == 'emergency':
            risk += 0.4
            
        if patient_data.get('asa_score', 1) >= 3:
            risk += 0.3
            
        return min(risk, 1.0)  # Normalize to 0-1 scale
    
    def _aggregate_risks(self, risk_components: Dict[str, float]) -> float:
        """Aggregate individual risk components into overall risk score."""
        # Weighted average approach for MVP
        weights = {
            'cardiac_risk': 0.2,
            'pulmonary_risk': 0.2,
            'renal_risk': 0.1,
            'metabolic_risk': 0.1,
            'oncologic_risk': 0.2,
            'procedural_risk': 0.2
        }
        
        weighted_sum = sum(risk * weights[component] 
                           for component, risk in risk_components.items())
        
        return weighted_sum
    
    def _categorize_risk(self, overall_risk: float) -> str:
        """Categorize overall risk into risk levels."""
        if overall_risk < 0.2:
            return "LOW"
        elif overall_risk < 0.4:
            return "MODERATE"
        elif overall_risk < 0.7:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _suggest_mitigation(self, risk_components: Dict[str, float]) -> List[str]:
        """Suggest risk mitigation strategies based on identified risks."""
        strategies = []
        
        if risk_components.get('cardiac_risk', 0) > 0.3:
            strategies.append("Cardiac optimization prior to surgery")
            strategies.append("Consider cardiology consultation")
        
        if risk_components.get('pulmonary_risk', 0) > 0.3:
            strategies.append("Pulmonary function optimization")
            strategies.append("Smoking cessation if applicable")
        
        if risk_components.get('renal_risk', 0) > 0.3:
            strategies.append("Renal function monitoring")
            strategies.append("Nephrology consultation if necessary")
            
        # Add generic strategies
        strategies.append("Follow enhanced recovery protocol")
        strategies.append("Optimize nutritional status")
        
        return strategies
    
    def _calculate_confidence_interval(self, risk_score: float) -> Dict[str, float]:
        """Calculate confidence interval for risk prediction."""
        # Simplified implementation for MVP
        return {
            "lower_bound": max(0, risk_score - 0.1),
            "upper_bound": min(1.0, risk_score + 0.1)
        }


class OutcomePredictionEngine:
    """AI-powered surgical outcome prediction engine."""
    
    def __init__(self):
        # In MVP, we'll use simplified models
        # Future: Replace with actual ML models
        self.models = {
            'mortality': self._load_mortality_model(),
            'morbidity': self._load_morbidity_model(),
            'los': self._load_length_of_stay_model(),
            'readmission': self._load_readmission_model()
        }
    
    def _load_mortality_model(self):
        """Load the mortality prediction model."""
        # Placeholder for actual model loading
        # In MVP, return a simplified model class
        return SimplePredictionModel('mortality')
    
    def _load_morbidity_model(self):
        """Load the morbidity prediction model."""
        return SimplePredictionModel('morbidity')
    
    def _load_length_of_stay_model(self):
        """Load the length of stay prediction model."""
        return SimplePredictionModel('los')
    
    def _load_readmission_model(self):
        """Load the readmission prediction model."""
        return SimplePredictionModel('readmission')
    
    def _prepare_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize features for prediction."""
        # Extract relevant features for prediction
        features = {
            # Demographics
            'age': case_data.get('age', 65),
            'gender_code': 1 if case_data.get('gender') == 'male' else 0,
            'bmi': case_data.get('bmi', 25),
            
            # Clinical
            'asa_score': case_data.get('asa_score', 2),
            'emergency': 1 if case_data.get('urgency') == 'emergency' else 0,
            
            # Comorbidities (binary features)
            'has_diabetes': 1 if 'diabetes' in case_data.get('comorbidities', []) else 0,
            'has_hypertension': 1 if 'hypertension' in case_data.get('comorbidities', []) else 0,
            'has_cardiac': 1 if any(x in case_data.get('comorbidities', []) for x in 
                                 ['coronary_artery_disease', 'heart_failure']) else 0,
            'has_pulmonary': 1 if any(x in case_data.get('comorbidities', []) for x in 
                                    ['copd', 'asthma']) else 0,
            'has_renal': 1 if 'chronic_kidney_disease' in case_data.get('comorbidities', []) else 0,
            
            # Surgery specific
            'is_open_approach': 1 if case_data.get('surgical_approach') == 'open' else 0,
            'tumor_advanced': 1 if any(x in case_data.get('tumor_stage', '') 
                                    for x in ['T3', 'T4', 'N2', 'M1']) else 0
        }
        
        return features
    
    def predict_surgical_outcomes(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered surgical outcome prediction"""
        predictions = {}
        features = self._prepare_features(case_data)
        
        for outcome, model in self.models.items():
            prediction = model.predict(features)
            confidence = model.predict_proba(features)
            
            predictions[outcome] = {
                'prediction': prediction,
                'confidence': confidence,
                'risk_factors': self._identify_risk_factors(case_data, outcome)
            }
        
        return predictions
    
    def _identify_risk_factors(self, case_data: Dict[str, Any], outcome: str) -> List[str]:
        """Identify key risk factors contributing to outcome prediction."""
        risk_factors = []
        
        # Common risk factors for most outcomes
        if case_data.get('age', 0) > 75:
            risk_factors.append("Advanced age (>75)")
            
        if case_data.get('asa_score', 0) >= 3:
            risk_factors.append(f"High ASA score ({case_data.get('asa_score')})")
            
        if case_data.get('urgency') == 'emergency':
            risk_factors.append("Emergency surgery")
            
        # Outcome-specific risk factors
        if outcome == 'mortality':
            if 'heart_failure' in case_data.get('comorbidities', []):
                risk_factors.append("History of heart failure")
                
            if case_data.get('lab_values', {}).get('albumin', 4.0) < 3.0:
                risk_factors.append("Low albumin")
                
        elif outcome == 'morbidity':
            if case_data.get('bmi', 25) > 35:
                risk_factors.append("Severe obesity (BMI > 35)")
                
            if 'diabetes' in case_data.get('comorbidities', []):
                risk_factors.append("Diabetes")
                
        elif outcome == 'los':
            if case_data.get('frailty_score', 0) > 5:
                risk_factors.append("Frailty")
                
            if 'functional_dependency' in case_data.get('comorbidities', []):
                risk_factors.append("Functional dependency")
                
        elif outcome == 'readmission':
            if 'previous_readmission' in case_data.get('medical_history', []):
                risk_factors.append("Previous hospital readmission")
                
            if len(case_data.get('medications', [])) > 10:
                risk_factors.append("Polypharmacy")
                
        return risk_factors


class SimplePredictionModel:
    """Simple prediction model for MVP implementation."""
    
    def __init__(self, outcome_type: str):
        self.outcome_type = outcome_type
    
    def predict(self, features: Dict[str, Any]) -> Any:
        """Make a prediction based on features."""
        # Simple rule-based prediction for MVP
        if self.outcome_type == 'mortality':
            # Simple mortality risk
            if features.get('asa_score', 2) >= 4 or features.get('age', 65) > 85:
                return "high_risk"
            elif features.get('emergency', 0) == 1 and features.get('has_cardiac', 0) == 1:
                return "high_risk"
            else:
                return "standard_risk"
                
        elif self.outcome_type == 'morbidity':
            # Simple morbidity risk
            risk_score = 0
            risk_score += features.get('asa_score', 2) * 0.5
            risk_score += features.get('age', 65) / 20
            risk_score += features.get('has_diabetes', 0) * 1.0
            risk_score += features.get('emergency', 0) * 1.5
            
            if risk_score > 5:
                return "high_risk"
            elif risk_score > 3:
                return "moderate_risk"
            else:
                return "low_risk"
                
        elif self.outcome_type == 'los':
            # Predict length of stay in days
            base_los = 5  # Base LOS for average patient
            
            # Add days for risk factors
            base_los += features.get('asa_score', 2) - 2  # ASA score adjustment
            base_los += 3 if features.get('emergency', 0) == 1 else 0  # Emergency
            base_los += 2 if features.get('has_pulmonary', 0) == 1 else 0  # Pulmonary issues
            base_los += 2 if features.get('is_open_approach', 0) == 1 else 0  # Open surgery
            base_los += 1 if features.get('has_diabetes', 0) == 1 else 0  # Diabetes
            
            # Age adjustment (simplified)
            if features.get('age', 65) > 75:
                base_los += 2
            
            return base_los
            
        elif self.outcome_type == 'readmission':
            # Simple readmission risk
            risk_factors = 0
            risk_factors += 1 if features.get('has_cardiac', 0) == 1 else 0
            risk_factors += 1 if features.get('has_pulmonary', 0) == 1 else 0
            risk_factors += 1 if features.get('has_renal', 0) == 1 else 0
            risk_factors += 1 if features.get('age', 65) > 75 else 0
            
            if risk_factors >= 3:
                return "high_risk"
            elif risk_factors >= 1:
                return "moderate_risk"
            else:
                return "low_risk"
                
        return None
    
    def predict_proba(self, features: Dict[str, Any]) -> float:
        """Return prediction probability/confidence."""
        # Simplified confidence scores for MVP
        if self.outcome_type == 'mortality':
            base_confidence = 0.7
            # Adjust based on clear risk factors
            if features.get('asa_score', 2) >= 4:
                base_confidence += 0.1
            if features.get('age', 65) > 85:
                base_confidence += 0.1
            return min(base_confidence, 0.95)  # Cap at 95% confidence
            
        elif self.outcome_type == 'morbidity':
            return 0.75  # Fixed confidence for MVP
            
        elif self.outcome_type == 'los':
            return 0.8  # Fixed confidence for MVP
            
        elif self.outcome_type == 'readmission':
            return 0.65  # Fixed confidence for MVP
            
        return 0.5  # Default


class QualityMetricsEngine:
    """Engine for calculating surgery-specific quality metrics."""
    
    def calculate_quality_indicators(self, case_data: Dict[str, Any], 
                                    surgery_type: str) -> Dict[str, Any]:
        """Calculate surgery-specific quality metrics"""
        metrics = {}
        
        if surgery_type == "gastric_flot":
            metrics.update(self._gastric_quality_metrics(case_data))
        elif surgery_type == "colorectal_eras":
            metrics.update(self._colorectal_quality_metrics(case_data))
        elif surgery_type == "hepatobiliary":
            metrics.update(self._hepatobiliary_quality_metrics(case_data))
        
        # Universal quality metrics
        metrics.update({
            'time_to_surgery': self._calculate_time_to_surgery(case_data),
            'protocol_adherence': self._calculate_protocol_adherence(case_data),
            'patient_satisfaction_predicted': self._predict_satisfaction(case_data),
            'cost_effectiveness': self._calculate_cost_effectiveness(case_data)
        })
        
        return metrics
    
    def _gastric_quality_metrics(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate gastric surgery specific quality metrics."""
        metrics = {}
        
        # FLOT-specific metrics
        if 'flot_cycles_completed' in case_data:
            metrics['flot_completion_rate'] = min(1.0, case_data['flot_cycles_completed'] / 4)
            
        # Lymph node harvest quality metric
        if 'lymph_nodes_examined' in case_data:
            nodes_examined = case_data['lymph_nodes_examined']
            metrics['adequate_lymph_node_examination'] = 1.0 if nodes_examined >= 15 else (nodes_examined / 15)
            
        # R0 resection rate
        if 'resection_margin' in case_data:
            metrics['r0_resection_achieved'] = 1.0 if case_data['resection_margin'] == 'R0' else 0.0
            
        # Complication-specific metrics
        complications = case_data.get('complications', [])
        metrics['anastomotic_leak_rate'] = 1.0 if 'anastomotic_leak' in complications else 0.0
            
        return metrics
    
    def _colorectal_quality_metrics(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate colorectal surgery specific quality metrics."""
        # Placeholder for colorectal metrics in MVP
        return {
            'colorectal_quality_score': 0.85,  # Placeholder
            'eras_adherence': 0.9  # Placeholder
        }
    
    def _hepatobiliary_quality_metrics(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate hepatobiliary surgery specific quality metrics."""
        # Placeholder for hepatobiliary metrics in MVP
        return {
            'hepatobiliary_quality_score': 0.8,  # Placeholder
            'liver_function_preservation': 0.9  # Placeholder
        }
    
    def _calculate_time_to_surgery(self, case_data: Dict[str, Any]) -> float:
        """Calculate time from diagnosis to surgery metric."""
        # Placeholder implementation for MVP
        if 'diagnosis_date' in case_data and 'surgery_date' in case_data:
            # Calculate days between dates in a real implementation
            time_to_surgery = 21  # Placeholder value
            
            # Normalize to 0-1 scale, with 1 being optimal
            # Assuming 28 days as target for non-emergency cases
            if case_data.get('urgency') != 'emergency':
                return min(1.0, 28 / max(1, time_to_surgery))
            else:
                # For emergency, shorter is better (target 24 hours)
                return min(1.0, 1 / max(0.1, time_to_surgery))
        
        return 0.8  # Default placeholder
    
    def _calculate_protocol_adherence(self, case_data: Dict[str, Any]) -> float:
        """Calculate adherence to clinical protocol."""
        # Placeholder implementation for MVP
        # In real implementation, check each protocol element
        return 0.85  # Default placeholder
    
    def _predict_satisfaction(self, case_data: Dict[str, Any]) -> float:
        """Predict patient satisfaction based on case factors."""
        # Placeholder implementation for MVP
        # In real implementation, use ML model
        return 0.75  # Default placeholder
    
    def _calculate_cost_effectiveness(self, case_data: Dict[str, Any]) -> float:
        """Calculate cost effectiveness of the surgical case."""
        # Placeholder implementation for MVP
        return 0.8  # Default placeholder


class ProtocolManager:
    """Manages and selects optimal surgical protocols based on case data."""
    
    def select_optimal_protocol(self, case_data: Dict[str, Any], 
                               surgery_type: str) -> Dict[str, Any]:
        """Select and customize optimal surgical protocol."""
        protocol_info = {}
        
        if surgery_type == "gastric_flot":
            protocol_info = self._select_gastric_protocol(case_data)
        elif surgery_type == "colorectal_eras":
            protocol_info = self._select_colorectal_protocol(case_data)
        elif surgery_type == "hepatobiliary":
            protocol_info = self._select_hepatobiliary_protocol(case_data)
        elif surgery_type == "emergency":
            protocol_info = self._select_emergency_protocol(case_data)
        else:
            protocol_info = self._select_general_protocol(case_data)
            
        # Add common protocol elements
        protocol_info.update({
            'vte_prophylaxis': self._recommend_vte_prophylaxis(case_data),
            'antibiotic_prophylaxis': self._recommend_antibiotics(case_data),
            'nutritional_support': self._recommend_nutrition(case_data)
        })
        
        return protocol_info
    
    def _select_gastric_protocol(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Select protocol for gastric surgery."""
        protocol = {
            'recommended_protocol': 'FLOT-Enhanced Recovery',
            'protocol_elements': [
                'Preoperative FLOT chemotherapy',
                'Minimally invasive approach if feasible',
                'Enhanced recovery pathway',
                'Early mobilization',
                'Early oral intake'
            ],
            'contraindications': []
        }
        
        # Check for protocol modifications
        comorbidities = case_data.get('comorbidities', [])
        
        if 'diabetes' in comorbidities:
            protocol['protocol_elements'].append('Tight glycemic control')
        
        if case_data.get('bmi', 25) > 30:
            protocol['protocol_elements'].append('Bariatric considerations')
        
        if case_data.get('asa_score', 2) >= 3:
            protocol['protocol_elements'].append('High-risk monitoring pathway')
        
        # Check for contraindications
        if 'severe_liver_disease' in comorbidities:
            protocol['contraindications'].append('FLOT may require dose reduction')
        
        return protocol
    
    def _select_colorectal_protocol(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Select protocol for colorectal surgery."""
        # Placeholder for MVP
        return {
            'recommended_protocol': 'Enhanced Recovery After Surgery (ERAS)',
            'protocol_elements': [
                'Preoperative carbohydrate loading',
                'Minimally invasive approach',
                'No routine nasogastric tubes',
                'Early mobilization',
                'Early oral intake'
            ],
            'contraindications': []
        }
    
    def _select_hepatobiliary_protocol(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Select protocol for hepatobiliary surgery."""
        # Placeholder for MVP
        return {
            'recommended_protocol': 'Enhanced Liver Recovery Pathway',
            'protocol_elements': [
                'Preoperative liver optimization',
                'Intraoperative low CVP',
                'Selective vascular occlusion',
                'Goal-directed fluid therapy',
                'Early mobilization'
            ],
            'contraindications': []
        }
    
    def _select_emergency_protocol(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Select protocol for emergency surgery."""
        # Placeholder for MVP
        return {
            'recommended_protocol': 'Emergency Surgery Pathway',
            'protocol_elements': [
                'Rapid assessment',
                'Early resuscitation',
                'Damage control strategy if needed',
                'Early antibiotics',
                'Intensive monitoring'
            ],
            'contraindications': []
        }
    
    def _select_general_protocol(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Select protocol for general surgery."""
        # Placeholder for MVP
        return {
            'recommended_protocol': 'Standard Surgical Care',
            'protocol_elements': [
                'Preoperative risk assessment',
                'Standard preoperative preparation',
                'Evidence-based perioperative care',
                'Early mobilization',
                'Pain management protocol'
            ],
            'contraindications': []
        }
    
    def _recommend_vte_prophylaxis(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend VTE prophylaxis based on patient risk."""
        # Simple implementation for MVP
        high_risk = (case_data.get('age', 0) > 60 or 
                    case_data.get('bmi', 0) > 30 or
                    'cancer' in case_data.get('comorbidities', []) or
                    'previous_vte' in case_data.get('medical_history', []))
        
        if high_risk:
            return {
                'recommendation': 'Extended pharmacological prophylaxis',
                'duration': '28 days',
                'notes': 'Consider extended prophylaxis given high VTE risk'
            }
        else:
            return {
                'recommendation': 'Standard pharmacological prophylaxis',
                'duration': 'Until discharge',
                'notes': 'Combine with mechanical prophylaxis'
            }
    
    def _recommend_antibiotics(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend antibiotic prophylaxis."""
        # Simple implementation for MVP
        return {
            'recommendation': 'Standard surgical prophylaxis',
            'timing': 'Within 60 minutes before incision',
            'notes': 'Redose for procedures >4 hours'
        }
    
    def _recommend_nutrition(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend nutritional support based on patient status."""
        # Simple implementation for MVP
        if case_data.get('albumin', 4.0) < 3.0 or case_data.get('weight_loss_percentage', 0) > 10:
            return {
                'recommendation': 'Intensive nutritional support',
                'type': 'Preoperative immunonutrition',
                'notes': 'Consider delaying surgery for nutritional optimization if feasible'
            }
        else:
            return {
                'recommendation': 'Standard nutritional protocol',
                'type': 'Early oral intake',
                'notes': 'Regular diet as tolerated within 24 hours post-surgery'
            }
        

class IntegratedSurgeryAnalyzer:
    """
    Comprehensive surgical case analysis system that integrates multiple
    specialized analyzers for surgical decision support.
    """
    
    def __init__(self):
        """Initialize the integrated surgery analyzer with all required components."""
        self.flot_analyzer = FLOTAnalyzer()
        self.risk_calculator = SurgicalRiskCalculator()
        self.outcome_predictor = OutcomePredictionEngine()
        self.quality_metrics = QualityMetricsEngine()
        self.protocol_manager = ProtocolManager()
        self.impact_metrics = ImpactMetricsCalculator()
        
        # Logging and audit setup
        self.logger = logging.getLogger(__name__)
    
    async def analyze_surgical_case(self, case_data: Dict[str, Any], 
                                   surgery_type: str) -> Dict[str, Any]:
        """
        Perform a comprehensive surgical case analysis.
        
        Args:
            case_data: Dictionary containing all case and patient data
            surgery_type: Type of surgery (gastric_flot, colorectal_eras, etc.)
            
        Returns:
            Dictionary containing complete analysis results
        """
        try:
            # Start audit logging
            audit_log(f"Starting surgery analysis for case {case_data.get('case_id')}", 
                    "ANALYSIS_START", case_data.get('case_id'))
            
            # Core analysis components
            risk_assessment = self.risk_calculator.calculate_comprehensive_risk(case_data)
            protocol_recommendations = self.protocol_manager.select_optimal_protocol(case_data, surgery_type)
            outcome_predictions = self.outcome_predictor.predict_surgical_outcomes(case_data)
            quality_indicators = self.quality_metrics.calculate_quality_indicators(case_data, surgery_type)
            
            # Surgery-specific analysis
            surgery_specific_analysis = {}
            
            if surgery_type == "gastric_flot":
                # Use FLOT analyzer for gastric cases
                gastric_analysis = await self._analyze_gastric_case(case_data)
                surgery_specific_analysis["gastric_analysis"] = gastric_analysis
            
            # Generate decision support information
            decision_support = self._generate_recommendations(
                case_data, 
                risk_assessment,
                protocol_recommendations,
                outcome_predictions
            )
            
            # Assemble comprehensive results
            results = {
                'case_id': case_data.get('id', case_data.get('case_id')),
                'surgery_type': surgery_type,
                'analysis_timestamp': datetime.now().isoformat(),
                'risk_assessment': risk_assessment,
                'protocol_recommendations': protocol_recommendations,
                'outcome_predictions': outcome_predictions,
                'quality_indicators': quality_indicators,
                'surgery_specific_analysis': surgery_specific_analysis,
                'decision_support': decision_support,
                'confidence_score': self._calculate_overall_confidence(
                    risk_assessment, outcome_predictions
                )
            }
            
            # Complete audit logging
            audit_log(f"Completed surgery analysis for case {case_data.get('case_id')}", 
                     "ANALYSIS_COMPLETE", case_data.get('case_id'))
            
            return results
            
        except Exception as e:
            # Log error with appropriate clinical context
            self.logger.error(f"Surgery analysis failed for case {case_data.get('case_id')}: {str(e)}")
            audit_log(f"Surgery analysis error: {str(e)}", 
                     "ANALYSIS_ERROR", case_data.get('case_id'))
            raise e
    
    async def _analyze_gastric_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform gastric surgery specific analysis using FLOT analyzer."""
        # Call FLOT analyzer
        flot_analysis = await self.flot_analyzer.analyze_gastric_surgery_case(case_data)
        
        # Enhance with surgical specific elements
        surgical_enhancements = {
            'preoperative_optimization': self._optimize_preop_care(case_data),
            'surgical_planning': self._plan_surgical_approach(case_data),
            'perioperative_management': self._manage_periop_care(case_data),
            'postoperative_pathway': self._design_postop_pathway(case_data),
            'complication_prevention': self._prevent_complications(case_data)
        }
        
        # Combine FLOT analysis with surgical enhancements
        return {**flot_analysis, **surgical_enhancements}
    
    def _optimize_preop_care(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize preoperative care for gastric surgery patients."""
        # MVP implementation
        return {
            "nutrition_optimization": "Enhanced protein supplementation recommended",
            "cardiopulmonary_optimization": "Incentive spirometry and smoking cessation",
            "anemia_management": "Iron supplementation if Hb < 12g/dL" 
        }
    
    def _plan_surgical_approach(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Plan optimal surgical approach based on patient factors."""
        # MVP implementation
        approach = "laparoscopic"
        
        # Check for factors that might suggest open approach
        if patient_data.get('bmi', 0) > 35:
            approach = "open"
            rationale = "High BMI may complicate laparoscopic approach"
        elif 'prior_major_abdominal_surgery' in patient_data.get('medical_history', []):
            approach = "open"
            rationale = "Prior abdominal surgery with potential adhesions"
        elif 'T4' in patient_data.get('tumor_stage', ''):
            approach = "open"
            rationale = "Advanced T-stage with potential adjacent organ involvement"
        else:
            rationale = "Standard case suitable for minimally invasive approach"
            
        return {
            "recommended_approach": approach,
            "rationale": rationale,
            "technical_considerations": [
                "D2 lymphadenectomy required",
                "Consider placement of jejunostomy tube",
                "Assess for peritoneal metastases"
            ]
        }
    
    def _manage_periop_care(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage perioperative care for gastric surgery."""
        # MVP implementation
        return {
            "fluid_management": "Goal-directed therapy recommended",
            "pain_control": "Multimodal approach with regional anesthesia",
            "glucose_management": "Target 140-180 mg/dL",
            "monitoring_requirements": "Standard monitoring plus arterial line"
        }
    
    def _design_postop_pathway(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Design postoperative pathway for gastric surgery."""
        # MVP implementation
        if patient_data.get('asa_score', 2) >= 3:
            level_of_care = "ICU"
            rationale = "High ASA score indicates need for intensive monitoring"
        else:
            level_of_care = "Regular ward with enhanced monitoring"
            rationale = "Standard case without high-risk features"
            
        return {
            "level_of_care": level_of_care,
            "rationale": rationale,
            "mobilization_plan": "Ambulation within 24 hours",
            "nutrition_plan": "Clear liquids by POD 1, advance as tolerated",
            "drain_management": "Remove when output < 50 mL/day and amylase normal",
            "discharge_criteria": [
                "Tolerating oral diet",
                "Pain controlled with oral medications",
                "Ambulating independently",
                "Normal vital signs"
            ]
        }
    
    def _prevent_complications(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Develop complication prevention strategies."""
        # MVP implementation
        strategies = [
            "Enhanced VTE prophylaxis",
            "Strict glycemic control"
        ]
        
        if 'diabetes' in patient_data.get('comorbidities', []):
            strategies.append("Endocrinology consultation")
            
        if patient_data.get('age', 0) > 75:
            strategies.append("Geriatric consultation for frailty assessment")
            
        if 'copd' in patient_data.get('comorbidities', []):
            strategies.append("Pulmonary optimization with bronchodilators")
            
        return {
            "prevention_strategies": strategies,
            "high_vigilance_areas": [
                "Anastomotic integrity",
                "Respiratory function",
                "Nutritional status"
            ]
        }
    
    def _generate_recommendations(self, case_data: Dict[str, Any], 
                                 risk_assessment: Dict[str, Any],
                                 protocol: Dict[str, Any],
                                 outcomes: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable clinical recommendations based on analysis."""
        recommendations = []
        alerts = []
        next_steps = []
        
        # Risk-based recommendations
        if risk_assessment.get('risk_category') in ['HIGH', 'CRITICAL']:
            recommendations.append("Consider preoperative risk mitigation strategies")
            recommendations.append("Multidisciplinary team discussion recommended")
            alerts.append(f"High-risk case ({risk_assessment.get('risk_category')})")
            
        # Add mitigation strategies from risk assessment
        for strategy in risk_assessment.get('mitigation_strategies', []):
            recommendations.append(strategy)
        
        # Protocol recommendations
        recommendations.append(f"Follow {protocol.get('recommended_protocol')} protocol")
        
        # Check for contraindications
        for contraindication in protocol.get('contraindications', []):
            alerts.append(f"Protocol contraindication: {contraindication}")
        
        # Outcome-based recommendations
        mortality_risk = outcomes.get('mortality', {}).get('prediction')
        if mortality_risk == "high_risk":
            alerts.append("Elevated mortality risk detected")
            recommendations.append("Consider ICU monitoring postoperatively")
            
        # LOS recommendations
        los_prediction = outcomes.get('los', {}).get('prediction')
        if los_prediction and los_prediction > 7:
            recommendations.append(f"Prepare for extended LOS (predicted: {los_prediction} days)")
            recommendations.append("Early discharge planning and care coordination")
        
        # Standard next steps
        next_steps = [
            "Complete preoperative assessment",
            "Secure OR time and resources",
            "Confirm adherence to protocol elements",
            "Schedule follow-up for 2 weeks post-discharge"
        ]
        
        return {
            "recommendations": recommendations,
            "alerts": alerts,
            "next_steps": next_steps
        }
    
    def _calculate_overall_confidence(self, risk_assessment: Dict[str, Any],
                                     outcome_predictions: Dict[str, Any]) -> float:
        """Calculate overall confidence score for the analysis."""
        # Simple implementation for MVP
        # Future: More sophisticated confidence calculation
        
        # Base confidence of 0.8
        confidence = 0.8
        
        # Adjust based on outcome prediction confidence
        outcome_confidence = outcome_predictions.get('mortality', {}).get('confidence', 0.7)
        confidence = (confidence + outcome_confidence) / 2
        
        return confidence
    
    async def generate_surgical_recommendations(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable recommendations based on analysis results."""
        # For MVP, simply return the decision support section
        return analysis_results.get('decision_support', {})
    
    async def calculate_surgical_impact(self, case_data: Dict[str, Any], 
                                      analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate impact metrics for the surgical case."""
        # Use impact metrics calculator
        impact_metrics_result = await self.impact_metrics.calculate_metrics(
            case_data, 
            analysis_type="surgical"
        )
        
        # Enhance with surgery-specific impact metrics
        surgery_impact = {
            "estimated_cost_savings": self._calculate_cost_savings(case_data, analysis_results),
            "estimated_complication_reduction": self._estimate_complication_reduction(analysis_results),
            "estimated_quality_improvement": self._estimate_quality_improvement(analysis_results)
        }
        
        # Combine with standard impact metrics
        return {**impact_metrics_result, **surgery_impact}
    
    def _calculate_cost_savings(self, case_data: Dict[str, Any], 
                               analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate estimated cost savings from protocol adherence."""
        # MVP implementation
        return {
            "baseline_cost": 15000,  # Placeholder
            "optimized_cost": 12500,  # Placeholder
            "savings_percentage": 16.7,
            "confidence_interval": [10.2, 23.5]
        }
    
    def _estimate_complication_reduction(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate complication reduction from protocol adherence."""
        # MVP implementation
        return {
            "baseline_complication_rate": 0.25,  # Placeholder
            "expected_complication_rate": 0.18,  # Placeholder
            "reduction_percentage": 28,
            "confidence_interval": [15, 40]
        }
    
    def _estimate_quality_improvement(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate quality improvement from protocol adherence."""
        # MVP implementation
        return {
            "quality_score_improvement": 0.15,  # Placeholder
            "key_metrics_improved": [
                "Length of stay",
                "Readmission rate",
                "Patient satisfaction"
            ]
        }


class IntegratedSurgeryAnalyzer:
    """
    Integrated Surgery Analyzer for Decision Precision in Surgery Platform
    
    This class provides a comprehensive analysis framework that integrates:
    - ADCI decision engine
    - FLOT protocol impact assessment
    - Surgical risk assessment
    - Outcome prediction
    - Precision decision support
    """
    
    def __init__(self):
        """Initialize the integrated surgery analyzer with its components"""
        self.risk_calculator = SurgicalRiskCalculator()
        self.adci_engine = ADCIEngine()
        self.flot_analyzer = FLOTAnalyzer()
        self.impact_calculator = ImpactMetricsCalculator()
        self.version = "3.0-Precision"
        
        logger.info(f"Integrated Surgery Analyzer initialized with version {self.version}")
    
    async def analyze_case(self, case_data: Dict[str, Any], 
                     collaboration_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Public API for case analysis with collaboration support.
        
        Args:
            case_data: Dictionary containing all case and patient data
            collaboration_context: Optional collaboration context for collaborative analysis
            
        Returns:
            Dictionary containing complete analysis results with collaboration data
        """
        # Determine surgery type from case data
        surgery_type = case_data.get('surgery_type', 'gastric_flot')
        
        # Perform base surgical analysis
        analysis_result = await self.analyze_surgical_case(case_data, surgery_type)
        
        # Add collaboration data if provided
        if collaboration_context:
            analysis_result['collaboration'] = {
                'context': collaboration_context,
                'collaborative_insights': self._generate_collaborative_insights(
                    analysis_result, collaboration_context
                ),
                'consensus_status': collaboration_context.get('consensus_level', 'pending'),
                'collaboration_timestamp': datetime.now().isoformat()
            }
            
            # Log collaboration with audit trail
            audit_log(
                action="collaborative_analysis",
                resource_type="surgical_case",
                resource_id=case_data.get('case_id'),
                details=f"Collaborative analysis performed with {len(collaboration_context.get('contributors', []))} contributors"
            )
            
        return analysis_result
        
    def _generate_collaborative_insights(self, analysis_result: Dict[str, Any], 
                                         collaboration_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights based on collaborative input."""
        # MVP implementation
        return {
            "contributors": collaboration_context.get("contributors", []),
            "key_discussion_points": [],
            "consensus_recommendations": [],
            "follow_up_actions": []
        }
