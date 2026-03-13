import asyncio
import logging
import time

from celery import Celery
from celery.schedules import crontab

from src.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(__name__)

celery_app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "fetch-prices-every-minute": {
        "task": "src.tasks.fetch_prices.fetch_prices_task",
        "schedule": crontab(minute="*/1"),
    },
}

TRACKED_TICKERS = ["BTC_USD", "ETH_USD"]

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_prices_task(self):
    
    async def _fetch():
        from src.database import async_session
        from src.utils import DBManager
        from src.services.deribit_client import DeribitClient

        client = DeribitClient()
        prices_data = await client.get_multiple_prices(TRACKED_TICKERS)

        if not prices_data:
            logger.warning("Не получены цены от Deribit")
            return {"status": "no_data", "timestamp": int(time.time())}

        current_timestamp = int(time.time())
        saved = {}

        async with DBManager(session_factory=async_session) as db:
            for ticker, price in prices_data.items():
                try:
                    await db.prices.add_price(ticker, price, current_timestamp)
                    saved[ticker] = price
                    logger.info(f"Сохранена цена {ticker}: {price}")
                except Exception as e:
                    logger.error(f"Ошибка сохранения {ticker}: {e}")
            await db.commit()

        return {
            "status": "success",
            "saved_prices": saved,
            "timestamp": current_timestamp,
            "count": len(saved),
        }

    try:
        return asyncio.run(_fetch())
    except Exception as e:
        logger.error(f"Ошибка в fetch_prices_task: {e}")
        countdown = self.request.retries * 60
        raise self.retry(exc=e, countdown=countdown)
