# import os
# from agency_swarm.tools import BaseTool
# from dotenv import load_dotenv
# from pydantic import Field

# from voice_assistant.config import SCRATCH_PAD_DIR
# from voice_assistant.models import CreateFileResponse
# from voice_assistant.utils.decorators import timeit_decorator
# from voice_assistant.utils.llm_utils import get_structured_output_completion

# load_dotenv()

# class CreateFile(BaseTool):
#     """A tool for creating a new file with generated content based on a prompt or writing the prompt directly."""

#     file_name: str = Field(..., description="The name of the file to be created.")
#     prompt: str = Field(
#         ..., description="The prompt to generate content for the new file or to be written as is."
#     )
#     format: str = Field(
#         "txt", description="The format of the file content, e.g., 'txt'."
#     )
#     write_prompt_as_is: bool = Field(
#         False, description="If True, writes the prompt directly as the file content."
#     )

#     async def run(self):
#         result = await create_file(self.file_name, self.prompt, self.format, self.write_prompt_as_is)
#         return str(result)

# @timeit_decorator
# async def create_file(file_name: str, prompt: str, format: str, write_prompt_as_is: bool) -> dict:
#     # Ensure the file has the correct extension
#     if format == "txt" and not file_name.endswith(".txt"):
#         file_name += ".txt"

#     file_path = os.path.join(SCRATCH_PAD_DIR, file_name)

#     if os.path.exists(file_path):
#         return {"status": "File already exists"}

#     if write_prompt_as_is:
#         text_content = prompt  # Directly write the prompt
#     else:
#         response = await get_structured_output_completion(prompt, CreateFileResponse)
#         text_content = response.file_content

#     # Write the content to the file
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(text_content)

#     return {"status": "File created", "file_name": file_name}

import os
from agency_swarm.tools import BaseTool
from dotenv import load_dotenv
from pydantic import Field

from voice_assistant.config import SCRATCH_PAD_DIR
from voice_assistant.models import CreateFileResponse
from voice_assistant.utils.decorators import timeit_decorator
from voice_assistant.utils.llm_utils import get_structured_output_completion

load_dotenv()

class CreateFile(BaseTool):
    """A tool for creating a new file with generated content based on a prompt or writing the prompt directly."""

    file_name: str = Field(..., description="The name of the file to be created.")
    prompt: str = Field(
        ..., description="The prompt to generate content for the new file or to be written as is."
    )
    format: str = Field(
        "txt", description="The format of the file content, e.g., 'txt'."
    )
    write_prompt_as_is: bool = Field(
        False, description="If True, writes the prompt directly as the file content."
    )

    async def run(self):
        result = await create_file(self.file_name, self.prompt, self.format, self.write_prompt_as_is)
        return str(result)

@timeit_decorator
async def create_file(file_name: str, prompt: str, format: str, write_prompt_as_is: bool) -> dict:
    # Ensure the file has the correct extension
    if format == "txt" and not file_name.endswith(".txt"):
        file_name += ".txt"

    file_path = os.path.join(SCRATCH_PAD_DIR, file_name)

    if os.path.exists(file_path):
        return {"status": "File already exists"}

    if write_prompt_as_is:
        text_content = prompt  # Directly write the prompt
    else:
        # Create structured prompt with strict instructions
        creation_instructions = f"""File Creation Request:
        - User Instructions: 
        {prompt}

        - Requirements:
        1. Write EXACTLY the content specified by the user
        2. No summaries, descriptions, or additional notes
        3. Maintain original formatting from the instructions
        4. Respond with only the raw content to be written to the file"""

        response = await get_structured_output_completion(creation_instructions, CreateFileResponse)
        text_content = response.file_content

    # Write the content to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text_content)

    return {"status": "File created", "file_name": file_name}