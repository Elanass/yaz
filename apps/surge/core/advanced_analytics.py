"""
Advanced Analytics & Reporting for Surgical Outcomes
Kaplan-Meier survival curves, cohort comparisons, and cost-benefit analysis
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test, multivariate_logrank_test
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

class SurvivalAnalytics:
    """State-of-the-art survival analysis and cohort comparison"""
    
    def __init__(self):
        self.kmf = KaplanMeierFitter()
        self.cox_model = CoxPHFitter()
        
    async def kaplan_meier_analysis(self, 
                                   survival_data: pd.DataFrame,
                                   time_col: str = 'survival_months',
                                   event_col: str = 'death_event',
                                   group_col: Optional[str] = None) -> Dict[str, Any]:
        """Generate Kaplan-Meier survival curves with statistical analysis"""
        
        try:
            results = {
                'analysis_type': 'kaplan_meier',
                'timestamp': datetime.utcnow().isoformat(),
                'total_patients': len(survival_data),
                'median_followup': float(survival_data[time_col].median()),
                'curves': {},
                'statistics': {},
                'plot_data': {}
            }
            
            if group_col and group_col in survival_data.columns:
                # Multi-group survival analysis
                groups = survival_data[group_col].unique()
                survival_curves = {}
                
                for group in groups:
                    group_data = survival_data[survival_data[group_col] == group]
                    
                    # Fit Kaplan-Meier for this group
                    self.kmf.fit(
                        durations=group_data[time_col],
                        event_observed=group_data[event_col],
                        label=str(group)
                    )
                    
                    # Extract survival function
                    survival_function = self.kmf.survival_function_
                    
                    survival_curves[str(group)] = {
                        'timeline': survival_function.index.tolist(),
                        'survival_probability': survival_function.iloc[:, 0].tolist(),
                        'confidence_interval_lower': self.kmf.confidence_interval_.iloc[:, 0].tolist(),
                        'confidence_interval_upper': self.kmf.confidence_interval_.iloc[:, 1].tolist(),
                        'median_survival': float(self.kmf.median_survival_time_) if self.kmf.median_survival_time_ is not None else None,
                        'events': int(group_data[event_col].sum()),
                        'censored': int(len(group_data) - group_data[event_col].sum()),
                        'n_patients': len(group_data)
                    }
                
                results['curves'] = survival_curves
                
                # Log-rank test for group comparison
                if len(groups) == 2:
                    group1_data = survival_data[survival_data[group_col] == groups[0]]
                    group2_data = survival_data[survival_data[group_col] == groups[1]]
                    
                    log_rank_test = LogRankTest(
                        group1_data[time_col], group2_data[time_col],
                        group1_data[event_col], group2_data[event_col]
                    )
                    
                    results['statistics']['log_rank_test'] = {
                        'test_statistic': float(log_rank_test.test_statistic),
                        'p_value': float(log_rank_test.p_value),
                        'significant': log_rank_test.p_value < 0.05,
                        'groups_compared': [str(groups[0]), str(groups[1])]
                    }
                
                elif len(groups) > 2:
                    # Multivariate log-rank test
                    multivar_test = multivariate_logrank_test(
                        survival_data[time_col],
                        survival_data[group_col],
                        survival_data[event_col]
                    )
                    
                    results['statistics']['multivariate_log_rank'] = {
                        'test_statistic': float(multivar_test.test_statistic),
                        'p_value': float(multivar_test.p_value),
                        'significant': multivar_test.p_value < 0.05,
                        'degrees_of_freedom': int(multivar_test.degrees_of_freedom)
                    }
                
            else:
                # Single-group survival analysis
                self.kmf.fit(
                    durations=survival_data[time_col],
                    event_observed=survival_data[event_col],
                    label='Overall Survival'
                )
                
                survival_function = self.kmf.survival_function_
                
                results['curves']['overall'] = {
                    'timeline': survival_function.index.tolist(),
                    'survival_probability': survival_function.iloc[:, 0].tolist(),
                    'confidence_interval_lower': self.kmf.confidence_interval_.iloc[:, 0].tolist(),
                    'confidence_interval_upper': self.kmf.confidence_interval_.iloc[:, 1].tolist(),
                    'median_survival': float(self.kmf.median_survival_time_) if self.kmf.median_survival_time_ is not None else None,
                    'events': int(survival_data[event_col].sum()),
                    'censored': int(len(survival_data) - survival_data[event_col].sum()),
                    'n_patients': len(survival_data)
                }
            
            # Generate survival milestones
            results['milestones'] = await self._calculate_survival_milestones(results['curves'])
            
            # Generate plotly visualization data
            results['plot_data'] = await self._generate_survival_plot_data(results['curves'])
            
            logger.info(f"✅ Kaplan-Meier analysis completed for {len(survival_data)} patients")
            return results
            
        except Exception as e:
            logger.error(f"Error in Kaplan-Meier analysis: {str(e)}")
            raise
    
    async def cox_proportional_hazards(self, 
                                      survival_data: pd.DataFrame,
                                      time_col: str = 'survival_months',
                                      event_col: str = 'death_event',
                                      covariates: List[str] = None) -> Dict[str, Any]:
        """Cox Proportional Hazards model for multivariable survival analysis"""
        
        try:
            if covariates is None:
                covariates = ['age', 'tumor_stage_numeric', 'histology_grade', 'treatment_response']
            
            # Prepare data for Cox model
            cox_data = survival_data[[time_col, event_col] + covariates].copy()
            cox_data = cox_data.dropna()
            
            # Fit Cox model
            self.cox_model.fit(cox_data, duration_col=time_col, event_col=event_col)
            
            # Extract hazard ratios and confidence intervals
            hazard_ratios = {}
            for covariate in covariates:
                hr = float(np.exp(self.cox_model.params_[covariate]))
                ci_lower = float(np.exp(self.cox_model.confidence_intervals_.loc[covariate, 'lower 95%']))
                ci_upper = float(np.exp(self.cox_model.confidence_intervals_.loc[covariate, 'upper 95%']))
                p_value = float(self.cox_model.summary.loc[covariate, 'p'])
                
                hazard_ratios[covariate] = {
                    'hazard_ratio': hr,
                    'confidence_interval': [ci_lower, ci_upper],
                    'p_value': p_value,
                    'significant': p_value < 0.05,
                    'interpretation': 'increased risk' if hr > 1 else 'decreased risk' if hr < 1 else 'neutral'
                }
            
            # Model performance metrics
            concordance_index = float(self.cox_model.concordance_index_)
            log_likelihood = float(self.cox_model.log_likelihood_)
            
            results = {
                'analysis_type': 'cox_proportional_hazards',
                'timestamp': datetime.utcnow().isoformat(),
                'hazard_ratios': hazard_ratios,
                'model_performance': {
                    'concordance_index': concordance_index,
                    'log_likelihood': log_likelihood,
                    'n_patients': len(cox_data),
                    'n_events': int(cox_data[event_col].sum())
                },
                'covariates': covariates
            }
            
            logger.info(f"✅ Cox model fitted with C-index: {concordance_index:.3f}")
            return results
            
        except Exception as e:
            logger.error(f"Error in Cox analysis: {str(e)}")
            raise
    
    async def _calculate_survival_milestones(self, curves: Dict) -> Dict[str, Any]:
        """Calculate key survival milestones (1-year, 3-year, 5-year survival)"""
        milestones = {}
        
        for group_name, curve_data in curves.items():
            timeline = np.array(curve_data['timeline'])
            survival_prob = np.array(curve_data['survival_probability'])
            
            # Find survival probabilities at key timepoints
            timepoints = [12, 36, 60]  # 1, 3, 5 years in months
            survival_at_timepoints = {}
            
            for tp in timepoints:
                # Find closest timepoint
                if len(timeline) > 0 and tp <= timeline.max():
                    idx = np.argmin(np.abs(timeline - tp))
                    survival_at_timepoints[f'{tp//12}_year'] = float(survival_prob[idx])
                else:
                    survival_at_timepoints[f'{tp//12}_year'] = None
            
            milestones[group_name] = survival_at_timepoints
        
        return milestones
    
    async def _generate_survival_plot_data(self, curves: Dict) -> Dict[str, Any]:
        """Generate Plotly-compatible data for survival curve visualization"""
        
        plot_data = {
            'data': [],
            'layout': {
                'title': 'Kaplan-Meier Survival Curves',
                'xaxis': {'title': 'Time (months)'},
                'yaxis': {'title': 'Survival Probability'},
                'showlegend': True
            }
        }
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        for i, (group_name, curve_data) in enumerate(curves.items()):
            color = colors[i % len(colors)]
            
            # Main survival curve
            plot_data['data'].append({
                'x': curve_data['timeline'],
                'y': curve_data['survival_probability'],
                'type': 'scatter',
                'mode': 'lines',
                'name': f'{group_name} (n={curve_data["n_patients"]})',
                'line': {'color': color, 'width': 3}
            })
            
            # Confidence intervals
            plot_data['data'].append({
                'x': curve_data['timeline'] + curve_data['timeline'][::-1],
                'y': curve_data['confidence_interval_upper'] + curve_data['confidence_interval_lower'][::-1],
                'type': 'scatter',
                'mode': 'none',
                'fill': 'tonexty',
                'fillcolor': f'rgba{tuple(list(px.colors.hex_to_rgb(color)) + [0.2])}',
                'name': f'{group_name} 95% CI',
                'showlegend': False
            })
        
        return plot_data

    async def health_check(self) -> Dict:
        """Health check for survival analytics"""
        return {
            'status': 'healthy',
            'kmf_available': self.kmf is not None,
            'cox_model_available': self.cox_model is not None,
            'timestamp': datetime.utcnow().isoformat()
        }


class CohortComparison:
    """Advanced cohort comparison and statistical analysis"""
    
    def __init__(self):
        self.survival_analytics = SurvivalAnalytics()
    
    async def compare_treatment_cohorts(self, 
                                       cohort_data: pd.DataFrame,
                                       treatment_col: str = 'treatment_type',
                                       outcome_metrics: List[str] = None) -> Dict[str, Any]:
        """Comprehensive comparison between treatment cohorts"""
        
        if outcome_metrics is None:
            outcome_metrics = ['survival_months', 'complication_rate', 'readmission_rate', 'length_of_stay']
        
        try:
            treatments = cohort_data[treatment_col].unique()
            comparison_results = {
                'analysis_type': 'cohort_comparison',
                'timestamp': datetime.utcnow().isoformat(),
                'treatments_compared': treatments.tolist(),
                'total_patients': len(cohort_data),
                'cohort_sizes': {},
                'outcome_comparisons': {},
                'survival_analysis': {},
                'statistical_tests': {}
            }
            
            # Calculate cohort sizes
            for treatment in treatments:
                comparison_results['cohort_sizes'][treatment] = len(
                    cohort_data[cohort_data[treatment_col] == treatment]
                )
            
            # Compare outcomes across cohorts
            for metric in outcome_metrics:
                if metric in cohort_data.columns:
                    comparison_results['outcome_comparisons'][metric] = await self._compare_metric_across_cohorts(
                        cohort_data, treatment_col, metric
                    )
            
            # Survival analysis by treatment
            if 'survival_months' in cohort_data.columns and 'death_event' in cohort_data.columns:
                survival_results = await self.survival_analytics.kaplan_meier_analysis(
                    cohort_data, 
                    time_col='survival_months',
                    event_col='death_event',
                    group_col=treatment_col
                )
                comparison_results['survival_analysis'] = survival_results
            
            # Propensity score matching (simplified)
            if len(treatments) == 2:
                matched_results = await self._propensity_score_matching(cohort_data, treatment_col)
                comparison_results['propensity_matching'] = matched_results
            
            logger.info(f"✅ Cohort comparison completed for {len(treatments)} treatment groups")
            return comparison_results
            
        except Exception as e:
            logger.error(f"Error in cohort comparison: {str(e)}")
            raise
    
    async def _compare_metric_across_cohorts(self, 
                                           data: pd.DataFrame,
                                           group_col: str,
                                           metric_col: str) -> Dict[str, Any]:
        """Statistical comparison of a metric across cohorts"""
        
        from scipy import stats
        
        groups = data[group_col].unique()
        group_data = {}
        
        # Calculate descriptive statistics for each group
        for group in groups:
            group_values = data[data[group_col] == group][metric_col].dropna()
            group_data[str(group)] = {
                'mean': float(group_values.mean()),
                'median': float(group_values.median()),
                'std': float(group_values.std()),
                'n': len(group_values),
                'min': float(group_values.min()),
                'max': float(group_values.max()),
                'q25': float(group_values.quantile(0.25)),
                'q75': float(group_values.quantile(0.75))
            }
        
        # Statistical tests
        if len(groups) == 2:
            # Two-sample t-test
            group1_data = data[data[group_col] == groups[0]][metric_col].dropna()
            group2_data = data[data[group_col] == groups[1]][metric_col].dropna()
            
            t_stat, t_pvalue = stats.ttest_ind(group1_data, group2_data)
            
            # Mann-Whitney U test (non-parametric)
            u_stat, u_pvalue = stats.mannwhitneyu(group1_data, group2_data)
            
            statistical_tests = {
                't_test': {
                    'statistic': float(t_stat),
                    'p_value': float(t_pvalue),
                    'significant': t_pvalue < 0.05
                },
                'mann_whitney': {
                    'statistic': float(u_stat),
                    'p_value': float(u_pvalue),
                    'significant': u_pvalue < 0.05
                }
            }
        else:
            # ANOVA for multiple groups
            group_values = [data[data[group_col] == group][metric_col].dropna() for group in groups]
            f_stat, f_pvalue = stats.f_oneway(*group_values)
            
            # Kruskal-Wallis test (non-parametric)
            h_stat, h_pvalue = stats.kruskal(*group_values)
            
            statistical_tests = {
                'anova': {
                    'statistic': float(f_stat),
                    'p_value': float(f_pvalue),
                    'significant': f_pvalue < 0.05
                },
                'kruskal_wallis': {
                    'statistic': float(h_stat),
                    'p_value': float(h_pvalue),
                    'significant': h_pvalue < 0.05
                }
            }
        
        return {
            'group_statistics': group_data,
            'statistical_tests': statistical_tests,
            'metric': metric_col
        }
    
    async def _propensity_score_matching(self, 
                                        data: pd.DataFrame,
                                        treatment_col: str) -> Dict[str, Any]:
        """Simplified propensity score matching for treatment effect estimation"""
        
        # This is a simplified version - in production, use proper PSM libraries
        try:
            treatments = data[treatment_col].unique()
            if len(treatments) != 2:
                return {'error': 'Propensity score matching requires exactly 2 treatment groups'}
            
            # Create binary treatment variable
            treatment_binary = (data[treatment_col] == treatments[1]).astype(int)
            
            # Use available covariates for matching
            covariate_cols = ['age', 'gender_numeric', 'comorbidity_count']
            available_covariates = [col for col in covariate_cols if col in data.columns]
            
            if not available_covariates:
                return {'error': 'No suitable covariates found for propensity score matching'}
            
            # Simple matching based on available covariates
            matched_pairs = []
            treated_group = data[data[treatment_col] == treatments[1]]
            control_group = data[data[treatment_col] == treatments[0]]
            
            # Calculate propensity scores (simplified)
            from sklearn.linear_model import LogisticRegression
            from sklearn.preprocessing import StandardScaler
            
            X = data[available_covariates].fillna(data[available_covariates].mean())
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            lr = LogisticRegression()
            lr.fit(X_scaled, treatment_binary)
            propensity_scores = lr.predict_proba(X_scaled)[:, 1]
            
            # Add propensity scores to data
            data_with_ps = data.copy()
            data_with_ps['propensity_score'] = propensity_scores
            
            # Simple nearest neighbor matching
            treated_with_ps = data_with_ps[data_with_ps[treatment_col] == treatments[1]]
            control_with_ps = data_with_ps[data_with_ps[treatment_col] == treatments[0]]
            
            matched_treated = []
            matched_control = []
            
            for _, treated_patient in treated_with_ps.iterrows():
                # Find closest control based on propensity score
                ps_diff = np.abs(control_with_ps['propensity_score'] - treated_patient['propensity_score'])
                if len(ps_diff) > 0:
                    closest_idx = ps_diff.idxmin()
                    closest_control = control_with_ps.loc[closest_idx]
                    
                    if ps_diff[closest_idx] < 0.1:  # Caliper of 0.1
                        matched_treated.append(treated_patient)
                        matched_control.append(closest_control)
                        # Remove matched control to avoid replacement
                        control_with_ps = control_with_ps.drop(closest_idx)
            
            return {
                'matched_pairs': len(matched_treated),
                'original_treated': len(treated_group),
                'original_control': len(control_group),
                'matching_rate': len(matched_treated) / len(treated_group) if len(treated_group) > 0 else 0,
                'covariates_used': available_covariates,
                'method': 'nearest_neighbor_with_caliper'
            }
            
        except Exception as e:
            logger.error(f"Error in propensity score matching: {str(e)}")
            return {'error': str(e)}


# Global analytics instance
advanced_analytics = SurvivalAnalytics()
cohort_comparison = CohortComparison()
