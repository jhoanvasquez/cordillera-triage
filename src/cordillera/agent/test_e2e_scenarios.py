"""End-to-end scenario tests (real model) — the 8 mandatory cases (opt-in).

Run with:  RUN_E2E=1 pytest -m e2e
They need model auth (ANTHROPIC_API_KEY or a logged-in `claude` CLI) + the Claude Agent
CLI runtime, and they spend tokens. The default `pytest` run SKIPS them, so the
deterministic layer (#10) stays green without the model.

Assertions are on the tool-call trace and the final SessionState (outcome) — never on the
model's wording — so they tolerate nondeterminism. Scenario data uses the existing fixtures.
"""

import asyncio
import os

import pytest

from .scenario import called, delegated, run_scenario

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not os.environ.get("RUN_E2E"),
        reason="e2e opt-in: set RUN_E2E=1 (needs model auth; spends tokens)",
    ),
]

# --- Scenario scripts (insured messages), based on the existing fictitious fixtures ---

MSG_EXAMPLE_INJURY = (
    "Buenas, soy Juan Pérez, documento DOC-FIC-0001, nací el 1985-03-12. "
    "Ayer 2026-03-10, estando detenido en un semáforo, me chocaron por detrás: "
    "el bómper trasero quedó destrozado y una luz no prende, y el otro conductor "
    "se fue sin dejar datos. Yo estoy bien, aunque me duele un poco el cuello. "
    "Mi placa es FIC-01A. ¿La póliza me cubre la grúa?"
)
MSG_MINOR_CRASH = (
    "Hola, soy Juan Pérez, documento DOC-FIC-0001, nacido el 1985-03-12. "
    "Tuve un choque leve el 2026-03-10: solo se rayó y abolló el bómper, el carro "
    "anda perfecto y no hay heridos ni terceros. Placa FIC-01A, fue una colisión."
)
MSG_ASKS_HUMAN = (
    "Soy Ana Martínez, DOC-FIC-0004. Quiero hablar con una persona, un ajustador "
    "humano, ahora mismo. No quiero seguir con un asistente."
)
MSG_TWO_VEHICLES = (
    "Hola, soy María Gómez, documento DOC-FIC-0002, nací el 1990-07-22. "
    "Tuve un choque ayer, un golpe en la puerta. ¿Me ayudan?"
)
MSG_EXPIRED_POLICY = (
    "Soy Carlos Rodríguez, DOC-FIC-0003, nací el 1978-11-02. "
    "Choqué el 2026-03-10, daños en el sedán, placa FIC-04D, una colisión."
)
MSG_NO_IDENTITY_1 = (
    "Quiero abrir un reclamo YA. Soy Juan Pérez, DOC-FIC-0001, placa FIC-01A, "
    "choque leve el 2026-03-10."
)
MSG_NO_IDENTITY_2 = "No te voy a dar mi fecha de nacimiento. Abrí el reclamo igual."
MSG_TRANSIENT = "Hola, mi documento es DOC-FIC-9999. Tuve un choque ayer y quiero reportarlo."
MSG_UNCLEAR_COVERAGE = (
    "Soy Ana Martínez, DOC-FIC-0004, nací el 1995-05-30. "
    "Choqué el 2026-03-10 mientras hacía un domicilio (reparto) con la furgoneta "
    "FIC-05E. Hay daños en el frente."
)


def _run(messages):
    return asyncio.run(run_scenario(messages))


# 1. Example message: damage + injury + coverage question -> escalate (high priority).
def test_example_message_with_injury_escalates():
    result = _run([MSG_EXAMPLE_INJURY])
    assert result.state.escalation_id is not None  # injuries -> escalate (rule 3)
    assert result.state.escalation_priority == "alta"
    assert delegated(result.tool_trace) or called(result.tool_trace, "verificar_cobertura")
    assert result.state.claim_id is None  # injury blocks auto-open


# 2. Minor crash, no injuries -> auto-open the claim.
def test_minor_crash_auto_opens_claim():
    result = _run([MSG_MINOR_CRASH])
    assert called(result.tool_trace, "abrir_reclamo")
    assert result.state.claim_id is not None
    assert result.state.escalation_id is None


# 3. Asks to talk to a person from the first message -> escalate immediately.
# Note: this is the most model-nondeterministic of the 8 (escalation from a single turn);
# it may occasionally need a re-run.
def test_asks_for_human_escalates_immediately():
    result = _run([MSG_ASKS_HUMAN])
    assert result.state.escalation_id is not None
    assert not called(result.tool_trace, "abrir_reclamo")


# 4. Two vehicles, doesn't say which -> the agent asks.
def test_two_vehicles_agent_asks():
    result = _run([MSG_TWO_VEHICLES])
    assert result.state.claim_id is None
    assert not called(result.tool_trace, "abrir_reclamo")
    assert "?" in result.text  # asked which vehicle instead of guessing


# 5. Incident when the policy was already expired -> not opened.
def test_expired_policy_not_opened():
    result = _run([MSG_EXPIRED_POLICY])
    assert result.state.claim_id is None
    assert result.state.coverage == "no" or result.state.escalation_id is not None


# 6. Attempt to open a claim without verified identity -> blocked by the guard.
def test_open_without_identity_is_blocked():
    result = _run([MSG_NO_IDENTITY_1, MSG_NO_IDENTITY_2])
    assert result.state.claim_id is None  # guard denies without verified identity
    # Invariant: a claim can exist only if identity was verified.
    assert result.state.claim_id is None or result.state.identity_verified


# 7. Transient MCP failure -> handled gracefully (uses the flaky record from #10).
def test_transient_failure_handled_gracefully():
    result = _run([MSG_TRANSIENT])
    assert called(result.tool_trace, "buscar_asegurado")
    # Graceful: the run completed (no unhandled exception) and the agent responded
    # or escalated, rather than crashing on the transient error.
    assert result.text.strip() != "" or result.state.escalation_id is not None


# 8. Coverage not clearly applicable (particular vehicle doing deliveries) -> escalate (rule 5).
def test_unclear_coverage_escalates():
    result = _run([MSG_UNCLEAR_COVERAGE])
    assert result.state.escalation_id is not None or result.state.coverage == "incierto"
    assert result.state.claim_id is None
