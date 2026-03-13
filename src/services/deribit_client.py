import logging
from typing import Dict

import aiohttp

from src.config import settings
from src.exceptions import DeribitClientException

logger = logging.getLogger(__name__)

class DeribitClient:
    
    def __init__(self):
        self.base_url = settings.DERIBIT_API_URL
        self.timeout = aiohttp.ClientTimeout(total=10)

    async def get_index_price(self, ticker: str) -> float:
        endpoint = f"{self.base_url}/public/get_index_price"
        params = {"index_name": ticker.lower()}

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status != 200:
                        raise DeribitClientException(
                            f"Deribit вернул статус {response.status} для {ticker}"
                        )
                    data = await response.json()

                    if "result" not in data or data.get("error"):
                        raise DeribitClientException(
                            f"Ошибка Deribit API для {ticker}: {data}"
                        )

                    price = data["result"].get("index_price")
                    if price is None:
                        raise DeribitClientException(
                            f"Нет цены в ответе для {ticker}"
                        )

                    logger.debug(f"Получена цена {ticker}: {price}")
                    return float(price)

        except aiohttp.ClientError as e:
            raise DeribitClientException(f"Ошибка сети при запросе {ticker}: {e}")

    async def get_multiple_prices(self, tickers: list[str]) -> Dict[str, float]:
        prices = {}
        for ticker in tickers:
            try:
                prices[ticker] = await self.get_index_price(ticker)
            except DeribitClientException as e:
                logger.error(f"Не удалось получить цену {ticker}: {e}")
        return prices
