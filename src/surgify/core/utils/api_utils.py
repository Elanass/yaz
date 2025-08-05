from typing import Any, Dict

from fastapi import HTTPException, status
from pydantic import ValidationError


class APIUtils:
    @staticmethod
    def handle_validation_error(error: ValidationError) -> HTTPException:
        """Handle Pydantic validation errors and return appropriate HTTP exception."""
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error.errors()
        )

    @staticmethod
    def handle_generic_error(error: Exception) -> HTTPException:
        """Handle generic errors and return appropriate HTTP exception."""
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)
        )

    @staticmethod
    def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
        """Create a standardized success response."""
        return {"status": "success", "message": message, "data": data}

    @staticmethod
    def create_error_response(message: str, error_code: str = None) -> Dict[str, Any]:
        """Create a standardized error response."""
        response = {"status": "error", "message": message}
        if error_code:
            response["error_code"] = error_code
        return response

    @staticmethod
    def validate_pagination_params(page: int = 1, per_page: int = 10) -> Dict[str, int]:
        """Validate and return pagination parameters."""
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page number must be greater than 0",
            )
        if per_page < 1 or per_page > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Per page must be between 1 and 100",
            )
        return {"page": page, "per_page": per_page}
