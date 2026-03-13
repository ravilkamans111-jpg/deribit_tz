from decimal import Decimal
from typing import List, Tuple

from sqlalchemy import select, func, desc

from src.models.prices import PriceOrm
from src.repos.base import BaseRepository
from src.repos.mappers.mappers import PriceDataMapper
from src.schemas.prices import PriceRead

class PriceRepository(BaseRepository):
    model = PriceOrm
    mapper = PriceDataMapper

    async def add_price(self, ticker: str, price: float, timestamp: int) -> PriceRead:
        return await self.add({
            "ticker": ticker,
            "price": Decimal(str(price)),
            "timestamp": timestamp,
        })

    async def get_all_by_ticker(
        self,
        ticker: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[PriceRead], int]:
        count_query = select(func.count()).where(PriceOrm.ticker == ticker)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        query = (
            select(PriceOrm)
            .where(PriceOrm.ticker == ticker)
            .order_by(desc(PriceOrm.timestamp))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        prices = [
            self.mapper.map_to_domain_entity_pyd(p)
            for p in result.scalars().all()
        ]
        return prices, total

    async def get_latest_by_ticker(self, ticker: str) -> PriceRead | None:
        query = (
            select(PriceOrm)
            .where(PriceOrm.ticker == ticker)
            .order_by(desc(PriceOrm.timestamp))
            .limit(1)
        )
        result = await self.session.execute(query)
        model = result.scalars().first()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity_pyd(model)

    async def get_by_ticker_and_date_range(
        self,
        ticker: str,
        date_from: int,
        date_to: int,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[PriceRead], int]:
        count_query = select(func.count()).where(
            PriceOrm.ticker == ticker,
            PriceOrm.timestamp >= date_from,
            PriceOrm.timestamp <= date_to,
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        query = (
            select(PriceOrm)
            .where(
                PriceOrm.ticker == ticker,
                PriceOrm.timestamp >= date_from,
                PriceOrm.timestamp <= date_to,
            )
            .order_by(desc(PriceOrm.timestamp))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        prices = [
            self.mapper.map_to_domain_entity_pyd(p)
            for p in result.scalars().all()
        ]
        return prices, total

    async def ticker_exists(self, ticker: str) -> bool:
        query = select(PriceOrm).where(PriceOrm.ticker == ticker).limit(1)
        result = await self.session.execute(query)
        return result.scalars().first() is not None
