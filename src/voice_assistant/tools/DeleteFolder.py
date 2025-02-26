import os
import shutil
import asyncio
from pathlib import Path
from typing import Dict
from agency_swarm.tools import BaseTool
from pydantic import Field

# Update these imports according to your project structure
from voice_assistant.config import SCRATCH_PAD_DIR
from voice_assistant.utils.file_validation import validate_file_path

class DeleteFolder(BaseTool):
    """
    Deletes folders in the Scratchpad directory, including nested directories.
    Handles path validation securely and provides options for recursive deletion.
    """

    folder_name: str = Field(
        ...,
        description="Name of the folder to delete (can include subdirectories)"
    )
    parent_folder: str = Field(
        default=".",
        description="Parent directory within Scratchpad (defaults to root)"
    )
    recursive: bool = Field(
        default=False,
        description="Delete folder and all its contents recursively"
    )

    async def run(self) -> Dict:
        """Asynchronous wrapper for synchronous folder deletion"""
        return await asyncio.to_thread(
            self._delete_folder_sync
        )

    def _delete_folder_sync(self) -> Dict:
        """Synchronous folder deletion logic with enhanced validation"""
        base_path = Path(SCRATCH_PAD_DIR).resolve()
        parent_path = (base_path / self.parent_folder.strip()).resolve()
        
        try:
            # Validate parent directory path structure
            validate_file_path(str(parent_path.relative_to(base_path)))
            
            # Ensure parent directory exists
            if not parent_path.exists():
                return {
                    "status": "error",
                    "message": f"Parent directory does not exist at {parent_path.relative_to(base_path)}",
                    "path": str(parent_path.relative_to(base_path))
                }
            
            # Construct full path and validate its structure
            full_path = (parent_path / self.folder_name.strip()).resolve()
            if not full_path.is_relative_to(base_path):
                raise ValueError("Invalid path structure - potential directory traversal attempt")

            # Check if the folder exists
            if not full_path.exists():
                return {
                    "status": "error",
                    "message": f"Folder does not exist at {full_path.relative_to(base_path)}",
                    "path": str(full_path.relative_to(base_path))
                }

            # Handle recursive deletion
            if self.recursive:
                shutil.rmtree(full_path)
            else:
                if any(full_path.iterdir()):
                    return {
                        "status": "error",
                        "message": f"Folder is not empty at {full_path.relative_to(base_path)}",
                        "path": str(full_path.relative_to(base_path))
                    }
                os.rmdir(full_path)

            return {
                "status": "success",
                "path": str(full_path.relative_to(base_path)),
                "message": "Folder and its contents deleted" if self.recursive else "Folder deleted"
            }

        except ValueError as ve:
            return {
                "status": "error",
                "message": str(ve),
                "attempted_path": str(full_path.relative_to(base_path))
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Operation failed: {str(e)}",
                "attempted_path": str(full_path.relative_to(base_path))
            }