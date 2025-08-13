import pytest
from datetime import datetime
from app.models.task import Task, StatusEnum, PriorityEnum


def test_task_creation():
    task = Task(
        title="Test Task",
        description="Test Description",
        status=StatusEnum.pending,
        priority=PriorityEnum.high
    )
    
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.status == StatusEnum.pending
    assert task.priority == PriorityEnum.high


def test_task_defaults():
    task = Task(title="Test Task")
    
    assert task.title == "Test Task"
    assert task.status == StatusEnum.pending
    assert task.priority == PriorityEnum.medium
    assert task.description is None
    assert task.due_date is None


def test_status_enum():
    assert StatusEnum.pending == "pending"
    assert StatusEnum.in_progress == "in_progress"
    assert StatusEnum.completed == "completed"


def test_priority_enum():
    assert PriorityEnum.low == "low"
    assert PriorityEnum.medium == "medium"
    assert PriorityEnum.high == "high"