import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.api import api_router
from app.middleware.logging import LoggingMiddleware
from app.middleware.security import SecurityHeadersMiddleware, RequestSizeMiddleware
from app.database import engine
from app.config import settings

logger = logging.getLogger(__name__)

# Rate limiter configuration
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_requests}/minute"] if settings.rate_limit_enabled else []
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup - Test database connection
    try:
        logger.info("Testing database connection...")
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        logger.info("Note: Use 'alembic upgrade head' to apply database migrations")
    except Exception as e:
        error_msg = f"Failed to connect to database: {str(e)}"
        logger.error(error_msg)
        
        # Provide helpful error messages based on the error type
        if "Connection refused" in str(e):
            logger.error("🔴 Database connection refused!")
            logger.error("💡 Make sure PostgreSQL is running. You can start it with:")
            logger.error("   docker-compose up -d postgres")
            logger.error("   or")
            logger.error("   docker run -d --name postgres-db -p 5432:5432 \\")
            logger.error("       -e POSTGRES_USER=taskuser \\")
            logger.error("       -e POSTGRES_PASSWORD=taskpass \\")
            logger.error("       -e POSTGRES_DB=taskdb \\")
            logger.error("       postgres:15")
        elif "does not exist" in str(e):
            logger.error("🔴 Database does not exist!")
            logger.error("💡 Create the database with:")
            logger.error("   docker exec <postgres-container> psql -U taskuser -d postgres -c 'CREATE DATABASE taskdb;'")
        else:
            logger.error(f"🔴 Database error: {error_msg}")
            logger.error(f"💡 Current database URL: {settings.database_url}")
            logger.error("💡 Check your database configuration in .env file")
        
        # Re-raise the exception to let calling code handle it
        # In production, this will cause the server to exit
        # In tests, the test framework can handle the exception
        raise e
    
    # Security-related startup checks
    if settings.is_production:
        security_warnings = []
        
        if settings.debug:
            security_warnings.append("Debug mode is enabled in production")
        
        if not settings.secret_key or len(settings.secret_key) < 32:
            security_warnings.append("Secret key is not set or is too short")
        
        if "localhost" in str(settings.cors_origins):
            security_warnings.append("Localhost origins allowed in production")
        
        if security_warnings:
            logger.error("SECURITY WARNINGS:")
            for warning in security_warnings:
                logger.error(f"  - {warning}")
            logger.error("Please review your production configuration!")
    
    cors_origins = settings.get_cors_origins()
    logger.info(f"Application started in {settings.environment} mode")
    logger.info(f"Rate limiting: {'enabled' if settings.rate_limit_enabled else 'disabled'}")
    logger.info(f"Security headers: {'enabled' if settings.security_headers_enabled else 'disabled'}")
    logger.info(f"CORS origins: {len(cors_origins)} configured")
    
    yield
    
    # Shutdown
    try:
        await engine.dispose()
        logger.info("Database connection closed successfully")
    except Exception as e:
        logger.warning(f"Error during database shutdown: {e}")


# Custom rate limit exceeded handler
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors"""
    logger.warning(
        f"Rate limit exceeded for {request.client.host if request.client else 'unknown'}",
        extra={
            "client_ip": request.client.host if request.client else "unknown",
            "method": request.method,
            "url": str(request.url),
            "rate_limit": str(exc.detail)
        }
    )
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "status_code": 429,
            "retry_after": 60
        },
        headers={"Retry-After": "60"}
    )


# Create FastAPI app with security considerations
app = FastAPI(
    title="Task Management API",
    description="A comprehensive task management system",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,  # Disable docs in production
    redoc_url="/redoc" if not settings.is_production else None,  # Disable redoc in production
    openapi_url="/openapi.json" if not settings.is_production else None,  # Disable OpenAPI in production
    lifespan=lifespan,
    debug=settings.debug and settings.is_development  # Only enable debug in development
)

# Add rate limiting
if settings.rate_limit_enabled:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Security headers middleware (add first for proper header setting)
if settings.security_headers_enabled:
    app.add_middleware(SecurityHeadersMiddleware, enabled=True)

# Request size limiting middleware
app.add_middleware(RequestSizeMiddleware, max_size=1024 * 1024)  # 1MB limit

# CORS middleware with proper security configuration
cors_origins = settings.get_cors_origins()
logger.info(f"CORS origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin",
        "User-Agent",
        "DNT",
        "Cache-Control",
        "X-Mx-ReqToken",
        "Keep-Alive",
        "X-CSRFToken"
    ],
    expose_headers=["X-Total-Count", "X-Rate-Limit-Remaining", "X-Rate-Limit-Reset"],
    max_age=600,  # 10 minutes
)

# Rate limiting middleware (add after CORS)
if settings.rate_limit_enabled:
    app.add_middleware(SlowAPIMiddleware)

# Custom logging middleware
app.add_middleware(LoggingMiddleware)

# Root endpoint with API information and task status
@app.get("/", include_in_schema=False)
@limiter.limit("10/minute") if settings.rate_limit_enabled else lambda x: x
async def root(request: Request):
    """API landing page with helpful information and task status"""
    try:
        # Check if there are any tasks in the database
        
        async with engine.begin() as conn:
            # Simple count query
            result = await conn.execute(text("SELECT COUNT(*) FROM tasks"))
            task_count = result.scalar() or 0
        
        base_url = f"{request.url.scheme}://{request.headers.get('host', 'localhost:8000')}"
        
        if task_count > 0:
            message = f"Welcome to Task Management API! You have {task_count} task{'s' if task_count != 1 else ''} in the system."
            suggestion = f"Get all tasks: GET {base_url}/api/tasks"
        else:
            message = "Welcome to Task Management API! No tasks found in the system."
            suggestion = f"Create your first task: POST {base_url}/api/tasks"
        
        return {
            "message": message,
            "suggestion": suggestion,
            "api_info": {
                "version": "1.0.0",
                "base_url": f"{base_url}/api",
                "documentation": f"{base_url}/docs" if not settings.is_production else "Documentation disabled in production",
                "health_check": f"{base_url}/api/health"
            },
            "available_endpoints": {
                "tasks": {
                    "list": "GET /api/tasks",
                    "get": "GET /api/tasks/{id}",
                    "create": "POST /api/tasks",
                    "update": "PUT /api/tasks/{id}",
                    "delete": "DELETE /api/tasks/{id}"
                },
                "health": "GET /api/health"
            },
            "example_create_task": {
                "method": "POST",
                "url": f"{base_url}/api/tasks",
                "body": {
                    "title": "My first task",
                    "description": "Task description",
                    "status": "pending",
                    "priority": "medium",
                    "due_date": "2025-12-31T23:59:59Z"
                }
            },
            "task_count": task_count,
            "environment": settings.environment
        }
    
    except Exception as e:
        logger.error(f"Error in root endpoint: {e}")
        base_url = f"{request.url.scheme}://{request.headers.get('host', 'localhost:8000')}"
        return {
            "message": "Welcome to Task Management API!",
            "error": "Could not check task status (database may not be initialized)",
            "suggestion": "Check API health and run database migrations",
            "api_info": {
                "version": "1.0.0",
                "base_url": f"{base_url}/api",
                "documentation": f"{base_url}/docs" if not settings.is_production else "Documentation disabled in production",
                "health_check": f"{base_url}/api/health"
            },
            "quick_start": {
                "1": "Check health: GET /api/health",
                "2": "Run migrations: alembic upgrade head",
                "3": "Create task: POST /api/tasks",
                "4": "List tasks: GET /api/tasks"
            }
        }

# Include API router
app.include_router(api_router, prefix="/api")