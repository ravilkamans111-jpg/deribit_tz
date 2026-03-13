from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
import logging

from src.exceptions import ObjectIsAlreadyExistsException

class BaseRepository:
    model = None
    mapper = None

    def __init__(self, session):
        self.session = session

    async def add(self, data):
        try:
            add_data_stmt = (
                insert(self.model).values(**data).returning(self.model)
            )
            result = await self.session.execute(add_data_stmt)
            model = result.scalars().one()
        except IntegrityError:
            raise ObjectIsAlreadyExistsException
        except Exception as ex:
            logging.error(f"Ошибка при добавлении: {ex}")
            raise
        return self.mapper.map_to_domain_entity_pyd(model)

    async def get_all(self, limit: int = 100, offset: int = 0):
        query = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity_pyd(model)
            for model in result.scalars().all()
        ]

    async def get_filtered(self, *filters, **filter_by):
        query = select(self.model).filter(*filters).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().all()
