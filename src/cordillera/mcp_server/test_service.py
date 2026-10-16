"""Tests for the pure tool logic (without starting MCP)."""

from cordillera.mcp_server import service

# --- US1: locate the insured ---


def test_single_search_by_document():
    r = service.search_insured("DOC-FIC-0001", "documento")
    assert r.ok is True
    assert r.resultCount == 1
    assert r.results[0].document == "DOC-FIC-0001"


def test_summary_does_not_expose_birth_date():
    r = service.search_insured("DOC-FIC-0001", "documento")
    assert not hasattr(r.results[0], "birth_date")


def test_multiple_results_by_name():
    r = service.search_insured("María Gómez", "nombre")
    assert r.ok is True
    assert r.resultCount >= 2


def test_search_by_plate():
    r = service.search_insured("FIC-01A", "placa")
    assert r.ok is True
    assert r.resultCount == 1
    assert r.results[0].id == "A-001"


# --- US3: structured errors and empty results ---


def test_empty_result_is_not_an_error():
    r = service.search_insured("DOC-FIC-0000-INEXISTENTE", "documento")
    assert r.ok is True
    assert r.resultCount == 0
    assert r.error is None


def test_blank_query_is_validation_error():
    r = service.search_insured("   ", None)
    assert r.ok is False
    assert r.error.errorCategory.value == "validation"
    assert r.error.isRetryable is False


def test_flaky_record_is_transient_error():
    r = service.search_insured("DOC-FIC-9999", "documento")
    assert r.ok is False
    assert r.error.errorCategory.value == "transient"
    assert r.error.isRetryable is True


# --- US2: verify identity ---


def test_correct_identity():
    r = service.verify_identity("DOC-FIC-0001", "1985-03-12")
    assert r.ok is True
    assert r.verified is True
    assert r.insured_id == "A-001"


def test_incorrect_identity():
    r = service.verify_identity("DOC-FIC-0001", "2000-01-01")
    assert r.ok is True
    assert r.verified is False
    assert r.insured_id is None


def test_identity_unknown_document():
    r = service.verify_identity("DOC-FIC-7777", "1985-03-12")
    assert r.ok is False
    assert r.error.errorCategory.value == "business"


def test_identity_flaky_record_is_transient_error():
    # The transient-fault injection (flaky record) also surfaces on verify_identity:
    # a transient error that is retryable (feeds the #12 transient-failure case).
    r = service.verify_identity("DOC-FIC-9999", "2000-01-01")
    assert r.ok is False
    assert r.error.errorCategory.value == "transient"
    assert r.error.isRetryable is True
