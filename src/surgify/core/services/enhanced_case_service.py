"""
Enhanced Case Service - Advanced case analytics and management
Provides comprehensive case processing capabilities for the Surgify platform
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.orm import Case, User
from ..cache import cache_response, invalidate_cache
from .logger import get_logger

logger = get_logger(__name__)


class EnhancedCaseService:
    """
    Enhanced case service providing advanced analytics and processing
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.logger = logger

    async def create_case(
        self, case_data: Dict[str, Any], user_id: int
    ) -> Dict[str, Any]:
        """Create a new case with enhanced validation and processing"""
        try:
            # Validate required fields
            required_fields = ["title", "description", "domain"]
            for field in required_fields:
                if field not in case_data:
                    raise ValueError(f"Missing required field: {field}")

            # Create case instance
            case = Case(
                title=case_data["title"],
                description=case_data["description"],
                domain=case_data.get("domain", "surgery"),
                status=case_data.get("status", "active"),
                priority=case_data.get("priority", "medium"),
                created_by=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            # Add case to database
            self.db.add(case)
            await self.db.commit()
            await self.db.refresh(case)

            # Invalidate cache
            await invalidate_cache(f"cases_user_{user_id}")
            await invalidate_cache("cases_all")

            self.logger.info(f"Created case {case.id} for user {user_id}")

            return {
                "id": case.id,
                "title": case.title,
                "description": case.description,
                "domain": case.domain,
                "status": case.status,
                "priority": case.priority,
                "created_by": case.created_by,
                "created_at": case.created_at.isoformat(),
                "updated_at": case.updated_at.isoformat(),
            }

        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to create case: {str(e)}")
            raise

    @cache_response(ttl=300)  # 5 minutes
    async def get_case_analytics(self, case_id: int) -> Dict[str, Any]:
        """Get comprehensive analytics for a specific case"""
        try:
            # Get case details
            result = await self.db.execute(select(Case).where(Case.id == case_id))
            case = result.scalar_one_or_none()

            if not case:
                raise ValueError(f"Case {case_id} not found")

            # Calculate analytics
            analytics = {
                "case_id": case_id,
                "basic_info": {
                    "title": case.title,
                    "domain": case.domain,
                    "status": case.status,
                    "priority": case.priority,
                    "age_days": (datetime.utcnow() - case.created_at).days,
                },
                "engagement_metrics": {
                    "views": getattr(case, "view_count", 0),
                    "comments": getattr(case, "comment_count", 0),
                    "shares": getattr(case, "share_count", 0),
                    "last_activity": case.updated_at.isoformat(),
                },
                "performance_indicators": {
                    "completion_score": self._calculate_completion_score(case),
                    "quality_score": self._calculate_quality_score(case),
                    "impact_score": self._calculate_impact_score(case),
                },
            }

            return analytics

        except Exception as e:
            self.logger.error(f"Failed to get case analytics for {case_id}: {str(e)}")
            raise

    @cache_response(ttl=600)  # 10 minutes
    async def get_cohort_analytics(self, domain: str = None) -> Dict[str, Any]:
        """Get analytics for case cohorts"""
        try:
            # Build query
            query = select(Case)
            if domain:
                query = query.where(Case.domain == domain)

            result = await self.db.execute(query)
            cases = result.scalars().all()

            if not cases:
                return {"total_cases": 0, "analytics": {}}

            # Convert to DataFrame for analysis
            df = pd.DataFrame(
                [
                    {
                        "id": case.id,
                        "domain": case.domain,
                        "status": case.status,
                        "priority": case.priority,
                        "created_at": case.created_at,
                        "updated_at": case.updated_at,
                    }
                    for case in cases
                ]
            )

            # Calculate cohort analytics
            analytics = {
                "total_cases": len(cases),
                "domain_distribution": df["domain"].value_counts().to_dict(),
                "status_distribution": df["status"].value_counts().to_dict(),
                "priority_distribution": df["priority"].value_counts().to_dict(),
                "temporal_trends": self._analyze_temporal_trends(df),
                "performance_metrics": self._calculate_cohort_metrics(df),
            }

            return analytics

        except Exception as e:
            self.logger.error(f"Failed to get cohort analytics: {str(e)}")
            raise

    async def process_csv_upload(
        self, file_content: bytes, domain: str, user_id: int
    ) -> Dict[str, Any]:
        """Process CSV upload for bulk case creation"""
        try:
            # Parse CSV
            df = pd.read_csv(pd.io.common.StringIO(file_content.decode("utf-8")))

            # Validate CSV structure
            required_columns = ["title", "description"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            # Process cases
            created_cases = []
            errors = []

            for index, row in df.iterrows():
                try:
                    case_data = {
                        "title": row["title"],
                        "description": row["description"],
                        "domain": domain,
                        "status": row.get("status", "active"),
                        "priority": row.get("priority", "medium"),
                    }

                    case = await self.create_case(case_data, user_id)
                    created_cases.append(case)

                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")

            # Return results
            result = {
                "total_rows": len(df),
                "created_cases": len(created_cases),
                "errors": len(errors),
                "cases": created_cases,
                "error_details": errors,
            }

            self.logger.info(
                f"Processed CSV upload: {result['created_cases']} cases created, {result['errors']} errors"
            )

            return result

        except Exception as e:
            self.logger.error(f"Failed to process CSV upload: {str(e)}")
            raise

    def _calculate_completion_score(self, case: Case) -> float:
        """Calculate case completion score based on various factors"""
        score = 0.0

        # Basic information completeness
        if case.title:
            score += 20
        if case.description:
            score += 20
        if case.status:
            score += 10
        if case.priority:
            score += 10

        # Activity recency
        days_since_update = (datetime.utcnow() - case.updated_at).days
        if days_since_update < 7:
            score += 20
        elif days_since_update < 30:
            score += 10

        # Status-based scoring
        if case.status == "completed":
            score += 20
        elif case.status == "in_progress":
            score += 15
        elif case.status == "active":
            score += 10

        return min(100.0, score)

    def _calculate_quality_score(self, case: Case) -> float:
        """Calculate case quality score"""
        score = 0.0

        # Description quality
        if case.description:
            desc_length = len(case.description)
            if desc_length > 100:
                score += 25
            elif desc_length > 50:
                score += 15
            elif desc_length > 20:
                score += 10

        # Title quality
        if case.title:
            title_length = len(case.title)
            if title_length > 20:
                score += 15
            elif title_length > 10:
                score += 10

        # Metadata completeness
        if case.domain:
            score += 10
        if case.priority:
            score += 10
        if case.status:
            score += 10

        # Engagement indicators
        if hasattr(case, "view_count") and case.view_count > 0:
            score += 10
        if hasattr(case, "comment_count") and case.comment_count > 0:
            score += 10

        # Update frequency
        update_frequency = (datetime.utcnow() - case.created_at).days
        if update_frequency > 0:
            score += min(10, (case.updated_at - case.created_at).days)

        return min(100.0, score)

    def _calculate_impact_score(self, case: Case) -> float:
        """Calculate case impact score"""
        score = 0.0

        # Priority-based scoring
        priority_scores = {"critical": 30, "high": 25, "medium": 15, "low": 10}
        score += priority_scores.get(case.priority, 10)

        # Domain-based scoring
        domain_scores = {"surgery": 25, "logistics": 20, "insurance": 20}
        score += domain_scores.get(case.domain, 15)

        # Engagement-based scoring
        if hasattr(case, "view_count"):
            score += min(20, case.view_count * 0.5)
        if hasattr(case, "comment_count"):
            score += min(15, case.comment_count * 2)
        if hasattr(case, "share_count"):
            score += min(10, case.share_count * 3)

        return min(100.0, score)

    def _analyze_temporal_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze temporal trends in case data"""
        try:
            # Convert dates
            df["created_at"] = pd.to_datetime(df["created_at"])
            df["updated_at"] = pd.to_datetime(df["updated_at"])

            # Calculate trends
            now = datetime.utcnow()
            last_week = now - timedelta(days=7)
            last_month = now - timedelta(days=30)

            trends = {
                "cases_last_week": len(df[df["created_at"] >= last_week]),
                "cases_last_month": len(df[df["created_at"] >= last_month]),
                "average_age_days": (now - df["created_at"]).dt.days.mean(),
                "most_active_day": df["created_at"].dt.day_name().mode().iloc[0]
                if len(df) > 0
                else None,
                "creation_trend": "increasing"
                if len(df[df["created_at"] >= last_week])
                > len(df[df["created_at"] >= last_month]) / 4
                else "stable",
            }

            return trends

        except Exception as e:
            self.logger.error(f"Failed to analyze temporal trends: {str(e)}")
            return {}

    def _calculate_cohort_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate cohort performance metrics"""
        try:
            metrics = {
                "completion_rate": len(df[df["status"] == "completed"]) / len(df) * 100
                if len(df) > 0
                else 0,
                "active_rate": len(df[df["status"] == "active"]) / len(df) * 100
                if len(df) > 0
                else 0,
                "high_priority_rate": len(df[df["priority"] == "high"]) / len(df) * 100
                if len(df) > 0
                else 0,
                "average_lifecycle_days": (
                    (
                        pd.to_datetime(df["updated_at"])
                        - pd.to_datetime(df["created_at"])
                    ).dt.days.mean()
                )
                if len(df) > 0
                else 0,
            }

            return metrics

        except Exception as e:
            self.logger.error(f"Failed to calculate cohort metrics: {str(e)}")
            return {}
