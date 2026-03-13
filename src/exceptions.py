class ObjectIsAlreadyExistsException(Exception):
    pass

class TickerNotFoundException(Exception):
    def __init__(self, ticker: str):
        self.ticker = ticker
        super().__init__(f"Нет данных для тикера: {ticker}")

class DeribitClientException(Exception):
    pass
