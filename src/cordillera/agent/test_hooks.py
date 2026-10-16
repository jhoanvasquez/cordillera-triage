"""Deterministic tests for the business-rule hooks — no LLM, no CLI (FR-007).

Covers: the session state populated from tool results, `motivos_bloqueo()` as a
pure function, the `guard_abrir_reclamo` and `force_priority_on_injuries` hooks
called directly, and the wiring into `build_options`.
"""

import asyncio

from .core import build_options
from .hooks import (
    build_hooks,
    extract_structured,
    make_force_priority_on_injuries,
    make_guard_abrir_reclamo,
    make_post_tool_use,
)
from .state import SessionState


def _complete_leve_state() -> SessionState:
    """A state that clears every block reason: a leve, injury-free, covered claim."""
    state = SessionState()
    state.record_identity({"ok": True, "verified": True, "insured_id": "INS-FIC-1"})
    state.record_policy(
        {
            "ok": True,
            "policy": {
                "number": "POL-FIC-1",
                "valid_from": "2026-01-01",
                "valid_to": "2026-12-31",
            },
        }
    )
    state.record_coverage({"ok": True, "covered": "si"})
    state.record_triage(
        {"severity": "leve", "incident_date": "2026-03-15", "injuries_reported": False}
    )
    return state


# --- US1: state from tool results -------------------------------------------


def test_extract_structured_handles_all_shapes():
    assert extract_structured({"structuredContent": {"ok": True, "covered": "si"}}) == {
        "ok": True,
        "covered": "si",
    }
    # registrar_triage: JSON text in a content block (no structuredContent)
    assert extract_structured({"content": [{"type": "text", "text": '{"severity": "leve"}'}]}) == {
        "severity": "leve"
    }
    assert extract_structured({"ok": True, "verified": True}) == {"ok": True, "verified": True}
    # The live CLI delivers MCP tool results as JSON strings (#12 finding).
    assert extract_structured('{"ok": true, "verified": true, "insured_id": "A-001"}') == {
        "ok": True,
        "verified": True,
        "insured_id": "A-001",
    }
    assert extract_structured("not json") == {}
    assert extract_structured(None) == {}


def test_recorders_populate_state_from_results():
    state = _complete_leve_state()
    assert state.identity_verified is True
    assert state.insured_id == "INS-FIC-1"
    assert state.policy_number == "POL-FIC-1"
    assert state.coverage == "si"
    assert state.triage is not None and state.triage.severity == "leve"


def test_recorders_ignore_negative_or_error_results():
    state = SessionState()
    state.record_identity({"ok": True, "verified": False})  # not a match
    state.record_coverage({"ok": False, "error": {"errorCategory": "transient"}})
    state.record_triage({"errorCategory": "validation", "description": "bad severity"})
    assert state.identity_verified is False
    assert state.coverage is None
    assert state.triage is None


def test_record_coverage_stores_each_verdict():
    for verdict in ("si", "no", "incierto"):
        state = SessionState()
        state.record_coverage({"ok": True, "covered": verdict})
        assert state.coverage == verdict


# --- US2: motivos_bloqueo (pure) + guard ------------------------------------


def test_motivos_bloqueo_empty_state_blocks_on_rules_1_and_2():
    # Coverage None does NOT block (rule 5 is a prompt judgment); rules 1/2 do.
    motivos = SessionState().motivos_bloqueo()
    assert any("identidad" in m for m in motivos)
    assert any("vigente" in m for m in motivos)
    assert any("severidad" in m.lower() for m in motivos)
    assert not any("cubre" in m for m in motivos)


def test_motivos_bloqueo_complete_leve_state_is_empty():
    assert _complete_leve_state().motivos_bloqueo() == []


def test_motivos_bloqueo_blocks_on_each_single_condition():
    # severity moderada
    s = _complete_leve_state()
    s.triage.severity = "moderada"
    assert any("severidad" in m.lower() for m in s.motivos_bloqueo())
    # injuries
    s = _complete_leve_state()
    s.triage.injuries_reported = True
    assert any("lesiones" in m.lower() for m in s.motivos_bloqueo())
    # coverage affirmatively "no" blocks
    s = _complete_leve_state()
    s.coverage = "no"
    assert any("cubre" in m for m in s.motivos_bloqueo())
    # policy out of date range
    s = _complete_leve_state()
    s.triage.incident_date = "2027-01-01"
    assert any("vigente" in m for m in s.motivos_bloqueo())


def test_motivos_bloqueo_coverage_none_or_incierto_does_not_block():
    # The leve auto-open case must open even if verificar_cobertura was not run
    # (coverage None); rule 5 ("incierto" → escalate) stays a prompt judgment.
    for coverage in (None, "incierto"):
        s = _complete_leve_state()
        s.coverage = coverage
        assert s.motivos_bloqueo() == []


def test_guard_denies_without_identity():
    state = SessionState()  # nothing verified
    guard = make_guard_abrir_reclamo(state)
    out = asyncio.run(guard({"tool_name": "mcp__cordillera__abrir_reclamo"}, None, None))
    hso = out["hookSpecificOutput"]
    assert hso["permissionDecision"] == "deny"
    assert "identidad" in hso["permissionDecisionReason"]
    assert "scala" in hso["permissionDecisionReason"]  # "Escala a un ajustador."


def test_guard_allows_complete_leve_state():
    guard = make_guard_abrir_reclamo(_complete_leve_state())
    out = asyncio.run(guard({"tool_name": "mcp__cordillera__abrir_reclamo"}, None, None))
    assert out == {}


# --- US3: force priority on injuries ----------------------------------------


def test_force_priority_overrides_to_alta_when_injuries():
    state = _complete_leve_state()
    state.triage.injuries_reported = True
    force = make_force_priority_on_injuries(state)
    hook_input = {
        "tool_name": "mcp__cordillera__escalar_a_ajustador",
        "tool_input": {"handoff": {"priority": "media", "insured_id": "INS-FIC-1"}},
    }
    out = asyncio.run(force(hook_input, None, None))
    updated = out["hookSpecificOutput"]["updatedInput"]
    assert updated["handoff"]["priority"] == "alta"
    assert out["hookSpecificOutput"]["permissionDecision"] == "allow"


def test_force_priority_noop_without_injuries():
    state = _complete_leve_state()  # injuries_reported False
    force = make_force_priority_on_injuries(state)
    hook_input = {"tool_input": {"handoff": {"priority": "media"}}}
    out = asyncio.run(force(hook_input, None, None))
    assert out == {}


def test_force_priority_sets_alta_when_priority_missing():
    # Deterministic even if the model omitted the priority field entirely.
    state = _complete_leve_state()
    state.triage.injuries_reported = True
    force = make_force_priority_on_injuries(state)
    hook_input = {"tool_input": {"handoff": {"insured_id": "INS-FIC-1"}}}
    out = asyncio.run(force(hook_input, None, None))
    assert out["hookSpecificOutput"]["updatedInput"]["handoff"]["priority"] == "alta"


# --- wiring -----------------------------------------------------------------


def test_build_hooks_registers_expected_matchers():
    hooks = build_hooks(SessionState())
    assert "PostToolUse" in hooks and "PreToolUse" in hooks
    pre_matchers = [m.matcher for m in hooks["PreToolUse"]]
    assert "mcp__cordillera__abrir_reclamo" in pre_matchers
    assert "mcp__cordillera__escalar_a_ajustador" in pre_matchers


def test_build_options_attaches_hooks_only_with_state():
    with_state = build_options(state=SessionState())
    assert with_state.hooks is not None
    assert "PreToolUse" in with_state.hooks
    without_state = build_options()
    assert not without_state.hooks  # #6 behavior unchanged (no hooks)


def test_post_tool_use_dispatches_by_tool_name():
    state = SessionState()
    record = make_post_tool_use(state)
    asyncio.run(
        record(
            {
                "tool_name": "mcp__cordillera__verificar_identidad",
                "tool_response": {
                    "structuredContent": {"ok": True, "verified": True, "insured_id": "X"}
                },
            },
            None,
            None,
        )
    )
    assert state.identity_verified is True and state.insured_id == "X"
