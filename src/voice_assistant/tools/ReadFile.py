import os
from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field
from voice_assistant.config import SCRATCH_PAD_DIR

load_dotenv()

class ReadFile(BaseTool):
    """Tool for reading the content of a file inside the scratchpad directory, including subdirectories."""

    file_name: str = Field(..., description="Relative path of the file to read, including subdirectories if applicable")

    async def run(self):
        try:
            # Construct full file path
            file_path = os.path.join(SCRATCH_PAD_DIR, self.file_name)

            # Ensure file exists
            if not os.path.isfile(file_path):
                return {"status": "error", "message": f"File '{self.file_name}' does not exist in the scratchpad."}

            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "status": "success",
                "file_name": self.file_name,
                "content": content
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}
