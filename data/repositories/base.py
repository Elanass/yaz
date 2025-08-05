"""
Base Repository Pattern
Healthcare-grade data access layer with audit trails and HIPAA compliance
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from sqlalchemy import and_, asc, delete, desc, func, or_, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.models.base import ApiResponse, PaginationMeta, PaginationParams
from core.services.logger import get_logger

T = TypeVar("T")  # ORM model type
P = TypeVar("P")  # Pydantic model type

logger = get_logger(__name__)


class BaseRepository(ABC, Generic[T]):
    """
    Base repository class providing common CRUD operations
    with audit trails and healthcare-grade security
    """

    def __init__(self, model: type[T], session: AsyncSession):
        self.model = model
        self.session = session
        self.logger = get_logger(f"{self.__class__.__name__}")

    async def create(self, entity: T, user_id: str = None) -> T:
        """Create a new entity with audit trail"""
        try:
            # Set audit fields if available
            if hasattr(entity, "created_by") and user_id:
                entity.created_by = user_id

            self.session.add(entity)
            await self.session.flush()  # Get ID without committing

            # Log creation
            await self._log_audit_event(
                action="create",
                entity_id=getattr(entity, "id", None),
                user_id=user_id,
                new_values=self._entity_to_dict(entity),
            )

            return entity

        except IntegrityError as e:
            await self.session.rollback()
            self.logger.error(f"Integrity error creating {self.model.__name__}: {e}")
            raise ValueError(f"Data integrity violation: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error creating {self.model.__name__}: {e}")
            raise

    async def get_by_id(self, entity_id: UUID, user_id: str = None) -> Optional[T]:
        """Get entity by ID with audit trail"""
        try:
            query = select(self.model).where(self.model.id == entity_id)
            result = await self.session.execute(query)
            entity = result.scalar_one_or_none()

            if entity:
                # Log access
                await self._log_audit_event(
                    action="read", entity_id=entity_id, user_id=user_id
                )

            return entity

        except Exception as e:
            self.logger.error(
                f"Error getting {self.model.__name__} by ID {entity_id}: {e}"
            )
            raise

    async def get_all(
        self,
        pagination: PaginationParams = None,
        filters: Dict[str, Any] = None,
        order_by: str = "created_at",
        order_direction: str = "desc",
        user_id: str = None,
    ) -> tuple[List[T], PaginationMeta]:
        """Get all entities with pagination and filtering"""
        try:
            query = select(self.model)

            # Apply filters
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field) and value is not None:
                        if isinstance(value, list):
                            query = query.where(getattr(self.model, field).in_(value))
                        else:
                            query = query.where(getattr(self.model, field) == value)

            # Count total for pagination
            count_query = select(func.count(self.model.id))
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field) and value is not None:
                        if isinstance(value, list):
                            count_query = count_query.where(
                                getattr(self.model, field).in_(value)
                            )
                        else:
                            count_query = count_query.where(
                                getattr(self.model, field) == value
                            )

            total_result = await self.session.execute(count_query)
            total = total_result.scalar()

            # Apply ordering
            if hasattr(self.model, order_by):
                order_func = desc if order_direction.lower() == "desc" else asc
                query = query.order_by(order_func(getattr(self.model, order_by)))

            # Apply pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.size)
                page = pagination.page
                size = pagination.size
            else:
                page = 1
                size = total

            result = await self.session.execute(query)
            entities = result.scalars().all()

            # Create pagination metadata
            pagination_meta = PaginationMeta.create(page, size, total)

            # Log bulk access
            await self._log_audit_event(
                action="read",
                user_id=user_id,
                new_values={"count": len(entities), "filters": filters},
            )

            return list(entities), pagination_meta

        except Exception as e:
            self.logger.error(f"Error getting all {self.model.__name__}: {e}")
            raise

    async def update(
        self, entity_id: UUID, updates: Dict[str, Any], user_id: str = None
    ) -> Optional[T]:
        """Update entity with audit trail"""
        try:
            # Get current entity for audit
            entity = await self.get_by_id(entity_id)
            if not entity:
                return None

            old_values = self._entity_to_dict(entity)

            # Apply updates
            for field, value in updates.items():
                if hasattr(entity, field):
                    setattr(entity, field, value)

            # Set audit fields
            if hasattr(entity, "updated_by") and user_id:
                entity.updated_by = user_id

            await self.session.flush()

            # Log update
            await self._log_audit_event(
                action="update",
                entity_id=entity_id,
                user_id=user_id,
                old_values=old_values,
                new_values=self._entity_to_dict(entity),
            )

            return entity

        except IntegrityError as e:
            await self.session.rollback()
            self.logger.error(f"Integrity error updating {self.model.__name__}: {e}")
            raise ValueError(f"Data integrity violation: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error updating {self.model.__name__} {entity_id}: {e}")
            raise

    async def delete(self, entity_id: UUID, user_id: str = None) -> bool:
        """Soft delete entity with audit trail"""
        try:
            # Get entity for audit
            entity = await self.get_by_id(entity_id)
            if not entity:
                return False

            old_values = self._entity_to_dict(entity)

            # Soft delete if supported, otherwise hard delete
            if hasattr(entity, "deleted_at"):
                entity.deleted_at = func.now()
                if hasattr(entity, "deleted_by"):
                    entity.deleted_by = user_id
            else:
                await self.session.delete(entity)

            await self.session.flush()

            # Log deletion
            await self._log_audit_event(
                action="delete",
                entity_id=entity_id,
                user_id=user_id,
                old_values=old_values,
            )

            return True

        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error deleting {self.model.__name__} {entity_id}: {e}")
            raise

    async def search(
        self,
        search_term: str,
        search_fields: List[str],
        pagination: PaginationParams = None,
        user_id: str = None,
    ) -> tuple[List[T], PaginationMeta]:
        """Search entities across specified fields"""
        try:
            query = select(self.model)

            # Build search conditions
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    field_attr = getattr(self.model, field)
                    if (
                        hasattr(field_attr.type, "python_type")
                        and field_attr.type.python_type == str
                    ):
                        search_conditions.append(field_attr.ilike(f"%{search_term}%"))

            if search_conditions:
                query = query.where(or_(*search_conditions))

            # Count total
            count_query = select(func.count(self.model.id))
            if search_conditions:
                count_query = count_query.where(or_(*search_conditions))

            total_result = await self.session.execute(count_query)
            total = total_result.scalar()

            # Apply pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.size)
                page = pagination.page
                size = pagination.size
            else:
                page = 1
                size = total

            result = await self.session.execute(query)
            entities = result.scalars().all()

            pagination_meta = PaginationMeta.create(page, size, total)

            # Log search
            await self._log_audit_event(
                action="search",
                user_id=user_id,
                new_values={
                    "search_term": search_term,
                    "fields": search_fields,
                    "count": len(entities),
                },
            )

            return list(entities), pagination_meta

        except Exception as e:
            self.logger.error(f"Error searching {self.model.__name__}: {e}")
            raise

    async def exists(self, entity_id: UUID) -> bool:
        """Check if entity exists"""
        try:
            query = select(func.count(self.model.id)).where(self.model.id == entity_id)
            result = await self.session.execute(query)
            count = result.scalar()
            return count > 0
        except Exception as e:
            self.logger.error(
                f"Error checking existence of {self.model.__name__} {entity_id}: {e}"
            )
            raise

    async def bulk_create(self, entities: List[T], user_id: str = None) -> List[T]:
        """Bulk create entities"""
        try:
            for entity in entities:
                if hasattr(entity, "created_by") and user_id:
                    entity.created_by = user_id
                self.session.add(entity)

            await self.session.flush()

            # Log bulk creation
            await self._log_audit_event(
                action="bulk_create",
                user_id=user_id,
                new_values={"count": len(entities)},
            )

            return entities

        except IntegrityError as e:
            await self.session.rollback()
            self.logger.error(
                f"Integrity error bulk creating {self.model.__name__}: {e}"
            )
            raise ValueError(f"Data integrity violation: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error bulk creating {self.model.__name__}: {e}")
            raise

    # Protected methods

    def _entity_to_dict(self, entity: T) -> Dict[str, Any]:
        """Convert entity to dictionary for audit logging"""
        result = {}
        for column in entity.__table__.columns:
            value = getattr(entity, column.name)
            if value is not None:
                # Convert complex types to serializable format
                if hasattr(value, "isoformat"):  # datetime
                    result[column.name] = value.isoformat()
                elif hasattr(value, "__str__"):  # UUID, enums
                    result[column.name] = str(value)
                else:
                    result[column.name] = value
        return result

    async def _log_audit_event(
        self,
        action: str,
        entity_id: UUID = None,
        user_id: str = None,
        old_values: Dict[str, Any] = None,
        new_values: Dict[str, Any] = None,
    ):
        """Log audit event for compliance"""
        # This would integrate with your audit logging system
        # For now, we'll use the logger
        audit_data = {
            "entity_type": self.model.__name__,
            "entity_id": str(entity_id) if entity_id else None,
            "action": action,
            "user_id": user_id,
            "old_values": old_values,
            "new_values": new_values,
        }

        self.logger.info(f"AUDIT: {audit_data}")

        # TODO: Implement proper audit log storage
        # This could write to a separate audit table or external audit service
