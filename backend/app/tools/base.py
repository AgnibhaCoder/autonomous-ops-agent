from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel

class BaseTool(ABC):
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema definition for OpenAI Function Calling
    requires_approval: bool = False  # HITL Flag

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Executes the tool logic asynchronously."""
        pass