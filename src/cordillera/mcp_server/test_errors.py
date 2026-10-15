"""Tests for the error envelope."""

from cordillera.mcp_server.errors import ErrorCategory, error_info


def test_transient_is_retryable():
    e = error_info(ErrorCategory.TRANSIENT, "timeout")
    assert e.errorCategory == ErrorCategory.TRANSIENT
    assert e.isRetryable is True


def test_other_categories_are_not_retryable():
    for cat in (ErrorCategory.VALIDATION, ErrorCategory.BUSINESS, ErrorCategory.PERMISSIONS):
        assert error_info(cat, "x").isRetryable is False
