"""
Analysis Engine for generating insights and publications from surgical data
"""

from typing import Dict, List, Optional, Union, Any
import asyncio
from datetime import datetime
import uuid

import pandas as pd
import numpy as np
from fastapi import BackgroundTasks
from sklearn.ensemble import RandomForestClassifier
from lifelines import CoxPHFitter

from core.models.surgery import SurgicalCaseModel
from feature.analysis.surgery_analyzer import IntegratedSurgeryAnalyzer
from feature.analysis.impact_metrics import ImpactMetricsCalculator
from feature.protocols.flot_analyzer import FLOTAnalyzer
from core.services.logger import get_logger
from web.templates.reports.reports import ReportGenerator, PublicationType, OutputFormat

logger = get_logger(__name__)

class AnalysisEngine:
    """Analysis engine for generating insights and publications from surgical data"""
    
    def __init__(self):
        self.surgery_analyzer = IntegratedSurgeryAnalyzer()
        self.impact_metrics = ImpactMetricsCalculator()
        self.flot_analyzer = FLOTAnalyzer()
        self.report_generator = ReportGenerator()
        
        # In-memory cache for storing publication results
        self._publications_cache = {}
        
    async def generate_insights(
        self, 
        cohort_data: List[SurgicalCaseModel],
        insight_types: List[str],
        background_tasks: Optional[BackgroundTasks] = None,
        notify_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate insights from cohort data
        
        Args:
            cohort_data: List of surgical cases
            insight_types: Types of insights to generate
            background_tasks: Optional background tasks for long-running insights
            notify_email: Optional email to notify when background tasks complete
            
        Returns:
            Dictionary of insights
        """
        logger.info(f"Generating insights for {len(cohort_data)} cases")
        
        # Initialize insights container
        insights = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "cohort_size": len(cohort_data),
            "results": {}
        }
        
        # Process quick insights synchronously
        if "basic_statistics" in insight_types:
            insights["results"]["basic_statistics"] = await self._generate_basic_statistics(cohort_data)
            
        if "flot_adherence" in insight_types:
            insights["results"]["flot_adherence"] = await self._analyze_flot_adherence(cohort_data)
            
        if "albumin_trends" in insight_types:
            insights["results"]["albumin_trends"] = await self._analyze_albumin_trends(cohort_data)
            
        # Process complex insights as background tasks if provided
        complex_insights = [t for t in insight_types if t in [
            "survival_analysis", "multivariate_analysis", "decision_impact"
        ]]
        
        if complex_insights and background_tasks:
            # Store partial results
            self._publications_cache[insights["id"]] = insights
            
            # Schedule background task
            background_tasks.add_task(
                self._process_complex_insights,
                insights_id=insights["id"],
                cohort_data=cohort_data,
                insight_types=complex_insights,
                notify_email=notify_email
            )
            
            # Add pending status
            for insight_type in complex_insights:
                insights["results"][insight_type] = {"status": "processing"}
                
        return insights
    
    async def _process_complex_insights(
        self, 
        insights_id: str,
        cohort_data: List[SurgicalCaseModel],
        insight_types: List[str],
        notify_email: Optional[str] = None
    ):
        """Process complex insights in background"""
        logger.info(f"Processing complex insights for ID {insights_id}")
        
        # Get insights from cache
        insights = self._publications_cache.get(insights_id)
        if not insights:
            logger.error(f"Insights with ID {insights_id} not found in cache")
            return
            
        try:
            # Process each complex insight
            if "survival_analysis" in insight_types:
                insights["results"]["survival_analysis"] = await self._perform_survival_analysis(cohort_data)
                
            if "multivariate_analysis" in insight_types:
                insights["results"]["multivariate_analysis"] = await self._perform_multivariate_analysis(cohort_data)
                
            if "decision_impact" in insight_types:
                insights["results"]["decision_impact"] = await self._analyze_decision_impact(cohort_data)
                
            # Update status
            insights["status"] = "completed"
            insights["completed_at"] = datetime.now().isoformat()
            
            # TODO: Implement email notification if notify_email is provided
            
        except Exception as e:
            logger.error(f"Error processing complex insights: {e}", exc_info=True)
            insights["status"] = "error"
            insights["error"] = str(e)
    
    async def _generate_basic_statistics(self, cohort_data: List[SurgicalCaseModel]) -> Dict[str, Any]:
        """Generate basic statistics from cohort data"""
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([case.model_dump() for case in cohort_data])
        
        # Basic demographics
        stats = {
            "total_cases": len(df),
            "demographics": {
                "age": {
                    "mean": df.get("age", pd.Series()).mean(),
                    "median": df.get("age", pd.Series()).median(),
                    "range": [df.get("age", pd.Series()).min(), df.get("age", pd.Series()).max()]
                },
                "gender_distribution": df.get("gender", pd.Series()).value_counts().to_dict()
            },
            "clinical": {
                "asa_distribution": df.get("asa_grade", pd.Series()).value_counts().to_dict(),
                "stage_distribution": df.get("tumor_stage", pd.Series()).value_counts().to_dict(),
                "albumin_levels": {
                    "mean": df.get("preop_albumin", pd.Series()).mean(),
                    "below_threshold": (df.get("preop_albumin", pd.Series()) < 3.5).sum()
                }
            },
            "protocol": {
                "flot_cycles_completed": df.get("flot_cycles", pd.Series()).value_counts().to_dict(),
                "trg_score_distribution": df.get("trg_score", pd.Series()).value_counts().to_dict()
            }
        }
        
        return stats
        
    async def _analyze_flot_adherence(self, cohort_data: List[SurgicalCaseModel]) -> Dict[str, Any]:
        """Analyze FLOT protocol adherence"""
        return await self.flot_analyzer.analyze_adherence(cohort_data)
    
    async def _analyze_albumin_trends(self, cohort_data: List[SurgicalCaseModel]) -> Dict[str, Any]:
        """Analyze albumin level trends and impact"""
        df = pd.DataFrame([case.model_dump() for case in cohort_data])
        
        # Group by albumin ranges
        if "preop_albumin" in df.columns:
            df["albumin_range"] = pd.cut(
                df["preop_albumin"], 
                bins=[0, 3.0, 3.5, 4.0, 5.0], 
                labels=["< 3.0", "3.0-3.5", "3.5-4.0", "> 4.0"]
            )
            
            # Analysis by albumin range
            analysis = {
                "distribution": df["albumin_range"].value_counts().to_dict(),
                "by_albumin_range": {}
            }
            
            # Analyze outcomes by albumin range
            for albumin_range in df["albumin_range"].unique():
                if pd.isna(albumin_range):
                    continue
                    
                range_df = df[df["albumin_range"] == albumin_range]
                
                analysis["by_albumin_range"][str(albumin_range)] = {
                    "count": len(range_df),
                    "complications": range_df.get("complications", pd.Series()).sum() / len(range_df) if "complications" in range_df else None,
                    "mortality": range_df.get("mortality", pd.Series()).sum() / len(range_df) if "mortality" in range_df else None,
                    "readmission": range_df.get("readmission", pd.Series()).sum() / len(range_df) if "readmission" in range_df else None,
                    "mean_los": range_df.get("length_of_stay", pd.Series()).mean() if "length_of_stay" in range_df else None
                }
                
            return analysis
        
        return {"error": "Albumin data not available"}
    
    async def _perform_survival_analysis(self, cohort_data: List[SurgicalCaseModel]) -> Dict[str, Any]:
        """Perform survival analysis using Cox regression"""
        df = pd.DataFrame([case.model_dump() for case in cohort_data])
        
        # Check if required fields exist
        required_fields = ["survival_time", "mortality"]
        if not all(field in df.columns for field in required_fields):
            return {"error": "Required survival data fields missing"}
        
        try:
            # Prepare data for Cox model
            cox_data = df[["survival_time", "mortality"]].copy()
            
            # Add potential factors
            for factor in ["age", "preop_albumin", "flot_cycles", "trg_score"]:
                if factor in df.columns:
                    cox_data[factor] = df[factor]
            
            # Fit Cox model
            cph = CoxPHFitter()
            cph.fit(cox_data, duration_col="survival_time", event_col="mortality")
            
            # Extract results
            summary = cph.summary.to_dict()
            
            return {
                "model": "Cox Proportional Hazards",
                "factors": list(summary.keys()),
                "hazard_ratios": {k: summary[k]["exp(coef)"] for k in summary},
                "p_values": {k: summary[k]["p"] for k in summary},
                "concordance": cph.concordance_index_
            }
            
        except Exception as e:
            logger.error(f"Error in survival analysis: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def _perform_multivariate_analysis(self, cohort_data: List[SurgicalCaseModel]) -> Dict[str, Any]:
        """Perform multivariate analysis using Random Forest"""
        df = pd.DataFrame([case.model_dump() for case in cohort_data])
        
        # Check if outcome variable exists
        if "complications" not in df.columns:
            return {"error": "Outcome variable 'complications' missing"}
        
        try:
            # Select features
            potential_features = ["age", "gender", "asa_grade", "preop_albumin", 
                                 "flot_cycles", "nutrition_support", "trg_score"]
            
            # Filter to available features
            features = [f for f in potential_features if f in df.columns]
            
            if not features:
                return {"error": "No usable features found for multivariate analysis"}
            
            # Prepare data
            X = pd.get_dummies(df[features])
            y = df["complications"]
            
            # Train Random Forest
            rf = RandomForestClassifier(n_estimators=100, random_state=42)
            rf.fit(X, y)
            
            # Extract feature importance
            feature_importance = dict(zip(X.columns, rf.feature_importances_))
            sorted_importance = {k: v for k, v in sorted(
                feature_importance.items(), 
                key=lambda item: item[1], 
                reverse=True
            )}
            
            return {
                "model": "Random Forest",
                "target": "complications",
                "feature_importance": sorted_importance,
                "accuracy": rf.score(X, y)
            }
            
        except Exception as e:
            logger.error(f"Error in multivariate analysis: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def _analyze_decision_impact(self, cohort_data: List[SurgicalCaseModel]) -> Dict[str, Any]:
        """Analyze decision impact"""
        return await self.impact_metrics.calculate_impact_metrics(cohort_data)
    
    async def generate_publication(
        self,
        cohort_data: List[SurgicalCaseModel],
        publication_type: PublicationType,
        output_format: OutputFormat,
        title: str,
        authors: List[str],
        background_tasks: Optional[BackgroundTasks] = None,
        notify_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate publication from cohort data
        
        Args:
            cohort_data: List of surgical cases
            publication_type: Type of publication (memoir, article, infographic)
            output_format: Output format (pdf, docx, html)
            title: Publication title
            authors: List of authors
            background_tasks: Optional background tasks for long publications
            notify_email: Optional email to notify when background tasks complete
            
        Returns:
            Publication metadata with download info
        """
        logger.info(f"Generating {publication_type} publication in {output_format} format")
        
        # Generate publication ID
        publication_id = str(uuid.uuid4())
        
        # Create publication metadata
        publication_meta = {
            "id": publication_id,
            "title": title,
            "authors": authors,
            "type": publication_type,
            "format": output_format,
            "timestamp": datetime.now().isoformat(),
            "cohort_size": len(cohort_data),
            "status": "processing"
        }
        
        # Store in cache
        self._publications_cache[publication_id] = publication_meta
        
        # Generate content in background to avoid blocking
        if background_tasks:
            background_tasks.add_task(
                self._generate_publication_content,
                publication_id=publication_id,
                cohort_data=cohort_data,
                publication_type=publication_type,
                output_format=output_format,
                title=title,
                authors=authors,
                notify_email=notify_email
            )
        else:
            # For testing/smaller publications, generate synchronously
            await self._generate_publication_content(
                publication_id=publication_id,
                cohort_data=cohort_data,
                publication_type=publication_type,
                output_format=output_format,
                title=title,
                authors=authors
            )
        
        return publication_meta
    
    async def _generate_publication_content(
        self,
        publication_id: str,
        cohort_data: List[SurgicalCaseModel],
        publication_type: PublicationType,
        output_format: OutputFormat,
        title: str,
        authors: List[str],
        notify_email: Optional[str] = None
    ):
        """Generate publication content in background"""
        logger.info(f"Generating publication content for ID {publication_id}")
        
        try:
            # Get publication from cache
            publication = self._publications_cache.get(publication_id)
            if not publication:
                logger.error(f"Publication with ID {publication_id} not found in cache")
                return
                
            # First, generate insights for the publication
            insight_types = ["basic_statistics", "flot_adherence", "albumin_trends"]
            
            # Add complex insights for articles
            if publication_type == PublicationType.ARTICLE:
                insight_types.extend(["survival_analysis", "multivariate_analysis", "decision_impact"])
                
            # Generate insights synchronously for publication
            insights = await self.generate_insights(cohort_data, insight_types)
            
            # Generate publication using report generator
            output_path = await self.report_generator.generate_report(
                insights=insights["results"],
                cohort_data=cohort_data,
                publication_type=publication_type,
                output_format=output_format,
                title=title,
                authors=authors,
                output_dir="data/publications"
            )
            
            # Update publication metadata
            publication["status"] = "completed"
            publication["completed_at"] = datetime.now().isoformat()
            publication["file_path"] = output_path
            publication["download_url"] = f"/api/v1/analysis/publication/download/{publication_id}"
            
            # TODO: Implement email notification if notify_email is provided
            
        except Exception as e:
            logger.error(f"Error generating publication: {e}", exc_info=True)
            
            publication = self._publications_cache.get(publication_id)
            if publication:
                publication["status"] = "error"
                publication["error"] = str(e)
    
    def get_publication_status(self, publication_id: str) -> Optional[Dict[str, Any]]:
        """Get publication status from cache"""
        return self._publications_cache.get(publication_id)
    
    def get_publication_file_path(self, publication_id: str) -> Optional[str]:
        """Get publication file path for download"""
        publication = self._publications_cache.get(publication_id)
        if publication and publication.get("status") == "completed":
            return publication.get("file_path")
        return None

# Create singleton instance
analysis_engine = AnalysisEngine()
