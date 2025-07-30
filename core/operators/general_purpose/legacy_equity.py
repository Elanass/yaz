"""
Equity Operations Manager
Handles access control, fairness algorithms, and equitable resource distribution
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import statistics

from core.services.base import BaseService
from core.services.logger import get_logger

logger = get_logger(__name__)

class EquityMetric(Enum):
    """Types of equity metrics to track"""
    ACCESS_TIME = "access_time"
    WAIT_TIME = "wait_time"
    OUTCOME_QUALITY = "outcome_quality"
    COST_BURDEN = "cost_burden"
    RESOURCE_ALLOCATION = "resource_allocation"

class DemographicGroup(Enum):
    """Demographic groups for equity analysis"""
    AGE_YOUNG = "age_18_35"
    AGE_MIDDLE = "age_36_64"
    AGE_SENIOR = "age_65_plus"
    INCOME_LOW = "income_low"
    INCOME_MIDDLE = "income_middle"
    INCOME_HIGH = "income_high"
    RURAL = "rural"
    URBAN = "urban"
    SUBURBAN = "suburban"

@dataclass
class EquityAssessment:
    """Equity assessment result"""
    metric: EquityMetric
    groups: Dict[str, float]
    disparity_score: float
    concerning_disparities: List[str]
    recommendations: List[str]
    assessment_date: datetime

@dataclass
class ResourceAllocation:
    """Resource allocation recommendation"""
    resource_type: str
    total_available: int
    allocations: Dict[str, int]
    equity_score: float
    justification: str

class EquityOperator(BaseService):
    """Operations for ensuring equitable healthcare delivery"""
    
    def __init__(self):
        super().__init__()
        self.disparity_threshold = 0.2  # 20% disparity threshold
    
    async def assess_access_equity(
        self, 
        access_data: Dict[str, List[float]],
        metric: EquityMetric
    ) -> EquityAssessment:
        """Assess equity across demographic groups"""
        
        try:
            group_stats = {}
            all_values = []
            
            # Calculate statistics for each group
            for group, values in access_data.items():
                if values:
                    group_mean = statistics.mean(values)
                    group_stats[group] = group_mean
                    all_values.extend(values)
            
            if not group_stats:
                raise ValueError("No valid data provided for equity assessment")
            
            # Calculate overall statistics
            overall_mean = statistics.mean(all_values)
            
            # Calculate disparity score (coefficient of variation)
            group_means = list(group_stats.values())
            if len(group_means) > 1:
                disparity_score = statistics.stdev(group_means) / overall_mean
            else:
                disparity_score = 0.0
            
            # Identify concerning disparities
            concerning_disparities = []
            recommendations = []
            
            for group, value in group_stats.items():
                relative_difference = abs(value - overall_mean) / overall_mean
                
                if relative_difference > self.disparity_threshold:
                    if value > overall_mean:
                        concerning_disparities.append(
                            f"{group} has {relative_difference:.1%} higher {metric.value} than average"
                        )
                    else:
                        concerning_disparities.append(
                            f"{group} has {relative_difference:.1%} lower {metric.value} than average"
                        )
            
            # Generate recommendations
            recommendations = await self._generate_equity_recommendations(
                metric, group_stats, overall_mean
            )
            
            assessment = EquityAssessment(
                metric=metric,
                groups=group_stats,
                disparity_score=disparity_score,
                concerning_disparities=concerning_disparities,
                recommendations=recommendations,
                assessment_date=datetime.now()
            )
            
            await self._log_equity_assessment(assessment)
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error assessing access equity: {e}")
            raise
    
    async def optimize_resource_allocation(
        self,
        resource_type: str,
        total_resources: int,
        demand_by_group: Dict[str, int],
        priority_weights: Optional[Dict[str, float]] = None
    ) -> ResourceAllocation:
        """Optimize resource allocation for equity"""
        
        try:
            if priority_weights is None:
                # Default equal weighting
                priority_weights = {group: 1.0 for group in demand_by_group.keys()}
            
            total_demand = sum(demand_by_group.values())
            total_weight = sum(priority_weights.values())
            
            if total_demand <= total_resources:
                # Sufficient resources for all demand
                allocations = demand_by_group.copy()
                justification = "Sufficient resources to meet all demand"
                equity_score = 1.0
            else:
                # Need to allocate proportionally
                allocations = {}
                
                for group, demand in demand_by_group.items():
                    weight = priority_weights.get(group, 1.0)
                    weighted_proportion = (weight / total_weight)
                    
                    # Allocate based on weighted proportion
                    allocation = min(
                        demand,  # Don't exceed demand
                        int(total_resources * weighted_proportion)
                    )
                    allocations[group] = allocation
                
                # Redistribute any remaining resources
                remaining = total_resources - sum(allocations.values())
                while remaining > 0:
                    # Find groups with unmet demand
                    for group in demand_by_group:
                        if allocations[group] < demand_by_group[group] and remaining > 0:
                            allocations[group] += 1
                            remaining -= 1
                
                justification = f"Proportional allocation with {total_demand - total_resources} unmet demand"
                
                # Calculate equity score (lower is more equitable)
                allocation_rates = [
                    allocations[group] / demand_by_group[group] 
                    for group in demand_by_group
                    if demand_by_group[group] > 0
                ]
                
                if allocation_rates:
                    equity_score = 1.0 - (statistics.stdev(allocation_rates) if len(allocation_rates) > 1 else 0.0)
                else:
                    equity_score = 0.0
            
            allocation = ResourceAllocation(
                resource_type=resource_type,
                total_available=total_resources,
                allocations=allocations,
                equity_score=equity_score,
                justification=justification
            )
            
            await self._log_resource_allocation(allocation)
            
            return allocation
            
        except Exception as e:
            self.logger.error(f"Error optimizing resource allocation: {e}")
            raise
    
    async def calculate_fairness_score(
        self,
        outcomes_by_group: Dict[str, List[float]],
        demographic_parity: bool = True,
        equalized_odds: bool = True
    ) -> Dict[str, Any]:
        """Calculate algorithmic fairness scores"""
        
        try:
            fairness_metrics = {}
            
            # Demographic Parity: equal positive outcome rates across groups
            if demographic_parity:
                positive_rates = {}
                for group, outcomes in outcomes_by_group.items():
                    if outcomes:
                        positive_rate = sum(1 for x in outcomes if x > 0.5) / len(outcomes)
                        positive_rates[group] = positive_rate
                
                if positive_rates:
                    rate_values = list(positive_rates.values())
                    demographic_parity_score = 1.0 - (statistics.stdev(rate_values) if len(rate_values) > 1 else 0.0)
                    fairness_metrics["demographic_parity"] = {
                        "score": demographic_parity_score,
                        "rates_by_group": positive_rates
                    }
            
            # Equalized Odds: equal true positive and false positive rates
            if equalized_odds:
                # Simplified version - equal outcome variance across groups
                variance_scores = {}
                for group, outcomes in outcomes_by_group.items():
                    if len(outcomes) > 1:
                        variance_scores[group] = statistics.variance(outcomes)
                
                if variance_scores:
                    variance_values = list(variance_scores.values())
                    equalized_odds_score = 1.0 - (statistics.stdev(variance_values) if len(variance_values) > 1 else 0.0)
                    fairness_metrics["equalized_odds"] = {
                        "score": equalized_odds_score,
                        "variances_by_group": variance_scores
                    }
            
            # Overall fairness score
            scores = [metric["score"] for metric in fairness_metrics.values()]
            overall_fairness = statistics.mean(scores) if scores else 0.0
            
            result = {
                "overall_fairness_score": overall_fairness,
                "metrics": fairness_metrics,
                "assessment_date": datetime.now().isoformat(),
                "recommendations": await self._generate_fairness_recommendations(fairness_metrics)
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating fairness score: {e}")
            raise
    
    async def monitor_equity_trends(
        self,
        historical_assessments: List[EquityAssessment],
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """Monitor equity trends over time"""
        
        try:
            cutoff_date = datetime.now() - timedelta(days=lookback_days)
            recent_assessments = [
                a for a in historical_assessments 
                if a.assessment_date >= cutoff_date
            ]
            
            if not recent_assessments:
                return {"error": "No recent assessments available"}
            
            # Track disparity score trends
            disparity_trends = [a.disparity_score for a in recent_assessments]
            
            trend_analysis = {
                "lookback_days": lookback_days,
                "assessment_count": len(recent_assessments),
                "disparity_trend": {
                    "current": disparity_trends[-1] if disparity_trends else 0,
                    "average": statistics.mean(disparity_trends),
                    "trend": "improving" if len(disparity_trends) > 1 and disparity_trends[-1] < disparity_trends[0] else "stable"
                },
                "most_common_concerns": await self._analyze_common_concerns(recent_assessments),
                "recommendations": await self._generate_trend_recommendations(recent_assessments)
            }
            
            return trend_analysis
            
        except Exception as e:
            self.logger.error(f"Error monitoring equity trends: {e}")
            raise
    
    async def _generate_equity_recommendations(
        self, 
        metric: EquityMetric, 
        group_stats: Dict[str, float], 
        overall_mean: float
    ) -> List[str]:
        """Generate equity improvement recommendations"""
        
        recommendations = []
        
        # Find groups that are underperforming
        underperforming = [
            group for group, value in group_stats.items()
            if (value - overall_mean) / overall_mean < -self.disparity_threshold
        ]
        
        overperforming = [
            group for group, value in group_stats.items()
            if (value - overall_mean) / overall_mean > self.disparity_threshold
        ]
        
        if metric == EquityMetric.ACCESS_TIME:
            if underperforming:
                recommendations.append(f"Improve access infrastructure for: {', '.join(underperforming)}")
            if overperforming:
                recommendations.append(f"Consider redistributing resources from: {', '.join(overperforming)}")
        
        elif metric == EquityMetric.WAIT_TIME:
            if underperforming:
                recommendations.append(f"Increase scheduling capacity for: {', '.join(underperforming)}")
                recommendations.append("Implement priority queueing for underserved groups")
        
        elif metric == EquityMetric.OUTCOME_QUALITY:
            if underperforming:
                recommendations.append(f"Enhance care protocols for: {', '.join(underperforming)}")
                recommendations.append("Provide additional training for providers serving these groups")
        
        if not recommendations:
            recommendations.append("Continue monitoring - no immediate equity concerns identified")
        
        return recommendations
    
    async def _generate_fairness_recommendations(
        self, 
        fairness_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate algorithmic fairness recommendations"""
        
        recommendations = []
        
        for metric_name, metric_data in fairness_metrics.items():
            score = metric_data["score"]
            
            if score < 0.8:
                if metric_name == "demographic_parity":
                    recommendations.append("Consider rebalancing training data across demographic groups")
                    recommendations.append("Implement post-processing calibration for demographic parity")
                elif metric_name == "equalized_odds":
                    recommendations.append("Review model features for potential bias")
                    recommendations.append("Consider fairness-aware machine learning algorithms")
        
        if not recommendations:
            recommendations.append("Fairness metrics are within acceptable ranges")
        
        return recommendations
    
    async def _analyze_common_concerns(
        self, 
        assessments: List[EquityAssessment]
    ) -> List[str]:
        """Analyze most common equity concerns"""
        
        all_concerns = []
        for assessment in assessments:
            all_concerns.extend(assessment.concerning_disparities)
        
        # Count occurrences (simplified)
        concern_counts = {}
        for concern in all_concerns:
            # Extract group name from concern string
            words = concern.split()
            if words:
                group = words[0]
                concern_counts[group] = concern_counts.get(group, 0) + 1
        
        # Return top concerns
        sorted_concerns = sorted(concern_counts.items(), key=lambda x: x[1], reverse=True)
        return [f"{group}: {count} occurrences" for group, count in sorted_concerns[:5]]
    
    async def _generate_trend_recommendations(
        self, 
        assessments: List[EquityAssessment]
    ) -> List[str]:
        """Generate recommendations based on equity trends"""
        
        if len(assessments) < 2:
            return ["Insufficient data for trend analysis"]
        
        # Check if disparities are increasing
        recent_scores = [a.disparity_score for a in assessments[-5:]]
        if len(recent_scores) > 1 and recent_scores[-1] > recent_scores[0]:
            return [
                "Equity disparities are increasing - immediate intervention recommended",
                "Review recent policy changes that may have impacted equity",
                "Increase monitoring frequency"
            ]
        
        return ["Equity trends are stable - continue current monitoring"]
    
    async def _log_equity_assessment(self, assessment: EquityAssessment):
        """Log equity assessment for audit trail"""
        await self.audit_log(
            action="equity_assessment",
            entity_type="equity_metric",
            metadata={
                "metric": assessment.metric.value,
                "disparity_score": assessment.disparity_score,
                "concerns_count": len(assessment.concerning_disparities)
            }
        )
    
    async def _log_resource_allocation(self, allocation: ResourceAllocation):
        """Log resource allocation for audit trail"""
        await self.audit_log(
            action="resource_allocation",
            entity_type="resource_distribution",
            metadata={
                "resource_type": allocation.resource_type,
                "total_available": allocation.total_available,
                "equity_score": allocation.equity_score
            }
        )
