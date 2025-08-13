import time
import json
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid4())
        start_time = time.time()
        
        logger.info(json.dumps({
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "timestamp": time.time()
        }))
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(json.dumps({
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time": process_time,
            "timestamp": time.time()
        }))
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response