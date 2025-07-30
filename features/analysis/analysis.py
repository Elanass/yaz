"""
Simplified Analysis Module - Gastric Surgery Decision Support
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class AnalysisEngine:
    """Consolidated analysis engine for surgical decision support"""
    
    def __init__(self):
        self.models = {}
        logger.info("Analysis engine initialized")
    
    def analyze(self, data: Dict[str, Any], analysis_type: str = "prospective") -> Dict[str, Any]:
        """
        Perform analysis on provided data
        
        Args:
            data: Analysis data
            analysis_type: "prospective" or "retrospective"
            
        Returns:
            Analysis results
        """
        if analysis_type == "prospective":
            return self._prospective_analysis(data)
        elif analysis_type == "retrospective":
            return self._retrospective_analysis(data)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    def _prospective_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Random Forest analysis for prospective prediction"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Separate features and target
            if 'outcome' in df.columns:
                X = df.drop('outcome', axis=1)
                y = df['outcome']
            else:
                raise ValueError("No outcome column found")
            
            # Train Random Forest
            rf = RandomForestClassifier(n_estimators=100, random_state=42)
            rf.fit(X, y)
            
            # Predictions and metrics
            y_pred = rf.predict(X)
            y_prob = rf.predict_proba(X)[:, 1]
            
            return {
                "model_type": "Random Forest",
                "accuracy": accuracy_score(y, y_pred),
                "auc": roc_auc_score(y, y_prob),
                "feature_importance": dict(zip(X.columns, rf.feature_importances_)),
                "summary": "Prospective analysis completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Prospective analysis failed: {e}")
            return {"error": str(e)}
    
    def _retrospective_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simplified retrospective analysis without Cox regression for now"""
        try:
            # For MVP, return a simplified analysis result
            # Can be enhanced later when scipy compatibility is resolved
            return {
                "model_type": "Simplified Retrospective Analysis",
                "summary": "Retrospective analysis placeholder - will be enhanced in future versions",
                "note": "Cox regression temporarily disabled due to library compatibility"
            }
            
        except Exception as e:
            logger.error(f"Retrospective analysis failed: {e}")
            return {"error": str(e)}
        if not self.validate_data(data, analysis_type):
            return {"error": "Invalid data for analysis", "type": analysis_type}
        
        if analysis_type == "prospective":
            return self._analyze_prospective(data)
        elif analysis_type == "retrospective":
            return self._analyze_retrospective(data)
        else:
            return {"error": f"Unsupported analysis type: {analysis_type}"}
    
    def validate_data(self, data: dict, analysis_type: str = "prospective") -> bool:
        """
        Validate input data for analysis.
        
        Args:
            data: Dictionary containing the data to validate
            analysis_type: Type of analysis to validate for
            
        Returns:
            Boolean indicating whether the data is valid
        """
        if analysis_type == "prospective":
            required_fields = ["features", "labels"]
        else:  # retrospective
            required_fields = ["patient_id", "outcome", "time_to_event"]
        
        return all(field in data for field in required_fields)
    
    def _analyze_prospective(self, data: dict) -> dict:
        """
        Perform prospective analysis using Random Forest.
        
        Args:
            data: Dictionary containing features and labels
            
        Returns:
            Dictionary with prospective analysis results
        """
        features = data.get("features", [])
        labels = data.get("labels", [])
        
        if not features or not labels:
            return {"error": "Empty features or labels"}
        
        try:
            # Convert to dataframes if needed
            if isinstance(features, list) and isinstance(features[0], dict):
                features_df = pd.DataFrame(features)
            elif isinstance(features, pd.DataFrame):
                features_df = features
            else:
                return {"error": "Unsupported features format"}
            
            # Prepare data
            X_train, X_test, y_train, y_test = train_test_split(
                features_df, labels, test_size=0.2, random_state=42
            )
            
            # Train model
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1] if len(set(labels)) == 2 else None
            
            # Get metrics
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, average='weighted'),
                "recall": recall_score(y_test, y_pred, average='weighted'),
                "f1": f1_score(y_test, y_pred, average='weighted')
            }
            
            if y_prob is not None:
                metrics["auc"] = roc_auc_score(y_test, y_prob)
            
            # Feature importance
            feature_imp = {
                "features": features_df.columns.tolist(),
                "importance": model.feature_importances_.tolist()
            }
            
            return {
                "metrics": metrics,
                "feature_importance": feature_imp,
                "type": "prospective",
                "model": "random_forest"
            }
            
        except Exception as e:
            logger.error(f"Error in prospective analysis: {str(e)}")
            return {"error": str(e), "type": "prospective"}
    
    def _analyze_retrospective(self, data: dict) -> dict:
        """
        Perform retrospective analysis using Cox and Logistic Regression.
        
        Args:
            data: Dictionary containing patient data with outcomes and time to events
            
        Returns:
            Dictionary with retrospective analysis results
        """
        try:
            # Extract data
            patient_ids = data.get("patient_id", [])
            outcomes = data.get("outcome", [])
            times = data.get("time_to_event", [])
            features_dict = data.get("features", {})
            
            # Create dataframe
            df = pd.DataFrame({
                "patient_id": patient_ids,
                "outcome": outcomes,
                "time": times
            })
            
            # Add features
            for feature, values in features_dict.items():
                if len(values) == len(patient_ids):
                    df[feature] = values
            
            # Cox regression for survival analysis
            cox_results = self._run_cox_regression(df)
            
            # Logistic regression for binary outcome prediction
            logreg_results = self._run_logistic_regression(df)
            
            return {
                "cox_regression": cox_results,
                "logistic_regression": logreg_results,
                "type": "retrospective"
            }
            
        except Exception as e:
            logger.error(f"Error in retrospective analysis: {str(e)}")
            return {"error": str(e), "type": "retrospective"}
    
    def _run_cox_regression(self, df: pd.DataFrame) -> dict:
        """Run Cox proportional hazards regression"""
        try:
            # Prepare data
            feature_cols = [col for col in df.columns 
                            if col not in ['patient_id', 'outcome', 'time']]
            
            # Create and fit Cox model
            cph = CoxPHFitter()
            cph.fit(df, duration_col='time', event_col='outcome', formula="+".join(feature_cols))
            
            # Extract results
            summary = cph.summary.to_dict()
            
            # Convert to serializable format
            results = {
                "coef": summary.get("coef", {}).values(),
                "exp_coef": summary.get("exp(coef)", {}).values(),
                "p_values": summary.get("p", {}).values(),
                "features": feature_cols
            }
            
            return results
        except Exception as e:
            logger.error(f"Error in Cox regression: {str(e)}")
            return {"error": str(e)}
    
    def _run_logistic_regression(self, df: pd.DataFrame) -> dict:
        """Run logistic regression for binary outcome prediction"""
        try:
            # Prepare data
            feature_cols = [col for col in df.columns 
                           if col not in ['patient_id', 'outcome', 'time']]
            X = df[feature_cols]
            y = df['outcome']
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Create and fit model
            logreg = LogisticRegression(max_iter=1000)
            logreg.fit(X_train_scaled, y_train)
            
            # Predictions
            y_pred = logreg.predict(X_test_scaled)
            y_prob = logreg.predict_proba(X_test_scaled)[:, 1]
            
            # Metrics
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred),
                "recall": recall_score(y_test, y_pred),
                "f1": f1_score(y_test, y_pred),
                "auc": roc_auc_score(y_test, y_prob)
            }
            
            # Coefficients
            coef_dict = {
                feature: coef for feature, coef in zip(feature_cols, logreg.coef_[0])
            }
            
            return {
                "metrics": metrics,
                "coefficients": coef_dict
            }
        except Exception as e:
            logger.error(f"Error in logistic regression: {str(e)}")
            return {"error": str(e)}
