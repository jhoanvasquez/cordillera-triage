"""Deterministic tests for the console chat interface — no LLM, no terminal (FR-007).

Covers the pure renderer, the claim/escalation recorders and their PostToolUse
dispatch, and the new-event selection. The live loop (stdin + model) is #12.
"""

import asyncio

from . import chat
from .chat import (
    new_event_lines,
    render_agent,
    render_claim_opened,
    render_escalation,
    render_insured,
)
from .hooks import make_post_tool_use
from .state import SessionState

# --- US1: turn rendering ----------------------------------------------------


def test_insured_and_agent_turns_are_distinguishable():
    insured = render_insured("me chocaron por detrás")
    agent = render_agent("Entiendo, ¿me confirma su documento?")
    assert "Asegurado" in insured
    assert "Agente" in agent
    assert insured != agent
    assert "me chocaron por detrás" in insured


# --- US2: evident action events ---------------------------------------------


def test_render_claim_opened_shows_id_and_is_evident():
    line = render_claim_opened("CLM-FIC-001")
    assert "CLM-FIC-001" in line
    assert "Reclamo abierto" in line
    assert line != render_agent("CLM-FIC-001")  # not a plain chat turn


def test_render_escalation_shows_priority():
    line = render_escalation("ESC-FIC-001", "alta")
    assert "alta" in line
    assert "Escalado" in line


def test_record_claim_and_escalation_from_results():
    state = SessionState()
    state.record_claim({"ok": True, "claim_id": "CLM-FIC-001"})
    state.record_escalation({"ok": True, "escalation_id": "ESC-FIC-001", "priority": "alta"})
    assert state.claim_id == "CLM-FIC-001"
    assert state.escalation_id == "ESC-FIC-001"
    assert state.escalation_priority == "alta"


def test_recorders_ignore_error_results():
    state = SessionState()
    state.record_claim({"ok": False, "error": {"errorCategory": "business"}})
    state.record_escalation({"ok": False})
    # ok=True but no id: nothing to record (guard on id, not just ok).
    state.record_claim({"ok": True})
    state.record_escalation({"ok": True, "priority": "alta"})
    assert state.claim_id is None
    assert state.escalation_id is None
    assert state.escalation_priority is None


def test_post_tool_use_dispatches_claim_and_escalation():
    state = SessionState()
    record = make_post_tool_use(state)
    asyncio.run(
        record(
            {
                "tool_name": "mcp__cordillera__abrir_reclamo",
                "tool_response": {"structuredContent": {"ok": True, "claim_id": "CLM-FIC-9"}},
            },
            None,
            None,
        )
    )
    asyncio.run(
        record(
            {
                "tool_name": "mcp__cordillera__escalar_a_ajustador",
                "tool_response": {
                    "structuredContent": {"ok": True, "escalation_id": "ESC-9", "priority": "alta"}
                },
            },
            None,
            None,
        )
    )
    assert state.claim_id == "CLM-FIC-9"
    assert state.escalation_id == "ESC-9"
    assert state.escalation_priority == "alta"


# --- US3: new-event selection + entry point ---------------------------------


def test_new_event_lines_emits_once():
    state = SessionState()
    rendered: set[str] = set()
    assert new_event_lines(state, rendered) == []  # nothing yet

    state.claim_id = "CLM-FIC-001"
    first = new_event_lines(state, rendered)
    assert len(first) == 1 and "CLM-FIC-001" in first[0]

    # Same state again: already rendered, nothing new.
    assert new_event_lines(state, rendered) == []


def test_chat_module_exposes_entry_point():
    assert callable(chat.run_chat)
    assert callable(chat.main)
