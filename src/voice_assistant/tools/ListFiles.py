import os
from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field
from voice_assistant.config import SCRATCH_PAD_DIR

load_dotenv()

class ListFiles(BaseTool):
    """Tool for listing all available files inside the scratchpad directory, including subdirectories."""

    async def run(self):
        try:
            file_list = []

            # Walk through all directories and subdirectories
            for root, _, files in os.walk(SCRATCH_PAD_DIR):
                for file in files:
                    # Get relative path from scratchpad directory
                    relative_path = os.path.relpath(os.path.join(root, file), SCRATCH_PAD_DIR)
                    file_list.append(relative_path)

            if not file_list:
                return {"status": "success", "message": "No notes found in the scratchpad directory."}

            return {
                "status": "success",
                "files": file_list,
                "message": f"Found {len(file_list)} note(s) in the scratchpad directory, including subdirectories."
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}
