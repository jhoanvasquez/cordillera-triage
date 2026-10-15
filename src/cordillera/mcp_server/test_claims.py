"""Tests for open_claim and escalate_to_adjuster (pure logic + in-memory state)."""

import pytest
from pydantic import ValidationError

from cordillera.mcp_server import service, state
from cordillera.mcp_server.models import EscalationCause, Handoff, Triage


def _fresh() -> tuple[state.VerificationRegistry, state.ClaimStore]:
    return state.VerificationRegistry(), state.ClaimStore()


def _triage(incident_date: str = "2026-10-10") -> Triage:
    return Triage(severity="leve", injuries_reported=False, incident_date=incident_date)


# --- US1 + US2: open_claim with rule-1 defense in depth ---


def test_open_claim_success():
    registry, store = _fresh()
    registry.mark_verified("DOC-FIC-0001")
    r = service.open_claim(
        "DOC-FIC-0001", "POL-FIC-0001", _triage(), registry=registry, store=store
    )
    assert r.ok is True
    assert r.claim_id and r.claim_id.startswith("RCL-")


def test_open_claim_blocked_without_identity():
    registry, store = _fresh()
    r = service.open_claim(
        "DOC-FIC-0001", "POL-FIC-0001", _triage(), registry=registry, store=store
    )
    assert r.ok is False
    assert r.error.errorCategory.value == "business"


def test_open_claim_blocked_when_policy_not_valid_on_date():
    registry, store = _fresh()
    registry.mark_verified("DOC-FIC-0003")
    # POL-FIC-0004 expired (valid_to 2025-01-01); incident on 2026-10-10.
    r = service.open_claim(
        "DOC-FIC-0003", "POL-FIC-0004", _triage("2026-10-10"), registry=registry, store=store
    )
    assert r.ok is False
    assert r.error.errorCategory.value == "business"
    assert "vigente" in r.error.description.lower()


def test_verify_identity_records_verification():
    registry = state.VerificationRegistry()
    service.verify_identity("DOC-FIC-0001", "1985-03-12", registry=registry)
    assert registry.is_verified("DOC-FIC-0001") is True

    other = state.VerificationRegistry()
    service.verify_identity("DOC-FIC-0001", "2000-01-01", registry=other)  # wrong date
    assert other.is_verified("DOC-FIC-0001") is False


# --- US3: escalate_to_adjuster ---


def test_escalate_success():
    _, store = _fresh()
    handoff = Handoff(
        insured_id="A-001",
        policy_number="POL-FIC-0001",
        triage=_triage(),
        actions_taken=["verified identity", "checked coverage"],
        escalation_cause=EscalationCause.LESIONES,
        priority="alta",
        recommended_action="Contactar al asegurado y asignar perito.",
    )
    r = service.escalate_to_adjuster(handoff, store=store)
    assert r.ok is True
    assert r.escalation_id and r.escalation_id.startswith("ESC-")
    assert r.priority == "alta"


def test_handoff_rejects_invalid_escalation_cause():
    with pytest.raises(ValidationError):
        Handoff(
            insured_id="A-001",
            triage=_triage(),
            escalation_cause="motivo_invalido",  # not in the enum
            priority="alta",
            recommended_action="x",
        )
