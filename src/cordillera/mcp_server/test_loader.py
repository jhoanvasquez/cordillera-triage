"""Tests for the fixture loader."""

from cordillera.mcp_server import loader


def test_expected_counts():
    assert len(loader.load_insured()) == 6
    assert len(loader.load_vehicles()) == 6
    assert len(loader.load_policies()) == 6


def test_insured_have_required_fields():
    for a in loader.load_insured():
        assert {"id", "document", "name", "birth_date"} <= a.keys()
