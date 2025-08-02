"""
Unit tests for Protocols feature
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from feature.protocols.service import ProtocolService, ProtocolStatus, ProtocolType, DeviationType
from feature.protocols.flot_analyzer import FLOTAnalyzer


class TestProtocolService:
    """Test cases for ProtocolService"""
    
    @pytest.fixture
    def protocol_service(self):
        """Create ProtocolService instance for testing"""
        return ProtocolService()
    
    @pytest.fixture
    def sample_protocol_data(self):
        """Sample protocol data"""
        return {
            'name': 'FLOT-4 Modified',
            'type': ProtocolType.FLOT,
            'version': '1.0',
            'description': 'Modified FLOT protocol for gastric cancer',
            'parameters': {
                'cycle_duration_days': 14,
                'total_cycles': 8,
                'dosing': {
                    'fluorouracil': '2600 mg/m²',
                    'leucovorin': '200 mg/m²',
                    'oxaliplatin': '85 mg/m²',
                    'docetaxel': '50 mg/m²'
                }
            }
        }
    
    @pytest.fixture
    def sample_patient_treatment_data(self):
        """Sample patient treatment data for compliance checking"""
        return {
            'patient_id': 'P001',
            'protocol_id': 'PROT001',
            'treatment_cycles': [
                {
                    'cycle_number': 1,
                    'start_date': '2024-01-01',
                    'medications': {
                        'fluorouracil': {'dose': '2600 mg/m²', 'given': True},
                        'leucovorin': {'dose': '200 mg/m²', 'given': True},
                        'oxaliplatin': {'dose': '85 mg/m²', 'given': True},
                        'docetaxel': {'dose': '50 mg/m²', 'given': True}
                    },
                    'completed': True
                },
                {
                    'cycle_number': 2,
                    'start_date': '2024-01-15',
                    'medications': {
                        'fluorouracil': {'dose': '2600 mg/m²', 'given': True},
                        'leucovorin': {'dose': '200 mg/m²', 'given': True},
                        'oxaliplatin': {'dose': '68 mg/m²', 'given': True},  # Dose reduction
                        'docetaxel': {'dose': '50 mg/m²', 'given': True}
                    },
                    'completed': True,
                    'deviations': ['oxaliplatin_dose_reduction']
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_create_protocol(self, protocol_service, sample_protocol_data):
        """Test protocol creation"""
        with patch('feature.protocols.service.save_protocol_to_db') as mock_save:
            mock_save.return_value = {
                'id': 'PROT001',
                **sample_protocol_data,
                'status': ProtocolStatus.DRAFT,
                'created_at': datetime.now()
            }
            
            result = await protocol_service.create_protocol(sample_protocol_data)
            
            assert result is not None
            assert result['id'] == 'PROT001'
            assert result['name'] == 'FLOT-4 Modified'
            assert result['status'] == ProtocolStatus.DRAFT
    
    @pytest.mark.asyncio
    async def test_validate_compliance_full_compliance(self, protocol_service, sample_patient_treatment_data):
        """Test compliance validation with full compliance"""
        # Remove deviations for full compliance test
        sample_patient_treatment_data['treatment_cycles'][1].pop('deviations', None)
        
        with patch('feature.protocols.service.get_protocol_by_id') as mock_get_protocol:
            mock_protocol = {
                'id': 'PROT001',
                'type': ProtocolType.FLOT,
                'parameters': {
                    'cycle_duration_days': 14,
                    'dosing': {
                        'fluorouracil': '2600 mg/m²',
                        'leucovorin': '200 mg/m²',
                        'oxaliplatin': '85 mg/m²',
                        'docetaxel': '50 mg/m²'
                    }
                }
            }
            mock_get_protocol.return_value = mock_protocol
            
            result = await protocol_service.validate_compliance(
                protocol_id='PROT001',
                patient_data=sample_patient_treatment_data
            )
            
            assert result is not None
            assert result['compliance_score'] >= 0.95  # High compliance
            assert result['is_compliant'] is True
            assert len(result['deviations']) == 0
    
    @pytest.mark.asyncio
    async def test_validate_compliance_with_deviations(self, protocol_service, sample_patient_treatment_data):
        """Test compliance validation with protocol deviations"""
        with patch('feature.protocols.service.get_protocol_by_id') as mock_get_protocol:
            mock_protocol = {
                'id': 'PROT001',
                'type': ProtocolType.FLOT,
                'parameters': {
                    'cycle_duration_days': 14,
                    'dosing': {
                        'fluorouracil': '2600 mg/m²',
                        'leucovorin': '200 mg/m²',
                        'oxaliplatin': '85 mg/m²',
                        'docetaxel': '50 mg/m²'
                    }
                }
            }
            mock_get_protocol.return_value = mock_protocol
            
            result = await protocol_service.validate_compliance(
                protocol_id='PROT001',
                patient_data=sample_patient_treatment_data
            )
            
            assert result is not None
            assert result['compliance_score'] < 1.0  # Not perfect due to deviations
            assert len(result['deviations']) > 0
            assert any('oxaliplatin_dose_reduction' in str(dev) for dev in result['deviations'])
    
    @pytest.mark.asyncio
    async def test_track_deviations(self, protocol_service):
        """Test deviation tracking functionality"""
        deviation_data = {
            'protocol_id': 'PROT001',
            'patient_id': 'P001',
            'deviation_type': DeviationType.MAJOR,
            'description': 'Oxaliplatin dose reduced due to neuropathy',
            'cycle_number': 2,
            'justification': 'Patient safety due to grade 2 neuropathy'
        }
        
        with patch('feature.protocols.service.save_deviation_to_db') as mock_save:
            mock_save.return_value = {
                'id': 'DEV001',
                **deviation_data,
                'timestamp': datetime.now()
            }
            
            result = await protocol_service.track_deviations(deviation_data)
            
            assert result is not None
            assert result['id'] == 'DEV001'
            assert result['deviation_type'] == DeviationType.MAJOR
    
    @pytest.mark.asyncio
    async def test_generate_compliance_report(self, protocol_service):
        """Test compliance report generation"""
        protocol_id = 'PROT001'
        date_range = {
            'start_date': datetime.now() - timedelta(days=30),
            'end_date': datetime.now()
        }
        
        with patch('feature.protocols.service.get_compliance_data') as mock_get_data:
            mock_compliance_data = [
                {'patient_id': 'P001', 'compliance_score': 0.95},
                {'patient_id': 'P002', 'compliance_score': 0.88},
                {'patient_id': 'P003', 'compliance_score': 0.92}
            ]
            mock_get_data.return_value = mock_compliance_data
            
            report = await protocol_service.generate_compliance_report(
                protocol_id, 
                date_range
            )
            
            assert report is not None
            assert 'summary' in report
            assert 'patient_compliance' in report
            assert report['summary']['average_compliance'] > 0.8
            assert len(report['patient_compliance']) == 3
    
    def test_calculate_compliance_score(self, protocol_service):
        """Test compliance score calculation"""
        protocol_requirements = {
            'total_cycles': 8,
            'required_medications': 4,
            'timing_tolerance_hours': 24
        }
        
        patient_performance = {
            'completed_cycles': 7,
            'medication_adherence': 0.95,
            'timing_adherence': 0.88
        }
        
        score = protocol_service.calculate_compliance_score(
            protocol_requirements,
            patient_performance
        )
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    def test_classify_deviation_severity(self, protocol_service):
        """Test deviation severity classification"""
        test_cases = [
            {
                'deviation': 'dose_reduction_20_percent',
                'expected': DeviationType.MAJOR
            },
            {
                'deviation': 'timing_delay_2_hours',
                'expected': DeviationType.MINOR
            },
            {
                'deviation': 'treatment_discontinuation',
                'expected': DeviationType.CRITICAL
            }
        ]
        
        for case in test_cases:
            severity = protocol_service.classify_deviation_severity(case['deviation'])
            assert severity == case['expected']


class TestFLOTAnalyzer:
    """Test cases for FLOTAnalyzer"""
    
    @pytest.fixture
    def flot_analyzer(self):
        """Create FLOTAnalyzer instance"""
        return FLOTAnalyzer()
    
    @pytest.fixture
    def flot_patient_data(self):
        """FLOT-specific patient data"""
        return {
            'patient_id': 'P001',
            'diagnosis': 'gastric_adenocarcinoma',
            'stage': 'T3N2M0',
            'flot_cycles': [
                {
                    'cycle': 1,
                    'date': '2024-01-01',
                    'medications': {
                        'fluorouracil': {'dose_mg_m2': 2600, 'administered': True},
                        'leucovorin': {'dose_mg_m2': 200, 'administered': True},
                        'oxaliplatin': {'dose_mg_m2': 85, 'administered': True},
                        'docetaxel': {'dose_mg_m2': 50, 'administered': True}
                    },
                    'toxicities': [],
                    'performance_status': 1
                },
                {
                    'cycle': 2,
                    'date': '2024-01-15',
                    'medications': {
                        'fluorouracil': {'dose_mg_m2': 2600, 'administered': True},
                        'leucovorin': {'dose_mg_m2': 200, 'administered': True},
                        'oxaliplatin': {'dose_mg_m2': 68, 'administered': True},  # Reduced
                        'docetaxel': {'dose_mg_m2': 50, 'administered': True}
                    },
                    'toxicities': ['grade2_neuropathy'],
                    'performance_status': 1
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_analyze_adherence_high_adherence(self, flot_analyzer, flot_patient_data):
        """Test FLOT adherence analysis with high adherence"""
        result = await flot_analyzer.analyze_adherence(flot_patient_data)
        
        assert result is not None
        assert 'adherence_score' in result
        assert 'dose_intensity' in result
        assert 'cycle_completion_rate' in result
        assert 'toxicity_profile' in result
        
        # Should have reasonable adherence despite dose reduction
        assert result['adherence_score'] > 0.8
    
    @pytest.mark.asyncio
    async def test_calculate_dose_intensity(self, flot_analyzer, flot_patient_data):
        """Test dose intensity calculation"""
        dose_intensity = await flot_analyzer.calculate_dose_intensity(flot_patient_data)
        
        assert 'relative_dose_intensity' in dose_intensity
        assert 'by_medication' in dose_intensity
        
        # Check individual medication dose intensities
        for med in ['fluorouracil', 'leucovorin', 'oxaliplatin', 'docetaxel']:
            assert med in dose_intensity['by_medication']
            assert 0 <= dose_intensity['by_medication'][med] <= 1.0
    
    @pytest.mark.asyncio
    async def test_assess_toxicity_profile(self, flot_analyzer, flot_patient_data):
        """Test toxicity profile assessment"""
        toxicity_assessment = await flot_analyzer.assess_toxicity_profile(flot_patient_data)
        
        assert 'toxicity_grade' in toxicity_assessment
        assert 'affected_systems' in toxicity_assessment
        assert 'dose_modifications_recommended' in toxicity_assessment
        
        # Should identify neuropathy
        assert 'neuropathy' in str(toxicity_assessment['affected_systems'])
    
    def test_calculate_flot_compliance_score(self, flot_analyzer, flot_patient_data):
        """Test FLOT-specific compliance scoring"""
        compliance_score = flot_analyzer.calculate_flot_compliance_score(flot_patient_data)
        
        assert isinstance(compliance_score, float)
        assert 0.0 <= compliance_score <= 1.0
    
    def test_identify_dose_modifications(self, flot_analyzer, flot_patient_data):
        """Test dose modification identification"""
        modifications = flot_analyzer.identify_dose_modifications(flot_patient_data)
        
        assert isinstance(modifications, list)
        assert len(modifications) > 0  # Should identify oxaliplatin reduction
        
        # Check for oxaliplatin dose reduction
        oxaliplatin_mod = next(
            (mod for mod in modifications if 'oxaliplatin' in mod['medication']), 
            None
        )
        assert oxaliplatin_mod is not None
        assert oxaliplatin_mod['type'] == 'dose_reduction'
    
    @pytest.mark.asyncio
    async def test_predict_treatment_outcome(self, flot_analyzer, flot_patient_data):
        """Test treatment outcome prediction"""
        with patch('feature.protocols.flot_analyzer.ml_model_predict') as mock_predict:
            mock_predict.return_value = {
                'response_probability': 0.75,
                'toxicity_risk': 0.3,
                'completion_probability': 0.85
            }
            
            prediction = await flot_analyzer.predict_treatment_outcome(flot_patient_data)
            
            assert prediction is not None
            assert 'response_probability' in prediction
            assert 'toxicity_risk' in prediction
            assert 'completion_probability' in prediction
    
    def test_generate_flot_report(self, flot_analyzer, flot_patient_data):
        """Test FLOT analysis report generation"""
        report = flot_analyzer.generate_flot_report(flot_patient_data)
        
        assert 'patient_summary' in report
        assert 'adherence_analysis' in report
        assert 'toxicity_summary' in report
        assert 'recommendations' in report
        
        # Check patient summary
        assert report['patient_summary']['patient_id'] == 'P001'
        assert report['patient_summary']['total_cycles'] == 2
    
    def test_validate_flot_protocol_parameters(self, flot_analyzer):
        """Test FLOT protocol parameter validation"""
        valid_params = {
            'fluorouracil': 2600,
            'leucovorin': 200,
            'oxaliplatin': 85,
            'docetaxel': 50
        }
        
        invalid_params = {
            'fluorouracil': 3000,  # Too high
            'leucovorin': 150,     # Too low
            'oxaliplatin': 85,
            'docetaxel': 50
        }
        
        assert flot_analyzer.validate_protocol_parameters(valid_params) is True
        assert flot_analyzer.validate_protocol_parameters(invalid_params) is False
    
    @pytest.mark.asyncio
    async def test_recommend_dose_adjustments(self, flot_analyzer, flot_patient_data):
        """Test dose adjustment recommendations"""
        recommendations = await flot_analyzer.recommend_dose_adjustments(flot_patient_data)
        
        assert isinstance(recommendations, list)
        
        # Should recommend continuing current dose reduction for oxaliplatin
        oxaliplatin_rec = next(
            (rec for rec in recommendations if 'oxaliplatin' in rec['medication']),
            None
        )
        
        if oxaliplatin_rec:  # May not always have recommendations
            assert 'continue_reduction' in oxaliplatin_rec['action'] or 'maintain' in oxaliplatin_rec['action']


if __name__ == '__main__':
    pytest.main([__file__])
