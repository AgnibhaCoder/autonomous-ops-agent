import os
from app.tools.base import BaseTool

class FileWriterTool(BaseTool):
    name = "write_file"
    description = "Writes or overwrites text content to a target file. REQUIRES HUMAN APPROVAL."
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Relative path to the file inside workspace."
            },
            "content": {
                "type": "string",
                "description": "The exact text content to write into the file."
            }
        },
        "required": ["file_path", "content"]
    }
    requires_approval = True  # Triggers AWAITING_APPROVAL state

    async def execute(self, file_path: str, content: str) -> str:
        sandbox_dir = os.path.abspath("./sandbox")
        target_path = os.path.abspath(os.path.join(sandbox_dir, file_path))

        if not target_path.startswith(sandbox_dir):
            return "Error: Access denied. Cannot write outside sandbox directory."

        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to {file_path}."
        except Exception as e:
            return f"Error writing file: {str(e)}"