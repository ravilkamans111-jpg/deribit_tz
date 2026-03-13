import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from src.api.dependencies import DBDep
from src.exceptions import TickerNotFoundException, ObjectIsAlreadyExistsException
from src.schemas.prices import PricesListResponse, SinglePriceResponse, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prices", tags=["prices"])

@router.get(
    "",
    response_model=PricesListResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_prices(
    db: DBDep,
    ticker: str = Query(..., min_length=1, max_length=20, description="Тикер, например BTC_USD"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    prices, total = await db.prices.get_all_by_ticker(ticker, limit, offset)

    if not prices:
        raise HTTPException(status_code=404, detail=f"Нет данных для тикера: {ticker}")

    return PricesListResponse(data=prices, total=total, limit=limit, offset=offset)

@router.get(
    "/latest",
    response_model=SinglePriceResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_latest_price(
    db: DBDep,
    ticker: str = Query(..., min_length=1, max_length=20),
):
    price = await db.prices.get_latest_by_ticker(ticker)

    if not price:
        raise HTTPException(status_code=404, detail=f"Нет данных для тикера: {ticker}")

    return SinglePriceResponse(data=price)

@router.get(
    "/by-date",
    response_model=PricesListResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_prices_by_date(
    db: DBDep,
    ticker: str = Query(..., min_length=1, max_length=20),
    date_from: Optional[int] = Query(None, ge=0, description="Unix timestamp начала"),
    date_to: Optional[int] = Query(None, ge=0, description="Unix timestamp конца"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    if date_from is not None and date_to is not None:
        if date_from > date_to:
            raise HTTPException(status_code=400, detail="date_from должен быть меньше date_to")

        prices, total = await db.prices.get_by_ticker_and_date_range(
            ticker, date_from, date_to, limit, offset
        )
    else:
        prices, total = await db.prices.get_all_by_ticker(ticker, limit, offset)

    if not prices:
        raise HTTPException(status_code=404, detail=f"Нет данных для тикера: {ticker}")

    return PricesListResponse(data=prices, total=total, limit=limit, offset=offset)
