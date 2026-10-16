"""SDK hooks that enforce the business rules (constitution Principle I).

PostToolUse hooks populate a `SessionState` from tool *results*. PreToolUse
hooks then make deterministic decisions from that state:
- `guard_abrir_reclamo` denies opening a claim unless `motivos_bloqueo()` is empty.
- `force_priority_on_injuries` forces `priority="alta"` when injuries are reported.

The exact shape of `tool_response` for MCP tools is set by the CLI at runtime;
`extract_structured` isolates that seam (prefers `structuredContent`, falls back
to JSON text in `content` — needed for the in-process `registrar_triage`).
"""

from __future__ import annotations

import json
from typing import Any

from claude_agent_sdk import HookMatcher

from .state import SessionState


def _field(obj: Any, name: str) -> Any:
    """Read a field whether the hook input is a dict (TypedDict) or an object."""
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def _parse_text_content(content: Any) -> dict[str, Any] | None:
    """Return the JSON object in the first text block of an MCP content list."""
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                try:
                    parsed = json.loads(block["text"])
                except (ValueError, KeyError, TypeError):
                    return None
                return parsed if isinstance(parsed, dict) else None
    return None


def extract_structured(tool_response: Any) -> dict[str, Any]:
    """Best-effort extraction of the structured result from a tool_response.

    The live CLI delivers an MCP tool result as a **JSON string** (confirmed in #12),
    e.g. '{"ok":true,"verified":true,...}'. We also handle the shapes used in tests:
    a dict carrying `structuredContent`, a content-list whose text block is JSON, or
    an already-structured dict.
    """
    if isinstance(tool_response, str):
        try:
            parsed = json.loads(tool_response)
        except ValueError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    if isinstance(tool_response, dict):
        structured = tool_response.get("structuredContent")
        if isinstance(structured, dict):
            return structured
        parsed = _parse_text_content(tool_response.get("content"))
        if parsed is not None:
            return parsed
        return tool_response
    parsed = _parse_text_content(tool_response)
    return parsed if parsed is not None else {}


def make_post_tool_use(state: SessionState):
    """One PostToolUse callback that records the result of our known tools."""

    async def record(hook_input: Any, tool_use_id: str | None, context: Any) -> dict[str, Any]:
        name = _field(hook_input, "tool_name") or ""
        resp = extract_structured(_field(hook_input, "tool_response"))
        if name.endswith("verificar_identidad"):
            state.record_identity(resp)
        elif name.endswith("consultar_poliza"):
            state.record_policy(resp)
        elif name.endswith("verificar_cobertura"):
            state.record_coverage(resp)
        elif name.endswith("registrar_triage"):
            state.record_triage(resp)
        elif name.endswith("abrir_reclamo"):
            state.record_claim(resp)
        elif name.endswith("escalar_a_ajustador"):
            state.record_escalation(resp)
        return {}

    return record


def make_guard_abrir_reclamo(state: SessionState):
    """PreToolUse: deny `abrir_reclamo` unless the state clears all block reasons."""

    async def guard(hook_input: Any, tool_use_id: str | None, context: Any) -> dict[str, Any]:
        motivos = state.motivos_bloqueo()
        if not motivos:
            return {}
        reason = " ".join(motivos) + " Escala a un ajustador."
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }

    return guard


def make_force_priority_on_injuries(state: SessionState):
    """PreToolUse: force `priority="alta"` on `escalar_a_ajustador` when injuries exist (rule 3)."""

    async def force(hook_input: Any, tool_use_id: str | None, context: Any) -> dict[str, Any]:
        if not state.injuries_reported:
            return {}
        tool_input = _field(hook_input, "tool_input") or {}
        handoff = tool_input.get("handoff")
        if not isinstance(handoff, dict) or handoff.get("priority") == "alta":
            return {}
        updated_input = dict(tool_input)
        updated_input["handoff"] = {**handoff, "priority": "alta"}
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "updatedInput": updated_input,
            }
        }

    return force


def build_hooks(state: SessionState) -> dict[str, list[HookMatcher]]:
    """Wire the hooks for one session, closing over `state`."""
    return {
        "PostToolUse": [HookMatcher(matcher=None, hooks=[make_post_tool_use(state)])],
        "PreToolUse": [
            HookMatcher(
                matcher="mcp__cordillera__abrir_reclamo",
                hooks=[make_guard_abrir_reclamo(state)],
            ),
            HookMatcher(
                matcher="mcp__cordillera__escalar_a_ajustador",
                hooks=[make_force_priority_on_injuries(state)],
            ),
        ],
    }
