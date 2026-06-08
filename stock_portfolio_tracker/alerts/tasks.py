"""
Celery background tasks.

Interview explanation:
Celery is a task queue.
Instead of checking alerts in every API request (wasteful),
we schedule a background task that runs every 5 minutes automatically.

Flow:
1. User creates an alert via API
2. Every 5 minutes, Celery beats scheduler triggers check_alerts task
3. Task fetches active alerts, checks prices, triggers matching ones
4. No user request needed — runs in background

This is exactly how Trendlyne would send notifications to users 
when a stock hits their target price.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_price_alerts():
    """Run every 5 minutes via Celery Beat."""
    from alerts.views import check_and_trigger_alerts
    triggered = check_and_trigger_alerts()
    logger.info(f"Alert check complete: {triggered} triggered")
    return triggered
