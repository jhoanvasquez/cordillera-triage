"""Console chat interface for the triage agent.

Renders the conversation turn by turn and makes claim/escalation actions evident,
so someone who does not know the code can follow what happened (brief behavior #11).
Rendering is pure (testable without the model or a terminal); `run_chat` is the thin
I/O loop that runs the agent (#6) once per insured message.

Claim and escalation events are read from `SessionState`, which the PostToolUse hooks
(#7) populate from tool results — never from the model's text (Principle I). The chat
only presents; it does not reimplement any rule.

User-facing labels are Spanish (the insured-facing contract); code is English (VI).
"""

from __future__ import annotations

import asyncio
import sys
from collections.abc import Callable, Iterable

from claude_agent_sdk import ClaudeSDKClient, ClaudeSDKError

from .core import build_options, consume
from .state import SessionState

_EXIT_COMMANDS = {"salir", "exit", "quit"}


# --- pure rendering ---------------------------------------------------------


def render_insured(text: str) -> str:
    """Render an insured (user) turn."""
    return f"Asegurado: {text}"


def render_agent(text: str) -> str:
    """Render an agent turn, distinguishable from the insured."""
    return f"Agente: {text}"


def render_claim_opened(claim_id: str) -> str:
    """Render an evident 'claim opened' line, distinct from a chat turn."""
    return f"  ✓ Reclamo abierto #{claim_id}"


def render_escalation(escalation_id: str | None, priority: str | None) -> str:
    """Render an evident 'escalated' line with the (hook-forced) priority."""
    suffix = f" (#{escalation_id})" if escalation_id else ""
    return f"  ↑ Escalado a ajustador — prioridad {priority or '?'}{suffix}"


def new_event_lines(state: SessionState, rendered: set[str]) -> list[str]:
    """Return render lines for action events not shown yet; marks them in `rendered`."""
    lines: list[str] = []
    if state.claim_id and "claim" not in rendered:
        rendered.add("claim")
        lines.append(render_claim_opened(state.claim_id))
    if state.escalation_id and "escalation" not in rendered:
        rendered.add("escalation")
        lines.append(render_escalation(state.escalation_id, state.escalation_priority))
    return lines


# --- live loop (exercised end-to-end in #12) --------------------------------


async def run_chat(messages: Iterable[str], out: Callable[[str], None] = print) -> None:
    """Run the terminal chat: one agent turn per insured message.

    Keeps one `ClaudeSDKClient` and one `SessionState` for the whole session so the
    conversation context and the business-rule hooks (#7) persist across turns.
    """
    state = SessionState()
    options = build_options(state=state)
    rendered: set[str] = set()
    try:
        async with ClaudeSDKClient(options=options) as client:
            for raw in messages:
                message = raw.strip()
                if not message or message.lower() in _EXIT_COMMANDS:
                    break
                out(render_insured(message))
                await client.query(message)
                result = await consume(client.receive_response())
                if result.text:
                    out(render_agent(result.text))
                # Safe to read events now: the PostToolUse hooks run synchronously
                # while `consume` drains this turn's stream, so `state` already
                # reflects any claim/escalation by the time `consume` returns.
                for line in new_event_lines(state, rendered):
                    out(line)
    except ClaudeSDKError as exc:
        out(f"[error] no se pudo comunicar con el agente: {exc}")


def _stdin_lines() -> Iterable[str]:
    yield from sys.stdin


def main() -> None:
    print("Chat de triage de Cordillera. Escribí el reporte del siniestro (o 'salir').")
    asyncio.run(run_chat(_stdin_lines()))


if __name__ == "__main__":
    main()
