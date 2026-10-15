"""In-memory server state: identity verifications and opened claims/escalations.

Defense in depth for rule 1 (spec #005): the simulated core "remembers" which
insured documents were verified this session, so `open_claim` can refuse an
unverified insured even if the SDK hook (#7) were bypassed. State lives in the
long-running stdio server process; tests inject fresh instances to stay isolated.
"""


class VerificationRegistry:
    """Tracks which insured documents were verified in this session."""

    def __init__(self) -> None:
        self._verified: set[str] = set()

    def mark_verified(self, document: str) -> None:
        self._verified.add(document)

    def is_verified(self, document: str) -> bool:
        return document in self._verified

    def reset(self) -> None:
        self._verified.clear()


class ClaimStore:
    """Stores opened claims and escalations, assigning sequential ids."""

    def __init__(self) -> None:
        self._claims: list[dict] = []
        self._escalations: list[dict] = []

    def open(self, insured_id: str, policy_number: str | None, triage: object) -> str:
        claim_id = f"RCL-{len(self._claims) + 1:04d}"
        self._claims.append(
            {
                "claim_id": claim_id,
                "insured_id": insured_id,
                "policy_number": policy_number,
                "triage": triage,
            }
        )
        return claim_id

    def escalate(self, handoff: object) -> str:
        escalation_id = f"ESC-{len(self._escalations) + 1:04d}"
        self._escalations.append({"escalation_id": escalation_id, "handoff": handoff})
        return escalation_id

    def reset(self) -> None:
        self._claims.clear()
        self._escalations.clear()


# Module-level singletons: process state for the running MCP server.
verification_registry = VerificationRegistry()
claim_store = ClaimStore()
