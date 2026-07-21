"""
Rate Limiting Middleware
Implements token bucket algorithm for request throttling
"""
import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window"""
    
    def __init__(self, app, requests_per_window: int = None, window_seconds: int = None):
        super().__init__(app)
        self.requests_per_window = requests_per_window or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW
        self.request_history = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.request_history[client_ip] = [
            timestamp for timestamp in self.request_history[client_ip]
            if current_time - timestamp < self.window_seconds
        ]
        
        # Check rate limit
        if len(self.request_history[client_ip]) >= self.requests_per_window:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Too many requests. Limit: {self.requests_per_window} per {self.window_seconds}s",
                    "retry_after": int(self.window_seconds)
                }
            )
        
        # Record request
        self.request_history[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        return response
