"""
Tests for statistical analysis modules
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch

from features.analysis.retrospective import RetrospectiveAnalyzer
from features.analysis.prospective import ProspectiveAnalyzer


class TestRetrospectiveAnalyzer:
    """Tests for the RetrospectiveAnalyzer"""
    
    def setup_method(self):
        """Setup test data"""
        self.analyzer = RetrospectiveAnalyzer()
        
        # Create mock dataset for Cox regression
        np.random.seed(42)
        n = 100
        
        # Time to event data
        time = np.random.exponential(scale=30, size=n)
        
        # Censoring indicator (1=event, 0=censored)
        event = np.random.binomial(n=1, p=0.7, size=n)
        
        # Covariates
        age = np.random.normal(loc=65, scale=10, size=n)
        stage = np.random.choice([1, 2, 3, 4], size=n, p=[0.2, 0.3, 0.3, 0.2])
        treatment = np.random.choice([0, 1], size=n, p=[0.5, 0.5])
        
        self.df_cox = pd.DataFrame({
            'time': time,
            'event': event,
            'age': age,
            'stage': stage,
            'treatment': treatment
        })
        
        # Create mock dataset for logistic regression
        response = np.random.binomial(n=1, p=0.6, size=n)
        
        self.df_logistic = pd.DataFrame({
            'response': response,
            'age': age,
            'stage': stage,
            'treatment': treatment
        })
    
    def test_cox_regression(self):
        """Test Cox regression"""
        # Run Cox regression
        with patch('lifelines.CoxPHFitter.fit'):  # Mock the fit method
            results = self.analyzer.run_cox_regression(
                df=self.df_cox,
                time_column='time',
                event_column='event',
                covariates=['age', 'stage', 'treatment']
            )
        
        # Check results structure
        assert isinstance(results, dict)
        assert 'summary' in results
        assert 'concordance' in results
        assert 'interpretation' in results
    
    def test_logistic_regression(self):
        """Test logistic regression"""
        # Run logistic regression
        with patch('statsmodels.api.Logit.fit'):  # Mock the fit method
            results = self.analyzer.run_logistic_regression(
                df=self.df_logistic,
                outcome_column='response',
                covariates=['age', 'stage', 'treatment']
            )
        
        # Check results structure
        assert isinstance(results, dict)
        assert 'summary' in results
        assert 'auc' in results
        assert 'accuracy' in results
        assert 'interpretation' in results


class TestProspectiveAnalyzer:
    """Tests for the ProspectiveAnalyzer"""
    
    def setup_method(self):
        """Setup test data"""
        self.analyzer = ProspectiveAnalyzer()
        
        # Create mock dataset for Random Forest
        np.random.seed(42)
        n = 100
        
        # Outcome
        outcome = np.random.binomial(n=1, p=0.6, size=n)
        
        # Features
        age = np.random.normal(loc=65, scale=10, size=n)
        stage = np.random.choice([1, 2, 3, 4], size=n, p=[0.2, 0.3, 0.3, 0.2])
        comorbidity_count = np.random.poisson(lam=1.5, size=n)
        
        self.df_rf = pd.DataFrame({
            'outcome': outcome,
            'age': age,
            'stage': stage,
            'comorbidity_count': comorbidity_count
        })
        
        # Mock patient data
        self.patient_data = {
            'id': 'P12345',
            'age': 67,
            'tumor_stage': 'T2N0M0',
            'comorbidities': ['hypertension', 'diabetes'],
            'performance_status': 1
        }
    
    def test_random_forest(self):
        """Test Random Forest model"""
        # Run Random Forest
        with patch('sklearn.ensemble.RandomForestClassifier.fit'):  # Mock the fit method
            results = self.analyzer.run_random_forest(
                df=self.df_rf,
                outcome_column='outcome',
                feature_columns=['age', 'stage', 'comorbidity_count'],
                n_estimators=100,
                test_size=0.2
            )
        
        # Check results structure
        assert isinstance(results, dict)
        assert 'metrics' in results
        assert 'feature_importance' in results
        assert 'interpretation' in results
    
    def test_predict_random_forest(self):
        """Test prediction with Random Forest"""
        # Run prediction
        results = self.analyzer.predict(
            patient_data=self.patient_data,
            model_type='random_forest'
        )
        
        # Check results structure
        assert isinstance(results, dict)
        assert 'prediction' in results
        assert 'confidence' in results
        assert 'recommendations' in results
    
    def test_predict_reinforcement_learning(self):
        """Test prediction with Reinforcement Learning"""
        # Run prediction
        results = self.analyzer.predict(
            patient_data=self.patient_data,
            model_type='reinforcement_learning'
        )
        
        # Check results structure
        assert isinstance(results, dict)
        assert 'prediction' in results
        assert 'confidence' in results
        assert 'recommendations' in results
