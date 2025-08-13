from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid
from datetime import datetime, timezone
import enum


class StatusEnum(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class PriorityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    # Set Python-side defaults so instances have values before flush/commit
    status = Column(Enum(StatusEnum), default=StatusEnum.pending, nullable=False)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.medium, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    # Test field for migration generation
    # test_field = Column(String(50), nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if getattr(self, "status", None) is None:
            self.status = StatusEnum.pending
        if getattr(self, "priority", None) is None:
            self.priority = PriorityEnum.medium
        if getattr(self, "created_at", None) is None:
            self.created_at = datetime.now(timezone.utc)
        if getattr(self, "updated_at", None) is None:
            self.updated_at = datetime.now(timezone.utc)