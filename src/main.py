from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.prices import router as prices_router
from src.exceptions import TickerNotFoundException, DeribitClientException

app = FastAPI(
    title="Deribit Price Tracker",
    description="Трекер цен криптовалют с Deribit",
    version="1.0.0",
)

app.include_router(prices_router)

@app.exception_handler(TickerNotFoundException)
async def handle_ticker_not_found(request: Request, exc: TickerNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": str(exc)},
    )

@app.exception_handler(DeribitClientException)
async def handle_deribit_error(request: Request, exc: DeribitClientException):
    return JSONResponse(
        status_code=503,
        content={"success": False, "error": "Ошибка внешнего API. Попробуйте позже."},
    )

@app.get("/")
async def root():
    return {"status": "ok", "message": "Deribit Price Tracker запущен"}
