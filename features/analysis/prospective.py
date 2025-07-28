"""
Prospective Analysis Module

This module provides prospective analysis tools for gastric cancer data
using Random Forest and other machine learning models.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, KFold, train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from typing import Dict, List, Optional, Tuple, Any
import os
import pickle
import json

from core.services.logger import get_logger

logger = get_logger(__name__)

class ProspectiveAnalyzer:
    """
    Performs prospective analysis on gastric cancer datasets using
    machine learning for decision support.
    """
    
    def __init__(self, csv_path: str = "data/cases.csv", model_path: str = "data/models"):
        """
        Initialize the prospective analyzer with a dataset
        
        Args:
            csv_path: Path to the CSV file containing patient data
            model_path: Directory to save/load trained models
        """
        self.csv_path = csv_path
        self.model_path = model_path
        self._load_data()
        
        # Ensure model directory exists
        os.makedirs(self.model_path, exist_ok=True)
        
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
    
    def prepare_features(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features for machine learning models
        
        Returns:
            Tuple of (X, y) where X is feature matrix and y is target vector
        """
        if self.df.empty:
            logger.warning("Empty dataframe, no data to prepare")
            return pd.DataFrame(), pd.Series()
            
        try:
            # Make a copy to avoid modifying the original
            df = self.df.copy()
            
            # Filter relevant columns for prediction
            required_cols = ["Age", "WHO PS", "T-stage", "Primary Treatment", 
                           "Vital Status", "HER2 Status"]
            
            df = df.dropna(subset=required_cols)
            
            # Target variable: mortality (1=deceased, 0=alive)
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
            
            # Encode HER2 Status
            her2_map = {"Positive": 1, "Negative": 0}
            df["her2_bin"] = df["HER2 Status"].map(her2_map)
            
            # Handle Regression (pathologic response if available)
            if "Regression" in df.columns:
                # Assume Regression is a percentage value or categorical value
                df["regression_value"] = pd.to_numeric(df["Regression"], errors="coerce")
            else:
                df["regression_value"] = np.nan
            
            # Feature matrix X and target variable y
            features = ["Age", "who_ps_num", "t_stage_num", "her2_bin", "treatment_bin"]
            if df["regression_value"].notna().sum() > len(df) * 0.5:  # If regression available for >50%
                features.append("regression_value")
                
            X = df[features].copy()
            y = df["event"]
            
            logger.info(f"Features prepared: {X.shape[1]} features, {len(X)} samples")
            return X, y
            
        except Exception as e:
            logger.error(f"Error preparing features: {str(e)}")
            return pd.DataFrame(), pd.Series()
    
    def random_forest(self, n_estimators: int = 100, max_depth: Optional[int] = None) -> Dict[str, Any]:
        """
        Train and evaluate a Random Forest model for outcome prediction
        
        Args:
            n_estimators: Number of trees in the forest
            max_depth: Maximum depth of trees (None for unlimited)
            
        Returns:
            Dictionary with model performance metrics and feature importances
        """
        try:
            X, y = self.prepare_features()
            
            if X.empty or len(y) == 0:
                return {"error": "Insufficient data for Random Forest model"}
            
            if len(X) < 20:  # Minimum sample size for reasonable model
                return {"error": "Insufficient samples for reliable Random Forest"}
            
            # Split data for evaluation
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
            
            # Create pipeline with preprocessing
            numeric_features = X.columns[X.dtypes != 'object'].tolist()
            categorical_features = X.columns[X.dtypes == 'object'].tolist()
            
            numeric_transformer = Pipeline(steps=[
                ('scaler', StandardScaler())
            ])
            
            preprocessor = ColumnTransformer(
                transformers=[
                    ('num', numeric_transformer, numeric_features)
                ]
            )
            
            if categorical_features:
                categorical_transformer = Pipeline(steps=[
                    ('onehot', OneHotEncoder(handle_unknown='ignore'))
                ])
                preprocessor.transformers.append(
                    ('cat', categorical_transformer, categorical_features)
                )
            
            # Create and train the model
            rf = RandomForestClassifier(
                n_estimators=n_estimators, 
                max_depth=max_depth,
                class_weight='balanced',
                random_state=42
            )
            
            model = Pipeline(steps=[
                ('preprocessor', preprocessor),
                ('classifier', rf)
            ])
            
            # Cross-validation
            cv = KFold(n_splits=5, shuffle=True, random_state=42)
            cv_scores = cross_val_score(model, X, y, cv=cv, scoring='roc_auc')
            
            # Train on full training data
            model.fit(X_train, y_train)
            
            # Evaluate on test data
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            metrics = {
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "precision": float(precision_score(y_test, y_pred, zero_division=0)),
                "recall": float(recall_score(y_test, y_pred, zero_division=0)),
                "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
                "roc_auc": float(roc_auc_score(y_test, y_prob))
            }
            
            # Get feature importances
            feature_importances = {}
            if hasattr(model['classifier'], 'feature_importances_'):
                # Get feature names after preprocessing
                if categorical_features:
                    # With categorical features, need to get transformed feature names
                    # This is a simplified version - may need adjustment based on actual preprocessing
                    feature_names = numeric_features + [f"{cat}_{val}" for cat in categorical_features 
                                                      for val in model['preprocessor'].transformers_[1][1]['onehot'].categories_[0]]
                else:
                    feature_names = numeric_features
                
                importances = model['classifier'].feature_importances_
                
                # Map importances to features (only for numeric features to keep it simple)
                for i, feature in enumerate(numeric_features):
                    if i < len(importances):
                        feature_importances[feature] = float(importances[i])
            
            # Save the model
            model_filename = os.path.join(self.model_path, "random_forest_model.pkl")
            with open(model_filename, 'wb') as f:
                pickle.dump(model, f)
            
            logger.info(f"Random Forest model trained and saved: {model_filename}")
            
            # Return results
            result = {
                "cv_scores": cv_scores.tolist(),
                "cv_mean_score": float(cv_scores.mean()),
                "metrics": metrics,
                "feature_importances": feature_importances,
                "sample_size": int(len(X)),
                "model_path": model_filename
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Random Forest model: {str(e)}")
            return {"error": str(e)}
    
    def predict(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make predictions for a new patient using the trained model
        
        Args:
            patient_data: Dictionary with patient features
            
        Returns:
            Dictionary with prediction results and confidence
        """
        try:
            # Load the model
            model_filename = os.path.join(self.model_path, "random_forest_model.pkl")
            if not os.path.exists(model_filename):
                # Train a new model if none exists
                self.random_forest()
                
                if not os.path.exists(model_filename):
                    return {"error": "Could not train or load model"}
            
            with open(model_filename, 'rb') as f:
                model = pickle.load(f)
            
            # Prepare input data
            # Mapping from input keys to feature names
            feature_mapping = {
                "age": "Age",
                "who_ps": "who_ps_num",
                "t_stage": "t_stage_num",
                "her2_status": "her2_bin",
                "treatment": "treatment_bin",
                "regression": "regression_value"
            }
            
            # Extract features
            features = {}
            for input_key, feature_name in feature_mapping.items():
                if input_key in patient_data:
                    features[feature_name] = patient_data[input_key]
            
            # Convert to DataFrame
            X = pd.DataFrame([features])
            
            # Make prediction
            prediction_prob = model.predict_proba(X)[0, 1]
            prediction_class = 1 if prediction_prob >= 0.5 else 0
            
            # Get feature importance for this prediction
            feature_contribution = {}
            
            # Return prediction results
            result = {
                "prediction": {
                    "class": int(prediction_class),
                    "probability": float(prediction_prob),
                    "interpretation": "High risk" if prediction_prob >= 0.7 else 
                                    "Moderate risk" if prediction_prob >= 0.3 else "Low risk"
                },
                "confidence": {
                    "value": float(max(prediction_prob, 1 - prediction_prob)),
                    "assessment": "High" if max(prediction_prob, 1 - prediction_prob) >= 0.8 else
                                "Moderate" if max(prediction_prob, 1 - prediction_prob) >= 0.6 else "Low"
                },
                "feature_contributions": feature_contribution
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            return {"error": str(e)}
