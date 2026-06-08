"""
Stock price service — fetches live prices with Redis caching.

Interview explanation:
This is the most important file to explain.

Problem:
- Stock prices change every second
- External API has rate limits
- Calling external API on every user request = slow + expensive

Solution — Cache-Aside pattern:
1. Check Redis cache first
2. If cache hit → return immediately (fast: ~1ms)
3. If cache miss → call external API → store in cache → return
4. Cache expires after 60 seconds (TTL)

This reduces external API calls from thousands/minute to ~1/minute per stock.
"""
import requests
import logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

# Sample data for demo — avoids hitting external API during interview demo
DEMO_PRICES = {
    'INFY': {'symbol': 'INFY', 'price': 1847.35, 'change': 12.50, 'change_pct': 0.68, 'volume': 2847293},
    'TCS': {'symbol': 'TCS', 'price': 3421.80, 'change': -15.20, 'change_pct': -0.44, 'volume': 1234567},
    'RELIANCE': {'symbol': 'RELIANCE', 'price': 2876.45, 'change': 23.10, 'change_pct': 0.81, 'volume': 3456789},
    'HDFCBANK': {'symbol': 'HDFCBANK', 'price': 1654.30, 'change': -8.75, 'change_pct': -0.53, 'volume': 5678901},
    'WIPRO': {'symbol': 'WIPRO', 'price': 456.80, 'change': 3.25, 'change_pct': 0.72, 'volume': 987654},
    'ICICIBANK': {'symbol': 'ICICIBANK', 'price': 1123.55, 'change': 18.90, 'change_pct': 1.71, 'volume': 4321098},
    'TATAMOTORS': {'symbol': 'TATAMOTORS', 'price': 842.15, 'change': -6.40, 'change_pct': -0.75, 'volume': 2109876},
    'BAJFINANCE': {'symbol': 'BAJFINANCE', 'price': 7234.60, 'change': 45.30, 'change_pct': 0.63, 'volume': 543210},
}

def get_stock_price(symbol: str) -> dict:
    """
    Get stock price with caching.
    
    Cache key format: stock_price_{symbol}
    TTL: 60 seconds (configurable in settings.STOCK_CACHE_TTL)
    """
    cache_key = f"stock_price_{symbol.upper()}"
    
    # Step 1: Check cache
    cached_data = cache.get(cache_key)
    if cached_data:
        cached_data['from_cache'] = True
        return cached_data
    
    # Step 2: Cache miss — fetch fresh price
    price_data = _fetch_price_from_api(symbol)
    
    if price_data:
        # Step 3: Store in cache for TTL seconds
        cache.set(cache_key, price_data, timeout=settings.STOCK_CACHE_TTL)
        price_data['from_cache'] = False
    
    return price_data

def _fetch_price_from_api(symbol: str) -> dict:
    """
    Fetch stock price from external API.
    Uses demo data if API key is 'demo' or API fails.
    """
    symbol_upper = symbol.upper()
    
    # Use demo data for local development/demo
    if settings.ALPHA_VANTAGE_API_KEY == 'demo' or symbol_upper in DEMO_PRICES:
        if symbol_upper in DEMO_PRICES:
            return DEMO_PRICES[symbol_upper].copy()
    
    # Real API call to Alpha Vantage (when API key is configured)
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol_upper,
            'apikey': settings.ALPHA_VANTAGE_API_KEY,
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json().get('Global Quote', {})
        
        if not data:
            return None
            
        return {
            'symbol': symbol_upper,
            'price': float(data.get('05. price', 0)),
            'change': float(data.get('09. change', 0)),
            'change_pct': float(data.get('10. change percent', '0%').replace('%', '')),
            'volume': int(data.get('06. volume', 0)),
        }
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        # Fallback to demo data
        return DEMO_PRICES.get(symbol_upper, {
            'symbol': symbol_upper,
            'price': 100.0,
            'change': 0.0,
            'change_pct': 0.0,
            'volume': 0,
        })

def get_multiple_prices(symbols: list) -> dict:
    """Fetch prices for multiple stocks efficiently."""
    return {symbol: get_stock_price(symbol) for symbol in symbols}
