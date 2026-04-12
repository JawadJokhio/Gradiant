from fastapi import HTTPException

class LLMProviderError(HTTPException):
    """Exception raised when an LLM provider fails."""
    def __init__(self, detail: str):
        super().__init__(status_code=503, detail=f"LLM Provider Error: {detail}")

class DataNotFoundException(HTTPException):
    """Exception raised when required data is not found."""
    def __init__(self, detail: str):
        super().__init__(status_code=404, detail=detail)

class InvalidImageException(HTTPException):
    """Exception raised when uploaded image is invalid or cannot be parsed."""
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)
