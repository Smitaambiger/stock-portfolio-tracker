import time
import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    """
    Custom middleware to log every API request.
    
    Interview explanation:
    Middleware sits between the request and view.
    This one logs METHOD, PATH, STATUS CODE, and response time.
    Useful for monitoring API performance in a high-traffic system like Trendlyne.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        # Code before view runs
        response = self.get_response(request)
        
        # Code after view — calculate response time
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        logger.info(
            f"{request.method} {request.path} "
            f"→ {response.status_code} "
            f"[{duration_ms}ms]"
        )
        
        return response
