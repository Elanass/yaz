"""
Reports Generation Module for Surgery Analysis Platform

This module provides templating and export functionality for generating
various types of reports, publications, and visualizations from surgical data,
supporting PDF, Word, and HTML formats.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import logging
import asyncio
import uuid
from enum import Enum

# Temporarily commented out due to installation issues
# from weasyprint import HTML, CSS
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("Warning: weasyprint not available, PDF generation will be limited")
    
    # Placeholder classes
    class HTML:
        def __init__(self, *args, **kwargs):
            print("Using placeholder HTML class - install weasyprint for full functionality")
        def write_pdf(self, *args, **kwargs):
            raise NotImplementedError("weasyprint not available")
    
    class CSS:
        def __init__(self, *args, **kwargs):
            print("Using placeholder CSS class - install weasyprint for full functionality")

try:
    from docxtpl import DocxTemplate
    DOCXTPL_AVAILABLE = True
except ImportError:
    DOCXTPL_AVAILABLE = False
    print("Warning: docxtpl not available, Word document generation will be limited")
    
    class DocxTemplate:
        def __init__(self, *args, **kwargs):
            print("Using placeholder DocxTemplate class - install docxtpl for full functionality")
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from jinja2 import Environment, FileSystemLoader

from core.services.logger import get_logger

logger = get_logger(__name__)

# Initialize Jinja2 environment
template_dir = Path(__file__).parent
env = Environment(loader=FileSystemLoader(template_dir))


class PublicationType(Enum):
    """Types of publications that can be generated"""
    ARTICLE = "article"
    MEMOIR = "memoir" 
    INFOGRAPHIC = "infographic"
    SUMMARY = "summary"
    PRESENTATION = "presentation"
    POSTER = "poster"

class OutputFormat(Enum):
    """Output formats for reports"""
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    PPTX = "pptx"


class ReportGenerator:
    """Generate reports and publications from surgical data"""
    
    def __init__(self):
        """Initialize the report generator"""
        self.supported_formats = ["pdf", "docx", "html"]
        self.supported_types = ["memoir", "article", "infographic", "summary", "presentation"]
        self.template_dir = template_dir
        self.output_dir = Path("data/publications")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Report Generator initialized with templates from {template_dir}")
    
    async def generate_report(
        self,
        report_id: str,
        report_type: str,
        title: str,
        data: Dict[str, Any],
        output_format: str = "pdf",
        template_name: Optional[str] = None,
        custom_fields: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a report from data
        
        Args:
            report_id: Unique identifier for the report
            report_type: Type of report (memoir, article, etc.)
            title: Report title
            data: Data to include in the report
            output_format: Output format (pdf, docx, html)
            template_name: Optional template name to use
            custom_fields: Optional custom fields to include
            
        Returns:
            Path to the generated report file
        """
        if output_format not in self.supported_formats:
            raise ValueError(f"Unsupported output format: {output_format}")
            
        if report_type not in self.supported_types:
            raise ValueError(f"Unsupported report type: {report_type}")
            
        # Select template based on report type if not specified
        if not template_name:
            template_name = f"{report_type}_template"
            
        # Create context for template rendering
        context = {
            "title": title,
            "generated_date": datetime.now().strftime("%Y-%m-%d"),
            "report_id": report_id,
            "data": data
        }
        
        # Add custom fields if provided
        if custom_fields:
            context.update(custom_fields)
            
        # Generate report based on output format
        output_file = None
        if output_format == "pdf":
            output_file = await self._generate_pdf(report_id, template_name, context)
        elif output_format == "docx":
            output_file = await self._generate_docx(report_id, template_name, context)
        elif output_format == "html":
            output_file = await self._generate_html(report_id, template_name, context)
            
        logger.info(f"Generated {report_type} report: {output_file}")
        return output_file
    
    async def _generate_pdf(self, report_id: str, template_name: str, context: Dict[str, Any]) -> str:
        """Generate PDF report using WeasyPrint"""
        # First generate HTML
        html_file = await self._generate_html(report_id, template_name, context, is_intermediate=True)
        
        # Convert HTML to PDF
        pdf_path = self.output_dir / f"{report_id}.pdf"
        html = HTML(filename=html_file)
        html.write_pdf(pdf_path)
        
        # Remove intermediate HTML file
        if os.path.exists(html_file):
            os.remove(html_file)
            
        return str(pdf_path)
    
    async def _generate_docx(self, report_id: str, template_name: str, context: Dict[str, Any]) -> str:
        """Generate DOCX report using DocxTemplate"""
        # Look for .docx template
        template_path = self.template_dir / f"{template_name}.docx"
        
        if not template_path.exists():
            raise FileNotFoundError(f"DocX template not found: {template_path}")
            
        # Generate DOCX from template
        doc = DocxTemplate(template_path)
        doc.render(context)
        
        # Save the output
        output_path = self.output_dir / f"{report_id}.docx"
        doc.save(output_path)
        
        return str(output_path)
    
    async def _generate_html(
        self, 
        report_id: str, 
        template_name: str, 
        context: Dict[str, Any],
        is_intermediate: bool = False
    ) -> str:
        """Generate HTML report using Jinja2"""
        # Look for .html template
        template_file = f"{template_name}.html"
        
        try:
            template = env.get_template(template_file)
        except Exception as e:
            raise FileNotFoundError(f"HTML template not found: {template_file}. Error: {str(e)}")
            
        # Render the template
        html_content = template.render(**context)
        
        # Determine output path
        if is_intermediate:
            output_path = self.output_dir / f"{report_id}_intermediate.html"
        else:
            output_path = self.output_dir / f"{report_id}.html"
            
        # Write the output
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        return str(output_path)


class PublicationGenerator:
    """Generate publication-ready documents and visualizations"""
    
    def __init__(self):
        """Initialize the publication generator"""
        self.report_generator = ReportGenerator()
        self.visualization_generator = VisualizationGenerator()
        
    async def generate_publication(
        self,
        publication_id: str,
        publication_type: str,
        title: str,
        authors: List[str],
        cohort_data: List[Dict[str, Any]],
        template_id: Optional[str] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
        output_format: str = "pdf"
    ) -> str:
        """
        Generate a publication from cohort data
        
        Args:
            publication_id: Unique identifier for the publication
            publication_type: Type of publication (memoir, article, infographic)
            title: Publication title
            authors: List of authors
            cohort_data: Cohort data to include in the publication
            template_id: Optional template identifier
            custom_fields: Optional custom fields to include
            output_format: Output format (pdf, docx, html)
            
        Returns:
            Path to the generated publication file
        """
        # Process cohort data
        processed_data = self._process_cohort_data(cohort_data, publication_type)
        
        # Generate visualizations if needed
        visualizations = {}
        if publication_type in ["memoir", "article", "infographic"]:
            visualizations = await self.visualization_generator.generate_visualizations(
                processed_data, 
                publication_type
            )
            
        # Prepare context for publication
        context = {
            "title": title,
            "authors": authors,
            "processed_data": processed_data,
            "visualizations": visualizations,
            "publication_date": datetime.now().strftime("%Y-%m-%d"),
            "publication_id": publication_id
        }
        
        # Add custom fields if provided
        if custom_fields:
            context.update(custom_fields)
            
        # Generate the publication
        template_name = template_id if template_id else f"{publication_type}_template"
        output_file = await self.report_generator.generate_report(
            report_id=publication_id,
            report_type=publication_type,
            title=title,
            data=context,
            output_format=output_format,
            template_name=template_name
        )
        
        return output_file
    
    def _process_cohort_data(self, cohort_data: List[Dict[str, Any]], publication_type: str) -> Dict[str, Any]:
        """Process cohort data for publication"""
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(cohort_data)
        
        # Basic statistics
        stats = {}
        
        # Demographics
        if "age" in df.columns:
            stats["age"] = {
                "mean": df["age"].mean(),
                "median": df["age"].median(),
                "range": [df["age"].min(), df["age"].max()]
            }
            
        if "gender" in df.columns:
            stats["gender"] = df["gender"].value_counts().to_dict()
            
        # FLOT-specific statistics
        if "flot_cycles_completed" in df.columns:
            stats["flot_cycles"] = {
                "mean": df["flot_cycles_completed"].mean(),
                "median": df["flot_cycles_completed"].median(),
                "distribution": df["flot_cycles_completed"].value_counts().to_dict()
            }
            
        if "trg_score" in df.columns:
            stats["trg_score"] = {
                "mean": df["trg_score"].mean(),
                "median": df["trg_score"].median(),
                "distribution": df["trg_score"].value_counts().to_dict()
            }
            
        # Outcome statistics if available
        if "complications" in df.columns:
            # Flatten the list of complications
            all_complications = []
            for comps in df["complications"].dropna():
                if isinstance(comps, list):
                    all_complications.extend(comps)
                    
            stats["complications"] = {
                "count": len(all_complications),
                "frequency": pd.Series(all_complications).value_counts().to_dict()
            }
            
        if "resection_margin" in df.columns:
            stats["resection_margin"] = df["resection_margin"].value_counts().to_dict()
            
        # Additional processing for specific publication types
        if publication_type == "memoir":
            # More comprehensive analysis for memoir
            stats["cohort_size"] = len(df)
            stats["raw_data"] = cohort_data
            
        elif publication_type == "article":
            # Focus on statistical significance for article
            stats["cohort_size"] = len(df)
            
            # Survival analysis if data available
            if "survival_months" in df.columns and "event" in df.columns:
                # Placeholder for survival analysis
                stats["survival"] = {
                    "median_survival": df["survival_months"].median(),
                    "events": df["event"].sum()
                }
                
        elif publication_type == "infographic":
            # Simplified stats for infographic
            stats["cohort_size"] = len(df)
            stats["key_findings"] = self._extract_key_findings(df)
            
        return stats
    
    def _extract_key_findings(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract key findings for infographic"""
        findings = []
        
        # Example findings extraction
        if "flot_cycles_completed" in df.columns and "resection_margin" in df.columns:
            # Analyze impact of FLOT cycles on R0 resection
            r0_by_cycles = df.groupby("flot_cycles_completed")["resection_margin"].apply(
                lambda x: (x == "R0").mean()
            ).to_dict()
            
            findings.append({
                "title": "FLOT Cycles Impact on R0 Resection",
                "type": "correlation",
                "data": r0_by_cycles
            })
            
        if "albumin_level_pre_flot" in df.columns and "complications" in df.columns:
            # Analyze impact of albumin on complications
            df["has_complications"] = df["complications"].apply(
                lambda x: len(x) > 0 if isinstance(x, list) else False
            )
            
            # Group albumin into ranges
            df["albumin_range"] = pd.cut(
                df["albumin_level_pre_flot"],
                bins=[0, 3.0, 3.5, 4.0, 5.0],
                labels=["<3.0", "3.0-3.5", "3.5-4.0", ">4.0"]
            )
            
            complication_by_albumin = df.groupby("albumin_range")["has_complications"].mean().to_dict()
            
            findings.append({
                "title": "Pre-FLOT Albumin and Complication Risk",
                "type": "correlation",
                "data": complication_by_albumin
            })
            
        return findings


class VisualizationGenerator:
    """Generate visualizations for publications and reports"""
    
    def __init__(self):
        """Initialize visualization generator"""
        self.output_dir = Path("data/visualizations")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def generate_visualizations(
        self,
        data: Dict[str, Any],
        visualization_type: str
    ) -> Dict[str, str]:
        """
        Generate visualizations based on data and type
        
        Args:
            data: Processed data for visualization
            visualization_type: Type of visualization to generate
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        visualizations = {}
        
        # Generate different visualizations based on type
        if visualization_type == "memoir":
            # Comprehensive visualizations for memoir
            visualizations["demographics"] = await self._generate_demographics_chart(data)
            visualizations["flot_impact"] = await self._generate_flot_impact_chart(data)
            visualizations["outcomes"] = await self._generate_outcomes_chart(data)
            
        elif visualization_type == "article":
            # Focused visualizations for article
            visualizations["flot_impact"] = await self._generate_flot_impact_chart(data)
            visualizations["key_outcomes"] = await self._generate_key_outcomes_chart(data)
            
        elif visualization_type == "infographic":
            # Eye-catching visualizations for infographic
            visualizations["key_findings"] = await self._generate_key_findings_chart(data)
            
        return visualizations
    
    async def _generate_demographics_chart(self, data: Dict[str, Any]) -> str:
        """Generate demographics chart"""
        # Create a unique ID for the chart
        chart_id = f"demographics_{uuid.uuid4().hex[:8]}"
        output_path = self.output_dir / f"{chart_id}.png"
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Age distribution if available
        if "age" in data:
            age_data = data["age"]
            ax1.hist(age_data.get("raw_data", [age_data["mean"]]), bins=10, color="skyblue", edgecolor="black")
            ax1.set_title("Age Distribution")
            ax1.set_xlabel("Age (years)")
            ax1.set_ylabel("Frequency")
            
        # Gender distribution if available
        if "gender" in data:
            gender_data = data["gender"]
            labels = list(gender_data.keys())
            sizes = list(gender_data.values())
            ax2.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=["lightblue", "lightpink", "lightgreen"])
            ax2.set_title("Gender Distribution")
            
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        
        return str(output_path)
    
    async def _generate_flot_impact_chart(self, data: Dict[str, Any]) -> str:
        """Generate FLOT impact chart"""
        # Create a unique ID for the chart
        chart_id = f"flot_impact_{uuid.uuid4().hex[:8]}"
        output_path = self.output_dir / f"{chart_id}.png"
        
        # Check if necessary data is available
        if "flot_cycles" not in data or "resection_margin" not in data:
            # Create placeholder chart
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "Insufficient data for FLOT impact analysis", 
                    horizontalalignment="center", verticalalignment="center", fontsize=14)
            plt.axis("off")
            plt.savefig(output_path)
            plt.close()
            return str(output_path)
            
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Extract data
        flot_cycles = data["flot_cycles"]["distribution"]
        resection_margin = data["resection_margin"]
        
        # Create bar chart
        x = list(flot_cycles.keys())
        y = list(flot_cycles.values())
        
        plt.bar(x, y, color="skyblue", edgecolor="black")
        plt.title("Impact of FLOT Cycles on Outcomes")
        plt.xlabel("Number of FLOT Cycles")
        plt.ylabel("Number of Patients")
        
        # Add text annotations for R0 rates if available
        if "r0_by_cycles" in data:
            r0_rates = data["r0_by_cycles"]
            for i, cycle in enumerate(x):
                if cycle in r0_rates:
                    plt.text(i, y[i] + 0.5, f"R0: {r0_rates[cycle]:.1%}", 
                            horizontalalignment="center")
        
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        
        return str(output_path)
    
    async def _generate_outcomes_chart(self, data: Dict[str, Any]) -> str:
        """Generate outcomes chart"""
        # Create a unique ID for the chart
        chart_id = f"outcomes_{uuid.uuid4().hex[:8]}"
        output_path = self.output_dir / f"{chart_id}.png"
        
        # Check if complications data is available
        if "complications" not in data:
            # Create placeholder chart
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "Insufficient data for outcomes analysis", 
                    horizontalalignment="center", verticalalignment="center", fontsize=14)
            plt.axis("off")
            plt.savefig(output_path)
            plt.close()
            return str(output_path)
            
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Extract data
        complications = data["complications"]["frequency"]
        
        # Sort complications by frequency
        sorted_complications = dict(sorted(complications.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Create bar chart
        x = list(sorted_complications.keys())
        y = list(sorted_complications.values())
        
        plt.barh(x, y, color="salmon", edgecolor="black")
        plt.title("Top 10 Complications")
        plt.xlabel("Frequency")
        plt.ylabel("Complication Type")
        
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        
        return str(output_path)
    
    async def _generate_key_outcomes_chart(self, data: Dict[str, Any]) -> str:
        """Generate key outcomes chart for article"""
        # Create a unique ID for the chart
        chart_id = f"key_outcomes_{uuid.uuid4().hex[:8]}"
        output_path = self.output_dir / f"{chart_id}.png"
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Resection margin if available
        if "resection_margin" in data:
            labels = list(data["resection_margin"].keys())
            sizes = list(data["resection_margin"].values())
            ax1.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, 
                   colors=["lightgreen", "lightyellow", "lightcoral"])
            ax1.set_title("Resection Margin Status")
            
        # TRG score if available
        if "trg_score" in data:
            trg_data = data["trg_score"]["distribution"]
            x = list(trg_data.keys())
            y = list(trg_data.values())
            ax2.bar(x, y, color="lightblue", edgecolor="black")
            ax2.set_title("TRG Score Distribution")
            ax2.set_xlabel("TRG Score")
            ax2.set_ylabel("Number of Patients")
            
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        
        return str(output_path)
    
    async def _generate_key_findings_chart(self, data: Dict[str, Any]) -> str:
        """Generate key findings chart for infographic"""
        # Create a unique ID for the chart
        chart_id = f"key_findings_{uuid.uuid4().hex[:8]}"
        output_path = self.output_dir / f"{chart_id}.png"
        
        # Check if key findings data is available
        if "key_findings" not in data or not data["key_findings"]:
            # Create placeholder chart
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "No key findings available for visualization", 
                    horizontalalignment="center", verticalalignment="center", fontsize=14)
            plt.axis("off")
            plt.savefig(output_path)
            plt.close()
            return str(output_path)
            
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Get the first key finding
        finding = data["key_findings"][0]
        
        if finding["type"] == "correlation":
            # Extract data
            x = list(finding["data"].keys())
            y = list(finding["data"].values())
            
            # Create bar chart
            plt.bar(x, y, color="lightgreen", edgecolor="black")
            plt.title(finding["title"])
            plt.ylabel("Rate")
            
            # Add value labels
            for i, v in enumerate(y):
                plt.text(i, v + 0.02, f"{v:.1%}", ha="center")
                
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        
        return str(output_path)
