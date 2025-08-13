from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from app.api.dependencies import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.task_service import TaskService
from app.models.task import StatusEnum, PriorityEnum
from app.config import settings

router = APIRouter()

# Rate limiter for endpoints
limiter = Limiter(key_func=get_remote_address)


@router.get("/tasks", response_model=dict)
@limiter.limit("30/minute")
async def list_tasks(
    request: Request,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|due_date|priority)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all tasks with optional filtering and pagination.
    
    - **status**: Filter by task status (pending, in_progress, completed)
    - **priority**: Filter by task priority (low, medium, high)
    - **sort_by**: Field to sort by
    - **order**: Sort order (asc/desc)
    - **page**: Page number
    - **limit**: Items per page
    """
    
    # Validate status enum if provided
    if status is not None:
        try:
            status = StatusEnum(status)
        except ValueError:
            valid_statuses = [e.value for e in StatusEnum]
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Invalid status value",
                    "message": f"Status must be one of: {', '.join(valid_statuses)}",
                    "provided": status,
                    "valid_values": valid_statuses
                }
            )
    
    # Validate priority enum if provided
    if priority is not None:
        try:
            priority = PriorityEnum(priority)
        except ValueError:
            valid_priorities = [e.value for e in PriorityEnum]
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Invalid priority value",
                    "message": f"Priority must be one of: {', '.join(valid_priorities)}",
                    "provided": priority,
                    "valid_values": valid_priorities
                }
            )
    
    service = TaskService(db)
    tasks, total = await service.get_tasks(
        status=status,
        priority=priority,
        sort_by=sort_by,
        order=order,
        skip=(page - 1) * limit,
        limit=limit
    )
    
    return {
        "items": tasks,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/tasks/{task_id}", response_model=TaskResponse)
@limiter.limit("60/minute")
async def get_task(request: Request, task_id: UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific task by ID."""
    service = TaskService(db)
    task = await service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Not Found",
                "message": f"Task with ID {task_id} not found",
                "status_code": 404
            }
        )
    return task


@router.post("/tasks", response_model=TaskResponse, status_code=201)
@limiter.limit("10/minute")
async def create_task(request: Request, task: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create a new task."""
    service = TaskService(db)
    return await service.create_task(task)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
@limiter.limit("15/minute")
async def update_task(
    request: Request,
    task_id: UUID,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing task."""
    service = TaskService(db)
    task = await service.update_task(task_id, task_update)
    if not task:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Not Found",
                "message": f"Task with ID {task_id} not found",
                "status_code": 404
            }
        )
    return task


@router.delete("/tasks/{task_id}", status_code=204)
@limiter.limit("5/minute")
async def delete_task(request: Request, task_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a task by ID."""
    service = TaskService(db)
    if not await service.delete_task(task_id):
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Not Found",
                "message": f"Task with ID {task_id} not found",
                "status_code": 404
            }
        )