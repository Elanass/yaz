"""
Hypothesis Simulator Service
Interactive "what-if" analysis for clinical decision support
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import copy
import numpy as np
from sqlalchemy.orm import Session
import structlog

from ..engines.adci_engine import ADCIEngine
from ..engines.decision_engine import DecisionEngine
from ..engines.flot_engine import FLOTEngine
from ..db.models import Patient, ClinicalProtocol, DecisionLog
from ..schemas.simulation import SimulationScenario, SimulationResult

logger = structlog.get_logger(__name__)

class ParameterType(str, Enum):
    """Types of parameters that can be modified in simulations"""
    CLINICAL = "clinical"          # Lab values, vital signs, scores
    DEMOGRAPHIC = "demographic"    # Age, gender, comorbidities
    TREATMENT = "treatment"        # Drug dosages, protocols
    TEMPORAL = "temporal"          # Time-based factors
    ENVIRONMENTAL = "environmental" # Hospital, team factors

class SimulationOutcome(str, Enum):
    """Possible simulation outcomes"""
    IMPROVED = "improved"
    UNCHANGED = "unchanged"
    WORSENED = "worsened"
    CONTRAINDICATED = "contraindicated"
    REQUIRES_MONITORING = "requires_monitoring"

@dataclass
class Parameter:
    """Simulation parameter definition"""
    name: str
    parameter_type: ParameterType
    current_value: Union[float, int, str, bool]
    possible_values: List[Union[float, int, str, bool]]
    unit: Optional[str] = None
    description: str = ""
    clinical_significance: str = ""
    normal_range: Optional[Tuple[float, float]] = None
    
    def __post_init__(self):
        if self.current_value not in self.possible_values:
            self.possible_values.append(self.current_value)

@dataclass
class SimulationScenarioData:
    """Complete simulation scenario"""
    scenario_id: str
    patient_id: str
    protocol_id: str
    base_parameters: Dict[str, Parameter]
    modified_parameters: Dict[str, Any]
    simulation_type: str
    description: str
    created_by: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_effective_parameters(self) -> Dict[str, Any]:
        """Get combined base and modified parameters"""
        effective = {}
        for name, param in self.base_parameters.items():
            effective[name] = self.modified_parameters.get(name, param.current_value)
        return effective

class HypothesisSimulatorService:
    """Advanced hypothesis simulation service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.adci_engine = ADCIEngine()
        self.decision_engine = DecisionEngine()
        self.flot_engine = FLOTEngine()
        
        # Simulation configuration
        self.simulation_types = {
            "parameter_sweep": self._run_parameter_sweep,
            "outcome_prediction": self._run_outcome_prediction,
            "protocol_comparison": self._run_protocol_comparison,
            "temporal_analysis": self._run_temporal_analysis,
            "sensitivity_analysis": self._run_sensitivity_analysis
        }
    
    async def create_simulation_scenario(
        self,
        patient_id: str,
        protocol_id: str,
        simulation_type: str,
        description: str,
        created_by: Optional[int] = None
    ) -> SimulationScenarioData:
        """Create a new simulation scenario with baseline parameters"""
        
        try:
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
            
            # Extract baseline parameters
            base_parameters = self._extract_patient_parameters(patient)
            
            # Generate scenario ID
            scenario_id = f"SIM_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{patient_id[:8]}"
            
            scenario = SimulationScenarioData(
                scenario_id=scenario_id,
                patient_id=patient_id,
                protocol_id=protocol_id,
                base_parameters=base_parameters,
                modified_parameters={},
                simulation_type=simulation_type,
                description=description,
                created_by=created_by
            )
            
            logger.info(
                "Simulation scenario created",
                scenario_id=scenario_id,
                patient_id=patient_id,
                simulation_type=simulation_type
            )
            
            return scenario
            
        except Exception as e:
            logger.error("Failed to create simulation scenario", error=str(e))
            raise
    
    async def run_simulation(
        self,
        scenario: SimulationScenarioData,
        modifications: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run simulation with specified parameter modifications"""
        
        try:
            # Update scenario with modifications
            scenario.modified_parameters.update(modifications)
            
            # Get simulation function
            simulation_func = self.simulation_types.get(scenario.simulation_type)
            if not simulation_func:
                raise ValueError(f"Unknown simulation type: {scenario.simulation_type}")
            
            # Run simulation
            result = await simulation_func(scenario)
            
            # Add metadata
            result.update({
                "scenario_id": scenario.scenario_id,
                "simulation_type": scenario.simulation_type,
                "modifications": modifications,
                "timestamp": datetime.utcnow().isoformat(),
                "parameters_modified": len(modifications)
            })
            
            logger.info(
                "Simulation completed",
                scenario_id=scenario.scenario_id,
                simulation_type=scenario.simulation_type,
                outcome=result.get("outcome", "unknown")
            )
            
            return result
            
        except Exception as e:
            logger.error("Simulation failed", scenario_id=scenario.scenario_id, error=str(e))
            raise
    
    async def _run_parameter_sweep(self, scenario: SimulationScenarioData) -> Dict[str, Any]:
        """Run parameter sweep simulation"""
        
        results = []
        modified_params = scenario.modified_parameters
        
        # For each modified parameter, test different values
        for param_name, new_value in modified_params.items():
            if param_name not in scenario.base_parameters:
                continue
                
            param = scenario.base_parameters[param_name]
            
            # Test the new value
            test_parameters = scenario.get_effective_parameters()
            test_parameters[param_name] = new_value
            
            # Calculate outcomes
            baseline_outcome = await self._calculate_outcome(scenario, scenario.get_effective_parameters())
            modified_outcome = await self._calculate_outcome(scenario, test_parameters)
            
            # Compare outcomes
            comparison = self._compare_outcomes(baseline_outcome, modified_outcome)
            
            results.append({
                "parameter": param_name,
                "original_value": param.current_value,
                "modified_value": new_value,
                "baseline_confidence": baseline_outcome["confidence_score"],
                "modified_confidence": modified_outcome["confidence_score"],
                "confidence_change": modified_outcome["confidence_score"] - baseline_outcome["confidence_score"],
                "outcome_change": comparison["outcome"],
                "clinical_impact": comparison["clinical_impact"],
                "recommendations": comparison["recommendations"]
            })
        
        # Overall analysis
        overall_impact = self._analyze_overall_impact(results)
        
        return {
            "simulation_type": "parameter_sweep",
            "individual_results": results,
            "overall_impact": overall_impact,
            "outcome": self._determine_simulation_outcome(results),
            "confidence_summary": {
                "min_confidence": min(r["modified_confidence"] for r in results) if results else 0,
                "max_confidence": max(r["modified_confidence"] for r in results) if results else 0,
                "avg_confidence": np.mean([r["modified_confidence"] for r in results]) if results else 0
            }
        }
    
    async def _run_outcome_prediction(self, scenario: SimulationScenarioData) -> Dict[str, Any]:
        """Run outcome prediction simulation"""
        
        # Get effective parameters
        parameters = scenario.get_effective_parameters()
        
        # Calculate current outcome
        outcome = await self._calculate_outcome(scenario, parameters)
        
        # Predict different time horizons
        predictions = {}
        time_horizons = [30, 90, 180, 365]  # days
        
        for days in time_horizons:
            # Simulate parameter evolution over time
            evolved_params = self._evolve_parameters(parameters, days)
            predicted_outcome = await self._calculate_outcome(scenario, evolved_params)
            
            predictions[f"{days}_days"] = {
                "confidence_score": predicted_outcome["confidence_score"],
                "treatment_recommendation": predicted_outcome["treatment_recommendation"],
                "risk_factors": predicted_outcome["risk_factors"],
                "monitoring_requirements": predicted_outcome.get("monitoring_requirements", [])
            }
        
        return {
            "simulation_type": "outcome_prediction",
            "current_outcome": outcome,
            "predicted_outcomes": predictions,
            "outcome": SimulationOutcome.REQUIRES_MONITORING.value,
            "time_horizons": time_horizons,
            "confidence_trend": self._calculate_confidence_trend(predictions)
        }
    
    async def _run_protocol_comparison(self, scenario: SimulationScenarioData) -> Dict[str, Any]:
        """Compare outcomes across different protocols"""
        
        # Get available protocols for comparison
        protocols = self.db.query(ClinicalProtocol).filter(
            ClinicalProtocol.indication == "gastric_cancer"  # Filter by relevant indication
        ).all()
        
        protocol_results = []
        parameters = scenario.get_effective_parameters()
        
        for protocol in protocols:
            # Calculate outcome for this protocol
            temp_scenario = copy.deepcopy(scenario)
            temp_scenario.protocol_id = str(protocol.id)
            
            outcome = await self._calculate_outcome(temp_scenario, parameters)
            
            protocol_results.append({
                "protocol_id": str(protocol.id),
                "protocol_name": protocol.name,
                "protocol_type": protocol.protocol_type,
                "confidence_score": outcome["confidence_score"],
                "treatment_recommendation": outcome["treatment_recommendation"],
                "estimated_efficacy": outcome.get("estimated_efficacy", 0.5),
                "safety_profile": outcome.get("safety_profile", "moderate"),
                "contraindications": outcome.get("contraindications", [])
            })
        
        # Rank protocols by confidence score
        protocol_results.sort(key=lambda x: x["confidence_score"], reverse=True)
        
        # Analysis
        best_protocol = protocol_results[0] if protocol_results else None
        current_protocol_result = next(
            (p for p in protocol_results if p["protocol_id"] == scenario.protocol_id),
            None
        )
        
        return {
            "simulation_type": "protocol_comparison",
            "protocol_results": protocol_results,
            "best_protocol": best_protocol,
            "current_protocol": current_protocol_result,
            "outcome": self._determine_protocol_outcome(best_protocol, current_protocol_result),
            "recommendations": self._generate_protocol_recommendations(protocol_results)
        }
    
    async def _run_temporal_analysis(self, scenario: SimulationScenarioData) -> Dict[str, Any]:
        """Analyze temporal factors and optimal timing"""
        
        parameters = scenario.get_effective_parameters()
        
        # Analyze different timing scenarios
        timing_scenarios = [
            {"delay_days": 0, "description": "Immediate treatment"},
            {"delay_days": 7, "description": "1 week delay"},
            {"delay_days": 14, "description": "2 week delay"},
            {"delay_days": 30, "description": "1 month delay"}
        ]
        
        timing_results = []
        
        for timing in timing_scenarios:
            # Modify parameters based on delay
            delayed_params = self._apply_treatment_delay(parameters, timing["delay_days"])
            outcome = await self._calculate_outcome(scenario, delayed_params)
            
            timing_results.append({
                **timing,
                "confidence_score": outcome["confidence_score"],
                "estimated_outcome": outcome.get("estimated_outcome", "unknown"),
                "risk_increase": max(0, timing["delay_days"] * 0.01),  # Simple risk model
                "urgency_score": self._calculate_urgency_score(delayed_params)
            })
        
        # Find optimal timing
        optimal_timing = max(timing_results, key=lambda x: x["confidence_score"] - x["risk_increase"])
        
        return {
            "simulation_type": "temporal_analysis",
            "timing_results": timing_results,
            "optimal_timing": optimal_timing,
            "outcome": "requires_monitoring" if optimal_timing["delay_days"] > 0 else "improved",
            "urgency_assessment": self._assess_treatment_urgency(timing_results)
        }
    
    async def _run_sensitivity_analysis(self, scenario: SimulationScenarioData) -> Dict[str, Any]:
        """Analyze sensitivity to parameter changes"""
        
        parameters = scenario.get_effective_parameters()
        sensitivity_results = []
        
        # Test sensitivity for each parameter
        for param_name, param in scenario.base_parameters.items():
            if param.parameter_type == ParameterType.CLINICAL and param.normal_range:
                # Test parameter at different percentiles
                test_values = self._generate_test_values(param)
                param_sensitivity = []
                
                for test_value in test_values:
                    test_params = parameters.copy()
                    test_params[param_name] = test_value
                    
                    outcome = await self._calculate_outcome(scenario, test_params)
                    
                    param_sensitivity.append({
                        "value": test_value,
                        "confidence_score": outcome["confidence_score"],
                        "deviation_from_baseline": abs(test_value - param.current_value)
                    })
                
                # Calculate sensitivity score
                confidence_variance = np.var([ps["confidence_score"] for ps in param_sensitivity])
                
                sensitivity_results.append({
                    "parameter": param_name,
                    "sensitivity_score": float(confidence_variance),
                    "impact_category": self._categorize_sensitivity(confidence_variance),
                    "test_results": param_sensitivity,
                    "recommendations": self._generate_sensitivity_recommendations(
                        param_name, confidence_variance
                    )
                })
        
        # Sort by sensitivity score
        sensitivity_results.sort(key=lambda x: x["sensitivity_score"], reverse=True)
        
        return {
            "simulation_type": "sensitivity_analysis",
            "sensitivity_results": sensitivity_results,
            "most_sensitive_parameters": sensitivity_results[:3],
            "outcome": "requires_monitoring",
            "monitoring_priorities": [r["parameter"] for r in sensitivity_results[:5]]
        }
    
    async def _calculate_outcome(
        self,
        scenario: SimulationScenarioData,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate clinical outcome for given parameters"""
        
        try:
            # Create simulated patient data
            simulated_patient_data = self._create_simulated_patient(
                scenario.patient_id, parameters
            )
            
            # Get protocol
            protocol = self.db.query(ClinicalProtocol).filter(
                ClinicalProtocol.id == scenario.protocol_id
            ).first()
            
            if not protocol:
                raise ValueError(f"Protocol not found: {scenario.protocol_id}")
            
            # Calculate ADCI score
            adci_result = await self.adci_engine.calculate_adci_score(
                simulated_patient_data, protocol, "simulation"
            )
            
            # Get treatment recommendation
            treatment_recommendation = await self.decision_engine.get_treatment_recommendation(
                simulated_patient_data, protocol
            )
            
            return {
                "confidence_score": adci_result["confidence_score"],
                "treatment_recommendation": treatment_recommendation.get("recommendation", "unknown"),
                "risk_factors": adci_result.get("risk_factors", []),
                "estimated_efficacy": adci_result.get("estimated_efficacy", 0.5),
                "safety_profile": treatment_recommendation.get("safety_profile", "moderate"),
                "contraindications": treatment_recommendation.get("contraindications", []),
                "monitoring_requirements": treatment_recommendation.get("monitoring", [])
            }
            
        except Exception as e:
            logger.error("Failed to calculate outcome", error=str(e))
            # Return default outcome
            return {
                "confidence_score": 0.5,
                "treatment_recommendation": "requires_evaluation",
                "risk_factors": ["simulation_error"],
                "estimated_efficacy": 0.0,
                "safety_profile": "unknown",
                "contraindications": [],
                "monitoring_requirements": []
            }
    
    def _extract_patient_parameters(self, patient: Patient) -> Dict[str, Parameter]:
        """Extract modifiable parameters from patient data"""
        
        parameters = {}
        
        # Demographic parameters
        if patient.date_of_birth:
            age = (datetime.utcnow() - patient.date_of_birth).days // 365
            parameters["age"] = Parameter(
                name="age",
                parameter_type=ParameterType.DEMOGRAPHIC,
                current_value=age,
                possible_values=list(range(max(18, age-10), age+10)),
                unit="years",
                description="Patient age",
                clinical_significance="Age affects treatment tolerance and efficacy"
            )
        
        # Clinical parameters from biomarkers
        if patient.biomarkers:
            for biomarker, value in patient.biomarkers.items():
                if isinstance(value, (int, float)):
                    parameters[f"biomarker_{biomarker}"] = Parameter(
                        name=f"biomarker_{biomarker}",
                        parameter_type=ParameterType.CLINICAL,
                        current_value=value,
                        possible_values=self._generate_biomarker_range(biomarker, value),
                        description=f"Biomarker: {biomarker}",
                        clinical_significance=f"Clinical significance of {biomarker}"
                    )
        
        # Performance status
        if patient.ecog_score is not None:
            parameters["ecog_score"] = Parameter(
                name="ecog_score",
                parameter_type=ParameterType.CLINICAL,
                current_value=patient.ecog_score,
                possible_values=[0, 1, 2, 3, 4],
                description="ECOG Performance Status",
                clinical_significance="Performance status affects treatment eligibility",
                normal_range=(0, 2)
            )
        
        return parameters
    
    def _generate_biomarker_range(self, biomarker: str, current_value: float) -> List[float]:
        """Generate realistic range for biomarker values"""
        
        # Common biomarker ranges (simplified)
        ranges = {
            "hemoglobin": (8.0, 18.0),
            "albumin": (2.5, 5.0),
            "creatinine": (0.5, 3.0),
            "cea": (0, 20),
            "ca19_9": (0, 100)
        }
        
        if biomarker.lower() in ranges:
            min_val, max_val = ranges[biomarker.lower()]
        else:
            # Generic range around current value
            min_val = current_value * 0.5
            max_val = current_value * 1.5
        
        # Generate values
        step = (max_val - min_val) / 10
        return [round(min_val + i * step, 2) for i in range(11)]
    
    def _create_simulated_patient(self, patient_id: str, parameters: Dict[str, Any]) -> object:
        """Create simulated patient object with modified parameters"""
        
        # Get original patient
        patient = self.db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not patient:
            raise ValueError(f"Patient not found: {patient_id}")
        
        # Create copy and modify parameters
        simulated_patient = copy.deepcopy(patient)
        
        for param_name, value in parameters.items():
            if param_name == "age":
                # Modify birth date to achieve target age
                target_age = int(value)
                simulated_patient.date_of_birth = datetime.utcnow() - timedelta(days=target_age*365)
            elif param_name == "ecog_score":
                simulated_patient.ecog_score = int(value)
            elif param_name.startswith("biomarker_"):
                biomarker_name = param_name.replace("biomarker_", "")
                if not simulated_patient.biomarkers:
                    simulated_patient.biomarkers = {}
                simulated_patient.biomarkers[biomarker_name] = value
        
        return simulated_patient
    
    def _compare_outcomes(self, baseline: Dict[str, Any], modified: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two outcome scenarios"""
        
        confidence_diff = modified["confidence_score"] - baseline["confidence_score"]
        
        if confidence_diff > 0.1:
            outcome = SimulationOutcome.IMPROVED.value
            clinical_impact = "Significant improvement expected"
        elif confidence_diff > 0.05:
            outcome = SimulationOutcome.IMPROVED.value
            clinical_impact = "Moderate improvement expected"
        elif confidence_diff < -0.1:
            outcome = SimulationOutcome.WORSENED.value
            clinical_impact = "Significant deterioration expected"
        elif confidence_diff < -0.05:
            outcome = SimulationOutcome.WORSENED.value
            clinical_impact = "Moderate deterioration expected"
        else:
            outcome = SimulationOutcome.UNCHANGED.value
            clinical_impact = "Minimal change expected"
        
        recommendations = []
        if confidence_diff > 0.05:
            recommendations.append("Consider implementing this parameter change")
        elif confidence_diff < -0.05:
            recommendations.append("Avoid this parameter change")
        else:
            recommendations.append("Monitor closely if change is made")
        
        return {
            "outcome": outcome,
            "clinical_impact": clinical_impact,
            "confidence_difference": confidence_diff,
            "recommendations": recommendations
        }
    
    def _analyze_overall_impact(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall impact of all parameter changes"""
        
        if not results:
            return {"impact": "no_changes", "confidence_change": 0}
        
        total_confidence_change = sum(r["confidence_change"] for r in results)
        avg_confidence_change = total_confidence_change / len(results)
        
        positive_changes = [r for r in results if r["confidence_change"] > 0]
        negative_changes = [r for r in results if r["confidence_change"] < 0]
        
        return {
            "total_confidence_change": total_confidence_change,
            "average_confidence_change": avg_confidence_change,
            "positive_changes": len(positive_changes),
            "negative_changes": len(negative_changes),
            "most_impactful_parameter": max(results, key=lambda x: abs(x["confidence_change"]))["parameter"],
            "overall_recommendation": "implement" if avg_confidence_change > 0.05 else "monitor"
        }
    
    def _determine_simulation_outcome(self, results: List[Dict[str, Any]]) -> str:
        """Determine overall simulation outcome"""
        
        if not results:
            return SimulationOutcome.UNCHANGED.value
        
        avg_change = np.mean([r["confidence_change"] for r in results])
        
        if avg_change > 0.1:
            return SimulationOutcome.IMPROVED.value
        elif avg_change < -0.1:
            return SimulationOutcome.WORSENED.value
        else:
            return SimulationOutcome.REQUIRES_MONITORING.value
    
    def _evolve_parameters(self, parameters: Dict[str, Any], days: int) -> Dict[str, Any]:
        """Simulate parameter evolution over time"""
        
        evolved = parameters.copy()
        
        # Simple evolution model (would be more sophisticated in practice)
        for param_name, value in parameters.items():
            if param_name == "ecog_score" and isinstance(value, (int, float)):
                # ECOG may worsen over time without treatment
                degradation_rate = 0.001 * days  # Simple model
                evolved[param_name] = min(4, value + degradation_rate)
            elif "biomarker" in param_name and isinstance(value, (int, float)):
                # Biomarkers may change over time
                change_rate = np.random.normal(0, 0.1) * days / 30  # Monthly variation
                evolved[param_name] = max(0, value * (1 + change_rate))
        
        return evolved
    
    def _calculate_confidence_trend(self, predictions: Dict[str, Any]) -> str:
        """Calculate trend in confidence over time"""
        
        scores = [pred["confidence_score"] for pred in predictions.values()]
        
        if len(scores) < 2:
            return "insufficient_data"
        
        # Simple linear trend
        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]
        
        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "declining"
        else:
            return "stable"
    
    def _apply_treatment_delay(self, parameters: Dict[str, Any], delay_days: int) -> Dict[str, Any]:
        """Apply effects of treatment delay to parameters"""
        
        delayed = parameters.copy()
        
        # Disease progression during delay
        progression_factor = 1 + (delay_days * 0.002)  # 0.2% progression per day
        
        for param_name, value in parameters.items():
            if "tumor" in param_name.lower() and isinstance(value, (int, float)):
                delayed[param_name] = value * progression_factor
            elif param_name == "ecog_score" and isinstance(value, (int, float)):
                delayed[param_name] = min(4, value + delay_days * 0.01)
        
        return delayed
    
    def _calculate_urgency_score(self, parameters: Dict[str, Any]) -> float:
        """Calculate treatment urgency score"""
        
        urgency = 0.5  # Base urgency
        
        # Increase urgency based on parameters
        if "ecog_score" in parameters:
            ecog = parameters["ecog_score"]
            if ecog >= 3:
                urgency += 0.3
            elif ecog >= 2:
                urgency += 0.2
        
        # Other factors would be added here
        
        return min(1.0, urgency)
    
    def _assess_treatment_urgency(self, timing_results: List[Dict[str, Any]]) -> str:
        """Assess overall treatment urgency"""
        
        immediate_result = timing_results[0]  # No delay
        delayed_results = timing_results[1:]  # With delays
        
        confidence_drop = max([
            immediate_result["confidence_score"] - delayed["confidence_score"]
            for delayed in delayed_results
        ])
        
        if confidence_drop > 0.2:
            return "urgent"
        elif confidence_drop > 0.1:
            return "high"
        elif confidence_drop > 0.05:
            return "moderate"
        else:
            return "low"
    
    def _generate_test_values(self, param: Parameter) -> List[float]:
        """Generate test values for sensitivity analysis"""
        
        if param.normal_range:
            min_val, max_val = param.normal_range
            # Test at different percentiles
            percentiles = [0.1, 0.25, 0.5, 0.75, 0.9]
            return [min_val + p * (max_val - min_val) for p in percentiles]
        else:
            # Use current value ± variations
            current = float(param.current_value)
            variations = [-0.5, -0.25, 0, 0.25, 0.5]
            return [current + v * current for v in variations if current + v * current > 0]
    
    def _categorize_sensitivity(self, variance: float) -> str:
        """Categorize parameter sensitivity"""
        
        if variance > 0.1:
            return "high"
        elif variance > 0.05:
            return "moderate"
        elif variance > 0.02:
            return "low"
        else:
            return "minimal"
    
    def _generate_sensitivity_recommendations(self, param_name: str, variance: float) -> List[str]:
        """Generate recommendations based on sensitivity analysis"""
        
        recommendations = []
        
        if variance > 0.1:
            recommendations.append(f"⚠️ High sensitivity to {param_name} - monitor closely")
            recommendations.append(f"📊 Consider frequent {param_name} assessments")
        elif variance > 0.05:
            recommendations.append(f"📈 Moderate sensitivity to {param_name} - regular monitoring")
        else:
            recommendations.append(f"✅ Low sensitivity to {param_name} - standard monitoring")
        
        return recommendations
    
    def _determine_protocol_outcome(
        self,
        best_protocol: Optional[Dict[str, Any]],
        current_protocol: Optional[Dict[str, Any]]
    ) -> str:
        """Determine outcome of protocol comparison"""
        
        if not best_protocol or not current_protocol:
            return SimulationOutcome.UNCHANGED.value
        
        confidence_diff = best_protocol["confidence_score"] - current_protocol["confidence_score"]
        
        if confidence_diff > 0.1:
            return SimulationOutcome.IMPROVED.value
        elif confidence_diff < -0.1:
            return SimulationOutcome.WORSENED.value
        else:
            return SimulationOutcome.UNCHANGED.value
    
    def _generate_protocol_recommendations(self, protocol_results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on protocol comparison"""
        
        if not protocol_results:
            return ["No protocols available for comparison"]
        
        recommendations = []
        best_protocol = protocol_results[0]
        
        recommendations.append(f"🎯 Best performing protocol: {best_protocol['protocol_name']}")
        recommendations.append(f"📊 Confidence score: {best_protocol['confidence_score']:.1%}")
        
        if len(protocol_results) > 1:
            second_best = protocol_results[1]
            diff = best_protocol["confidence_score"] - second_best["confidence_score"]
            if diff < 0.05:
                recommendations.append("⚖️ Multiple protocols show similar efficacy - consider other factors")
        
        return recommendations
