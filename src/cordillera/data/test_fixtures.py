"""Deterministic fixture tests: fictional formats, integrity, and coverage.

No model or server required: validates data only (requirement #3 of the spec).
"""

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent
INCIDENT_DATE = "2026-10-10"  # reference date for the scenario (see plan.md)


def _load(name: str) -> list[dict]:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


INSURED = _load("insured.json")
VEHICLES = _load("vehicles.json")
POLICIES = _load("policies.json")


def _policy_active(policy: dict, date: str) -> bool:
    return policy["valid_from"] <= date <= policy["valid_to"]


# --- User story 1: integrity and coverage of the 8 cases ---


def test_referential_integrity():
    insured_ids = {a["id"] for a in INSURED}
    vehicle_ids = {v["id"] for v in VEHICLES}
    policy_ids = {p["id"] for p in POLICIES}
    for v in VEHICLES:
        assert v["insured_id"] in insured_ids, v
        assert v["policy_id"] in policy_ids, v
    for p in POLICIES:
        assert p["insured_id"] in insured_ids, p
        assert p["vehicle_id"] in vehicle_ids, p


def test_coverage_cases():
    # Cases 1 and 2: A-001 with active policy and towing coverage.
    p1 = next(p for p in POLICIES if p["insured_id"] == "A-001")
    assert _policy_active(p1, INCIDENT_DATE)
    assert any(c["type"] == "grua" and c["covered"] == "si" for c in p1["coverages"])

    # Case 4: A-002 with two vehicles, both with active policies.
    veh_a2 = [v for v in VEHICLES if v["insured_id"] == "A-002"]
    assert len(veh_a2) == 2
    for v in veh_a2:
        p = next(p for p in POLICIES if p["id"] == v["policy_id"])
        assert _policy_active(p, INCIDENT_DATE)

    # Case 5: A-003 with expired policy on the incident date.
    p_a3 = next(p for p in POLICIES if p["insured_id"] == "A-003")
    assert not _policy_active(p_a3, INCIDENT_DATE)

    # Case 8: A-004 personal use with uncertain coverage (delivery services).
    v_a4 = next(v for v in VEHICLES if v["insured_id"] == "A-004")
    assert v_a4["use"] == "particular"
    p_a4 = next(p for p in POLICIES if p["insured_id"] == "A-004")
    assert any(c["covered"] == "incierto" for c in p_a4["coverages"])


# --- User story 2: unambiguously fictional data ---

RE_DOC = re.compile(r"^DOC-FIC-\d{4}$")
RE_PLATE = re.compile(r"^FIC-\d{2}[A-Z]$")
RE_POL = re.compile(r"^POL-FIC-\d{4}$")


def test_fictional_formats():
    for a in INSURED:
        assert RE_DOC.match(a["document"]), a["document"]
    for v in VEHICLES:
        assert RE_PLATE.match(v["plate"]), v["plate"]
    for p in POLICIES:
        assert RE_POL.match(p["number"]), p["number"]


# Real Colombian formats that NO value may have.
RE_REAL_ID = re.compile(r"\b\d{8,10}\b")
RE_REAL_PLATE = re.compile(r"\b[A-Z]{3}\d{3}\b")


def test_no_real_data():
    for name in ("insured.json", "vehicles.json", "policies.json"):
        text = (DATA_DIR / name).read_text(encoding="utf-8")
        assert not RE_REAL_ID.search(text), f"possible real ID number in {name}"
        assert not RE_REAL_PLATE.search(text), f"possible real plate in {name}"


# --- User story 3: search and identity verification ---


def test_multiple_matches():
    marias = [a for a in INSURED if a["name"] == "María Gómez"]
    assert len(marias) >= 2
    assert len({a["document"] for a in marias}) == len(marias)


def test_second_identity_field():
    for a in INSURED:
        assert a.get("birth_date")


# --- User story 4: transient failure ---


def test_flaky_record_present():
    flaky = [a for a in INSURED if a["document"] == "DOC-FIC-9999"]
    assert len(flaky) == 1
    assert flaky[0].get("flaky") is True
