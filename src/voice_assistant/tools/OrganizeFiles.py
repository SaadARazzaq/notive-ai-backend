import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal
from agency_swarm.tools import BaseTool
from pydantic import Field

from voice_assistant.config import SCRATCH_PAD_DIR
from voice_assistant.utils.file_validation import validate_file_path

class OrganizeFiles(BaseTool):
    """
    File organization tool that uses predefined strategies without interactive voice prompts.
    """

    strategy: Literal["type", "date", "category"] = Field(
        "type",
        description="File organization strategy: type (by extension), date (by modified time), category (predefined patterns)",
    )
    file_pattern: str = Field(
        "*",
        description="Pattern to match files (e.g., *.txt, project_*)",
    )
    target_folder: str = Field(
        ...,
        description="Target folder where files should be organized.",
    )
    store_by_extension: bool = Field(
        False,
        description="Whether to sort files into folders based on their extensions.",
    )

    def run(self) -> Dict:
        """Executes file organization based on provided parameters"""
        return organize_files(
            target_folder=self.target_folder,
            strategy=self.strategy,
            file_pattern=self.file_pattern,
            store_by_extension=self.store_by_extension
        )

def organize_files(
    target_folder: str,
    strategy: str,
    file_pattern: str = "*",
    store_by_extension: bool = False
) -> Dict:
    """Organizes files based on provided parameters"""
    base_path = Path(SCRATCH_PAD_DIR)
    target_path = base_path / target_folder.strip()

    operations = []
    try:
        # Create target folder if it doesn't exist
        target_path.mkdir(parents=True, exist_ok=True)

        # Get matching files
        files = list(base_path.glob(file_pattern))
        if not files:
            return {"status": "error", "message": "No matching files found."}

        for file_path in files:
            if not file_path.is_file():
                continue

            # Determine destination
            if strategy == "type" and store_by_extension:
                dest_dir = target_path / file_path.suffix[1:]  # Remove dot from extension
            elif strategy == "date":
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                dest_dir = target_path / f"{mtime.year}-{mtime.month:02d}"
            elif strategy == "category":
                dest_dir = _match_category(file_path, CATEGORY_MAP, target_path)
            else:
                dest_dir = target_path  # Default location

            # Validate and create folder
            validate_file_path(str(dest_dir.relative_to(base_path)))
            dest_dir.mkdir(parents=True, exist_ok=True)

            # Move file
            new_path = dest_dir / file_path.name
            if new_path.exists():
                new_path = _unique_filename(dest_dir, file_path.name)

            shutil.move(str(file_path), str(new_path))
            operations.append({
                "original": str(file_path.relative_to(base_path)),
                "new_location": str(new_path.relative_to(base_path)),
                "status": "moved",
            })

        return {
            "status": "success",
            "moved_files": len(operations),
            "operations": operations,
            "target_dir": str(target_path.relative_to(base_path)),
        }

    except Exception as e:
        return {"status": "error", "message": str(e), "partial_operations": operations}

def _match_category(file_path: Path, category_map: Dict, base_path: Path) -> Path:
    """Matches files to predefined categories based on extension"""
    for category, patterns in category_map.items():
        for pattern in patterns:
            if file_path.match(pattern):
                return base_path / category
    return base_path / "uncategorized"


def _unique_filename(directory: Path, filename: str) -> Path:
    """Ensures filename uniqueness"""
    counter = 1
    name, suffix = os.path.splitext(filename)

    while (directory / filename).exists():
        filename = f"{name}_{counter}{suffix}"
        counter += 1

    return directory / filename
