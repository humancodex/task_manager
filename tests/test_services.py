import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import Task, StatusEnum, PriorityEnum


@pytest.fixture
def mock_db():
    return Mock()


@pytest.fixture
def task_service(mock_db):
    return TaskService(mock_db)


@pytest.mark.asyncio
async def test_create_task(task_service):
    task_data = TaskCreate(title="Test Task", description="Test Description")
    
    with patch.object(task_service.repository, 'create') as mock_create:
        mock_task = Task(
            id=uuid4(),
            title="Test Task",
            description="Test Description",
            status=StatusEnum.pending,
            priority=PriorityEnum.medium
        )
        mock_create.return_value = mock_task
        
        result = await task_service.create_task(task_data)
        
        assert result.title == "Test Task"
        mock_create.assert_called_once_with(task_data)


@pytest.mark.asyncio
async def test_get_task_by_id(task_service):
    task_id = uuid4()
    
    with patch.object(task_service.repository, 'get_by_id') as mock_get:
        mock_task = Task(
            id=task_id,
            title="Test Task",
            status=StatusEnum.pending,
            priority=PriorityEnum.medium
        )
        mock_get.return_value = mock_task
        
        result = await task_service.get_task_by_id(task_id)
        
        assert result.id == task_id
        mock_get.assert_called_once_with(task_id)


@pytest.mark.asyncio
async def test_get_nonexistent_task(task_service):
    task_id = uuid4()
    
    with patch.object(task_service.repository, 'get_by_id') as mock_get:
        mock_get.return_value = None
        
        result = await task_service.get_task_by_id(task_id)
        
        assert result is None