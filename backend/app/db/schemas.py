from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from app.db.models import TaskStatus

class TaskCreate(BaseModel):
    prompt: str

class ExecutionStepSchema(BaseModel):
    id: str
    step_number: int
    thought: Optional[str]
    tool_name: Optional[str]
    tool_input: Optional[Any]
    tool_output: Optional[Any]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ApprovalDecision(BaseModel):
    approved: bool
    reason: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    prompt: str
    status: TaskStatus
    total_tokens: int
    created_at: datetime
    steps: List[ExecutionStepSchema] = []

    class Config:
        from_attributes = True