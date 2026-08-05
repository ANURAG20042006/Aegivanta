from typing import Any, Optional
from fastapi import HTTPException, status


class SentinelAIException(HTTPException):
    """Base exception class for all custom application errors."""
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = "An unexpected error occurred in SentinelAI engine.",
        headers: Optional[dict] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class AuthenticationError(SentinelAIException):
    """Raised when authentication fails or token is invalid."""
    def __init__(self, detail: str = "Invalid credentials or expired authentication token."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class PermissionDeniedError(SentinelAIException):
    """Raised when a user lacks the required RBAC role permissions."""
    def __init__(self, detail: str = "You do not have permission to execute this operation."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class NotFoundError(SentinelAIException):
    """Raised when a requested database entity or resource is not found."""
    def __init__(self, resource_name: str = "Resource", resource_id: Any = ""):
        detail = f"{resource_name} with ID '{resource_id}' was not found." if resource_id else f"{resource_name} not found."
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ModelInferenceError(SentinelAIException):
    """Raised when machine learning prediction engine encounters an evaluation failure."""
    def __init__(self, detail: str = "ML Inference failed during flow vector evaluation."):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class InvalidDatasetError(SentinelAIException):
    """Raised when uploaded network traffic CSV lacks required CICIDS2017 feature columns."""
    def __init__(self, detail: str = "Uploaded CSV format is invalid or missing required CICIDS2017 features."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
