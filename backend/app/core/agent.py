import json
import asyncio
from datetime import datetime
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.config import settings
from app.db.models import Task, ExecutionStep, Approval, TaskStatus
from app.core.state_machine import validate_transition
from app.core.prompt_templates import SYSTEM_PROMPT, REJECTION_PROMPT_TEMPLATE
from app.core.ws_manager import ws_manager
from app.tools.registry import tool_registry

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY,
                            base_url="https://api.groq.com/openai/v1"
                            )

class AgentEngine:
    def __init__(self, task_id: str, db: AsyncSession):
        self.task_id = task_id
        self.db = db

    async def run(self):
        """Main execution loop."""
        task = await self._get_task()
        if not task:
            return

        # Transition Task to RUNNING
        await self._update_task_status(task, TaskStatus.RUNNING)

        # Build conversation state from past execution steps
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.append({"role": "user", "content": task.prompt})

        step_counter = len(task.steps) + 1

        while step_counter <= settings.MAX_AGENT_STEPS:
            # Re-fetch task to check if paused or cancelled
            await self.db.refresh(task)
            if task.status == TaskStatus.AWAITING_APPROVAL:
                # Pause loop until human approves/rejects via API endpoint
                return

            # 1. Call OpenAI LLM
            response = await openai_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=messages,
                tools=tool_registry.get_openai_tools(),
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            thought = response_message.content or ""

            # Log tokens
            if response.usage:
                task.total_tokens += response.usage.total_tokens
                await self.db.commit()

            # Case A: LLM produced a final text answer (No tool calls)
            if not tool_calls:
                step = ExecutionStep(
                    task_id=self.task_id,
                    step_number=step_counter,
                    thought=thought,
                    status="COMPLETED"
                )
                self.db.add(step)
                await self._update_task_status(task, TaskStatus.COMPLETED)
                await self.db.commit()

                await ws_manager.broadcast(self.task_id, {
                    "type": "STEP_COMPLETED",
                    "step_number": step_counter,
                    "thought": thought,
                    "status": "COMPLETED"
                })
                break

            # Case B: LLM wants to invoke a Tool
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                tool_obj = tool_registry.get_tool(tool_name)

                if not tool_obj:
                    # Unknown tool safety check
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": f"Error: Tool '{tool_name}' does not exist."
                    })
                    continue

                # Check HITL requirement
                if tool_obj.requires_approval:
                    # Record step awaiting approval
                    step = ExecutionStep(
                        task_id=self.task_id,
                        step_number=step_counter,
                        thought=thought,
                        tool_name=tool_name,
                        tool_input=tool_args,
                        status="AWAITING_APPROVAL"
                    )
                    approval = Approval(
                        task_id=self.task_id,
                        action_type=tool_name,
                        payload=tool_args,
                        is_approved="PENDING"
                    )
                    self.db.add(step)
                    self.db.add(approval)
                    await self._update_task_status(task, TaskStatus.AWAITING_APPROVAL)
                    await self.db.commit()

                    # Broadcast pause event to Frontend UI
                    await ws_manager.broadcast(self.task_id, {
                        "type": "AWAITING_APPROVAL",
                        "step_number": step_counter,
                        "thought": thought,
                        "tool_name": tool_name,
                        "payload": tool_args,
                        "approval_id": approval.id
                    })
                    return # Exit loop until resumed by endpoint

                # Tool is Read-Only: Execute with timeout
                step = ExecutionStep(
                    task_id=self.task_id,
                    step_number=step_counter,
                    thought=thought,
                    tool_name=tool_name,
                    tool_input=tool_args,
                    status="EXECUTING"
                )
                self.db.add(step)
                await self.db.commit()

                try:
                    output = await asyncio.wait_for(
                        tool_obj.execute(**tool_args),
                        timeout=settings.TOOL_TIMEOUT_SECONDS
                    )
                    step.status = "SUCCESS"
                    step.tool_output = {"result": output}
                except asyncio.TimeoutError:
                    output = f"Error: Tool '{tool_name}' timed out after {settings.TOOL_TIMEOUT_SECONDS}s."
                    step.status = "TIMEOUT"
                    step.tool_output = {"error": output}

                await self.db.commit()

                # Stream Observation back to UI
                await ws_manager.broadcast(self.task_id, {
                    "type": "STEP_UPDATE",
                    "step_number": step_counter,
                    "thought": thought,
                    "tool_name": tool_name,
                    "tool_input": tool_args,
                    "tool_output": step.tool_output,
                    "status": step.status
                })

                # Append tool results back into message memory for next iteration
                messages.append(response_message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(step.tool_output)
                })

            step_counter += 1

        # Safeguard: Halted on max steps
        if step_counter > settings.MAX_AGENT_STEPS:
            await self._update_task_status(task, TaskStatus.FAILED)
            await ws_manager.broadcast(self.task_id, {
                "type": "TASK_FAILED",
                "reason": f"Exceeded maximum limit of {settings.MAX_AGENT_STEPS} steps."
            })

    async def resume_after_approval(self, approval_id: str, approved: bool, reason: str = None):
        """Resumes task loop after human approves or rejects an action."""
        task = await self._get_task()
        stmt = select(Approval).where(Approval.id == approval_id)
        res = await self.db.execute(stmt)
        approval = res.scalar_one_or_none()

        if not approval or approval.is_approved != "PENDING":
            return

        if approved:
            approval.is_approved = "APPROVED"
            await self._update_task_status(task, TaskStatus.RUNNING)
            await self.db.commit()

            # Execute approved mutative tool
            tool_obj = tool_registry.get_tool(approval.action_type)
            output = await tool_obj.execute(**approval.payload)

            await ws_manager.broadcast(self.task_id, {
                "type": "APPROVAL_DECISION",
                "approved": True,
                "tool_output": output
            })

            # Re-enter execution loop
            await self.run()

        else:
            approval.is_approved = "REJECTED"
            await self._update_task_status(task, TaskStatus.REJECTED)
            await self.db.commit()

            await ws_manager.broadcast(self.task_id, {
                "type": "APPROVAL_DECISION",
                "approved": False,
                "reason": reason
            })

            # Re-enter loop: Prompt agent to replan around rejection
            await self.run()

    async def _get_task(self) -> Task:
        stmt = select(Task).options(selectinload(Task.steps)).where(Task.id == self.task_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def _update_task_status(self, task: Task, new_status: TaskStatus):
        validate_transition(task.status, new_status)
        task.status = new_status
        await self.db.commit()