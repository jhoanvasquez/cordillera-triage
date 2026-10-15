"""Pruebas del envelope de error."""

from cordillera.mcp_server.errors import CategoriaError, error_info


def test_transient_es_reintentable():
    e = error_info(CategoriaError.TRANSIENT, "timeout")
    assert e.errorCategory == CategoriaError.TRANSIENT
    assert e.isRetryable is True


def test_otras_categorias_no_son_reintentables():
    for cat in (CategoriaError.VALIDATION, CategoriaError.BUSINESS, CategoriaError.PERMISSIONS):
        assert error_info(cat, "x").isRetryable is False
