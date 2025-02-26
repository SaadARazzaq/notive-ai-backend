import os
import shutil
import asyncio
from pathlib import Path
from typing import Dict, List
from agency_swarm.tools import BaseTool
from pydantic import Field

# Update these imports according to your project structure
from voice_assistant.config import SCRATCH_PAD_DIR
from voice_assistant.utils.file_validation import validate_file_path

class CreateFolder(BaseTool):
    """
    Creates new folders in the Scratchpad directory with optional initial files.
    Handles existing folders and path validation securely.
    """

    folder_name: str = Field(
        ...,
        description="Name of the folder to create (can include subdirectories)"
    )
    parent_folder: str = Field(
        default=".",
        description="Parent directory within Scratchpad (defaults to root)"
    )
    overwrite_existing: bool = Field(
        default=False,
        description="Delete existing folder and contents if it exists"
    )
    initial_files: List[str] = Field(
        default=[],
        description="List of filenames to create inside the new folder"
    )

    async def run(self) -> Dict:
        """Asynchronous wrapper for synchronous folder creation"""
        return await asyncio.to_thread(
            self._create_folder_sync
        )

    def _create_folder_sync(self) -> Dict:
        """Synchronous folder creation logic with enhanced validation"""
        base_path = Path(SCRATCH_PAD_DIR).resolve()
        parent_path = (base_path / self.parent_folder.strip()).resolve()
        
        try:
            # Validate parent directory path structure
            validate_file_path(str(parent_path.relative_to(base_path)))
            
            # Ensure parent directory exists
            parent_path.mkdir(parents=True, exist_ok=True)
            
            # Construct full path and validate its structure
            full_path = (parent_path / self.folder_name.strip()).resolve()
            if not full_path.is_relative_to(base_path):
                raise ValueError("Invalid path structure - potential directory traversal attempt")

            # Handle existing folder
            if full_path.exists():
                if not self.overwrite_existing:
                    return {
                        "status": "error",
                        "message": f"Folder already exists at {full_path.relative_to(base_path)}",
                        "path": str(full_path.relative_to(base_path))
                    }
                
                # Remove existing folder if overwrite is enabled
                shutil.rmtree(full_path)

            # Create directory structure
            full_path.mkdir(parents=True, exist_ok=True)
            
            # Create initial files
            created_files = []
            for filename in self.initial_files:
                file_path = (full_path / filename.strip()).resolve()
                validate_file_path(str(file_path.relative_to(base_path)))
                file_path.touch()
                created_files.append(str(file_path.relative_to(base_path)))

            return {
                "status": "success",
                "path": str(full_path.relative_to(base_path)),
                "initial_files": created_files,
                "message": "Folder overwritten" if self.overwrite_existing else "Folder created"
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

    @staticmethod
    def _unique_filename(directory: Path, filename: str) -> Path:
        """Generate unique filename if conflict exists"""
        counter = 1
        name_stem = Path(filename).stem
        suffix = Path(filename).suffix

        while (directory / filename).exists():
            filename = f"{name_stem}_{counter}{suffix}"
            counter += 1

        return directory / filename