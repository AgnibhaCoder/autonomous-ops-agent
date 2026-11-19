from typing import Dict, List, Any
from app.tools.base import BaseTool
from app.tools.read_only.file_reader import FileReaderTool
from app.tools.mutative.file_writer import FileWriterTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(FileReaderTool())
        self.register(FileWriterTool())

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        return self._tools.get(name)

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Formats all registered tools into OpenAI Function Calling format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
            }
            for tool in self._tools.values()
        ]

tool_registry = ToolRegistry()