import time
import os
from collections import defaultdict
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class SearchRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        window_size: int = 60,  # 60 seconds window
        max_requests: int = 60,  # 60 requests per minute
    ):
        super().__init__(app)
        self.request_counts = defaultdict(list)
        self.WINDOW_SIZE = window_size
        self.MAX_REQUESTS = max_requests
        logger.info(f"Initialized SearchRateLimitMiddleware with {max_requests} requests per {window_size} seconds")

    async def dispatch(self, request: Request, call_next):
        # Only apply to search endpoints
        if request.url.path.startswith("/search/"):
            # Get client identifier (IP + user ID if authenticated)
            client_ip = request.client.host
            try:
                # Try to get user ID from auth token for more precise rate limiting
                user = request.state.user
                client_id = f"{client_ip}:{user.id}"
            except:
                client_id = client_ip

            now = time.time()
            
            # Remove old requests outside the window
            self.request_counts[client_id] = [
                req_time for req_time in self.request_counts[client_id]
                if now - req_time < self.WINDOW_SIZE
            ]
            
            # Check if rate limit is exceeded
            if len(self.request_counts[client_id]) >= self.MAX_REQUESTS:
                logger.warning(f"Rate limit exceeded for client {client_id}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Search rate limit exceeded. Please try again later.",
                        "retry_after": int(self.WINDOW_SIZE - (now - self.request_counts[client_id][0]))
                    }
                )
            
            # Add current request
            self.request_counts[client_id].append(now)
            
            # Clean up old entries periodically
            if len(self.request_counts) > 10000:  # Prevent memory leaks
                self._cleanup_old_entries(now)

        return await call_next(request)

    def _cleanup_old_entries(self, current_time: float):
        """Remove entries older than window size to prevent memory leaks"""
        for client_id in list(self.request_counts.keys()):
            if not self.request_counts[client_id] or \
               current_time - self.request_counts[client_id][-1] >= self.WINDOW_SIZE:
                del self.request_counts[client_id]

class CacheControlMiddleware(BaseHTTPMiddleware):
    """Add cache control headers for search results"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        if request.url.path.startswith("/search/"):
            # Add cache control headers
            response.headers["Cache-Control"] = "private, max-age=60"  # Cache for 1 minute
            response.headers["Vary"] = "Authorization"  # Vary cache by auth token
        
        return response 