"""Pydantic input/output models for the MCP tools.

Domain field names are in English; the technical envelope (`ok`, `error`,
`resultCount`) stays in English per the constitution (Principle IV/VI).
"""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from .errors import ErrorInfo


class InsuredSummary(BaseModel):
    """Public summary of an insured person. Does NOT include `birth_date`:

    that is the secret verification field and must not leak through search.
    """

    id: str
    document: str
    name: str


class SearchResponse(BaseModel):
    """Result of `buscar_asegurado`. A search with no results is `ok=True`."""

    ok: bool
    results: list[InsuredSummary] = []
    resultCount: int = 0
    error: ErrorInfo | None = None


class VerificationResponse(BaseModel):
    """Result of `verificar_identidad`. `verified` only reports; it does not decide."""

    ok: bool
    verified: bool | None = None
    insured_id: str | None = None
    error: ErrorInfo | None = None


class CoverageDetail(BaseModel):
    """Coverage item contracted within a policy."""

    type: str
    covered: Literal["si", "no", "incierto"]
    conditions: str = ""


class PolicyDetail(BaseModel):
    """Full policy for a vehicle: validity period, coverages, and deductible."""

    id: str
    number: str
    insured_id: str
    vehicle_id: str
    valid_from: str
    valid_to: str
    deductible: int
    coverages: list[CoverageDetail] = []


class PolicyResponse(BaseModel):
    """Result of `consultar_poliza`. A vehicle without a policy is `ok=True` with `policy=None`."""

    ok: bool
    policy: PolicyDetail | None = None
    error: ErrorInfo | None = None


class CoverageResponse(BaseModel):
    """Result of `verificar_cobertura`. `covered` only reports; it does not decide escalation."""

    ok: bool
    covered: Literal["si", "no", "incierto"] | None = None
    reason: str | None = None
    deductible: int | None = None
    error: ErrorInfo | None = None


class ThirdParties(BaseModel):
    """Third parties involved in the incident."""

    present: bool | None = None
    identified: bool | None = None
    description: str | None = None


class Triage(BaseModel):
    """Structured triage of the incident. Canonical owner: feature #5.

    Fields the report does not mention stay None; the agent must not invent them.
    """

    claim_type: str | None = None
    severity: Literal["leve", "moderada", "grave"] | None = None
    injuries_reported: bool | None = None
    injury_description: str | None = None
    third_parties: ThirdParties = Field(default_factory=ThirdParties)
    incident_date: str | None = None
    referenced_vehicle: str | None = None
    message_topics: list[str] = []
    missing_data: list[str] = []


class EscalationCause(str, Enum):
    """Why a case is escalated to a human adjuster (domain values, Spanish)."""

    SOLICITUD_ASEGURADO = "solicitud_asegurado"
    SEVERIDAD = "severidad"
    LESIONES = "lesiones"
    COBERTURA_INCIERTA = "cobertura_incierta"
    FALLA_TECNICA = "falla_tecnica"


class Handoff(BaseModel):
    """Structured summary for a human adjuster with no access to the conversation."""

    insured_id: str
    policy_number: str | None = None
    triage: Triage
    actions_taken: list[str] = []
    escalation_cause: EscalationCause
    priority: Literal["alta", "media", "baja"]
    recommended_action: str


class ClaimResponse(BaseModel):
    """Result of `abrir_reclamo`."""

    ok: bool
    claim_id: str | None = None
    error: ErrorInfo | None = None


class EscalationResponse(BaseModel):
    """Result of `escalar_a_ajustador`."""

    ok: bool
    escalation_id: str | None = None
    priority: str | None = None
    error: ErrorInfo | None = None
