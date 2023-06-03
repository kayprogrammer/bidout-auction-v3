from datetime import datetime
from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.db.models.base import File

ModelType = TypeVar("ModelType", bound=Base)


class BaseManager(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get_all(self, db: AsyncSession) -> Optional[List[ModelType]]:
        return await db.query(self.model).all()

    def get_all_ids(self, db: AsyncSession) -> Optional[List[ModelType]]:
        items = db.query(self.model.id).all()
        ids = [item[0] for item in items]
        return ids

    def get_by_id(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        return db.query(self.model).filter_by(id=id).first()

    def get_by_slug(self, db: AsyncSession, slug: str) -> Optional[ModelType]:
        return db.query(self.model).filter_by(slug=slug).first()

    def create(
        self, db: AsyncSession, obj_in: Optional[ModelType] = {}
    ) -> Optional[ModelType]:
        obj_in["created_at"] = datetime.utcnow()
        obj_in["updated_at"] = obj_in["created_at"]
        obj: self.model = obj_in.to_model_instance()

        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def bulk_create(self, db: AsyncSession, obj_in: list) -> Optional[bool]:
        items = db.execute(
            insert(self.model)
            .values(obj_in)
            .on_conflict_do_nothing()
            .returning(self.model.id)
        )
        db.commit()
        ids = [item[0] for item in items]
        return ids

    def update(
        self, db: AsyncSession, db_obj: Optional[ModelType], obj_in: Optional[ModelType]
    ) -> Optional[ModelType]:
        if not db_obj:
            return None
        for attr, value in obj_in.items():
            setattr(db_obj, attr, value)
        db_obj.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: AsyncSession, db_obj: Optional[ModelType]):
        if db_obj:
            db.delete(db_obj)
            db.commit()

    def delete_by_id(self, db: AsyncSession, id: UUID):
        obj = db.query(self.model).filter_by(id=id).first()
        if obj:
            db.delete(obj)
            db.commit()

    def delete_all(self, db: AsyncSession):
        db.query(self.model).delete()
        db.commit()


class FileManager(BaseManager[File]):
    pass


file_manager = FileManager(File)
