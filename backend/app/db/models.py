import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Enum, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class TaskStatus(str, PyEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt = Column(Text, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    total_tokens = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    steps = relationship("ExecutionStep", back_populates="task", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="task", cascade="all, delete-orphan")

class ExecutionStep(Base):
    __tablename__ = "execution_steps"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    thought = Column(Text, nullable=True)
    tool_name = Column(String, nullable=True)
    tool_input = Column(JSON, nullable=True)
    tool_output = Column(JSON, nullable=True)
    status = Column(String, nullable=False)  # e.g., EXECUTING, SUCCESS, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="steps")

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    action_type = Column(String, nullable=False)  # e.g., file_write, git_commit
    payload = Column(JSON, nullable=False)        # Proposed arguments
    is_approved = Column(String, nullable=True)   # "PENDING", "APPROVED", "REJECTED"
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="approvals")