"""Rate limiting middleware for Ariadne."""

import logging
from typing import Optional

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware for FastAPI."""
    
    def __init__(self, app, calls: int = 100, period: int = 3600):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next):
        """Process request through middleware."""
        # Skip rate limiting for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_identifier(request)
        
        # Simple rate limiting logic (in-memory for development)
        import time
        current_time = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if current_time - req_time < self.period
        ]
        
        # Check rate limit
        if len(self.requests[client_id]) >= self.calls:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.calls} requests per {self.period} seconds"
                },
                headers={"Retry-After": "3600"}
            )
        
        # Add current request
        self.requests[client_id].append(current_time)
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.calls - len(self.requests[client_id])
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.period))
        
        return response
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint should skip rate limiting."""
        public_paths = [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/robots.txt"
        ]
        return any(path.startswith(public_path) for public_path in public_paths)
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for client."""
        # Try to get user ID if authenticated
        if hasattr(request.state, 'user_id'):
            return f"user:{request.state.user_id}"
        
        # Use client IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"


# Rate limit error class
class RateLimitError(Exception):
    """Rate limit exceeded exception."""
    pass


# Convenience functions
def create_rate_limit_middleware(calls: int = 100, period: int = 3600):
    """Create rate limit middleware with specified limits."""
    def middleware(app):
        return RateLimitMiddleware(app, calls=calls, period=period)
    return middleware
