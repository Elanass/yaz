"""
ADCI Diagnostic Module - Gastric Adenocarcinoma Subtype Classification
Adaptive Decision Confidence Index for precise subtype identification

This module is a DIAGNOSTIC tool for identifying subtypes of gastric adenocarcinoma,
not a general scoring system. It provides evidence-based subtype classification
with confidence intervals for clinical decision support.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import structlog

from ..framework.decision_module import (
    DecisionModule, DecisionModuleType, DecisionContext, DecisionResult, CacheConfig, CacheStrategy
)

logger = structlog.get_logger(__name__)

class ADCIDiagnosticModule(DecisionModule):
    """
    ADCI Diagnostic Module for Gastric Adenocarcinoma Subtype Classification
    
    Purpose: Identify and classify gastric adenocarcinoma subtypes based on:
    - Histopathological features
    - Molecular markers (HER2, MSI, PD-L1)
    - Morphological patterns (Lauren classification)
    - WHO classification criteria
    - Immunohistochemistry profiles
    
    This is NOT a general scoring tool but a specialized diagnostic classifier
    for gastric cancer subtypes with clinical decision support capabilities.
    """
    
    def __init__(self):
        # Configure for high cache hit rate due to common diagnostic patterns
        cache_config = CacheConfig(
            strategy=CacheStrategy.AGGRESSIVE,
            ttl_seconds=43200,  # 12 hours - diagnostic patterns are stable
            hit_rate_target=0.92,
            max_size=5000
        )
        
        super().__init__(
            module_id="adci_gastric_diagnostic",
            module_type=DecisionModuleType.DIAGNOSTIC,
            version="3.0.0",
            domain="gastric_oncology",
            cache_config=cache_config
        )
        
        # WHO Classification System for Gastric Adenocarcinoma
        self.who_subtypes = {
            "tubular_well_differentiated": {
                "characteristics": ["well_formed_glands", "minimal_pleomorphism"],
                "markers": {"ki67": "<10%", "p53": "wild_type"},
                "prognosis": "favorable"
            },
            "tubular_moderately_differentiated": {
                "characteristics": ["irregular_glands", "moderate_pleomorphism"],
                "markers": {"ki67": "10-30%", "p53": "mixed"},
                "prognosis": "intermediate"
            },
            "tubular_poorly_differentiated": {
                "characteristics": ["minimal_gland_formation", "high_pleomorphism"],
                "markers": {"ki67": ">30%", "p53": "mutated"},
                "prognosis": "poor"
            },
            "signet_ring_cell": {
                "characteristics": ["signet_ring_morphology", "mucin_filled_cytoplasm"],
                "markers": {"cdh1": "loss", "muc2": "positive"},
                "prognosis": "poor"
            },
            "mucinous": {
                "characteristics": ["extracellular_mucin", "pools_of_mucin"],
                "markers": {"muc2": "positive", "muc5ac": "positive"},
                "prognosis": "intermediate"
            }
        }
        
        # Lauren Classification System
        self.lauren_types = {
            "intestinal": {
                "features": ["gland_formation", "cohesive_growth"],
                "epidemiology": "more_common_in_males",
                "location": "distal_stomach"
            },
            "diffuse": {
                "features": ["signet_ring_cells", "infiltrative_growth"],
                "epidemiology": "more_common_in_females",
                "location": "proximal_stomach"
            },
            "mixed": {
                "features": ["both_patterns", "variable_morphology"],
                "epidemiology": "intermediate",
                "location": "variable"
            }
        }
        
        # Molecular Subtypes (TCGA-based)
        self.molecular_subtypes = {
            "ebv_positive": {
                "markers": ["ebv_ish_positive", "pid3ca_mutation", "extreme_hypermethylation"],
                "frequency": "9%",
                "prognosis": "intermediate",
                "treatment_implications": "immune_checkpoint_responsive"
            },
            "microsatellite_instable": {
                "markers": ["msi_high", "mlh1_loss", "hypermutation"],
                "frequency": "22%", 
                "prognosis": "better",
                "treatment_implications": "immune_checkpoint_responsive"
            },
            "genomically_stable": {
                "markers": ["cdh1_mutation", "rhoa_mutation", "few_mutations"],
                "frequency": "20%",
                "prognosis": "poor",
                "treatment_implications": "limited_targeted_options"
            },
            "chromosomal_instability": {
                "markers": ["aneuploidy", "tp53_mutation", "pik3ca_amplification"],
                "frequency": "50%",
                "prognosis": "intermediate", 
                "treatment_implications": "targeted_therapy_options"
            }
        }
    
    async def process_decision(
        self,
        parameters: Dict[str, Any],
        context: DecisionContext,
        options: Optional[Dict[str, Any]] = None
    ) -> DecisionResult:
        """
        Process gastric adenocarcinoma subtype diagnosis
        
        Returns detailed subtype classification with confidence intervals
        and therapeutic implications
        """
        
        # Extract diagnostic parameters
        histology = parameters.get("histology", {})
        immunohistochemistry = parameters.get("immunohistochemistry", {})
        molecular_testing = parameters.get("molecular_testing", {})
        morphology = parameters.get("morphological_features", [])
        
        # Parallel subtype analysis
        classification_tasks = [
            self._classify_who_subtype(histology, immunohistochemistry),
            self._classify_lauren_type(morphology, histology),
            self._classify_molecular_subtype(molecular_testing, immunohistochemistry),
            self._assess_her2_status(immunohistochemistry, molecular_testing),
            self._evaluate_msi_status(molecular_testing, immunohistochemistry)
        ]
        
        who_result, lauren_result, molecular_result, her2_result, msi_result = await asyncio.gather(
            *classification_tasks
        )
        
        # Integrate classification results
        integrated_diagnosis = await self._integrate_classifications(
            who_result, lauren_result, molecular_result, her2_result, msi_result
        )
        
        # Calculate diagnostic confidence
        confidence_analysis = self._calculate_diagnostic_confidence(
            integrated_diagnosis, parameters
        )
        
        # Generate therapeutic implications
        treatment_implications = self._generate_treatment_implications(integrated_diagnosis)
        
        # Build comprehensive diagnostic result
        primary_diagnosis = {
            "primary_subtype": integrated_diagnosis["primary_subtype"],
            "who_classification": who_result,
            "lauren_classification": lauren_result,
            "molecular_subtype": molecular_result,
            "her2_status": her2_result,
            "msi_status": msi_result,
            "confidence_score": confidence_analysis["overall_confidence"],
            "diagnostic_certainty": confidence_analysis["certainty_level"],
            "supporting_evidence": integrated_diagnosis["evidence"],
            "treatment_implications": treatment_implications
        }
        
        # Generate alternative diagnoses if confidence is moderate
        alternatives = []
        if confidence_analysis["overall_confidence"] < 0.85:
            alternatives = await self._generate_alternative_diagnoses(
                integrated_diagnosis, confidence_analysis
            )
        
        return DecisionResult(
            primary_decision=primary_diagnosis,
            confidence=confidence_analysis["overall_confidence"],
            alternatives=alternatives,
            metadata={
                "diagnostic_approach": "multi_modal_classification",
                "evidence_level": "Grade A (WHO 2019, TCGA)",
                "classification_systems": ["WHO", "Lauren", "TCGA_molecular"],
                "confidence_breakdown": confidence_analysis,
                "clinical_actionability": treatment_implications["actionability_score"]
            }
        )
    
    async def _classify_who_subtype(
        self, 
        histology: Dict[str, Any], 
        ihc: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classify according to WHO 2019 criteria"""
        
        differentiation = histology.get("differentiation", "").lower()
        gland_formation = histology.get("gland_formation", "")
        pleomorphism = histology.get("nuclear_pleomorphism", "")
        
        # WHO subtype determination logic
        if "well" in differentiation or gland_formation == "well_formed":
            subtype = "tubular_well_differentiated"
        elif "moderate" in differentiation:
            subtype = "tubular_moderately_differentiated"
        elif "poor" in differentiation or gland_formation == "minimal":
            if histology.get("signet_ring_cells", False):
                subtype = "signet_ring_cell"
            else:
                subtype = "tubular_poorly_differentiated"
        elif histology.get("mucinous_component", 0) > 50:
            subtype = "mucinous"
        else:
            subtype = "tubular_moderately_differentiated"  # default
        
        confidence = self._calculate_subtype_confidence(histology, ihc, subtype)
        
        return {
            "subtype": subtype,
            "confidence": confidence,
            "supporting_features": self._get_supporting_features(histology, subtype),
            "who_grade": self._determine_who_grade(subtype, histology)
        }
    
    async def _classify_lauren_type(
        self, 
        morphology: List[str], 
        histology: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classify according to Lauren system"""
        
        intestinal_features = sum(1 for feature in morphology if feature in [
            "gland_formation", "cohesive_growth", "tumor_budding"
        ])
        
        diffuse_features = sum(1 for feature in morphology if feature in [
            "signet_ring_cells", "infiltrative_growth", "single_cell_infiltration"
        ])
        
        if intestinal_features > diffuse_features:
            lauren_type = "intestinal"
            confidence = 0.8 + (intestinal_features * 0.05)
        elif diffuse_features > intestinal_features:
            lauren_type = "diffuse"
            confidence = 0.8 + (diffuse_features * 0.05)
        else:
            lauren_type = "mixed"
            confidence = 0.7
        
        return {
            "type": lauren_type,
            "confidence": min(confidence, 0.95),
            "intestinal_score": intestinal_features,
            "diffuse_score": diffuse_features
        }
    
    async def _classify_molecular_subtype(
        self, 
        molecular: Dict[str, Any], 
        ihc: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classify according to TCGA molecular subtypes"""
        
        # EBV status
        ebv_positive = molecular.get("ebv_ish", False) or ihc.get("ebv_lmp1", False)
        
        # MSI status
        msi_status = molecular.get("msi_status", "stable").lower()
        msi_high = msi_status in ["high", "msi-h"]
        
        # Mutation burden
        mutation_count = molecular.get("mutation_count", 0)
        
        # Chromosomal instability markers
        aneuploidy_score = molecular.get("aneuploidy_score", 0)
        
        if ebv_positive:
            subtype = "ebv_positive"
            confidence = 0.95
        elif msi_high:
            subtype = "microsatellite_instable"
            confidence = 0.90
        elif mutation_count < 50:
            subtype = "genomically_stable"
            confidence = 0.75
        else:
            subtype = "chromosomal_instability"
            confidence = 0.80
        
        return {
            "subtype": subtype,
            "confidence": confidence,
            "ebv_status": ebv_positive,
            "msi_status": msi_status,
            "mutation_burden": mutation_count
        }
    
    async def _assess_her2_status(
        self, 
        ihc: Dict[str, Any], 
        molecular: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess HER2 status for targeted therapy"""
        
        her2_ihc = ihc.get("her2_score", 0)
        her2_fish = molecular.get("her2_amplification", False)
        
        if her2_ihc >= 3 or her2_fish:
            status = "positive"
            confidence = 0.95
        elif her2_ihc == 2:
            if her2_fish:
                status = "positive"
                confidence = 0.90
            else:
                status = "equivocal"
                confidence = 0.70
        else:
            status = "negative"
            confidence = 0.90
        
        return {
            "status": status,
            "confidence": confidence,
            "ihc_score": her2_ihc,
            "fish_result": her2_fish,
            "treatment_eligible": status == "positive"
        }
    
    async def _evaluate_msi_status(
        self, 
        molecular: Dict[str, Any], 
        ihc: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate microsatellite instability status"""
        
        msi_testing = molecular.get("msi_status", "").lower()
        
        # MMR protein expression
        mmr_proteins = ihc.get("mmr_proteins", {})
        mmr_loss = sum(1 for protein, status in mmr_proteins.items() if status == "loss")
        
        if msi_testing == "high" or msi_testing == "msi-h":
            status = "msi_high"
            confidence = 0.95
        elif mmr_loss >= 2:
            status = "msi_high"
            confidence = 0.85
        elif msi_testing in ["low", "stable"]:
            status = "msi_stable"
            confidence = 0.90
        else:
            status = "unknown"
            confidence = 0.50
        
        return {
            "status": status,
            "confidence": confidence,
            "mmr_status": mmr_proteins,
            "immunotherapy_eligible": status == "msi_high"
        }
    
    async def _integrate_classifications(
        self, 
        who_result: Dict[str, Any],
        lauren_result: Dict[str, Any],
        molecular_result: Dict[str, Any],
        her2_result: Dict[str, Any],
        msi_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Integrate multiple classification systems"""
        
        # Primary subtype is WHO classification
        primary_subtype = who_result["subtype"]
        
        # Gather supporting evidence
        evidence = {
            "histological": who_result["supporting_features"],
            "morphological": lauren_result["type"],
            "molecular": molecular_result["subtype"],
            "biomarkers": {
                "her2": her2_result["status"],
                "msi": msi_result["status"]
            }
        }
        
        # Check for consistency between classifications
        consistency_score = self._assess_classification_consistency(
            who_result, lauren_result, molecular_result
        )
        
        return {
            "primary_subtype": primary_subtype,
            "evidence": evidence,
            "consistency_score": consistency_score,
            "classification_confidence": {
                "who": who_result["confidence"],
                "lauren": lauren_result["confidence"],
                "molecular": molecular_result["confidence"]
            }
        }
    
    def _calculate_diagnostic_confidence(
        self, 
        integrated_diagnosis: Dict[str, Any], 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall diagnostic confidence"""
        
        # Base confidence from classification consistency
        consistency_weight = integrated_diagnosis["consistency_score"] * 0.4
        
        # Confidence from individual classification systems
        classification_confidences = integrated_diagnosis["classification_confidence"]
        avg_classification_confidence = sum(classification_confidences.values()) / len(classification_confidences)
        classification_weight = avg_classification_confidence * 0.4
        
        # Data completeness score
        required_fields = ["histology", "immunohistochemistry"]
        optional_fields = ["molecular_testing", "morphological_features"]
        
        completeness_score = 0.0
        for field in required_fields:
            if field in parameters and parameters[field]:
                completeness_score += 0.1
        
        for field in optional_fields:
            if field in parameters and parameters[field]:
                completeness_score += 0.05
        
        completeness_weight = min(completeness_score, 0.2)
        
        overall_confidence = consistency_weight + classification_weight + completeness_weight
        overall_confidence = min(max(overall_confidence, 0.0), 1.0)
        
        # Determine certainty level
        if overall_confidence >= 0.90:
            certainty_level = "high"
        elif overall_confidence >= 0.75:
            certainty_level = "moderate"
        elif overall_confidence >= 0.60:
            certainty_level = "low"
        else:
            certainty_level = "insufficient"
        
        return {
            "overall_confidence": round(overall_confidence, 3),
            "certainty_level": certainty_level,
            "confidence_components": {
                "classification_consistency": round(consistency_weight, 3),
                "individual_classifications": round(classification_weight, 3),
                "data_completeness": round(completeness_weight, 3)
            },
            "recommendations": self._get_confidence_recommendations(certainty_level)
        }
    
    def _generate_treatment_implications(
        self, 
        integrated_diagnosis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate treatment implications based on subtype"""
        
        primary_subtype = integrated_diagnosis["primary_subtype"]
        biomarkers = integrated_diagnosis["evidence"]["biomarkers"]
        
        implications = {
            "targeted_therapies": [],
            "chemotherapy_sensitivity": "",
            "immunotherapy_eligibility": False,
            "surgical_considerations": "",
            "prognosis": "",
            "actionability_score": 0.0
        }
        
        # HER2-targeted therapy
        if biomarkers["her2"] == "positive":
            implications["targeted_therapies"].append({
                "therapy": "Trastuzumab + chemotherapy",
                "evidence_level": "Grade A",
                "indication": "HER2-positive gastric cancer"
            })
            implications["actionability_score"] += 0.3
        
        # Immunotherapy eligibility
        if biomarkers["msi"] == "msi_high":
            implications["immunotherapy_eligibility"] = True
            implications["targeted_therapies"].append({
                "therapy": "Pembrolizumab",
                "evidence_level": "Grade A", 
                "indication": "MSI-high gastric cancer"
            })
            implications["actionability_score"] += 0.4
        
        # Subtype-specific implications
        subtype_implications = self.who_subtypes.get(primary_subtype, {})
        implications["prognosis"] = subtype_implications.get("prognosis", "unknown")
        
        if primary_subtype == "signet_ring_cell":
            implications["surgical_considerations"] = "Consider total gastrectomy due to diffuse growth pattern"
            implications["chemotherapy_sensitivity"] = "Often chemotherapy-resistant"
        elif primary_subtype in ["tubular_well_differentiated", "tubular_moderately_differentiated"]:
            implications["chemotherapy_sensitivity"] = "Generally chemotherapy-sensitive"
            implications["surgical_considerations"] = "Suitable for organ-preserving surgery if early stage"
        
        return implications
    
    async def _generate_alternative_diagnoses(
        self, 
        integrated_diagnosis: Dict[str, Any], 
        confidence_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate alternative diagnostic possibilities"""
        
        alternatives = []
        primary_subtype = integrated_diagnosis["primary_subtype"]
        
        # Generate alternatives based on uncertainty factors
        if confidence_analysis["certainty_level"] in ["low", "insufficient"]:
            
            # Alternative WHO subtypes
            for subtype, details in self.who_subtypes.items():
                if subtype != primary_subtype:
                    alternatives.append({
                        "diagnosis": f"Alternative WHO subtype: {subtype}",
                        "rationale": "Histological features may overlap between subtypes",
                        "additional_testing": "Consider additional IHC markers or expert consultation",
                        "confidence": 0.60
                    })
                    
                    if len(alternatives) >= 2:  # Limit alternatives
                        break
            
            # Suggest additional testing
            alternatives.append({
                "diagnosis": "Recommend molecular profiling",
                "rationale": "Complete molecular characterization for precise subtyping",
                "additional_testing": "NGS panel, MSI testing, HER2 FISH if equivocal",
                "confidence": 0.80
            })
        
        return alternatives
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> List[str]:
        """Validate diagnostic parameters"""
        errors = []
        
        # Required diagnostic data
        if "histology" not in parameters:
            errors.append("Missing histological data")
        else:
            histology = parameters["histology"]
            if "differentiation" not in histology:
                errors.append("Missing tumor differentiation grade")
        
        # Recommended but not required
        if "immunohistochemistry" not in parameters:
            errors.append("Warning: Immunohistochemistry data recommended for accurate subtyping")
        
        if "molecular_testing" not in parameters:
            errors.append("Warning: Molecular testing recommended for complete classification")
        
        return errors
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for ADCI diagnostic parameters"""
        return {
            "type": "object",
            "title": "ADCI Gastric Adenocarcinoma Diagnostic Parameters",
            "properties": {
                "histology": {
                    "type": "object",
                    "required": True,
                    "properties": {
                        "differentiation": {"type": "string", "enum": ["well", "moderate", "poor"]},
                        "gland_formation": {"type": "string", "enum": ["well_formed", "irregular", "minimal"]},
                        "nuclear_pleomorphism": {"type": "string", "enum": ["mild", "moderate", "severe"]},
                        "signet_ring_cells": {"type": "boolean"},
                        "mucinous_component": {"type": "number", "minimum": 0, "maximum": 100}
                    }
                },
                "immunohistochemistry": {
                    "type": "object",
                    "properties": {
                        "her2_score": {"type": "integer", "minimum": 0, "maximum": 3},
                        "mmr_proteins": {
                            "type": "object",
                            "properties": {
                                "mlh1": {"type": "string", "enum": ["intact", "loss"]},
                                "msh2": {"type": "string", "enum": ["intact", "loss"]},
                                "msh6": {"type": "string", "enum": ["intact", "loss"]},
                                "pms2": {"type": "string", "enum": ["intact", "loss"]}
                            }
                        },
                        "ki67": {"type": "string"},
                        "p53": {"type": "string", "enum": ["wild_type", "mutated", "null"]}
                    }
                },
                "molecular_testing": {
                    "type": "object",
                    "properties": {
                        "msi_status": {"type": "string", "enum": ["high", "low", "stable"]},
                        "her2_amplification": {"type": "boolean"},
                        "ebv_ish": {"type": "boolean"},
                        "mutation_count": {"type": "integer", "minimum": 0},
                        "aneuploidy_score": {"type": "number", "minimum": 0, "maximum": 1}
                    }
                },
                "morphological_features": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "gland_formation", "cohesive_growth", "tumor_budding",
                            "signet_ring_cells", "infiltrative_growth", "single_cell_infiltration"
                        ]
                    }
                }
            },
            "required": ["histology"]
        }
    
    def _calculate_subtype_confidence(
        self, 
        histology: Dict[str, Any], 
        ihc: Dict[str, Any], 
        subtype: str
    ) -> float:
        """Calculate confidence for WHO subtype classification"""
        
        base_confidence = 0.7
        
        # Boost confidence based on supporting features
        subtype_info = self.who_subtypes.get(subtype, {})
        characteristics = subtype_info.get("characteristics", [])
        
        # Check how many characteristics are present
        feature_matches = 0
        for characteristic in characteristics:
            if characteristic in str(histology.values()).lower():
                feature_matches += 1
        
        confidence_boost = (feature_matches / max(len(characteristics), 1)) * 0.2
        
        # IHC confirmation
        if ihc and subtype in ["signet_ring_cell", "mucinous"]:
            confidence_boost += 0.1
        
        return min(base_confidence + confidence_boost, 0.95)
    
    def _get_supporting_features(
        self, 
        histology: Dict[str, Any], 
        subtype: str
    ) -> List[str]:
        """Get supporting histological features for subtype"""
        
        features = []
        subtype_info = self.who_subtypes.get(subtype, {})
        
        for characteristic in subtype_info.get("characteristics", []):
            if characteristic in str(histology.values()).lower():
                features.append(characteristic)
        
        return features
    
    def _determine_who_grade(
        self, 
        subtype: str, 
        histology: Dict[str, Any]
    ) -> str:
        """Determine WHO grade based on subtype and features"""
        
        if "well" in subtype:
            return "Grade 1"
        elif "moderately" in subtype:
            return "Grade 2"
        elif "poorly" in subtype or subtype == "signet_ring_cell":
            return "Grade 3"
        else:
            return "Grade 2"  # default
    
    def _assess_classification_consistency(
        self, 
        who_result: Dict[str, Any],
        lauren_result: Dict[str, Any],
        molecular_result: Dict[str, Any]
    ) -> float:
        """Assess consistency between different classification systems"""
        
        consistency_score = 0.0
        
        # WHO vs Lauren consistency
        who_subtype = who_result["subtype"]
        lauren_type = lauren_result["type"]
        
        if who_subtype == "signet_ring_cell" and lauren_type == "diffuse":
            consistency_score += 0.3
        elif who_subtype in ["tubular_well_differentiated", "tubular_moderately_differentiated"] and lauren_type == "intestinal":
            consistency_score += 0.3
        elif lauren_type == "mixed":
            consistency_score += 0.2
        
        # Molecular consistency
        molecular_subtype = molecular_result["subtype"]
        if molecular_subtype == "genomically_stable" and who_subtype == "signet_ring_cell":
            consistency_score += 0.4
        elif molecular_subtype in ["ebv_positive", "microsatellite_instable"]:
            consistency_score += 0.3
        else:
            consistency_score += 0.2
        
        return min(consistency_score, 1.0)
    
    def _get_confidence_recommendations(self, certainty_level: str) -> List[str]:
        """Get recommendations based on diagnostic confidence"""
        
        recommendations = []
        
        if certainty_level == "insufficient":
            recommendations.extend([
                "Consider repeat biopsy with adequate tissue sampling",
                "Perform comprehensive immunohistochemistry panel",
                "Request molecular testing including MSI and HER2 status"
            ])
        elif certainty_level == "low":
            recommendations.extend([
                "Consider expert pathology consultation",
                "Additional molecular markers may be helpful",
                "Correlate with clinical and imaging findings"
            ])
        elif certainty_level == "moderate":
            recommendations.extend([
                "Classification is adequate for treatment planning",
                "Consider HER2 and MSI testing if not performed"
            ])
        else:  # high confidence
            recommendations.extend([
                "Classification is sufficient for treatment decisions",
                "Proceed with subtype-directed therapy planning"
            ])
        
        return recommendations
