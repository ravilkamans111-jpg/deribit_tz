from decimal import Decimal
from typing import List

from pydantic import BaseModel

class PriceRead(BaseModel):
    id: int
    ticker: str
    price: Decimal
    timestamp: int

    model_config = {"from_attributes": True}

class PricesListResponse(BaseModel):
    success: bool = True
    data: List[PriceRead]
    total: int
    limit: int
    offset: int

class SinglePriceResponse(BaseModel):
    success: bool = True
    data: PriceRead

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
