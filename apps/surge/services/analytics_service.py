"""Analytics service for advanced metrics and reporting."""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.cache import cache_response
from ..domain.models import Case, CaseActivity, CaseStatus, DashboardMetrics, User
from ..utils.redis_client import get_redis_client


class AnalyticsService:
    """Service for analytics and metrics."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.redis = get_redis_client()

    @cache_response(ttl=300)  # Cache for 5 minutes
    async def get_dashboard_metrics(
        self,
        team_id: UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> DashboardMetrics:
        """Get comprehensive dashboard metrics."""
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=30)
        if not date_to:
            date_to = datetime.utcnow()

        # Base query with optional team filter
        base_query = select(Case)
        if team_id:
            base_query = base_query.where(Case.team_id == team_id)

        # Get basic counts
        total_cases = await self._get_case_count(base_query)
        active_cases = await self._get_case_count(
            base_query.where(Case.status == CaseStatus.ACTIVE)
        )
        completed_cases = await self._get_case_count(
            base_query.where(Case.status == CaseStatus.COMPLETED)
        )
        overdue_cases = await self._get_case_count(
            base_query.where(
                and_(
                    Case.due_date < datetime.utcnow(),
                    Case.status.in_([CaseStatus.ACTIVE, CaseStatus.REVIEW]),
                )
            )
        )

        # Get team performance data
        team_performance = await self._get_team_performance(team_id, date_from, date_to)

        # Get recent activities
        recent_activities = await self._get_recent_activities(team_id, limit=10)

        # Get chart data
        charts_data = await self._get_charts_data(team_id, date_from, date_to)

        return DashboardMetrics(
            total_cases=total_cases,
            active_cases=active_cases,
            completed_cases=completed_cases,
            overdue_cases=overdue_cases,
            team_performance=team_performance,
            recent_activities=recent_activities,
            charts_data=charts_data,
        )

    async def track_event(
        self,
        event: str,
        user_id: UUID,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """Track analytics event."""
        event_data = {
            "event": event,
            "user_id": str(user_id),
            "properties": properties or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store in Redis for real-time analytics
        if self.redis:
            try:
                await self.redis.lpush("analytics:events", str(event_data))
                # Keep only last 10000 events
                await self.redis.ltrim("analytics:events", 0, 9999)
            except Exception:
                # Fail silently for analytics
                pass

    async def get_case_trends(
        self,
        team_id: UUID | None = None,
        days: int = 30,
    ) -> dict[str, list[dict[str, Any]]]:
        """Get case creation and completion trends."""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)

        # Get daily case creation counts
        creation_query = (
            select(
                func.date(Case.created_at).label("date"),
                func.count(Case.id).label("count"),
            )
            .where(
                and_(
                    func.date(Case.created_at) >= start_date,
                    func.date(Case.created_at) <= end_date,
                )
            )
            .group_by(func.date(Case.created_at))
            .order_by(func.date(Case.created_at))
        )

        if team_id:
            creation_query = creation_query.where(Case.team_id == team_id)

        creation_result = await self.db.execute(creation_query)
        creation_data = [
            {"date": row.date.isoformat(), "count": row.count}
            for row in creation_result
        ]

        # Get daily case completion counts
        completion_query = (
            select(
                func.date(Case.completed_at).label("date"),
                func.count(Case.id).label("count"),
            )
            .where(
                and_(
                    Case.completed_at.isnot(None),
                    func.date(Case.completed_at) >= start_date,
                    func.date(Case.completed_at) <= end_date,
                )
            )
            .group_by(func.date(Case.completed_at))
            .order_by(func.date(Case.completed_at))
        )

        if team_id:
            completion_query = completion_query.where(Case.team_id == team_id)

        completion_result = await self.db.execute(completion_query)
        completion_data = [
            {"date": row.date.isoformat(), "count": row.count}
            for row in completion_result
        ]

        return {
            "created": creation_data,
            "completed": completion_data,
        }

    async def get_status_distribution(
        self,
        team_id: UUID | None = None,
    ) -> list[dict[str, Any]]:
        """Get case status distribution."""
        query = select(Case.status, func.count(Case.id).label("count")).group_by(
            Case.status
        )

        if team_id:
            query = query.where(Case.team_id == team_id)

        result = await self.db.execute(query)

        return [
            {
                "status": row.status.value,
                "count": row.count,
                "label": row.status.value.title(),
            }
            for row in result
        ]

    async def get_priority_distribution(
        self,
        team_id: UUID | None = None,
    ) -> list[dict[str, Any]]:
        """Get case priority distribution."""
        query = select(Case.priority, func.count(Case.id).label("count")).group_by(
            Case.priority
        )

        if team_id:
            query = query.where(Case.team_id == team_id)

        result = await self.db.execute(query)

        return [
            {
                "priority": row.priority.value,
                "count": row.count,
                "label": row.priority.value.title(),
            }
            for row in result
        ]

    async def get_team_workload(
        self,
        team_id: UUID | None = None,
    ) -> list[dict[str, Any]]:
        """Get team member workload distribution."""
        query = (
            select(
                User.full_name, User.username, func.count(Case.id).label("active_cases")
            )
            .select_from(User)
            .outerjoin(Case, Case.assignee_id == User.id)
            .where(Case.status.in_([CaseStatus.ACTIVE, CaseStatus.REVIEW]))
            .group_by(User.id, User.full_name, User.username)
            .order_by(desc(func.count(Case.id)))
        )

        if team_id:
            # Join with team memberships if filtering by team
            from ..domain.models import TeamMembership

            query = query.join(TeamMembership, TeamMembership.user_id == User.id).where(
                TeamMembership.team_id == team_id
            )

        result = await self.db.execute(query)

        return [
            {
                "user": row.full_name,
                "username": row.username,
                "active_cases": row.active_cases,
            }
            for row in result
        ]

    async def get_completion_time_stats(
        self,
        team_id: UUID | None = None,
        days: int = 30,
    ) -> dict[str, Any]:
        """Get case completion time statistics."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get cases completed in the period
        query = select(
            Case.created_at,
            Case.completed_at,
            (
                func.extract("epoch", Case.completed_at)
                - func.extract("epoch", Case.created_at)
            ).label("duration_seconds"),
        ).where(
            and_(
                Case.completed_at.isnot(None),
                Case.completed_at >= start_date,
                Case.completed_at <= end_date,
            )
        )

        if team_id:
            query = query.where(Case.team_id == team_id)

        result = await self.db.execute(query)
        durations = [row.duration_seconds / 3600 for row in result]  # Convert to hours

        if not durations:
            return {
                "average_hours": 0,
                "median_hours": 0,
                "min_hours": 0,
                "max_hours": 0,
                "total_cases": 0,
            }

        durations.sort()
        count = len(durations)

        return {
            "average_hours": sum(durations) / count,
            "median_hours": durations[count // 2],
            "min_hours": min(durations),
            "max_hours": max(durations),
            "total_cases": count,
        }

    async def get_user_activity_heatmap(
        self,
        user_id: UUID,
        days: int = 30,
    ) -> list[dict[str, Any]]:
        """Get user activity heatmap data."""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)

        query = (
            select(
                func.date(CaseActivity.created_at).label("date"),
                func.count(CaseActivity.id).label("activity_count"),
            )
            .where(
                and_(
                    CaseActivity.user_id == user_id,
                    func.date(CaseActivity.created_at) >= start_date,
                    func.date(CaseActivity.created_at) <= end_date,
                )
            )
            .group_by(func.date(CaseActivity.created_at))
            .order_by(func.date(CaseActivity.created_at))
        )

        result = await self.db.execute(query)

        return [
            {
                "date": row.date.isoformat(),
                "activity_count": row.activity_count,
            }
            for row in result
        ]

    # Private methods

    async def _get_case_count(self, query) -> int:
        """Get count from a case query."""
        count_query = select(func.count()).select_from(query.subquery())
        result = await self.db.execute(count_query)
        return result.scalar()

    async def _get_team_performance(
        self,
        team_id: UUID | None,
        date_from: datetime,
        date_to: datetime,
    ) -> dict[str, Any]:
        """Get team performance metrics."""
        # Cases created vs completed in period
        base_query = select(Case)
        if team_id:
            base_query = base_query.where(Case.team_id == team_id)

        created_query = base_query.where(
            and_(
                Case.created_at >= date_from,
                Case.created_at <= date_to,
            )
        )

        completed_query = base_query.where(
            and_(
                Case.completed_at >= date_from,
                Case.completed_at <= date_to,
            )
        )

        created_count = await self._get_case_count(created_query)
        completed_count = await self._get_case_count(completed_query)

        # Calculate completion rate
        completion_rate = (
            (completed_count / created_count * 100) if created_count > 0 else 0
        )

        return {
            "cases_created": created_count,
            "cases_completed": completed_count,
            "completion_rate": round(completion_rate, 1),
            "period_days": (date_to - date_from).days,
        }

    async def _get_recent_activities(
        self,
        team_id: UUID | None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get recent case activities."""
        query = (
            select(CaseActivity)
            .join(Case, CaseActivity.case_id == Case.id)
            .join(User, CaseActivity.user_id == User.id)
            .order_by(desc(CaseActivity.created_at))
            .limit(limit)
        )

        if team_id:
            query = query.where(Case.team_id == team_id)

        result = await self.db.execute(query)
        activities = result.scalars().all()

        return [
            {
                "id": str(activity.id),
                "action": activity.action,
                "description": activity.description,
                "created_at": activity.created_at.isoformat(),
                "user": {
                    "full_name": activity.user.full_name,
                    "username": activity.user.username,
                },
                "case": {
                    "id": str(activity.case.id),
                    "title": activity.case.title,
                    "case_number": activity.case.case_number,
                },
            }
            for activity in activities
        ]

    async def _get_charts_data(
        self,
        team_id: UUID | None,
        date_from: datetime,
        date_to: datetime,
    ) -> dict[str, Any]:
        """Get chart data for dashboard."""
        return {
            "case_trends": await self.get_case_trends(team_id, 30),
            "status_distribution": await self.get_status_distribution(team_id),
            "priority_distribution": await self.get_priority_distribution(team_id),
            "team_workload": await self.get_team_workload(team_id),
            "completion_stats": await self.get_completion_time_stats(team_id, 30),
        }
