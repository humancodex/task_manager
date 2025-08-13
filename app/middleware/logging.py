import time
import json
import logging
from datetime import datetime, timezone
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())
        start_time = time.time()
        request_timestamp = datetime.now(timezone.utc)
        
        # Get client IP
        client_ip = "unknown"
        if request.client:
            client_ip = request.client.host
        elif "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        elif "x-real-ip" in request.headers:
            client_ip = request.headers["x-real-ip"]
        
        # Log incoming request
        request_log = {
            "type": "request",
            "request_id": request_id,
            "timestamp": request_timestamp.isoformat(),
            "method": request.method,
            "endpoint": request.url.path,
            "query_params": dict(request.query_params) if request.query_params else {},
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "content_type": request.headers.get("content-type"),
            "content_length": request.headers.get("content-length")
        }
        
        logger.info(json.dumps(request_log))
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        response_timestamp = datetime.now(timezone.utc)
        
        # Log outgoing response
        response_log = {
            "type": "response",
            "request_id": request_id,
            "timestamp": response_timestamp.isoformat(),
            "method": request.method,
            "endpoint": request.url.path,
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
            "content_type": response.headers.get("content-type"),
            "content_length": response.headers.get("content-length")
        }
        
        logger.info(json.dumps(response_log))
        
        # Add response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
        
        return response