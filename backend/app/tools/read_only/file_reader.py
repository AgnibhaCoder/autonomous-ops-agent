import os
from app.tools.base import BaseTool

class FileReaderTool(BaseTool):
    name = "read_file"
    description = "Reads and returns the contents of a specified text file from the workspace."
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Relative path to the file inside the workspace sandbox."
            }
        },
        "required": ["file_path"]
    }
    requires_approval = False

    async def execute(self, file_path: str) -> str:
        sandbox_dir = os.path.abspath("./sandbox")
        target_path = os.path.abspath(os.path.join(sandbox_dir, file_path))

        # Security check: Prevent path traversal outside sandbox
        if not target_path.startswith(sandbox_dir):
            return "Error: Access denied. Cannot read outside sandbox directory."

        if not os.path.exists(target_path):
            return f"Error: File '{file_path}' not found."

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"