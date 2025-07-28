"""
Retrospective Analysis Module

This module provides retrospective analysis tools for gastric cancer data
using Cox Proportional Hazards and Logistic Regression models.
"""

import pandas as pd
import numpy as np
from lifelines import CoxPHFitter
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional, Tuple, Any
import os
import json

from core.services.logger import get_logger

logger = get_logger(__name__)

class RetrospectiveAnalyzer:
    """
    Performs retrospective analysis on gastric cancer datasets using
    statistical survival analysis and regression techniques.
    """
    
    def __init__(self, csv_path: str = "data/cases.csv"):
        """
        Initialize the retrospective analyzer with a dataset
        
        Args:
            csv_path: Path to the CSV file containing patient data
        """
        self.csv_path = csv_path
        self._load_data()
        
    def _load_data(self) -> None:
        """Load the dataset from CSV"""
        try:
            if os.path.exists(self.csv_path):
                self.df = pd.read_csv(self.csv_path)
                logger.info(f"Loaded data from {self.csv_path}, {len(self.df)} records")
            else:
                # Create empty dataframe with expected columns for testing/development
                self.df = pd.DataFrame(columns=[
                    "Age", "Sex", "WHO PS", "T-stage", "N-stage", "M-stage", 
                    "Primary Treatment", "Vital Status", "Observation_time",
                    "HER2 Status", "Regression"
                ])
                logger.warning(f"CSV file {self.csv_path} not found, created empty dataframe")
        except Exception as e:
            logger.error(f"Error loading data from {self.csv_path}: {str(e)}")
            # Create empty dataframe
            self.df = pd.DataFrame()
    
    def prepare_data(self) -> pd.DataFrame:
        """
        Prepare data for statistical analysis
        
        Returns:
            DataFrame with processed data ready for analysis
        """
        if self.df.empty:
            logger.warning("Empty dataframe, no data to prepare")
            return pd.DataFrame()
            
        try:
            # Make a copy to avoid modifying the original
            df = self.df.copy()
            
            # Filter complete cases for survival analysis
            required_cols = ["Vital Status", "Observation_time", "Primary Treatment", 
                           "Age", "WHO PS", "T-stage"]
            
            df = df.dropna(subset=required_cols)
            
            # Create event indicator (1=deceased, 0=alive)
            df["event"] = df["Vital Status"].map({"Deceased": 1, "Alive": 0})
            
            # Encode treatment variable
            treatment_map = {
                "surgery-first": 0,
                "flot-first": 1,
                "other": 2
            }
            
            # Default unmapped values to 'other'
            df["treatment_bin"] = df["Primary Treatment"].apply(
                lambda x: treatment_map.get(x, 2) if pd.notna(x) else None
            )
            
            # Encode T-stage (T1-T4)
            t_stage_map = {
                "T1": 1, "T2": 2, "T3": 3, "T4": 4, 
                "T1a": 1, "T1b": 1, "T4a": 4, "T4b": 4
            }
            
            df["t_stage_num"] = df["T-stage"].apply(
                lambda x: t_stage_map.get(x, None) if pd.notna(x) else None
            )
            
            # Encode WHO PS (0-4)
            df["who_ps_num"] = pd.to_numeric(df["WHO PS"], errors="coerce")
            
            logger.info(f"Data prepared: {len(df)} complete records after filtering")
            return df
            
        except Exception as e:
            logger.error(f"Error preparing data: {str(e)}")
            return pd.DataFrame()
    
    def cox_model(self) -> Dict[str, Any]:
        """
        Fit a Cox Proportional Hazards model for survival analysis
        
        Returns:
            Dictionary with model summary and statistics
        """
        try:
            df = self.prepare_data()
            
            if df.empty:
                return {"error": "Insufficient data for Cox model"}
            
            # Select variables for the model
            covariates = [
                "Observation_time", 
                "event", 
                "Age", 
                "who_ps_num", 
                "t_stage_num", 
                "treatment_bin"
            ]
            
            # Filter complete cases for these variables
            model_df = df[covariates].dropna()
            
            if len(model_df) < 10:  # Minimum sample size for reasonable model
                return {"error": "Insufficient complete cases for Cox model"}
            
            # Fit the Cox model
            cph = CoxPHFitter()
            cph.fit(model_df, duration_col="Observation_time", event_col="event")
            
            # Extract summary statistics
            summary = cph.summary
            
            # Convert to serializable dictionary
            result = {
                "coefficients": {},
                "p_values": {},
                "hazard_ratios": {},
                "confidence_intervals": {}
            }
            
            for var in summary.index:
                result["coefficients"][var] = float(summary.loc[var, "coef"])
                result["p_values"][var] = float(summary.loc[var, "p"])
                result["hazard_ratios"][var] = float(np.exp(summary.loc[var, "coef"]))
                result["confidence_intervals"][var] = [
                    float(summary.loc[var, "coef lower 95%"]),
                    float(summary.loc[var, "coef upper 95%"])
                ]
            
            # Add model metrics
            result["concordance_index"] = float(cph.concordance_index_)
            result["log_likelihood"] = float(cph.log_likelihood_)
            result["sample_size"] = int(len(model_df))
            
            logger.info(f"Cox model fitted successfully with {len(model_df)} observations")
            return result
            
        except Exception as e:
            logger.error(f"Error in Cox model: {str(e)}")
            return {"error": str(e)}
    
    def logistic_model(self) -> Dict[str, Any]:
        """
        Fit a Logistic Regression model for binary outcome prediction
        
        Returns:
            Dictionary with model coefficients and statistics
        """
        try:
            df = self.prepare_data()
            
            if df.empty:
                return {"error": "Insufficient data for Logistic model"}
            
            # Select predictor variables
            predictors = ["Age", "who_ps_num", "t_stage_num", "treatment_bin"]
            
            # Outcome variable (mortality)
            outcome = "event"
            
            # Filter complete cases
            model_df = df[predictors + [outcome]].dropna()
            
            if len(model_df) < 10:  # Minimum sample size
                return {"error": "Insufficient complete cases for Logistic model"}
            
            # Standardize predictors
            scaler = StandardScaler()
            X = pd.DataFrame(
                scaler.fit_transform(model_df[predictors]),
                columns=predictors
            )
            y = model_df[outcome]
            
            # Fit logistic regression
            model = LogisticRegression(max_iter=1000, random_state=42)
            model.fit(X, y)
            
            # Prepare results
            result = {
                "coefficients": dict(zip(predictors, model.coef_[0].tolist())),
                "intercept": float(model.intercept_[0]),
                "odds_ratios": dict(zip(predictors, np.exp(model.coef_[0]).tolist())),
                "score": float(model.score(X, y)),
                "sample_size": int(len(model_df))
            }
            
            logger.info(f"Logistic model fitted successfully with {len(model_df)} observations")
            return result
            
        except Exception as e:
            logger.error(f"Error in Logistic model: {str(e)}")
            return {"error": str(e)}
    
    def combined_analysis(self) -> Dict[str, Any]:
        """
        Perform both Cox and Logistic regression analysis
        
        Returns:
            Dictionary with results from both models
        """
        return {
            "cox_model": self.cox_model(),
            "logistic_model": self.logistic_model()
        }
    
    def model_comparison(self) -> Dict[str, Any]:
        """
        Compare different models and approaches
        
        Returns:
            Dictionary with model comparison metrics
        """
        cox_results = self.cox_model()
        logistic_results = self.logistic_model()
        
        # Extract key features from both models
        comparison = {
            "sample_size": {
                "cox": cox_results.get("sample_size", 0),
                "logistic": logistic_results.get("sample_size", 0)
            },
            "key_factors": {
                "cox": {},
                "logistic": {}
            },
            "performance": {
                "cox": cox_results.get("concordance_index", 0),
                "logistic": logistic_results.get("score", 0)
            }
        }
        
        # Identify key factors from Cox model
        if "coefficients" in cox_results:
            # Sort by absolute coefficient size
            cox_coefs = cox_results["coefficients"]
            sorted_cox = sorted(cox_coefs.items(), key=lambda x: abs(x[1]), reverse=True)
            comparison["key_factors"]["cox"] = dict(sorted_cox)
        
        # Identify key factors from Logistic model
        if "coefficients" in logistic_results:
            # Sort by absolute coefficient size
            logistic_coefs = logistic_results["coefficients"]
            sorted_logistic = sorted(logistic_coefs.items(), key=lambda x: abs(x[1]), reverse=True)
            comparison["key_factors"]["logistic"] = dict(sorted_logistic)
        
        return comparison
