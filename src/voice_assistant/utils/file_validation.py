# src/voice_assistant/utils/file_validation.py
import os
from pathlib import Path

def validate_file_path(filename: str) -> Path:
    """Secure path validation for scratchpad operations"""
    base = Path(os.environ.get("SCRATCH_PAD_DIR", "./scratchpad")).resolve()
    full_path = (base / filename).resolve()
    
    if not full_path.is_relative_to(base):
        raise ValueError(f"Invalid path: {filename} attempts directory traversal")
    
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {filename}")
    
    return full_path