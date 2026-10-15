"""Structured error envelope shared by all MCP tools.

Decision (see plan 002): FastMCP v1 does not allow `isError: true` alongside
`structuredContent`. Therefore domain state always travels in `structuredContent`
with an `ok` flag; `errorCategory`/`isRetryable` remain readable for hooks (#7).
Envelope keys are in English (transport layer); domain values stay in Spanish.
"""

from enum import Enum

from pydantic import BaseModel


class ErrorCategory(str, Enum):
    """Error categories from the spec (behavior #4)."""

    TRANSIENT = "transient"
    VALIDATION = "validation"
    BUSINESS = "business"
    PERMISSIONS = "permissions"


# Only transient errors are retryable.
_RETRYABLE = {ErrorCategory.TRANSIENT}


class ErrorInfo(BaseModel):
    """Error descriptor carried inside the envelope."""

    errorCategory: ErrorCategory
    isRetryable: bool
    description: str


def error_info(category: ErrorCategory, description: str) -> ErrorInfo:
    """Build an ErrorInfo with `isRetryable` derived from the category."""
    return ErrorInfo(
        errorCategory=category,
        isRetryable=category in _RETRYABLE,
        description=description,
    )
