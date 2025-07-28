"""
Evidence Synthesis Engine
Generates insights by aggregating multi-center data and statistical analysis
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

import numpy as np
from scipy import stats

from core.utils.helpers import log_action, handle_error

logger = logging.getLogger(__name__)

class EvidenceSynthesisEngine:
    """
    Evidence Synthesis Engine for generating insights from aggregated data
    """
    
    def __init__(self):
        """Initialize the evidence synthesis engine"""
        logger.info("Initializing Evidence Synthesis Engine")
        
        # Define supported domains
        self.domains = [
            "surgery_outcomes", 
            "chemotherapy_responses", 
            "survival_rates", 
            "quality_of_life", 
            "complication_rates"
        ]
    
    def _calculate_statistics(self, data: List[Dict[str, Any]], field: str) -> Dict[str, Any]:
        """Calculate basic statistics for a field"""
        values = []
        
        for item in data:
            value = item.get(field)
            if value is not None:
                try:
                    values.append(float(value))
                except (ValueError, TypeError):
                    # Skip non-numeric values
                    pass
        
        if not values:
            return {
                "count": 0,
                "mean": None,
                "median": None,
                "std_dev": None,
                "min": None,
                "max": None
            }
        
        values = np.array(values)
        
        return {
            "count": len(values),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "std_dev": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "confidence_interval": [
                float(stats.t.interval(0.95, len(values)-1, loc=np.mean(values), scale=stats.sem(values))[0]),
                float(stats.t.interval(0.95, len(values)-1, loc=np.mean(values), scale=stats.sem(values))[1])
            ] if len(values) > 1 else None
        }
    
    def _calculate_categorical(self, data: List[Dict[str, Any]], field: str) -> Dict[str, Any]:
        """Calculate frequency distribution for categorical field"""
        values = {}
        total = 0
        
        for item in data:
            value = item.get(field)
            if value is not None:
                if isinstance(value, list):
                    for v in value:
                        values[v] = values.get(v, 0) + 1
                        total += 1
                else:
                    values[value] = values.get(value, 0) + 1
                    total += 1
        
        # Calculate percentages
        percentages = {}
        for key, count in values.items():
            percentages[key] = count / total if total > 0 else 0
        
        return {
            "count": total,
            "distribution": values,
            "percentages": percentages
        }
    
    def _stratify_data(self, data: List[Dict[str, Any]], strata_field: str) -> Dict[str, List[Dict[str, Any]]]:
        """Stratify data by a field"""
        result = {}
        
        for item in data:
            value = item.get(strata_field)
            if value is not None:
                if value not in result:
                    result[value] = []
                result[value].append(item)
        
        return result
    
    def _compare_groups(self, data: Dict[str, List[Dict[str, Any]]], target_field: str) -> Dict[str, Any]:
        """Compare a target field across stratified groups"""
        results = {}
        
        # Calculate statistics for each group
        for group, group_data in data.items():
            results[group] = self._calculate_statistics(group_data, target_field)
        
        # Perform statistical tests if we have at least two groups
        if len(data) >= 2:
            # Collect values for each group
            group_values = {}
            for group, group_data in data.items():
                values = []
                for item in group_data:
                    value = item.get(target_field)
                    if value is not None:
                        try:
                            values.append(float(value))
                        except (ValueError, TypeError):
                            pass
                if values:
                    group_values[group] = np.array(values)
            
            # Perform t-tests for all pairs of groups
            if len(group_values) >= 2:
                t_tests = {}
                groups = list(group_values.keys())
                for i in range(len(groups)):
                    for j in range(i+1, len(groups)):
                        group1 = groups[i]
                        group2 = groups[j]
                        values1 = group_values[group1]
                        values2 = group_values[group2]
                        
                        if len(values1) > 0 and len(values2) > 0:
                            t_stat, p_value = stats.ttest_ind(values1, values2, equal_var=False)
                            t_tests[f"{group1}_vs_{group2}"] = {
                                "t_statistic": float(t_stat),
                                "p_value": float(p_value),
                                "significant": p_value < 0.05
                            }
                
                results["statistical_tests"] = t_tests
        
        return results
    
    def generate_insights(self, domain: str, data: List[Dict[str, Any]], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate insights for a specific domain
        
        Args:
            domain: Domain area for insights (e.g., "surgery_outcomes")
            data: List of data records
            user_id: User ID for audit logging
            
        Returns:
            Dictionary containing generated insights
        """
        try:
            if domain not in self.domains:
                raise ValueError(f"Unsupported domain: {domain}. Supported domains: {self.domains}")
            
            if not data:
                raise ValueError("No data provided for analysis")
            
            # Generate insight ID
            insight_id = str(uuid.uuid4())
            
            # Log action if user ID provided
            if user_id:
                log_action(user_id, "generate_insights", {
                    "domain": domain,
                    "record_count": len(data),
                    "insight_id": insight_id
                })
            
            # Define relevant fields and analyses based on domain
            if domain == "surgery_outcomes":
                fields = {
                    "numeric": ["los", "complication_rate", "mortality_rate", "readmission_rate"],
                    "categorical": ["complication_type", "surgery_type", "stage"]
                }
                strata = ["stage", "age_group", "surgery_type"]
                comparisons = [
                    {"strata": "surgery_type", "target": "complication_rate"},
                    {"strata": "stage", "target": "mortality_rate"}
                ]
                
            elif domain == "chemotherapy_responses":
                fields = {
                    "numeric": ["response_rate", "progression_free_survival", "toxicity_grade"],
                    "categorical": ["response_type", "protocol", "stage"]
                }
                strata = ["protocol", "stage", "age_group"]
                comparisons = [
                    {"strata": "protocol", "target": "response_rate"},
                    {"strata": "stage", "target": "progression_free_survival"}
                ]
                
            elif domain == "survival_rates":
                fields = {
                    "numeric": ["overall_survival", "disease_free_survival", "five_year_survival"],
                    "categorical": ["treatment_approach", "stage", "histology"]
                }
                strata = ["treatment_approach", "stage", "age_group"]
                comparisons = [
                    {"strata": "treatment_approach", "target": "overall_survival"},
                    {"strata": "stage", "target": "five_year_survival"}
                ]
                
            elif domain == "quality_of_life":
                fields = {
                    "numeric": ["qol_score", "pain_score", "fatigue_score", "function_score"],
                    "categorical": ["treatment_type", "stage", "time_point"]
                }
                strata = ["treatment_type", "stage", "age_group", "time_point"]
                comparisons = [
                    {"strata": "treatment_type", "target": "qol_score"},
                    {"strata": "time_point", "target": "qol_score"}
                ]
                
            elif domain == "complication_rates":
                fields = {
                    "numeric": ["complication_rate", "severity_score", "hospital_stay"],
                    "categorical": ["complication_type", "procedure", "treatment_approach"]
                }
                strata = ["procedure", "treatment_approach", "age_group"]
                comparisons = [
                    {"strata": "procedure", "target": "complication_rate"},
                    {"strata": "treatment_approach", "target": "severity_score"}
                ]
            
            # Initialize results structure
            results = {
                "insight_id": insight_id,
                "domain": domain,
                "timestamp": str(datetime.now()),
                "record_count": len(data),
                "statistics": {},
                "categorical": {},
                "stratifications": {},
                "comparisons": {}
            }
            
            # Calculate statistics for numeric fields
            for field in fields["numeric"]:
                results["statistics"][field] = self._calculate_statistics(data, field)
            
            # Calculate distributions for categorical fields
            for field in fields["categorical"]:
                results["categorical"][field] = self._calculate_categorical(data, field)
            
            # Perform stratification analyses
            for strata_field in strata:
                stratified_data = self._stratify_data(data, strata_field)
                results["stratifications"][strata_field] = {
                    "count": {key: len(group) for key, group in stratified_data.items()},
                    "percentage": {key: len(group)/len(data) for key, group in stratified_data.items()}
                }
            
            # Perform comparison analyses
            for comparison in comparisons:
                strata_field = comparison["strata"]
                target_field = comparison["target"]
                
                stratified_data = self._stratify_data(data, strata_field)
                results["comparisons"][f"{strata_field}_vs_{target_field}"] = self._compare_groups(stratified_data, target_field)
            
            return {
                "success": True,
                "insights": results
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return handle_error(e)
