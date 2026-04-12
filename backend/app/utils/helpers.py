import json
import os
import re
from typing import Dict, Any

def load_json(path: str) -> Dict[str, Any]:
    """Helper to safely load a JSON file into a dictionary."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def extract_base64_from_file(file_content: bytes) -> str:
    """Helper to encode file content to base64."""
    import base64
    return base64.b64encode(file_content).decode('utf-8')
