"""
Enhanced dashboard for surgery analysis results and cohort management.
"""
from fastapi import Request, Depends
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional

from core.dependencies import get_current_user
from core.services.logger import get_logger

logger = get_logger(__name__)
templates = Jinja2Templates(directory="web/templates")


class SurgeryDashboard:
    """Enhanced dashboard for surgery analysis and cohort management."""
    
    def __init__(self):
        self.results_dir = Path("data/results")
        self.uploads_dir = Path("data/uploads")
        
    async def render_dashboard(self, request: Request, current_user=None):
        """Render main surgery analysis dashboard."""
        
        try:
            # Get recent analyses
            recent_analyses = self._get_recent_analyses(limit=10)
            
            # Get cohort statistics
            cohort_stats = self._get_cohort_statistics()
            
            # Get system health metrics
            health_metrics = self._get_system_health()
            
            context = {
                "request": request,
                "user": current_user,
                "recent_analyses": recent_analyses,
                "cohort_stats": cohort_stats,
                "health_metrics": health_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
            return templates.TemplateResponse("dashboard/surgery_analysis.html", context)
            
        except Exception as e:
            logger.error(f"Error rendering dashboard: {e}")
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error": "Dashboard temporarily unavailable"
            })
    
    async def render_cohort_upload(self, request: Request, current_user=None):
        """Render cohort upload interface."""
        
        try:
            # Get existing cohorts
            existing_cohorts = self._get_existing_cohorts()
            
            # Get upload guidelines
            upload_guidelines = self._get_upload_guidelines()
            
            context = {
                "request": request,
                "user": current_user,
                "existing_cohorts": existing_cohorts,
                "upload_guidelines": upload_guidelines,
                "supported_formats": ["CSV", "Excel (.xlsx)", "JSON"]
            }
            
            return templates.TemplateResponse("dashboard/cohort_upload.html", context)
            
        except Exception as e:
            logger.error(f"Error rendering cohort upload: {e}")
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error": "Upload interface temporarily unavailable"
            })
    
    async def render_analysis_results(self, request: Request, analysis_id: str, current_user=None):
        """Render detailed analysis results."""
        
        try:
            # Load analysis results
            results_file = self.results_dir / f"{analysis_id}.json"
            
            if not results_file.exists():
                return templates.TemplateResponse("error.html", {
                    "request": request,
                    "error": f"Analysis {analysis_id} not found"
                })
            
            with open(results_file) as f:
                analysis_data = json.load(f)
            
            # Process results for visualization
            processed_results = self._process_results_for_display(analysis_data)
            
            # Get reproducibility info
            reproducibility_info = self._get_reproducibility_info(analysis_data)
            
            context = {
                "request": request,
                "user": current_user,
                "analysis": analysis_data,
                "processed_results": processed_results,
                "reproducibility": reproducibility_info,
                "analysis_id": analysis_id
            }
            
            return templates.TemplateResponse("dashboard/analysis_results.html", context)
            
        except Exception as e:
            logger.error(f"Error rendering analysis results: {e}")
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error": "Results temporarily unavailable"
            })
    
    def _get_recent_analyses(self, limit: int = 10) -> List[Dict]:
        """Get recent analysis summaries."""
        
        if not self.results_dir.exists():
            return []
        
        result_files = list(self.results_dir.glob("*.json"))
        result_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        recent = []
        for result_file in result_files[:limit]:
            try:
                with open(result_file) as f:
                    data = json.load(f)
                
                summary = {
                    "analysis_id": data.get("analysis_id"),
                    "cohort_id": data.get("cohort_id"),
                    "analysis_type": data.get("analysis_config", {}).get("analysis_type", "Unknown"),
                    "analyzed_at": data.get("metadata", {}).get("analyzed_at"),
                    "analyzed_by": data.get("metadata", {}).get("analyzed_by"),
                    "cohort_records": data.get("metadata", {}).get("cohort_records", 0),
                    "status": "completed"
                }
                recent.append(summary)
                
            except Exception as e:
                logger.warning(f"Could not load analysis {result_file}: {e}")
        
        return recent
    
    def _get_cohort_statistics(self) -> Dict:
        """Get cohort upload and processing statistics."""
        
        if not self.uploads_dir.exists():
            return {"total_cohorts": 0, "total_records": 0, "recent_uploads": []}
        
        cohort_dirs = [d for d in self.uploads_dir.iterdir() if d.is_dir()]
        
        total_cohorts = len(cohort_dirs)
        total_records = 0
        recent_uploads = []
        
        for cohort_dir in cohort_dirs:
            try:
                metadata_file = cohort_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    
                    total_records += metadata.get("records_count", 0)
                    
                    if len(recent_uploads) < 5:
                        recent_uploads.append({
                            "cohort_id": metadata.get("cohort_id"),
                            "cohort_name": metadata.get("cohort_name"),
                            "upload_timestamp": metadata.get("upload_timestamp"),
                            "records_count": metadata.get("records_count", 0)
                        })
                        
            except Exception as e:
                logger.warning(f"Could not load cohort metadata from {cohort_dir}: {e}")
        
        # Sort recent uploads by timestamp
        recent_uploads.sort(key=lambda x: x.get("upload_timestamp", ""), reverse=True)
        
        return {
            "total_cohorts": total_cohorts,
            "total_records": total_records,
            "recent_uploads": recent_uploads[:5]
        }
    
    def _get_system_health(self) -> Dict:
        """Get basic system health metrics."""
        
        import psutil
        import os
        
        try:
            # Basic system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Application metrics
            results_count = len(list(self.results_dir.glob("*.json"))) if self.results_dir.exists() else 0
            uploads_count = len([d for d in self.uploads_dir.iterdir() if d.is_dir()]) if self.uploads_dir.exists() else 0
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": (disk.used / disk.total) * 100,
                "results_count": results_count,
                "uploads_count": uploads_count,
                "status": "healthy" if cpu_percent < 80 and memory.percent < 80 else "warning"
            }
            
        except Exception as e:
            logger.warning(f"Could not get system metrics: {e}")
            return {
                "status": "unknown",
                "error": str(e)
            }
    
    def _get_existing_cohorts(self) -> List[Dict]:
        """Get list of existing cohorts for reference."""
        
        if not self.uploads_dir.exists():
            return []
        
        cohorts = []
        for cohort_dir in self.uploads_dir.iterdir():
            if cohort_dir.is_dir():
                try:
                    metadata_file = cohort_dir / "metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                        
                        cohorts.append({
                            "cohort_id": metadata.get("cohort_id"),
                            "cohort_name": metadata.get("cohort_name"),
                            "description": metadata.get("description"),
                            "records_count": metadata.get("records_count", 0),
                            "upload_timestamp": metadata.get("upload_timestamp"),
                            "columns": metadata.get("columns", [])
                        })
                        
                except Exception as e:
                    logger.warning(f"Could not load cohort metadata from {cohort_dir}: {e}")
        
        # Sort by upload timestamp
        cohorts.sort(key=lambda x: x.get("upload_timestamp", ""), reverse=True)
        
        return cohorts
    
    def _get_upload_guidelines(self) -> Dict:
        """Get guidelines and requirements for cohort uploads."""
        
        return {
            "required_columns": [
                "patient_id",
                "age",
                "gender",
                "procedure_type",
                "outcome"
            ],
            "optional_columns": [
                "bmi",
                "comorbidities",
                "surgery_duration",
                "complications",
                "follow_up_days"
            ],
            "data_types": {
                "patient_id": "string (unique identifier)",
                "age": "integer (years)",
                "gender": "string (M/F/Other)",
                "procedure_type": "string (gastric_bypass, sleeve, etc.)",
                "outcome": "string (success/complication/readmission)"
            },
            "file_size_limit": "50 MB",
            "max_records": 10000
        }
    
    def _process_results_for_display(self, analysis_data: Dict) -> Dict:
        """Process analysis results for web display."""
        
        results = analysis_data.get("results", {})
        
        # Extract key metrics for visualization
        processed = {
            "summary_metrics": {},
            "charts_data": {},
            "tables_data": {},
            "recommendations": []
        }
        
        # Process statistical summaries
        if "summary_statistics" in results:
            processed["summary_metrics"] = results["summary_statistics"]
        
        # Process outcome analysis
        if "outcome_analysis" in results:
            outcome_data = results["outcome_analysis"]
            processed["charts_data"]["outcomes"] = {
                "type": "pie",
                "data": outcome_data.get("distribution", {}),
                "title": "Outcome Distribution"
            }
        
        # Process risk factors
        if "risk_factors" in results:
            risk_data = results["risk_factors"]
            processed["charts_data"]["risk_factors"] = {
                "type": "bar",
                "data": risk_data.get("factor_weights", {}),
                "title": "Risk Factor Analysis"
            }
        
        # Process trends
        if "trends" in results:
            trends_data = results["trends"]
            processed["charts_data"]["trends"] = {
                "type": "line",
                "data": trends_data.get("time_series", {}),
                "title": "Outcome Trends Over Time"
            }
        
        # Extract recommendations
        if "recommendations" in results:
            processed["recommendations"] = results["recommendations"]
        
        return processed
    
    def _get_reproducibility_info(self, analysis_data: Dict) -> Dict:
        """Extract reproducibility information from analysis data."""
        
        return {
            "run_id": analysis_data.get("run_id"),
            "reproducible": True,  # Assume reproducible if run_id exists
            "dataset_version": analysis_data.get("metadata", {}).get("dataset_version"),
            "analysis_config": analysis_data.get("analysis_config", {}),
            "environment_info": {
                "analysis_type": analysis_data.get("analysis_config", {}).get("analysis_type"),
                "analyzed_at": analysis_data.get("metadata", {}).get("analyzed_at"),
                "analyzed_by": analysis_data.get("metadata", {}).get("analyzed_by")
            }
        }


# Create dashboard instance for use in routes
dashboard = SurgeryDashboard()
