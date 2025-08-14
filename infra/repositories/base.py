"""Base repository interfaces and implementations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Union
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository interface."""
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: Union[str, UUID]) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: Union[str, UUID]) -> bool:
        """Delete entity by ID."""
        pass
    
    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        sort_by: str = None,
        sort_order: str = "asc"
    ) -> List[T]:
        """List entities with pagination and filtering."""
        pass
    
    @abstractmethod
    async def count(self, filters: Dict[str, Any] = None) -> int:
        """Count entities with optional filtering."""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: Union[str, UUID]) -> bool:
        """Check if entity exists."""
        pass


class Repository(BaseRepository[T]):
    """SQLAlchemy-based repository implementation."""
    
    def __init__(self, session: Session, model_class: type):
        """
        Initialize repository.
        
        Args:
            session: SQLAlchemy session
            model_class: SQLAlchemy model class
        """
        self.session = session
        self.model_class = model_class
    
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
    
    async def get_by_id(self, entity_id: Union[str, UUID]) -> Optional[T]:
        """Get entity by ID."""
        return await self.session.get(self.model_class, entity_id)
    
    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
    
    async def delete(self, entity_id: Union[str, UUID]) -> bool:
        """Delete entity by ID."""
        entity = await self.get_by_id(entity_id)
        if entity:
            await self.session.delete(entity)
            await self.session.commit()
            return True
        return False
    
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        sort_by: str = None,
        sort_order: str = "asc"
    ) -> List[T]:
        """List entities with pagination and filtering."""
        query = self.session.query(self.model_class)
        
        # Apply filters
        if filters:
            query = self._apply_filters(query, filters)
        
        # Apply sorting
        if sort_by:
            if hasattr(self.model_class, sort_by):
                column = getattr(self.model_class, sort_by)
                if sort_order.lower() == "desc":
                    query = query.order_by(desc(column))
                else:
                    query = query.order_by(asc(column))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        return query.all()
    
    async def count(self, filters: Dict[str, Any] = None) -> int:
        """Count entities with optional filtering."""
        query = self.session.query(self.model_class)
        
        if filters:
            query = self._apply_filters(query, filters)
        
        return query.count()
    
    async def exists(self, entity_id: Union[str, UUID]) -> bool:
        """Check if entity exists."""
        return await self.session.query(
            self.session.query(self.model_class).filter(
                self.model_class.id == entity_id
            ).exists()
        ).scalar()
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to query."""
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                column = getattr(self.model_class, key)
                
                if isinstance(value, dict):
                    # Handle complex filters
                    if 'eq' in value:
                        query = query.filter(column == value['eq'])
                    elif 'ne' in value:
                        query = query.filter(column != value['ne'])
                    elif 'gt' in value:
                        query = query.filter(column > value['gt'])
                    elif 'gte' in value:
                        query = query.filter(column >= value['gte'])
                    elif 'lt' in value:
                        query = query.filter(column < value['lt'])
                    elif 'lte' in value:
                        query = query.filter(column <= value['lte'])
                    elif 'in' in value:
                        query = query.filter(column.in_(value['in']))
                    elif 'not_in' in value:
                        query = query.filter(~column.in_(value['not_in']))
                    elif 'like' in value:
                        query = query.filter(column.like(value['like']))
                    elif 'ilike' in value:
                        query = query.filter(column.ilike(value['ilike']))
                elif isinstance(value, list):
                    # Handle IN clause
                    query = query.filter(column.in_(value))
                else:
                    # Simple equality
                    query = query.filter(column == value)
        
        return query


class CacheableRepository(Repository[T]):
    """Repository with caching capabilities."""
    
    def __init__(self, session: Session, model_class: type, cache_client=None):
        """
        Initialize cacheable repository.
        
        Args:
            session: SQLAlchemy session
            model_class: SQLAlchemy model class
            cache_client: Cache client (Redis, Memcached, etc.)
        """
        super().__init__(session, model_class)
        self.cache_client = cache_client
        self.cache_ttl = 300  # 5 minutes default
    
    async def get_by_id(self, entity_id: Union[str, UUID]) -> Optional[T]:
        """Get entity by ID with caching."""
        if self.cache_client:
            cache_key = f"{self.model_class.__name__}:{entity_id}"
            cached_entity = await self.cache_client.get(cache_key)
            
            if cached_entity:
                return cached_entity
        
        entity = await super().get_by_id(entity_id)
        
        if entity and self.cache_client:
            await self.cache_client.set(cache_key, entity, ttl=self.cache_ttl)
        
        return entity
    
    async def update(self, entity: T) -> T:
        """Update entity and invalidate cache."""
        updated_entity = await super().update(entity)
        
        if self.cache_client:
            cache_key = f"{self.model_class.__name__}:{entity.id}"
            await self.cache_client.delete(cache_key)
        
        return updated_entity
    
    async def delete(self, entity_id: Union[str, UUID]) -> bool:
        """Delete entity and invalidate cache."""
        result = await super().delete(entity_id)
        
        if result and self.cache_client:
            cache_key = f"{self.model_class.__name__}:{entity_id}"
            await self.cache_client.delete(cache_key)
        
        return result


class AuditableRepository(Repository[T]):
    """Repository with audit logging capabilities."""
    
    def __init__(self, session: Session, model_class: type, audit_logger=None):
        """
        Initialize auditable repository.
        
        Args:
            session: SQLAlchemy session
            model_class: SQLAlchemy model class
            audit_logger: Audit logging service
        """
        super().__init__(session, model_class)
        self.audit_logger = audit_logger
    
    async def create(self, entity: T) -> T:
        """Create entity with audit logging."""
        created_entity = await super().create(entity)
        
        if self.audit_logger:
            await self.audit_logger.log_create(
                entity_type=self.model_class.__name__,
                entity_id=str(created_entity.id),
                entity_data=self._serialize_entity(created_entity)
            )
        
        return created_entity
    
    async def update(self, entity: T) -> T:
        """Update entity with audit logging."""
        original_entity = await self.get_by_id(entity.id)
        updated_entity = await super().update(entity)
        
        if self.audit_logger:
            await self.audit_logger.log_update(
                entity_type=self.model_class.__name__,
                entity_id=str(entity.id),
                original_data=self._serialize_entity(original_entity),
                updated_data=self._serialize_entity(updated_entity)
            )
        
        return updated_entity
    
    async def delete(self, entity_id: Union[str, UUID]) -> bool:
        """Delete entity with audit logging."""
        entity = await self.get_by_id(entity_id)
        result = await super().delete(entity_id)
        
        if result and self.audit_logger and entity:
            await self.audit_logger.log_delete(
                entity_type=self.model_class.__name__,
                entity_id=str(entity_id),
                entity_data=self._serialize_entity(entity)
            )
        
        return result
    
    def _serialize_entity(self, entity: T) -> Dict[str, Any]:
        """Serialize entity for audit logging."""
        if hasattr(entity, '__dict__'):
            return {
                key: str(value) for key, value in entity.__dict__.items()
                if not key.startswith('_')
            }
        return {"id": str(entity.id) if hasattr(entity, 'id') else str(entity)}


class TransactionalRepository(Repository[T]):
    """Repository with transaction management."""
    
    async def create_batch(self, entities: List[T]) -> List[T]:
        """Create multiple entities in a single transaction."""
        try:
            for entity in entities:
                self.session.add(entity)
            
            await self.session.commit()
            
            for entity in entities:
                await self.session.refresh(entity)
            
            return entities
        except Exception:
            await self.session.rollback()
            raise
    
    async def update_batch(self, entities: List[T]) -> List[T]:
        """Update multiple entities in a single transaction."""
        try:
            for entity in entities:
                self.session.add(entity)
            
            await self.session.commit()
            
            for entity in entities:
                await self.session.refresh(entity)
            
            return entities
        except Exception:
            await self.session.rollback()
            raise
    
    async def delete_batch(self, entity_ids: List[Union[str, UUID]]) -> bool:
        """Delete multiple entities in a single transaction."""
        try:
            entities = []
            for entity_id in entity_ids:
                entity = await self.get_by_id(entity_id)
                if entity:
                    entities.append(entity)
            
            for entity in entities:
                await self.session.delete(entity)
            
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            raise


class SearchableRepository(Repository[T]):
    """Repository with full-text search capabilities."""
    
    def __init__(self, session: Session, model_class: type, search_fields: List[str]):
        """
        Initialize searchable repository.
        
        Args:
            session: SQLAlchemy session
            model_class: SQLAlchemy model class
            search_fields: List of fields to include in search
        """
        super().__init__(session, model_class)
        self.search_fields = search_fields
    
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> List[T]:
        """Search entities by text query."""
        db_query = self.session.query(self.model_class)
        
        # Apply filters first
        if filters:
            db_query = self._apply_filters(db_query, filters)
        
        # Apply search
        if query:
            search_conditions = []
            for field in self.search_fields:
                if hasattr(self.model_class, field):
                    column = getattr(self.model_class, field)
                    search_conditions.append(column.ilike(f"%{query}%"))
            
            if search_conditions:
                db_query = db_query.filter(or_(*search_conditions))
        
        # Apply pagination
        db_query = db_query.offset(skip).limit(limit)
        
        return db_query.all()
    
    async def search_count(
        self,
        query: str,
        filters: Dict[str, Any] = None
    ) -> int:
        """Count search results."""
        db_query = self.session.query(self.model_class)
        
        if filters:
            db_query = self._apply_filters(db_query, filters)
        
        if query:
            search_conditions = []
            for field in self.search_fields:
                if hasattr(self.model_class, field):
                    column = getattr(self.model_class, field)
                    search_conditions.append(column.ilike(f"%{query}%"))
            
            if search_conditions:
                db_query = db_query.filter(or_(*search_conditions))
        
        return db_query.count()
