from typing import Any, Optional

from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    """
    Raised when something was not found. i.e. a Database lookup.

    Inherits an HTTPException so that FastAPI can handle it
    if it is left unhandled.
    """

    def __init__(
        self,
        *,
        what="The requested resource",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(status_code, detail=f"{what} cannot be found.")


class ConditionError(HTTPException):
    def __init__(
        self,
        condition: str,
        detail: Optional[str] = None,
        status_code: int = status.HTTP_417_EXPECTATION_FAILED,
        **extras: Any,
    ) -> None:
        super().__init__(status_code, detail=detail or condition)
        self.condition = condition
        self.extras = extras or {}
