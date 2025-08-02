"""
Unit tests for Analysis feature
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, AsyncMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from feature.analysis.analysis import AnalysisEngine
from feature.analysis.analysis_engine import AdvancedAnalysisEngine
from feature.analysis.impact_metrics import ImpactMetrics
from feature.analysis.surgery_analyzer import SurgeryAnalyzer


class TestAnalysisEngine:
    """Test cases for AnalysisEngine"""
    
    @pytest.fixture
    def analysis_engine(self):
        """Create AnalysisEngine instance for testing"""
        return AnalysisEngine()
    
    @pytest.fixture
    def sample_cohort_data(self):
        """Sample cohort data for testing"""
        return pd.DataFrame({
            'patient_id': [1, 2, 3, 4, 5],
            'age': [65, 72, 58, 69, 61],
            'stage': ['T2N0M0', 'T3N1M0', 'T1N0M0', 'T3N2M0', 'T2N1M0'],
            'treatment': ['surgery', 'neoadjuvant', 'surgery', 'neoadjuvant', 'surgery'],
            'outcome': [1, 1, 1, 0, 1]  # 1=success, 0=failure
        })
    
    @pytest.mark.asyncio
    async def test_analyze_cohort_basic(self, analysis_engine, sample_cohort_data):
        """Test basic cohort analysis"""
        result = await analysis_engine.analyze_cohort(sample_cohort_data)
        
        assert result is not None
        assert 'summary' in result
        assert 'statistics' in result
        assert result['summary']['total_patients'] == 5
    
    @pytest.mark.asyncio
    async def test_generate_insights_prospective(self, analysis_engine):
        """Test insights generation for prospective analysis"""
        test_data = {"sample": "test_data"}
        
        result = await analysis_engine.generate_insights(
            data=test_data,
            analysis_type="prospective"
        )
        
        assert result is not None
        assert 'analysis_id' in result
        assert 'results' in result
        assert 'metadata' in result
        assert result.get('reproducible') is True
    
    @pytest.mark.asyncio
    async def test_generate_insights_retrospective(self, analysis_engine):
        """Test insights generation for retrospective analysis"""
        test_data = {"historical": "data"}
        
        result = await analysis_engine.generate_insights(
            data=test_data,
            analysis_type="retrospective"
        )
        
        assert result is not None
        assert result['metadata']['analysis_type'] == "retrospective"
    
    def test_validate_cohort_data_valid(self, analysis_engine, sample_cohort_data):
        """Test cohort data validation with valid data"""
        is_valid = analysis_engine.validate_cohort_data(sample_cohort_data)
        assert is_valid is True
    
    def test_validate_cohort_data_missing_columns(self, analysis_engine):
        """Test cohort data validation with missing required columns"""
        invalid_data = pd.DataFrame({'only_id': [1, 2, 3]})
        is_valid = analysis_engine.validate_cohort_data(invalid_data)
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_calculate_outcomes_success_rate(self, analysis_engine, sample_cohort_data):
        """Test outcome calculations"""
        outcomes = await analysis_engine.calculate_outcomes(sample_cohort_data)
        
        assert 'success_rate' in outcomes
        assert 'confidence_interval' in outcomes
        assert 0 <= outcomes['success_rate'] <= 1


class TestAdvancedAnalysisEngine:
    """Test cases for AdvancedAnalysisEngine"""
    
    @pytest.fixture
    def advanced_engine(self):
        """Create AdvancedAnalysisEngine instance"""
        return AdvancedAnalysisEngine()
    
    @pytest.mark.asyncio
    async def test_survival_analysis(self, advanced_engine):
        """Test survival analysis functionality"""
        # Mock survival data
        survival_data = pd.DataFrame({
            'duration': [12, 24, 36, 18, 30],
            'event': [1, 0, 1, 1, 0],  # 1=death, 0=censored
            'treatment': ['A', 'B', 'A', 'B', 'A']
        })
        
        with patch('lifelines.CoxPHFitter') as mock_cox:
            mock_cox.return_value.fit.return_value = Mock()
            mock_cox.return_value.summary = pd.DataFrame({'coef': [0.5], 'p': [0.02]})
            
            result = await advanced_engine.perform_survival_analysis(survival_data)
            assert result is not None
            assert 'hazard_ratios' in result
    
    @pytest.mark.asyncio
    async def test_ml_prediction(self, advanced_engine):
        """Test machine learning prediction"""
        # Mock training data
        X = np.random.rand(100, 5)
        y = np.random.randint(0, 2, 100)
        
        with patch('sklearn.ensemble.RandomForestClassifier') as mock_rf:
            mock_rf.return_value.fit.return_value = Mock()
            mock_rf.return_value.predict_proba.return_value = np.array([[0.3, 0.7], [0.8, 0.2]])
            
            result = await advanced_engine.predict_outcomes(X, y)
            assert result is not None
            assert 'predictions' in result
            assert 'confidence' in result


class TestImpactMetrics:
    """Test cases for ImpactMetrics"""
    
    @pytest.fixture
    def impact_metrics(self):
        """Create ImpactMetrics instance"""
        return ImpactMetrics()
    
    def test_calculate_effectiveness_score(self, impact_metrics):
        """Test effectiveness score calculation"""
        treatment_outcomes = [1, 1, 0, 1, 1]  # 80% success
        control_outcomes = [1, 0, 0, 1, 0]    # 40% success
        
        score = impact_metrics.calculate_effectiveness_score(
            treatment_outcomes, 
            control_outcomes
        )
        
        assert score > 0  # Treatment should be more effective
        assert isinstance(score, float)
    
    def test_calculate_confidence_interval(self, impact_metrics):
        """Test confidence interval calculation"""
        data = [0.8, 0.75, 0.9, 0.85, 0.8]
        
        ci = impact_metrics.calculate_confidence_interval(data, confidence=0.95)
        
        assert 'lower' in ci
        assert 'upper' in ci
        assert ci['lower'] <= ci['upper']
        assert ci['lower'] >= 0
        assert ci['upper'] <= 1


class TestSurgeryAnalyzer:
    """Test cases for SurgeryAnalyzer"""
    
    @pytest.fixture
    def surgery_analyzer(self):
        """Create SurgeryAnalyzer instance"""
        return SurgeryAnalyzer()
    
    @pytest.fixture
    def surgery_data(self):
        """Sample surgery data"""
        return {
            'procedure_type': 'gastrectomy',
            'approach': 'laparoscopic',
            'duration_minutes': 180,
            'complications': [],
            'patient_age': 65,
            'comorbidities': ['diabetes']
        }
    
    @pytest.mark.asyncio
    async def test_analyze_surgical_outcome(self, surgery_analyzer, surgery_data):
        """Test surgical outcome analysis"""
        result = await surgery_analyzer.analyze_surgical_outcome(surgery_data)
        
        assert result is not None
        assert 'risk_score' in result
        assert 'recommended_approach' in result
        assert 'success_probability' in result
    
    @pytest.mark.asyncio
    async def test_preoperative_assessment(self, surgery_analyzer, surgery_data):
        """Test preoperative assessment"""
        patient_data = {
            'age': surgery_data['patient_age'],
            'comorbidities': surgery_data['comorbidities'],
            'performance_status': 'good'
        }
        
        assessment = await surgery_analyzer.assess_preoperative_risk(patient_data)
        
        assert 'risk_level' in assessment
        assert 'recommendations' in assessment
        assert assessment['risk_level'] in ['low', 'medium', 'high']
    
    def test_calculate_surgical_complexity_score(self, surgery_analyzer, surgery_data):
        """Test surgical complexity scoring"""
        complexity = surgery_analyzer.calculate_complexity_score(surgery_data)
        
        assert isinstance(complexity, (int, float))
        assert 0 <= complexity <= 10  # Assuming 0-10 scale


if __name__ == '__main__':
    pytest.main([__file__])
