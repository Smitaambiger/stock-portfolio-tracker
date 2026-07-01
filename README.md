# Stock Portfolio Tracker — Real-Time Backend System

A production-ready Django REST API for tracking stock portfolios with live P&L calculation, price alerts, and Redis caching.

## Why I Built This

Retail investors typically track their stocks across multiple apps with no single unified view of portfolio performance. This backend solves that by providing a clean API for managing holdings, calculating real-time profit/loss, and setting automated price alerts.

This project is directly relevant to Trendlyne's work in financial analytics — it uses the same core tech stack (Django, PostgreSQL, Redis) and solves similar data challenges.

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | Django 4.2 + DRF | Industry standard Python web framework |
| Database | PostgreSQL / SQLite | Relational DB for structured financial data |
| Cache | Redis (optional) | Sub-millisecond price fetching |
| Auth | JWT (SimpleJWT) | Stateless, scalable API auth |
| Background Tasks | Celery + Redis | Async alert checking every 5 minutes |
| API Docs | Swagger (drf-yasg) | Auto-generated interactive API documentation |

## Key Features

- **JWT Authentication** — register, login, token refresh
- **Portfolio Management** — add/sell stocks, track holdings
- **Live P&L Calculation** — real-time profit/loss with Redis caching
- **Price Alerts** — set ABOVE/BELOW alerts, checked by background task
- **Redis Cache-Aside Pattern** — stock prices cached for 60 seconds
- **N+1 Query Prevention** — `select_related` on all portfolio queries
- **Atomic Transactions** — buy/sell operations wrapped in `db_transaction.atomic()`
- **Custom Middleware** — request logging with response time
- **Swagger API Docs** — at `/api/docs/`

## Project Structure

```
stock_portfolio_tracker/
├── core/               # Django project settings, URLs, middleware, Celery
├── users/              # Custom User model, JWT auth endpoints
├── stocks/             # Stock master data, price fetching service
├── portfolio/          # Holdings, transactions, P&L calculation
├── alerts/             # Price alerts, Celery background task
├── requirements.txt
├── .env.example
└── README.md
```

## Database Design

```
User (custom AbstractUser)
  ├── PortfolioHolding  (user + stock + quantity + avg_buy_price)
  │     └── Transaction (full buy/sell history — the ledger)
  ├── PriceAlert        (user + stock + condition + target_price)
  └── (references Stock)

Stock (master table: symbol, name, sector, exchange)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login, get JWT tokens |
| POST | `/api/auth/logout/` | Invalidate token |
| GET | `/api/auth/profile/` | Get/update user profile |
| GET | `/api/stocks/` | List all stocks |
| GET | `/api/stocks/search/?q=INFY` | Search stocks |
| GET | `/api/stocks/{id}/price/` | Live price (cached) |
| GET | `/api/portfolio/` | Portfolio with live P&L |
| POST | `/api/portfolio/add/` | Add stock to portfolio |
| POST | `/api/portfolio/sell/` | Sell shares |
| GET | `/api/portfolio/transactions/` | Transaction history |
| GET | `/api/alerts/` | List all alerts |
| POST | `/api/alerts/` | Create price alert |
| DELETE | `/api/alerts/{id}/` | Cancel alert |
| POST | `/api/alerts/check_now/` | Manually trigger alert check |
| GET | `/api/docs/` | Swagger API documentation |

## Setup & Run

### Step 1 — Clone and setup environment

```bash
git clone https://github.com/Smitaambiger/stock-portfolio-tracker.git
cd stock-portfolio-tracker

python -m venv venv
source venv/bin/activate        # Linux/Mac
# OR
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### Step 2 — Configure environment

```bash
cp .env.example .env
# Edit .env if needed — defaults work out of the box with SQLite
```

### Step 3 — Run migrations and seed data

```bash
python manage.py migrate
python manage.py seed_stocks
python manage.py createsuperuser
```

### Step 4 — Start the server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/api/docs/ for Swagger UI

### Step 5 — Test the API

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"smita","email":"smita@test.com","password":"Test@1234","password_confirm":"Test@1234"}'

# 2. Login and get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"smita@test.com","password":"Test@1234"}'

# 3. Add INFY to portfolio (use token from login)
curl -X POST http://localhost:8000/api/portfolio/add/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"stock_symbol":"INFY","quantity":50,"buy_price":1750}'

# 4. View portfolio with P&L
curl http://localhost:8000/api/portfolio/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 5. Set price alert
curl -X POST http://localhost:8000/api/alerts/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"stock_symbol":"INFY","condition":"ABOVE","target_price":1900}'
```

## Architecture Decisions

### Why Redis for price caching?

Stock prices change every second. Without caching:
- Every API request → external API call → 800ms+ response time
- Rate limit violations on external APIs
- Slow user experience

With Redis Cache-Aside pattern:
- First request: fetch from external API, store in Redis for 60 seconds
- Next 59 seconds: serve from Redis in ~1ms
- Cache expires → auto-refresh on next request

### Why Celery for alerts?

Checking alerts on every API request would be wasteful. Celery runs a background task every 5 minutes to check all active alerts against current prices. No user request needed — runs independently.

### Why select_related?

When displaying a portfolio with 10 stocks, without `select_related` Django runs 11 SQL queries (1 for holdings + 1 for each stock). With `select_related`, it runs 1 SQL JOIN — 10x fewer database calls.

### Why atomic transactions for buy/sell?

A buy operation updates two tables: `PortfolioHolding` and `Transaction`. If the server crashes between the two writes, data becomes inconsistent. Wrapping in `db_transaction.atomic()` ensures both succeed or both fail.

## Author

Smita Ambiger | Backend Software Engineer
- GitHub: https://github.com/Smitaambiger
- LinkedIn: https://www.linkedin.com/in/smita-ambiger1107/
- Email: smitaambiger11@gmail.com
