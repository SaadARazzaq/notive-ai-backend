# src/voice_assisstant/tools/RenameFile.py
import os
from typing import Optional

from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field, field_validator

from voice_assistant.config import SCRATCH_PAD_DIR
from voice_assistant.models import FileSelectionResponse
from voice_assistant.utils.decorators import timeit_decorator
from voice_assistant.utils.llm_utils import get_structured_output_completion

load_dotenv()


class RenameFile(BaseTool):
    """A tool for directly renaming files in the scratch pad directory."""
    
    current_name: str = Field(..., description="Current name of the file to rename")
    new_name: str = Field(..., description="New name for the file")
    confirmation: Optional[bool] = Field(
        False, 
        description="Set to True to confirm overwrite if new file exists"
    )

    @field_validator('current_name', 'new_name')
    def validate_filename(cls, v):
        if not v:
            raise ValueError("Filename cannot be empty")
        if os.path.isabs(v):
            raise ValueError("Filename must be relative to scratch pad directory")
        if '..' in v:
            raise ValueError("Parent directory references (..) are not allowed")
        return v

    async def run(self):
        result = await rename_file(
            self.current_name,
            self.new_name,
            self.confirmation
        )
        return str(result)


@timeit_decorator
async def rename_file(current_name: str, new_name: str, confirmation: bool = False) -> dict:
    # Ensure paths stay within scratch pad directory
    current_path = os.path.abspath(os.path.join(SCRATCH_PAD_DIR, current_name))
    new_path = os.path.abspath(os.path.join(SCRATCH_PAD_DIR, new_name))
    
    if not current_path.startswith(os.path.abspath(SCRATCH_PAD_DIR)):
        return {"status": "error", "message": "Invalid current file path"}
    
    if not new_path.startswith(os.path.abspath(SCRATCH_PAD_DIR)):
        return {"status": "error", "message": "Invalid new file path"}

    if not os.path.exists(current_path):
        return {"status": "error", "message": "Source file does not exist"}

    if os.path.exists(new_path) and not confirmation:
        return {
            "status": "confirmation_required",
            "message": f"Target file '{new_name}' exists. Set confirmation=True to overwrite."
        }

    try:
        os.rename(current_path, new_path)
        return {
            "status": "success",
            "message": f"Renamed '{current_name}' to '{new_name}'",
            "old_name": current_name,
            "new_name": new_name
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to rename file: {str(e)}"
        }

@classmethod
async def get_available_files(cls) -> list:
    return os.listdir(SCRATCH_PAD_DIR)

if __name__ == "__main__":
    import asyncio
    
    # Test the tool
    async def test():
        # Create test file
        test_file = "test_rename.txt"
        with open(os.path.join(SCRATCH_PAD_DIR, test_file), "w") as f:
            f.write("Test content")
        
        # Test rename
        tool = RenameFile(
            current_name=test_file,
            new_name="renamed_test.txt",
            confirmation=True
        )
        result = await tool.run()
        print(result)
    
    asyncio.run(test())