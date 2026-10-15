"""Expose `registrar_triage` as an in-process SDK MCP tool.

The agent emits the triage through this tool as validated structured output
(behavior #5): the Pydantic validation lives in `registrar_triage`, so a
malformed triage is rejected rather than accepted as free text. The tool's
input schema IS the `Triage` model (spec 006).

Note: the Claude Agent SDK in-process bridge forwards only `content` and
`is_error` from a tool result (it drops MCP `structuredContent`). The validated
triage therefore travels as JSON text in `content`; the structural guarantee
comes from the validation, not from the transport field.
"""

from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool

from ..mcp_server.models import Triage
from .triage import registrar_triage

_REGISTRAR_DESCRIPTION = (
    "Registra el triage del siniestro como salida estructurada validada. "
    "Lo que el reporte no menciona queda nulo; no inventes campos."
)


@tool("registrar_triage", _REGISTRAR_DESCRIPTION, Triage.model_json_schema())
async def registrar_triage_tool(args: dict[str, Any]) -> dict[str, Any]:
    """Validate and record a triage, returning the validated triage as JSON text.

    Valid data -> content with the validated `Triage`. Invalid data -> an error
    result (`is_error`) carrying the validation `ErrorInfo`; never a partial triage.
    """
    result = registrar_triage(args)
    if result.ok and result.triage is not None:
        return {"content": [{"type": "text", "text": result.triage.model_dump_json()}]}
    description = result.error.description if result.error else "invalid triage"
    error_text = result.error.model_dump_json() if result.error else description
    return {"content": [{"type": "text", "text": error_text}], "is_error": True}


triage_server = create_sdk_mcp_server(name="triage", version="1.0.0", tools=[registrar_triage_tool])
