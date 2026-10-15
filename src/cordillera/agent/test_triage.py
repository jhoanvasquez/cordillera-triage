"""Tests for the triage schema contract and registrar_triage."""

import pytest
from pydantic import ValidationError

from cordillera.agent.triage import registrar_triage
from cordillera.mcp_server.models import Triage

# --- US1: schema contract ---


def test_unmentioned_fields_stay_none():
    t = Triage(severity="leve", incident_date="2026-10-10")
    assert t.claim_type is None
    assert t.injuries_reported is None
    assert t.third_parties.present is None
    assert t.message_topics == []
    assert t.missing_data == []


def test_invalid_severity_is_rejected():
    with pytest.raises(ValidationError):
        Triage(severity="gravisima")


def test_claim_type_is_free_text():
    # Not enumerated in the brief: any string is accepted.
    t = Triage(claim_type="colision por alcance")
    assert t.claim_type == "colision por alcance"


def test_missing_data_list():
    t = Triage(missing_data=["fecha del siniestro", "vehiculo"])
    assert t.missing_data == ["fecha del siniestro", "vehiculo"]


# --- US2: registrar_triage ---


def test_registrar_triage_valid():
    r = registrar_triage(
        {"severity": "leve", "injuries_reported": False, "incident_date": "2026-10-10"}
    )
    assert r.ok is True
    assert isinstance(r.triage, Triage)
    assert r.triage.severity == "leve"


def test_registrar_triage_invalid_severity():
    r = registrar_triage({"severity": "muy grave"})
    assert r.ok is False
    assert r.error.errorCategory.value == "validation"
    assert r.triage is None
