"""
Security middleware for FastAPI application.
Provides security headers and other security enhancements.
"""
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    
    Adds headers to protect against common web vulnerabilities:
    - XSS attacks
    - Clickjacking
    - MIME type sniffing
    - Content type sniffing
    - Referrer policy
    """
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
        
        # Security headers configuration
        self.security_headers = {
            # Prevent XSS attacks
            "X-XSS-Protection": "1; mode=block",
            
            # Prevent clickjacking attacks
            "X-Frame-Options": "DENY",
            
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Content Security Policy (basic policy)
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            ),
            
            # Strict Transport Security (only in production)
            **({"Strict-Transport-Security": "max-age=31536000; includeSubDomains"} 
               if settings.is_production else {}),
            
            # Permissions policy
            "Permissions-Policy": (
                "accelerometer=(), "
                "camera=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "microphone=(), "
                "payment=(), "
                "usb=()"
            )
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response"""
        response = await call_next(request)
        
        if self.enabled:
            # Add security headers
            for header_name, header_value in self.security_headers.items():
                response.headers[header_name] = header_value
            
            # Remove server information leakage
            if "server" in response.headers:
                del response.headers["server"]
            
            # Add custom server header
            response.headers["Server"] = "TaskAPI/1.0"
        
        return response


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit request body size to prevent DoS attacks.
    """
    
    def __init__(self, app, max_size: int = 1024 * 1024):  # 1MB default
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check request size before processing"""
        content_length = request.headers.get("content-length")
        
        if content_length:
            content_length = int(content_length)
            if content_length > self.max_size:
                logger.warning(
                    f"Request size {content_length} exceeds maximum {self.max_size}",
                    extra={
                        "client_ip": request.client.host if request.client else "unknown",
                        "method": request.method,
                        "url": str(request.url),
                        "content_length": content_length,
                        "max_size": self.max_size
                    }
                )
                return Response(
                    content="Request entity too large",
                    status_code=413,
                    headers={"Content-Type": "text/plain"}
                )
        
        return await call_next(request)