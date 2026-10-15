"""Pruebas de `consultar_poliza` y `verificar_cobertura` (lógica pura + descripciones)."""

import asyncio

from cordillera.mcp_server import server, service

FECHA = "2026-10-10"


# --- US1: consultar_poliza ---


def test_consultar_poliza_por_placa():
    r = service.consultar_poliza("FIC-01A")
    assert r.ok is True
    assert r.poliza is not None
    assert r.poliza.numero == "POL-FIC-0001"
    assert any(a.tipo == "grua" and a.cubierto == "si" for a in r.poliza.amparos)


def test_consultar_poliza_placa_inexistente_es_vacio():
    r = service.consultar_poliza("FIC-99Z")
    assert r.ok is True
    assert r.poliza is None
    assert r.error is None


# --- US2: verificar_cobertura ---


def test_cobertura_grua_si():
    r = service.verificar_cobertura("POL-FIC-0001", "grua", FECHA)
    assert r.ok is True
    assert r.cubierto == "si"


def test_cobertura_incierto_por_uso():
    r = service.verificar_cobertura("POL-FIC-0005", "danos", FECHA)
    assert r.ok is True
    assert r.cubierto == "incierto"
    assert "domicilio" in r.motivo.lower() or "reparto" in r.motivo.lower()


def test_cobertura_poliza_vencida_es_no():
    r = service.verificar_cobertura("POL-FIC-0004", "danos", FECHA)
    assert r.ok is True
    assert r.cubierto == "no"
    assert "vigente" in r.motivo.lower()


def test_cobertura_amparo_no_contratado_es_no():
    r = service.verificar_cobertura("POL-FIC-0002", "grua", FECHA)
    assert r.ok is True
    assert r.cubierto == "no"


def test_cobertura_poliza_inexistente_es_error_business():
    r = service.verificar_cobertura("POL-FIC-0000", "danos", FECHA)
    assert r.ok is False
    assert r.error.errorCategory.value == "business"


# --- US3: descripciones distintas (behavior #3) ---


def test_descripciones_distintas_y_guia_multivehiculo():
    herramientas = {h.name: h for h in asyncio.run(server.mcp.list_tools())}
    d_poliza = herramientas["consultar_poliza"].description
    d_cobertura = herramientas["verificar_cobertura"].description
    assert d_poliza != d_cobertura
    assert "pregunta" in d_poliza.lower()
    assert "veh" in d_poliza.lower()
