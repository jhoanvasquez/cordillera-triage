"""Pydantic input/output models for the MCP tools.

Domain field names are in English; the technical envelope (`ok`, `error`,
`resultCount`) stays in English per the constitution (Principle IV/VI).
"""

from typing import Literal

from pydantic import BaseModel

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
