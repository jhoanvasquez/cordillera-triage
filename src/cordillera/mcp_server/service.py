"""Pure business logic for the MCP tools.

Separated from the FastMCP layer (`server.py`) so it can be tested without
starting the server. Functions accept data as parameters (injectable in tests)
and fall back to loading from fixtures when not provided.
"""

from typing import Literal

from . import loader
from .errors import ErrorCategory, error_info
from .models import (
    CoverageDetail,
    CoverageResponse,
    InsuredSummary,
    PolicyDetail,
    PolicyResponse,
    SearchResponse,
    VerificationResponse,
)

# Reserved record used to simulate a transient failure (see fixtures #1, case #7).
FLAKY_DOCUMENT = "DOC-FIC-9999"

SearchField = Literal["documento", "nombre", "placa"]


def _matches(
    insured: list[dict], vehicles: list[dict], query: str, by: SearchField | None
) -> list[dict]:
    q = query.lower()
    if by == "documento":
        return [a for a in insured if a["document"] == query]
    if by == "nombre":
        return [a for a in insured if q in a["name"].lower()]
    if by == "placa":
        ids = {v["insured_id"] for v in vehicles if v["plate"] == query}
        return [a for a in insured if a["id"] in ids]

    # No `by`: try document, name, and plate; deduplicate by id preserving order.
    by_id = {a["id"]: a for a in insured}
    found: dict[str, dict] = {}
    for a in insured:
        if a["document"] == query or q in a["name"].lower():
            found[a["id"]] = a
    for v in vehicles:
        if v["plate"] == query and v["insured_id"] in by_id:
            found[v["insured_id"]] = by_id[v["insured_id"]]
    return list(found.values())


def search_insured(
    query: str,
    by: SearchField | None = None,
    *,
    insured: list[dict] | None = None,
    vehicles: list[dict] | None = None,
) -> SearchResponse:
    """Search insured persons by document, name, or plate. May return multiple matches."""
    insured = insured if insured is not None else loader.load_insured()
    vehicles = vehicles if vehicles is not None else loader.load_vehicles()

    if not query or not query.strip():
        return SearchResponse(
            ok=False,
            error=error_info(
                ErrorCategory.VALIDATION, "El criterio de búsqueda no puede estar vacío."
            ),
        )
    query = query.strip()

    if query == FLAKY_DOCUMENT:
        return SearchResponse(
            ok=False,
            error=error_info(
                ErrorCategory.TRANSIENT,
                "Tiempo de espera agotado consultando el core de la aseguradora.",
            ),
        )

    matches = _matches(insured, vehicles, query, by)
    results = [InsuredSummary(id=a["id"], document=a["document"], name=a["name"]) for a in matches]
    return SearchResponse(ok=True, results=results, resultCount=len(results))


def verify_identity(
    document: str,
    birth_date: str,
    *,
    insured: list[dict] | None = None,
) -> VerificationResponse:
    """Confirm identity with a second data point. Only reports; rule 1 is applied by the hook."""
    insured = insured if insured is not None else loader.load_insured()

    if not document or not birth_date:
        return VerificationResponse(
            ok=False,
            error=error_info(
                ErrorCategory.VALIDATION, "Documento y fecha de nacimiento son obligatorios."
            ),
        )

    if document == FLAKY_DOCUMENT:
        return VerificationResponse(
            ok=False,
            error=error_info(
                ErrorCategory.TRANSIENT,
                "Tiempo de espera agotado consultando el core de la aseguradora.",
            ),
        )

    record = next((a for a in insured if a["document"] == document), None)
    if record is None:
        return VerificationResponse(
            ok=False,
            error=error_info(ErrorCategory.BUSINESS, "No existe un asegurado con ese documento."),
        )

    verified = record["birth_date"] == birth_date
    return VerificationResponse(
        ok=True,
        verified=verified,
        insured_id=record["id"] if verified else None,
    )


def get_policy(
    plate: str,
    *,
    vehicles: list[dict] | None = None,
    policies: list[dict] | None = None,
) -> PolicyResponse:
    """Return the full policy for the vehicle identified by plate."""
    vehicles = vehicles if vehicles is not None else loader.load_vehicles()
    policies = policies if policies is not None else loader.load_policies()

    if not plate or not plate.strip():
        return PolicyResponse(
            ok=False,
            error=error_info(ErrorCategory.VALIDATION, "La placa no puede estar vacía."),
        )
    plate = plate.strip()

    veh = next((v for v in vehicles if v["plate"] == plate), None)
    if veh is None:
        return PolicyResponse(ok=True, policy=None)  # empty result, not an error

    pol = next((p for p in policies if p["id"] == veh["policy_id"]), None)
    if pol is None:
        return PolicyResponse(ok=True, policy=None)

    policy = PolicyDetail(
        id=pol["id"],
        number=pol["number"],
        insured_id=pol["insured_id"],
        vehicle_id=pol["vehicle_id"],
        valid_from=pol["valid_from"],
        valid_to=pol["valid_to"],
        deductible=pol["deductible"],
        coverages=[CoverageDetail(**c) for c in pol["coverages"]],
    )
    return PolicyResponse(ok=True, policy=policy)


def check_coverage(
    policy_number: str,
    coverage_type: str,
    date: str,
    *,
    policies: list[dict] | None = None,
) -> CoverageResponse:
    """Answer whether the incident type is covered by the policy on the given date."""
    policies = policies if policies is not None else loader.load_policies()

    if not policy_number or not coverage_type or not date:
        return CoverageResponse(
            ok=False,
            error=error_info(
                ErrorCategory.VALIDATION, "numero_poliza, tipo y fecha son obligatorios."
            ),
        )

    pol = next((p for p in policies if p["number"] == policy_number), None)
    if pol is None:
        # Querying a non-existent policy is not "empty": it is an error (FR-009).
        return CoverageResponse(
            ok=False,
            error=error_info(ErrorCategory.BUSINESS, "No existe una póliza con ese número."),
        )

    # Policy validity takes precedence over coverage status.
    if not (pol["valid_from"] <= date <= pol["valid_to"]):
        return CoverageResponse(
            ok=True,
            covered="no",
            reason="La póliza no estaba vigente en la fecha del siniestro.",
            deductible=pol["deductible"],
        )

    coverage = next((c for c in pol["coverages"] if c["type"] == coverage_type), None)
    if coverage is None:
        return CoverageResponse(
            ok=True,
            covered="no",
            reason=f"El amparo '{coverage_type}' no está contratado en la póliza.",
            deductible=pol["deductible"],
        )

    reason = coverage.get("conditions") or f"Amparo '{coverage_type}': {coverage['covered']}."
    return CoverageResponse(
        ok=True,
        covered=coverage["covered"],
        reason=reason,
        deductible=pol["deductible"],
    )
