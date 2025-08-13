from fastapi import APIRouter, Request
from datetime import datetime, timezone
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import check_database_health

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Check API availability and system status."""
    try:
        # Use async health check without dependency injection to avoid circular issues
        db_healthy = await check_database_health()
        database_status = "connected" if db_healthy else "disconnected"
    except Exception as e:
        database_status = "disconnected"
    
    # Determine overall system status
    overall_status = "healthy" if database_status == "connected" else "degraded"
    
    response = {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "database": database_status
    }
    
    # Add helpful messages when database is down
    if database_status == "disconnected":
        response["message"] = "API is running but database is unavailable"
        response["suggestions"] = [
            "Start PostgreSQL: docker-compose up -d postgres",
            "Check database configuration in .env file",
            "Verify database credentials and connection string"
        ]
    
    return response