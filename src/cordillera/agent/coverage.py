"""Coverage review: the verdict schema, its parser, and the `revisor-cobertura` subagent.

The subagent (an SDK `AgentDefinition`) reviews whether the incident is covered and
returns a structured verdict. Its tools are restricted to the two coverage tools —
it cannot open claims or escalate. At runtime the main agent reads the verdict and,
on `incierto`, escalates (rule 5 — a prompt judgment, as decided in #7).

Field names are English, domain values Spanish (Principle VI). Mapping to issue #8:
`cubierto→covered`, `amparo→coverage_type`, `grua_cubierta→tow_covered`, `motivo→reason`.
"""

import json
from typing import Any, Literal

from claude_agent_sdk import AgentDefinition
from pydantic import BaseModel

from .prompt import load_coverage_reviewer_prompt

COVERAGE_TOOLS = [
    "mcp__cordillera__consultar_poliza",
    "mcp__cordillera__verificar_cobertura",
]


class CoverageVerdict(BaseModel):
    """Structured coverage verdict produced by `revisor-cobertura`.

    What the review does not establish stays None; `incierto` is a first-class value.
    """

    covered: Literal["si", "no", "incierto"]
    coverage_type: str | None = None
    deductible: int | None = None
    tow_covered: bool | None = None
    reason: str | None = None


def parse_coverage_verdict(text: str | dict[str, Any]) -> CoverageVerdict:
    """Validate a coverage verdict (JSON text or dict) into a `CoverageVerdict`.

    Invalid input raises (``ValidationError`` for a bad schema, ``ValueError`` for
    malformed JSON) — never a half-built verdict.
    """
    data = json.loads(text) if isinstance(text, str) else text
    return CoverageVerdict.model_validate(data)


_REVIEWER_DESCRIPTION = (
    "Revisa si el siniestro está cubierto por la póliza y devuelve un veredicto "
    "estructurado. Úsalo antes de abrir un reclamo o ante dudas de cobertura "
    "(por ejemplo, la grúa)."
)


def build_coverage_reviewer() -> AgentDefinition:
    """Build the `revisor-cobertura` subagent: coverage tools only, versioned prompt."""
    return AgentDefinition(
        description=_REVIEWER_DESCRIPTION,
        prompt=load_coverage_reviewer_prompt(),
        tools=list(COVERAGE_TOOLS),
        model="inherit",
    )
