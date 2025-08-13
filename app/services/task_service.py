from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.models.task import Task


class TaskService:
    def __init__(self, db: AsyncSession):
        self.repository = TaskRepository(db)

    async def get_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        sort_by: str = "created_at",
        order: str = "desc",
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[TaskResponse], int]:
        tasks, total = await self.repository.get_all(
            status=status,
            priority=priority,
            sort_by=sort_by,
            order=order,
            skip=skip,
            limit=limit
        )
        task_responses = [TaskResponse.model_validate(task) for task in tasks]
        return task_responses, total

    async def get_task_by_id(self, task_id: UUID) -> Optional[TaskResponse]:
        task = await self.repository.get_by_id(task_id)
        if not task:
            return None
        return TaskResponse.model_validate(task)

    async def create_task(self, task_data: TaskCreate) -> TaskResponse:
        task = await self.repository.create(task_data)
        return TaskResponse.model_validate(task)

    async def update_task(self, task_id: UUID, task_data: TaskUpdate) -> Optional[TaskResponse]:
        task = await self.repository.update(task_id, task_data)
        if not task:
            return None
        return TaskResponse.model_validate(task)

    async def delete_task(self, task_id: UUID) -> bool:
        return await self.repository.delete(task_id)