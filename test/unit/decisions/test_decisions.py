"""
Unit tests for Decisions feature
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from feature.decisions.service import DecisionService
from feature.decisions.base_decision_engine import BaseDecisionEngine
from feature.decisions.adci_engine import ADCIEngine
from feature.decisions.precision_engine import PrecisionEngine


class TestDecisionService:
    """Test cases for DecisionService"""
    
    @pytest.fixture
    def decision_service(self):
        """Create DecisionService instance for testing"""
        return DecisionService()
    
    @pytest.fixture
    def sample_patient_data(self):
        """Sample patient data for testing"""
        return {
            'patient_id': 'P001',
            'age': 65,
            'gender': 'M',
            'stage': 'T2N1M0',
            'grade': 'G2',
            'location': 'antrum',
            'comorbidities': ['diabetes', 'hypertension'],
            'performance_status': 1,
            'imaging_results': {
                'ct_scan': 'resectable',
                'pet_scan': 'no_distant_metastases'
            }
        }
    
    @pytest.mark.asyncio
    async def test_make_decision_adci_engine(self, decision_service, sample_patient_data):
        """Test decision making with ADCI engine"""
        with patch.object(decision_service, '_get_engine') as mock_get_engine:
            mock_engine = Mock()
            mock_engine.make_decision = AsyncMock(return_value={
                'recommendation': 'surgical_resection',
                'confidence_score': 0.85,
                'reasoning': 'Patient is suitable for surgery based on staging and fitness',
                'alternatives': ['neoadjuvant_therapy']
            })
            mock_get_engine.return_value = mock_engine
            
            result = await decision_service.make_decision(
                patient_data=sample_patient_data,
                engine_type='adci'
            )
            
            assert result is not None
            assert result['recommendation'] == 'surgical_resection'
            assert result['confidence_score'] == 0.85
            assert 'reasoning' in result
    
    @pytest.mark.asyncio
    async def test_make_decision_precision_engine(self, decision_service, sample_patient_data):
        """Test decision making with Precision engine"""
        with patch.object(decision_service, '_get_engine') as mock_get_engine:
            mock_engine = Mock()
            mock_engine.make_decision = AsyncMock(return_value={
                'recommendation': 'neoadjuvant_chemotherapy',
                'confidence_score': 0.92,
                'reasoning': 'High-precision analysis suggests neoadjuvant approach',
                'risk_assessment': 'medium'
            })
            mock_get_engine.return_value = mock_engine
            
            result = await decision_service.make_decision(
                patient_data=sample_patient_data,
                engine_type='precision'
            )
            
            assert result is not None
            assert result['recommendation'] == 'neoadjuvant_chemotherapy'
            assert result['confidence_score'] == 0.92
    
    @pytest.mark.asyncio
    async def test_calculate_confidence_score(self, decision_service, sample_patient_data):
        """Test confidence score calculation"""
        decision_factors = {
            'stage_certainty': 0.9,
            'imaging_quality': 0.85,
            'patient_fitness': 0.8,
            'evidence_strength': 0.88
        }
        
        confidence = await decision_service.calculate_confidence(decision_factors)
        
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_get_decision_history(self, decision_service):
        """Test retrieving decision history"""
        patient_id = 'P001'
        
        with patch('feature.decisions.service.get_decision_history_from_db') as mock_get_history:
            mock_history = [
                {
                    'decision_id': 'D001',
                    'timestamp': datetime.now(),
                    'recommendation': 'surgical_resection',
                    'confidence_score': 0.85
                },
                {
                    'decision_id': 'D002',
                    'timestamp': datetime.now(),
                    'recommendation': 'follow_up',
                    'confidence_score': 0.78
                }
            ]
            mock_get_history.return_value = mock_history
            
            history = await decision_service.get_decision_history(patient_id)
            
            assert len(history) == 2
            assert history[0]['decision_id'] == 'D001'
            assert history[1]['recommendation'] == 'follow_up'
    
    def test_validate_patient_data_valid(self, decision_service, sample_patient_data):
        """Test patient data validation with valid data"""
        is_valid = decision_service.validate_patient_data(sample_patient_data)
        assert is_valid is True
    
    def test_validate_patient_data_missing_required(self, decision_service):
        """Test patient data validation with missing required fields"""
        incomplete_data = {
            'patient_id': 'P001',
            'age': 65
            # Missing required fields
        }
        
        is_valid = decision_service.validate_patient_data(incomplete_data)
        assert is_valid is False


class TestBaseDecisionEngine:
    """Test cases for BaseDecisionEngine"""
    
    @pytest.fixture
    def base_engine(self):
        """Create BaseDecisionEngine instance"""
        return BaseDecisionEngine()
    
    def test_validate_input_valid(self, base_engine):
        """Test input validation with valid data"""
        valid_data = {
            'patient_id': 'P001',
            'age': 65,
            'stage': 'T2N1M0'
        }
        
        result = base_engine.validate_input(valid_data)
        assert result is True
    
    def test_validate_input_invalid(self, base_engine):
        """Test input validation with invalid data"""
        invalid_data = {
            'patient_id': '',  # Empty patient ID
            'age': -5,         # Invalid age
        }
        
        result = base_engine.validate_input(invalid_data)
        assert result is False
    
    def test_format_result(self, base_engine):
        """Test result formatting"""
        raw_result = {
            'recommendation': 'surgery',
            'confidence': 0.85
        }
        
        formatted = base_engine.format_result(raw_result)
        
        assert 'recommendation' in formatted
        assert 'confidence_score' in formatted
        assert 'timestamp' in formatted
        assert isinstance(formatted['timestamp'], datetime)


class TestADCIEngine:
    """Test cases for ADCIEngine"""
    
    @pytest.fixture
    def adci_engine(self):
        """Create ADCIEngine instance"""
        return ADCIEngine()
    
    @pytest.fixture
    def adci_patient_data(self):
        """ADCI-specific patient data"""
        return {
            'patient_id': 'P001',
            'age': 65,
            'stage': 'T2N1M0',
            'grade': 'G2',
            'performance_status': 1,
            'comorbidities': ['diabetes'],
            'tumor_size': 4.5,
            'lymph_nodes_positive': 2,
            'preoperative_albumin': 3.8,
            'hemoglobin': 12.5
        }
    
    @pytest.mark.asyncio
    async def test_make_decision_surgical_candidate(self, adci_engine, adci_patient_data):
        """Test ADCI decision for surgical candidate"""
        result = await adci_engine.make_decision(adci_patient_data)
        
        assert result is not None
        assert 'recommendation' in result
        assert 'confidence_score' in result
        assert 'adci_score' in result
        assert 'risk_factors' in result
        
        # ADCI score should be within valid range
        assert 0 <= result['adci_score'] <= 100
    
    def test_calculate_adci_score(self, adci_engine, adci_patient_data):
        """Test ADCI score calculation"""
        score = adci_engine.calculate_adci_score(adci_patient_data)
        
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100
    
    def test_assess_surgical_risk(self, adci_engine, adci_patient_data):
        """Test surgical risk assessment"""
        risk_assessment = adci_engine.assess_surgical_risk(adci_patient_data)
        
        assert 'risk_level' in risk_assessment
        assert 'risk_factors' in risk_assessment
        assert risk_assessment['risk_level'] in ['low', 'medium', 'high']
    
    def test_determine_treatment_pathway(self, adci_engine, adci_patient_data):
        """Test treatment pathway determination"""
        pathway = adci_engine.determine_treatment_pathway(adci_patient_data)
        
        assert pathway in [
            'immediate_surgery',
            'neoadjuvant_therapy',
            'palliative_care',
            'additional_staging'
        ]
    
    def test_calculate_confidence_factors(self, adci_engine, adci_patient_data):
        """Test confidence factor calculation"""
        factors = adci_engine.calculate_confidence_factors(adci_patient_data)
        
        assert 'staging_confidence' in factors
        assert 'fitness_assessment' in factors
        assert 'imaging_quality' in factors
        
        for factor_value in factors.values():
            assert 0 <= factor_value <= 1


class TestPrecisionEngine:
    """Test cases for PrecisionEngine"""
    
    @pytest.fixture
    def precision_engine(self):
        """Create PrecisionEngine instance"""
        return PrecisionEngine()
    
    @pytest.fixture
    def precision_patient_data(self):
        """Precision engine patient data with additional biomarkers"""
        return {
            'patient_id': 'P001',
            'age': 65,
            'stage': 'T2N1M0',
            'biomarkers': {
                'her2_status': 'positive',
                'msi_status': 'stable',
                'pd_l1_expression': 15
            },
            'genomic_data': {
                'mutations': ['TP53', 'PIK3CA'],
                'tumor_mutational_burden': 8.5
            },
            'imaging_features': {
                'radiomics_score': 0.75,
                'perfusion_parameters': {'ktrans': 0.3}
            }
        }
    
    @pytest.mark.asyncio
    async def test_make_precision_decision(self, precision_engine, precision_patient_data):
        """Test precision decision making"""
        with patch.object(precision_engine, '_run_ml_models') as mock_ml:
            mock_ml.return_value = {
                'survival_prediction': 0.82,
                'response_probability': 0.77,
                'feature_importance': {'age': 0.3, 'stage': 0.4}
            }
            
            result = await precision_engine.make_decision(precision_patient_data)
            
            assert result is not None
            assert 'recommendation' in result
            assert 'confidence_score' in result
            assert 'precision_metrics' in result
            assert 'uncertainty_bounds' in result
    
    @pytest.mark.asyncio
    async def test_analyze_biomarkers(self, precision_engine, precision_patient_data):
        """Test biomarker analysis"""
        analysis = await precision_engine.analyze_biomarkers(
            precision_patient_data['biomarkers']
        )
        
        assert 'targeted_therapy_eligible' in analysis
        assert 'immunotherapy_score' in analysis
        assert 'resistance_markers' in analysis
    
    def test_calculate_uncertainty_bounds(self, precision_engine):
        """Test uncertainty bound calculation"""
        predictions = np.array([0.8, 0.75, 0.9, 0.82, 0.78])
        
        bounds = precision_engine.calculate_uncertainty_bounds(predictions)
        
        assert 'lower_bound' in bounds
        assert 'upper_bound' in bounds
        assert bounds['lower_bound'] <= bounds['upper_bound']
    
    @pytest.mark.asyncio
    async def test_sensitivity_analysis(self, precision_engine, precision_patient_data):
        """Test sensitivity analysis"""
        with patch.object(precision_engine, '_run_ml_models') as mock_ml:
            # Simulate different predictions for parameter variations
            mock_ml.side_effect = [
                {'survival_prediction': 0.82},
                {'survival_prediction': 0.80},
                {'survival_prediction': 0.84}
            ]
            
            sensitivity = await precision_engine.perform_sensitivity_analysis(
                precision_patient_data
            )
            
            assert 'parameter_sensitivity' in sensitivity
            assert 'robust_prediction' in sensitivity
            assert isinstance(sensitivity['parameter_sensitivity'], dict)


if __name__ == '__main__':
    pytest.main([__file__])
