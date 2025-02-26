# src/voice_assistant/models.py
from enum import StrEnum

from pydantic import BaseModel, Field



class ModelName(StrEnum):
    BASE_MODEL = "gpt-4o"
    FAST_MODEL = "gpt-4o-mini"
    REASONING_MODEL_LARGE = "o1-preview"
    REASONING_MODEL_SMALL = "o1-mini"


class CreateFileResponse(BaseModel):
    file_content: str
    file_name: str


class FileSelectionResponse(BaseModel):
    file: str
    model: ModelName = ModelName.BASE_MODEL


class FileUpdateResponse(BaseModel):
    updates: str


class FileDeleteResponse(BaseModel):
    file: str
    force_delete: bool

# src/voice_assistant/models.py
class UpdateFileResponse(BaseModel):
    updated_content: str
    change_summary: str
    requires_confirmation: bool