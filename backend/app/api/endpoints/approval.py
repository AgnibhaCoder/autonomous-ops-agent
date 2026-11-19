'''
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, AsyncSessionLocal
from app.db.schemas import ApprovalDecision
from app.core.agent import AgentEngine

router = APIRouter()

async def resume_agent_background(task_id: str, approval_id: str, approved: bool, reason: str = None):
    async with AsyncSessionLocal() as db:
        engine = AgentEngine(task_id=task_id, db=db)
        await engine.resume_after_approval(approval_id=approval_id, approved=approved, reason=reason)

@router.post("/{task_id}/approvals/{approval_id}")
async def submit_approval_decision(
    task_id: str,
    approval_id: str,
    decision: ApprovalDecision,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    background_tasks.add_task(
        resume_agent_background,
        task_id=task_id,
        approval_id=approval_id,
        approved=decision.approved,
        reason=decision.reason
    )
    return {"status": "Decision received processing in background"}
'''


import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, AsyncSessionLocal
from app.db.schemas import ApprovalDecision
from app.core.agent import AgentEngine

logger = logging.getLogger(__name__)
router = APIRouter()

async def resume_agent_background(task_id: str, approval_id: str, approved: bool, reason: str = None):
    try:
        async with AsyncSessionLocal() as db:
            engine = AgentEngine(task_id=task_id, db=db)
            await engine.resume_after_approval(approval_id=approval_id, approved=approved, reason=reason)
    except Exception as e:
        logger.error(f"Failed to resume agent for task {task_id}: {str(e)}", exc_info=True)

@router.post("/{task_id}/approvals/{approval_id}")
async def submit_approval_decision(
    task_id: str,
    approval_id: str,
    decision: ApprovalDecision,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    background_tasks.add_task(
        resume_agent_background,
        task_id=task_id,
        approval_id=approval_id,
        approved=decision.approved,
        reason=decision.reason
    )
    return {"status": "Decision received processing in background"}