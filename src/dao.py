from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

from .database import async_session_maker, Base
# from .logger import logger


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseDAO(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    model = None

    @classmethod
    async def find_one_or_none(cls, *filter, **filter_by) -> Optional[ModelType]:
        stmt = select(cls.model).filter(*filter).filter_by(**filter_by)
        async with async_session_maker() as session:
            result = await session.execute(stmt)
            return result.scalars().one_or_none()

    @classmethod
    async def find_all(
        cls,
        *filter,
        offset: int = 0,
        limit: int = 100,
        **filter_by
    ) -> List[ModelType]:
        stmt = (
            select(cls.model)
            .filter(*filter)
            .filter_by(**filter_by)
            .offset(offset)
            .limit(limit)
        )
        async with async_session_maker() as session:

            result = await session.execute(stmt)
            return result.scalars().all()

    @classmethod
    async def add(
        cls,
        obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(exclude_unset=True)
        try:
            stmt = insert(cls.model).values(
                **create_data).returning(cls.model)
            async with async_session_maker() as session:
                result = await session.execute(stmt)
                await session.commit()
                return result.scalars().first()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot insert data into table"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot insert data into table"

            # logger.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            # print(msg)
            return None

    @classmethod
    async def delete(cls, **filter_by) -> None:
        stmt = delete(cls.model).filter_by(**filter_by)
        async with async_session_maker() as session:
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def update(
        cls,
        *,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        id: Any
    ) -> Optional[ModelType]:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        stmt = (
            update(cls.model).
            where(cls.model.c.id == id).
            values(**update_data).
            returning(cls.model)
        )
        async with async_session_maker() as session:
            result = await session.execute(stmt)
            await session.commit()

        return result.scalars().one()

    @classmethod
    async def add_bulk(cls, *data):
        try:
            stmt = insert(cls.model).values(*data).returning(cls.model.id)
            async with async_session_maker() as session:
                result = await session.execute(stmt)
                await session.commit()
                return result.scalars().first()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": Cannot bulk insert data into table"

            # logger.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            return None
