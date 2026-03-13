# Deribit Price Tracker

Трекер цен криптовалют с биржи Deribit. Каждую минуту получает цены BTC/USD и ETH/USD и сохраняет в PostgreSQL.

## Стек

- **FastAPI** — REST API
- **SQLAlchemy** (async) + **asyncpg** — работа с БД
- **Alembic** — миграции
- **Celery** + **Redis** — фоновые задачи
- **aiohttp** — запросы к Deribit API

## Структура проекта

```
src/
├── api/
│   ├── dependencies.py     # DBDep
│   └── prices.py           # роутеры
├── models/
│   └── prices.py           # ORM модель
├── repos/
│   ├── base.py             # BaseRepository
│   ├── prices.py           # PriceRepository
│   └── mappers/
│       └── mappers.py      # маппер ORM → схема
├── schemas/
│   └── prices.py           # Pydantic схемы
├── services/
│   └── deribit_client.py   # HTTP клиент Deribit
├── tasks/
│   └── fetch_prices.py     # Celery задача
├── config.py
├── database.py
├── exceptions.py
├── main.py
└── utils.py                # DBManager
```

## Установка и запуск

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/ваш_ник/deribit-price-tracker.git
cd deribit-price-tracker
```

### 2. Создайте `.env` файл

```bash
cp .env.example .env
```

Заполните переменные:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=deribit_db
DB_USER=deribit_user
DB_PASSWORD=deribit_password

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### 3. Установите зависимости

```bash
uv sync
```

### 4. Запустите БД и Redis через Docker

```bash
docker-compose up -d db redis
```

### 5. Примените миграции

```bash
uv run alembic upgrade head
```

### 6. Запустите приложение

```bash
uv run fastapi dev src/main.py
```

### 7. Запустите Celery (в отдельных терминалах)

```bash
# Worker
celery -A src.tasks.fetch_prices.celery_app worker --loglevel=info

# Beat (планировщик)
celery -A src.tasks.fetch_prices.celery_app beat --loglevel=info
```

## API эндпоинты

| Метод | URL | Описание |
|---|---|---|
| GET | `/prices?ticker=BTC_USD` | Все цены с пагинацией |
| GET | `/prices/latest?ticker=BTC_USD` | Последняя цена |
| GET | `/prices/by-date?ticker=BTC_USD&date_from=...&date_to=...` | Цены за период |

### Параметры запроса

- `ticker` — тикер, например `BTC_USD` или `ETH_USD`
- `limit` — количество записей (по умолчанию 100, максимум 1000)
- `offset` — смещение для пагинации
- `date_from` / `date_to` — Unix timestamp

### Пример ответа

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "ticker": "BTC_USD",
      "price": "85000.50",
      "timestamp": 1741870200
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

## Документация API

После запуска доступна по адресу: [http://localhost:8000/docs](http://localhost:8000/docs)
