"""Service layer for case management business logic."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..domain.models import (
    Case,
    CaseActivity,
    CaseComment,
    CaseCreate,
    CasePriority,
    CaseResponse,
    CaseStatus,
    CaseUpdate,
    CommentCreate,
    CommentResponse,
    NotificationType,
)
from ..utils.exceptions import NotFoundError
from ..utils.pagination import Page, PageParams
from .analytics_service import AnalyticsService
from .notification_service import NotificationService


class CaseService:
    """Service for case management operations."""

    def __init__(
        self,
        db: AsyncSession,
        analytics_service: AnalyticsService,
        notification_service: NotificationService,
    ) -> None:
        self.db = db
        self.analytics = analytics_service
        self.notifications = notification_service

    async def create_case(
        self,
        case_data: CaseCreate,
        creator_id: UUID,
    ) -> CaseResponse:
        """Create a new case."""
        # Generate case number
        case_number = await self._generate_case_number()

        # Create case
        case = Case(
            case_number=case_number,
            creator_id=creator_id,
            **case_data.model_dump(exclude_unset=True),
        )

        self.db.add(case)
        await self.db.flush()

        # Create activity log
        await self._log_activity(
            case_id=case.id,
            user_id=creator_id,
            action="created",
            description=f"Case created: {case.title}",
        )

        # Send notifications
        if case.assignee_id:
            await self.notifications.create_notification(
                user_id=case.assignee_id,
                type=NotificationType.CASE_ASSIGNED,
                title="New Case Assigned",
                message=f"You have been assigned to case: {case.title}",
                data={"case_id": str(case.id)},
            )

        # Track analytics
        await self.analytics.track_event(
            event="case_created",
            user_id=creator_id,
            properties={
                "case_id": str(case.id),
                "priority": case.priority.value,
                "has_assignee": case.assignee_id is not None,
            },
        )

        await self.db.commit()

        # Return with relationships loaded
        return await self.get_case(case.id)

    async def get_case(self, case_id: UUID) -> CaseResponse:
        """Get a case by ID."""
        query = (
            select(Case)
            .options(
                selectinload(Case.creator),
                selectinload(Case.assignee),
                selectinload(Case.team),
            )
            .where(Case.id == case_id)
        )

        result = await self.db.execute(query)
        case = result.scalar_one_or_none()

        if not case:
            msg = f"Case {case_id} not found"
            raise NotFoundError(msg)

        return CaseResponse.model_validate(case)

    async def update_case(
        self,
        case_id: UUID,
        case_data: CaseUpdate,
        user_id: UUID,
    ) -> CaseResponse:
        """Update a case."""
        # Get existing case
        case = await self._get_case_entity(case_id)

        # Track changes for activity log
        changes = {}
        update_data = case_data.model_dump(exclude_unset=True)

        for field, new_value in update_data.items():
            old_value = getattr(case, field)
            if old_value != new_value:
                changes[field] = {"old": old_value, "new": new_value}

        # Update case
        for field, value in update_data.items():
            setattr(case, field, value)

        # Update timestamps based on status changes
        if "status" in changes:
            new_status = changes["status"]["new"]
            if new_status == CaseStatus.ACTIVE and not case.started_at:
                case.started_at = datetime.utcnow()
            elif new_status == CaseStatus.COMPLETED:
                case.completed_at = datetime.utcnow()

        # Log activity
        if changes:
            change_descriptions = []
            for field, change in changes.items():
                change_descriptions.append(
                    f"{field}: {change['old']} → {change['new']}"
                )

            await self._log_activity(
                case_id=case.id,
                user_id=user_id,
                action="updated",
                description=f"Case updated: {', '.join(change_descriptions)}",
                changes=changes,
            )

            # Send notifications for significant changes
            if "status" in changes:
                await self._notify_status_change(case, user_id)

            if "priority" in changes:
                await self._notify_priority_change(case, user_id)

            if "assignee_id" in changes and changes["assignee_id"]["new"]:
                await self.notifications.create_notification(
                    user_id=changes["assignee_id"]["new"],
                    type=NotificationType.CASE_ASSIGNED,
                    title="Case Assigned",
                    message=f"You have been assigned to case: {case.title}",
                    data={"case_id": str(case.id)},
                )

        await self.db.commit()

        return await self.get_case(case.id)

    async def list_cases(
        self,
        page_params: PageParams,
        user_id: UUID | None = None,
        team_id: UUID | None = None,
        status: CaseStatus | None = None,
        priority: CasePriority | None = None,
        assigned_to: UUID | None = None,
        search: str | None = None,
    ) -> Page[CaseResponse]:
        """List cases with filtering and pagination."""
        query = select(Case).options(
            selectinload(Case.creator),
            selectinload(Case.assignee),
            selectinload(Case.team),
        )

        # Apply filters
        filters = []

        if team_id:
            filters.append(Case.team_id == team_id)

        if status:
            filters.append(Case.status == status)

        if priority:
            filters.append(Case.priority == priority)

        if assigned_to:
            filters.append(Case.assignee_id == assigned_to)

        if search:
            search_term = f"%{search}%"
            filters.append(
                Case.title.ilike(search_term)
                | Case.description.ilike(search_term)
                | Case.case_number.ilike(search_term)
            )

        if filters:
            query = query.where(and_(*filters))

        # Apply ordering
        query = query.order_by(desc(Case.updated_at))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        query = query.offset(page_params.skip).limit(page_params.size)

        result = await self.db.execute(query)
        cases = result.scalars().all()

        return Page(
            items=[CaseResponse.model_validate(case) for case in cases],
            total=total,
            page=page_params.page,
            size=page_params.size,
        )

    async def add_comment(
        self,
        case_id: UUID,
        comment_data: CommentCreate,
        author_id: UUID,
    ) -> CommentResponse:
        """Add a comment to a case."""
        # Verify case exists
        await self._get_case_entity(case_id)

        # Create comment
        comment = CaseComment(
            case_id=case_id, author_id=author_id, **comment_data.model_dump()
        )

        self.db.add(comment)
        await self.db.flush()

        # Log activity
        await self._log_activity(
            case_id=case_id,
            user_id=author_id,
            action="commented",
            description="Added comment to case",
        )

        # Send notifications to case participants
        if not comment.is_internal:
            await self._notify_comment_added(case_id, author_id, comment.content)

        await self.db.commit()

        # Return with author loaded
        query = (
            select(CaseComment)
            .options(selectinload(CaseComment.author))
            .where(CaseComment.id == comment.id)
        )

        result = await self.db.execute(query)
        comment_with_author = result.scalar_one()

        return CommentResponse.model_validate(comment_with_author)

    async def get_case_comments(
        self,
        case_id: UUID,
        include_internal: bool = False,
    ) -> list[CommentResponse]:
        """Get comments for a case."""
        query = (
            select(CaseComment)
            .options(selectinload(CaseComment.author))
            .where(CaseComment.case_id == case_id)
        )

        if not include_internal:
            query = query.where(not CaseComment.is_internal)

        query = query.order_by(CaseComment.created_at)

        result = await self.db.execute(query)
        comments = result.scalars().all()

        return [CommentResponse.model_validate(comment) for comment in comments]

    async def get_case_activities(
        self,
        case_id: UUID,
        limit: int = 50,
    ) -> list[dict]:
        """Get activities for a case."""
        query = (
            select(CaseActivity)
            .options(selectinload(CaseActivity.user))
            .where(CaseActivity.case_id == case_id)
            .order_by(desc(CaseActivity.created_at))
            .limit(limit)
        )

        result = await self.db.execute(query)
        activities = result.scalars().all()

        return [
            {
                "id": str(activity.id),
                "action": activity.action,
                "description": activity.description,
                "changes": activity.changes,
                "user": {
                    "id": str(activity.user.id),
                    "full_name": activity.user.full_name,
                    "username": activity.user.username,
                }
                if activity.user
                else None,
                "created_at": activity.created_at,
            }
            for activity in activities
        ]

    async def delete_case(self, case_id: UUID, user_id: UUID) -> None:
        """Delete a case (soft delete by archiving)."""
        case = await self._get_case_entity(case_id)

        # Archive instead of delete
        case.status = CaseStatus.ARCHIVED

        # Log activity
        await self._log_activity(
            case_id=case.id,
            user_id=user_id,
            action="archived",
            description="Case archived",
        )

        await self.db.commit()

    async def get_overdue_cases(
        self, team_id: UUID | None = None
    ) -> list[CaseResponse]:
        """Get overdue cases."""
        query = (
            select(Case)
            .options(
                selectinload(Case.creator),
                selectinload(Case.assignee),
                selectinload(Case.team),
            )
            .where(
                and_(
                    Case.due_date < datetime.utcnow(),
                    Case.status.in_([CaseStatus.ACTIVE, CaseStatus.REVIEW]),
                )
            )
        )

        if team_id:
            query = query.where(Case.team_id == team_id)

        result = await self.db.execute(query)
        cases = result.scalars().all()

        return [CaseResponse.model_validate(case) for case in cases]

    # Private methods

    async def _get_case_entity(self, case_id: UUID) -> Case:
        """Get case entity or raise not found."""
        result = await self.db.execute(select(Case).where(Case.id == case_id))
        case = result.scalar_one_or_none()

        if not case:
            msg = f"Case {case_id} not found"
            raise NotFoundError(msg)

        return case

    async def _generate_case_number(self) -> str:
        """Generate unique case number."""
        # Get current year and count
        year = datetime.utcnow().year

        count_result = await self.db.execute(
            select(func.count(Case.id)).where(
                func.extract("year", Case.created_at) == year
            )
        )
        count = count_result.scalar() + 1

        return f"CASE-{year}-{count:04d}"

    async def _log_activity(
        self,
        case_id: UUID,
        user_id: UUID,
        action: str,
        description: str,
        changes: dict | None = None,
    ) -> None:
        """Log case activity."""
        activity = CaseActivity(
            case_id=case_id,
            user_id=user_id,
            action=action,
            description=description,
            changes=changes or {},
        )

        self.db.add(activity)

    async def _notify_status_change(self, case: Case, user_id: UUID) -> None:
        """Send notifications for status changes."""
        # Notify assignee if different from user making the change
        if case.assignee_id and case.assignee_id != user_id:
            await self.notifications.create_notification(
                user_id=case.assignee_id,
                type=NotificationType.STATUS_CHANGED,
                title="Case Status Changed",
                message=f"Case '{case.title}' status changed to {case.status.value}",
                data={"case_id": str(case.id), "new_status": case.status.value},
            )

    async def _notify_priority_change(self, case: Case, user_id: UUID) -> None:
        """Send notifications for priority changes."""
        # Notify assignee if different from user making the change
        if case.assignee_id and case.assignee_id != user_id:
            await self.notifications.create_notification(
                user_id=case.assignee_id,
                type=NotificationType.PRIORITY_CHANGED,
                title="Case Priority Changed",
                message=f"Case '{case.title}' priority changed to {case.priority.value}",
                data={"case_id": str(case.id), "new_priority": case.priority.value},
            )

    async def _notify_comment_added(
        self,
        case_id: UUID,
        author_id: UUID,
        content: str,
    ) -> None:
        """Send notifications when comments are added."""
        # Get case to find participants
        case = await self._get_case_entity(case_id)

        # Notify creator and assignee (if different from comment author)
        recipients = []

        if case.creator_id != author_id:
            recipients.append(case.creator_id)

        if case.assignee_id and case.assignee_id != author_id:
            recipients.append(case.assignee_id)

        for recipient_id in recipients:
            await self.notifications.create_notification(
                user_id=recipient_id,
                type=NotificationType.COMMENT_ADDED,
                title="New Comment",
                message=f"New comment on case '{case.title}': {content[:100]}...",
                data={"case_id": str(case.id)},
            )
