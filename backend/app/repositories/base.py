"""
SAP TestOS - Repository Pattern Base
Generic async repository with CRUD operations
"""
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository with async CRUD operations"""
    
    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session
    
    async def get(self, id: int) -> Optional[ModelType]:
        """Get single record by ID"""
        result = await self.db_session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get all records with pagination and optional filters"""
        query = select(self.model)
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    conditions.append(getattr(self.model, key) == value)
            if conditions:
                query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        result = await self.db_session.execute(query)
        return list(result.scalars().all())
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create new record"""
        db_obj = self.model(**obj_in)
        self.db_session.add(db_obj)
        await self.db_session.flush()
        await self.db_session.refresh(db_obj)
        return db_obj
    
    async def update(self, id: int, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update existing record"""
        db_obj = await self.get(id)
        if not db_obj:
            return None
        
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.db_session.add(db_obj)
        await self.db_session.flush()
        await self.db_session.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: int) -> bool:
        """Delete record by ID"""
        db_obj = await self.get(id)
        if not db_obj:
            return False
        
        await self.db_session.delete(db_obj)
        await self.db_session.flush()
        return True
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters"""
        query = select(func.count()).select_from(self.model)
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    conditions.append(getattr(self.model, key) == value)
            if conditions:
                query = query.where(and_(*conditions))
        
        result = await self.db_session.execute(query)
        return result.scalar() or 0
    
    async def search(
        self, 
        search_term: str, 
        search_fields: List[str],
        limit: int = 50
    ) -> List[ModelType]:
        """Search across multiple fields"""
        conditions = []
        for field in search_fields:
            if hasattr(self.model, field):
                conditions.append(
                    getattr(self.model, field).ilike(f"%{search_term}%")
                )
        
        if not conditions:
            return []
        
        query = select(self.model).where(or_(*conditions)).limit(limit)
        result = await self.db_session.execute(query)
        return list(result.scalars().all())
