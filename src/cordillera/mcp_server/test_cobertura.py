"""Tests for `consultar_poliza` and `verificar_cobertura` (pure logic + descriptions)."""

import asyncio

from cordillera.mcp_server import server, service

DATE = "2026-10-10"


# --- US1: consultar_poliza ---


def test_get_policy_by_plate():
    r = service.get_policy("FIC-01A")
    assert r.ok is True
    assert r.policy is not None
    assert r.policy.number == "POL-FIC-0001"
    assert any(c.type == "grua" and c.covered == "si" for c in r.policy.coverages)


def test_get_policy_unknown_plate_is_empty():
    r = service.get_policy("FIC-99Z")
    assert r.ok is True
    assert r.policy is None
    assert r.error is None


# --- US2: verificar_cobertura ---


def test_towing_coverage_yes():
    r = service.check_coverage("POL-FIC-0001", "grua", DATE)
    assert r.ok is True
    assert r.covered == "si"


def test_uncertain_coverage_by_use():
    r = service.check_coverage("POL-FIC-0005", "danos", DATE)
    assert r.ok is True
    assert r.covered == "incierto"
    assert "domicilio" in r.reason.lower() or "reparto" in r.reason.lower()


def test_expired_policy_coverage_is_no():
    r = service.check_coverage("POL-FIC-0004", "danos", DATE)
    assert r.ok is True
    assert r.covered == "no"
    assert "vigente" in r.reason.lower()


def test_uncovered_incident_type_is_no():
    r = service.check_coverage("POL-FIC-0002", "grua", DATE)
    assert r.ok is True
    assert r.covered == "no"


def test_unknown_policy_is_business_error():
    r = service.check_coverage("POL-FIC-0000", "danos", DATE)
    assert r.ok is False
    assert r.error.errorCategory.value == "business"


# --- US3: distinct descriptions (behavior #3) ---


def test_distinct_descriptions_and_multivehicle_guidance():
    tools = {h.name: h for h in asyncio.run(server.mcp.list_tools())}
    d_policy = tools["consultar_poliza"].description
    d_coverage = tools["verificar_cobertura"].description
    assert d_policy != d_coverage
    assert "pregunta" in d_policy.lower()
    assert "veh" in d_policy.lower()
