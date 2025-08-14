"""Logistics Models Module.

This module provides Pydantic models for logistics-related data structures
used throughout the platform. These models include comprehensive supply chain,
inventory, transportation, and delivery data with proper validation and type hints.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class LogisticsType(str, Enum):
    """Supported types of logistics operations in the platform."""

    INVENTORY_MANAGEMENT = "inventory_management"
    SUPPLY_CHAIN = "supply_chain"
    TRANSPORTATION = "transportation"
    WAREHOUSE = "warehouse"
    DELIVERY = "delivery"
    PROCUREMENT = "procurement"
    GENERAL = "general"


class PriorityLevel(str, Enum):
    """Priority levels for logistics operations."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class LogisticsCaseModel(BaseModel):
    """Comprehensive model for logistics case data with all
    required fields for analysis and optimization.
    """

    case_id: str = Field(..., description="Unique case identifier")
    operation_id: str = Field(..., description="Operation identifier")
    logistics_type: LogisticsType = Field(
        ..., description="Type of logistics operation"
    )

    # Basic Operation Data
    supplier: str | None = Field(None, description="Supplier or vendor name")
    product_name: str | None = Field(None, description="Product or item name")
    product_code: str | None = Field(None, description="Product identifier code")
    quantity: int | None = Field(None, ge=0, description="Quantity of items")
    unit_cost: float | None = Field(None, ge=0, description="Cost per unit")
    total_cost: float | None = Field(None, ge=0, description="Total operation cost")

    # Timing and Scheduling
    order_date: datetime | None = Field(None, description="Date order was placed")
    expected_delivery: datetime | None = Field(
        None, description="Expected delivery date"
    )
    actual_delivery: datetime | None = Field(None, description="Actual delivery date")
    lead_time_days: int | None = Field(None, ge=0, description="Lead time in days")

    # Location and Transportation
    origin_location: str | None = Field(None, description="Origin location")
    destination_location: str | None = Field(None, description="Destination location")
    transportation_mode: str | None = Field(None, description="Transportation method")
    tracking_number: str | None = Field(None, description="Shipment tracking number")

    # Status and Priority
    status: str = Field(default="pending", description="Current operation status")
    priority: PriorityLevel = Field(
        default=PriorityLevel.NORMAL, description="Operation priority level"
    )

    # Quality and Compliance
    quality_score: float | None = Field(
        None, ge=0, le=5, description="Quality rating (0-5 scale)"
    )
    compliance_issues: list[str] = Field(
        default=[], description="List of compliance issues"
    )

    # Performance Metrics
    delivery_performance: float | None = Field(
        None, ge=0, le=1, description="On-time delivery rate"
    )
    cost_efficiency: float | None = Field(
        None, ge=0, le=1, description="Cost efficiency score"
    )
    resource_utilization: float | None = Field(
        None, ge=0, le=1, description="Resource utilization rate"
    )

    # Text and Image Data Fields
    operation_notes: str | None = Field(
        None, description="Free-form operational notes and observations"
    )
    delivery_instructions: str | None = Field(
        None, description="Special delivery instructions"
    )
    quality_feedback: str | None = Field(
        None, description="Quality feedback and inspection notes"
    )
    incident_report: str | None = Field(None, description="Incident or problem reports")

    # Image and Media References
    product_images: list[str] | None = Field(
        default_factory=list, description="List of product image file paths or IDs"
    )
    shipment_photos: list[str] | None = Field(
        default_factory=list, description="List of shipment photo file paths or IDs"
    )
    damage_images: list[str] | None = Field(
        default_factory=list,
        description="List of damage documentation image file paths or IDs",
    )
    warehouse_photos: list[str] | None = Field(
        default_factory=list,
        description="List of warehouse/storage image file paths or IDs",
    )
    inspection_images: list[str] | None = Field(
        default_factory=list,
        description="List of quality inspection image file paths or IDs",
    )

    # Document References
    purchase_orders: list[str] | None = Field(
        default_factory=list,
        description="List of purchase order document file paths or IDs",
    )
    invoices: list[str] | None = Field(
        default_factory=list, description="List of invoice document file paths or IDs"
    )
    shipping_documents: list[str] | None = Field(
        default_factory=list, description="List of shipping document file paths or IDs"
    )
    certificates: list[str] | None = Field(
        default_factory=list,
        description="List of certificate document file paths or IDs",
    )

    # Audit fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str | None = Field(None, description="User who created the record")

    @model_validator(mode="after")
    def validate_total_cost(self):
        """Validate that total cost is reasonable based on quantity and unit cost."""
        v = self.total_cost
        quantity = self.quantity
        unit_cost = self.unit_cost
        if v and quantity and unit_cost:
            expected_total = quantity * unit_cost
            if abs(v - expected_total) > expected_total * 0.1:  # 10% tolerance
                msg = f"Total cost {v} doesn't match quantity × unit cost ({expected_total})"
                raise ValueError(msg)
        return self

    class Config:
        schema_extra = {
            "example": {
                "case_id": "LOG001",
                "operation_id": "OP001",
                "logistics_type": "supply_chain",
                "supplier": "MedSupply Corp",
                "product_name": "Surgical Instruments Set",
                "product_code": "SI-2024-001",
                "quantity": 50,
                "unit_cost": 125.50,
                "total_cost": 6275.00,
                "order_date": "2025-01-15T10:00:00",
                "expected_delivery": "2025-01-30T15:00:00",
                "lead_time_days": 15,
                "origin_location": "Manufacturing Plant A",
                "destination_location": "Hospital Central Warehouse",
                "transportation_mode": "Ground Freight",
                "status": "in_transit",
                "priority": "high",
                "operation_notes": "Urgent restocking of surgical instruments.",
                "delivery_instructions": "Deliver to loading dock B, requires signature.",
                "product_images": ["/path/to/product_image1.jpg"],
                "shipping_documents": ["/path/to/shipping_doc.pdf"],
            }
        }


class LogisticsAnalysisResult(BaseModel):
    """Model for storing and presenting comprehensive logistics analysis
    results including optimization recommendations and performance metrics.
    """

    case_id: str
    logistics_type: LogisticsType
    analysis_timestamp: datetime

    # Performance Analysis
    overall_performance: str = Field(..., description="Overall performance rating")
    efficiency_metrics: dict[str, float] = Field(default_factory=dict)
    cost_analysis: dict[str, float] = Field(default_factory=dict)

    # Optimization Recommendations
    optimization_opportunities: list[str] = Field(default_factory=list)
    cost_reduction_potential: float | None = Field(
        None, description="Potential cost savings"
    )
    efficiency_improvements: list[str] = Field(default_factory=list)

    # Risk Assessment
    risk_factors: list[str] = Field(default_factory=list)
    risk_mitigation: list[str] = Field(default_factory=list)
    bottlenecks: list[dict[str, Any]] = Field(default_factory=list)

    # Performance Predictions
    predicted_delivery_time: float | None = Field(
        None, description="Predicted delivery time in days"
    )
    predicted_cost: float | None = Field(None, description="Predicted total cost")
    success_probability: float | None = Field(
        None, ge=0, le=1, description="Success probability"
    )

    # Benchmarking
    industry_benchmarks: dict[str, float] = Field(default_factory=dict)
    performance_ranking: str | None = Field(
        None, description="Performance ranking vs benchmarks"
    )

    # Action Items
    immediate_actions: list[str] = Field(default_factory=list)
    strategic_recommendations: list[str] = Field(default_factory=list)
    next_review_date: datetime | None = Field(None, description="Next scheduled review")

    # Text and Image Output Data
    generated_report: str | None = Field(
        None, description="Generated comprehensive logistics analysis report"
    )
    optimization_summary: str | None = Field(
        None, description="Generated optimization recommendations summary"
    )
    performance_narrative: str | None = Field(
        None, description="Generated performance analysis narrative"
    )
    supplier_feedback: str | None = Field(
        None, description="Generated supplier performance feedback"
    )

    # Generated Images and Visualizations
    performance_dashboard: str | None = Field(
        None, description="Path to generated performance dashboard visualization"
    )
    cost_trend_charts: list[str] | None = Field(
        default_factory=list, description="List of generated cost trend charts"
    )
    efficiency_graphs: list[str] | None = Field(
        default_factory=list,
        description="List of generated efficiency visualization graphs",
    )
    supply_chain_map: str | None = Field(
        None, description="Path to generated supply chain visualization map"
    )

    # Generated Documents
    full_analysis_pdf: str | None = Field(
        None, description="Path to generated full logistics analysis PDF"
    )
    executive_summary_pdf: str | None = Field(
        None, description="Path to generated executive summary PDF"
    )
    optimization_plan_doc: str | None = Field(
        None, description="Path to generated optimization plan document"
    )

    # Confidence and Validation
    confidence_score: float = Field(
        ..., ge=0, le=1, description="Overall confidence in analysis results"
    )
    data_quality_score: float | None = Field(
        None, ge=0, le=1, description="Quality of input data used"
    )

    class Config:
        schema_extra = {
            "example": {
                "case_id": "LOG001",
                "logistics_type": "supply_chain",
                "analysis_timestamp": "2025-01-20T14:30:00",
                "overall_performance": "good",
                "efficiency_metrics": {
                    "on_time_delivery": 0.85,
                    "cost_efficiency": 0.78,
                },
                "cost_analysis": {"total_cost": 6275.00, "cost_per_unit": 125.50},
                "optimization_opportunities": [
                    "Bulk ordering discount",
                    "Alternative supplier evaluation",
                ],
                "cost_reduction_potential": 850.00,
                "risk_factors": ["Single supplier dependency", "Weather delays"],
                "predicted_delivery_time": 12.5,
                "predicted_cost": 5950.00,
                "confidence_score": 0.82,
                "generated_report": "Comprehensive logistics analysis shows...",
                "performance_dashboard": "/path/to/dashboard.png",
                "full_analysis_pdf": "/path/to/logistics_analysis.pdf",
            }
        }
