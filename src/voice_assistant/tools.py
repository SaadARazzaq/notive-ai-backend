# src/voice_assistant/tools.py
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "update_file_content",
            "description": "Directly updates the content of an existing file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "Name of the file to update"
                    },
                    "update_prompt": {
                        "type": "string", 
                        "description": "Detailed instructions for what needs to be updated"
                    },
                    "create_backup": {
                        "type": "boolean",
                        "description": "Whether to create a backup file before updating",
                        "default": True
                    }
                },
                "required": ["file_name", "update_prompt"]
            }
        }
    },
    # ... other tool schemas
]