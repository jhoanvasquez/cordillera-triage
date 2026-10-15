"""Session state derived ONLY from tool results (constitution Principle I).

The state is populated by PostToolUse hooks that read tool *results* — never the
model's text. `motivos_bloqueo()` is a pure function over this state: it lists
the reasons a claim cannot be opened, so the PreToolUse guard is deterministic
and unit-testable without the model.

Field names are in English; domain values and block reasons are in Spanish
(Principles IV/VI). `motivos_bloqueo` keeps its Spanish name: it is the contract
named in issue #7.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from pydantic import ValidationError

from ..mcp_server.models import Triage

Coverage = Literal["si", "no", "incierto"]


@dataclass
class SessionState:
    """Facts accumulated from tool results during one agent run."""

    identity_verified: bool = False
    insured_id: str | None = None
    policy_number: str | None = None
    policy_valid_from: str | None = None
    policy_valid_to: str | None = None
    coverage: Coverage | None = None
    triage: Triage | None = None

    # --- recorders: called by PostToolUse hooks with the structured tool result ---

    def record_identity(self, resp: dict[str, Any]) -> None:
        """Mark identity verified only when the tool reports a positive match."""
        if resp.get("ok") and resp.get("verified") is True:
            self.identity_verified = True
            self.insured_id = resp.get("insured_id")

    def record_policy(self, resp: dict[str, Any]) -> None:
        """Store the consulted policy's number and validity window."""
        if not resp.get("ok"):
            return
        policy = resp.get("policy")
        if isinstance(policy, dict):
            self.policy_number = policy.get("number")
            self.policy_valid_from = policy.get("valid_from")
            self.policy_valid_to = policy.get("valid_to")

    def record_coverage(self, resp: dict[str, Any]) -> None:
        """Store the coverage verdict (si | no | incierto)."""
        if resp.get("ok") and resp.get("covered") is not None:
            self.coverage = resp.get("covered")

    def record_triage(self, resp: dict[str, Any]) -> None:
        """Store the validated triage; ignore an error envelope.

        `registrar_triage` (see agent/sdk_tools.py) returns either a raw
        `Triage.model_dump()` (success) or a raw `ErrorInfo` dict (failure),
        neither of which has an `ok` flag — so the `errorCategory` key is what
        discriminates an error envelope from a triage here.
        """
        if not isinstance(resp, dict) or "errorCategory" in resp:
            return
        try:
            self.triage = Triage.model_validate(resp)
        except ValidationError:
            return

    # --- derived facts ---

    @property
    def injuries_reported(self) -> bool:
        return bool(self.triage and self.triage.injuries_reported)

    def _policy_valid_on_incident_date(self) -> bool:
        date = self.triage.incident_date if self.triage else None
        if not date or not self.policy_valid_from or not self.policy_valid_to:
            return False
        # ISO date strings compare lexicographically, as in service.py.
        return self.policy_valid_from <= date <= self.policy_valid_to

    def motivos_bloqueo(self) -> list[str]:
        """Pure: reasons a claim cannot be opened. Empty list ⇒ it may be opened.

        Combines rules 1 (identity + policy in force), 2 (leve only) and the
        claim-blocking part of rule 3 (no injuries). Coverage only blocks when it
        is affirmatively "no" (a clearly-uncovered claim must never auto-open);
        the "incierto" judgment (rule 5) is left to the prompt, per the brief.
        """
        motivos: list[str] = []
        if not self.identity_verified:
            motivos.append("La identidad del asegurado no fue verificada.")
        if not self._policy_valid_on_incident_date():
            motivos.append("La póliza no estaba vigente en la fecha del siniestro.")
        severity = self.triage.severity if self.triage else None
        if severity != "leve":
            motivos.append("La severidad no es leve; requiere un ajustador humano.")
        if self.injuries_reported:
            motivos.append("Hay lesiones reportadas; requiere un ajustador humano.")
        if self.coverage == "no":
            motivos.append("La póliza no cubre el siniestro.")
        return motivos
