import asyncio
import os
from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field
from voice_assistant.config import SCRATCH_PAD_DIR
from voice_assistant.models import UpdateFileResponse
from voice_assistant.utils.llm_utils import get_structured_output_completion

load_dotenv()

class UpdateFile(BaseTool):
    """Tool for directly modifying existing file content"""
    
    file_name: str = Field(..., description="Name of the file to update")
    update_prompt: str = Field(..., description="Clear instructions for the required changes")

    def run(self):
        # Check if an event loop is already running
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            return asyncio.ensure_future(self._update_file_content())  # Use ensure_future for non-blocking execution
        else:
            return asyncio.run(self._update_file_content())  # Use asyncio.run() only when no loop is running

    async def _update_file_content(self):
        file_path = os.path.join(SCRATCH_PAD_DIR, self.file_name)

        if not os.path.exists(file_path):
            return {"status": "error", "message": f"File {self.file_name} does not exist"}

        try:
            # Read current content
            with open(file_path, "r") as f:
                current_content = f.read()

            # Generate update instructions
            update_instructions = f"""File Update Request:
            - Current Content:
            {current_content}
            
            - Update Instructions: 
            {self.update_prompt}
            
            - Requirements:
            1. Maintain original file format
            2. Only modify specified sections
            3. Preserve unrelated content"""

            # Get structured update
            response = await get_structured_output_completion(
                update_instructions,
                UpdateFileResponse
            )

            # Direct in-place update
            with open(file_path, "w") as f:
                f.write(response.updated_content)

            return {
                "status": "success",
                "file_name": self.file_name,
                "changes_made": response.change_summary,
                "requires_confirmation": response.requires_confirmation # Force direct update
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}
