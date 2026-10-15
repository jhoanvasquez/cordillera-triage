"""Pruebas de la lógica pura de las herramientas (sin levantar MCP)."""

from cordillera.mcp_server import service

# --- US1: localizar al asegurado ---


def test_busqueda_unica_por_documento():
    r = service.buscar_asegurado("DOC-FIC-0001", "documento")
    assert r.ok is True
    assert r.resultCount == 1
    assert r.resultados[0].documento == "DOC-FIC-0001"


def test_resumen_no_filtra_fecha_nacimiento():
    r = service.buscar_asegurado("DOC-FIC-0001", "documento")
    assert not hasattr(r.resultados[0], "fecha_nacimiento")


def test_busqueda_multiple_por_nombre():
    r = service.buscar_asegurado("María Gómez", "nombre")
    assert r.ok is True
    assert r.resultCount >= 2


def test_busqueda_por_placa():
    r = service.buscar_asegurado("FIC-01A", "placa")
    assert r.ok is True
    assert r.resultCount == 1
    assert r.resultados[0].id == "A-001"


# --- US3: errores estructurados y vacío ---


def test_busqueda_vacia_no_es_error():
    r = service.buscar_asegurado("DOC-FIC-0000-INEXISTENTE", "documento")
    assert r.ok is True
    assert r.resultCount == 0
    assert r.error is None


def test_criterio_vacio_es_validation():
    r = service.buscar_asegurado("   ", None)
    assert r.ok is False
    assert r.error.errorCategory.value == "validation"
    assert r.error.isRetryable is False


def test_registro_flaky_es_transient():
    r = service.buscar_asegurado("DOC-FIC-9999", "documento")
    assert r.ok is False
    assert r.error.errorCategory.value == "transient"
    assert r.error.isRetryable is True


# --- US2: verificar identidad ---


def test_identidad_correcta():
    r = service.verificar_identidad("DOC-FIC-0001", "1985-03-12")
    assert r.ok is True
    assert r.verificado is True
    assert r.asegurado_id == "A-001"


def test_identidad_incorrecta():
    r = service.verificar_identidad("DOC-FIC-0001", "2000-01-01")
    assert r.ok is True
    assert r.verificado is False
    assert r.asegurado_id is None


def test_identidad_documento_inexistente():
    r = service.verificar_identidad("DOC-FIC-7777", "1985-03-12")
    assert r.ok is False
    assert r.error.errorCategory.value == "business"
