"""Structured-output production of the triage.

`registrar_triage` turns structured data into a validated `Triage`. It is the
in-process tool the agent (#6) uses to emit the triage as validated structured
output, never free text (behavior #5). Fields the report does not mention stay None.
"""

from pydantic import BaseModel, ValidationError

from ..mcp_server.errors import ErrorCategory, ErrorInfo, error_info
from ..mcp_server.models import Triage


class TriageResult(BaseModel):
    """Outcome of `registrar_triage`: a validated triage or a validation error."""

    ok: bool
    triage: Triage | None = None
    error: ErrorInfo | None = None


def registrar_triage(data: dict) -> TriageResult:
    """Produce a validated triage from structured data. Never free text.

    What the report does not mention stays None (schema defaults); the agent must not invent it.
    """
    try:
        triage = Triage(**data)
    except ValidationError as exc:
        return TriageResult(ok=False, error=error_info(ErrorCategory.VALIDATION, str(exc)))
    return TriageResult(ok=True, triage=triage)
