from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db, AsyncSessionLocal
from app.db.models import Task, TaskStatus
from app.db.schemas import TaskCreate, TaskResponse
from app.core.agent import AgentEngine
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

router = APIRouter()

async def run_agent_background(task_id: str):
    """Background runner with isolated session dependency."""
    async with AsyncSessionLocal() as db:
        engine = AgentEngine(task_id=task_id, db=db)
        await engine.run()

@router.post("/", response_model=TaskResponse)
async def create_task(
    payload: TaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    task = Task(prompt=payload.prompt, status=TaskStatus.PENDING)
    db.add(task)
    await db.commit()
    

    # Trigger async agent run in background
    background_tasks.add_task(run_agent_background, task.id)
    stmt = select(Task).options(selectinload(Task.steps)).where(Task.id == task.id)
    res = await db.execute(stmt)
    return res.scalar_one()

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(db: AsyncSession = Depends(get_db)):
    stmt = select(Task).options(selectinload(Task.steps)).order_by(Task.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Task).options(selectinload(Task.steps)).where(Task.id == task_id)
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task