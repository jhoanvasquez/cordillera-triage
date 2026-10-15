"""Pruebas del cargador de fixtures."""

from cordillera.mcp_server import loader


def test_conteos_esperados():
    assert len(loader.cargar_asegurados()) == 6
    assert len(loader.cargar_vehiculos()) == 6
    assert len(loader.cargar_polizas()) == 6


def test_asegurados_tienen_campos_clave():
    for a in loader.cargar_asegurados():
        assert {"id", "documento", "nombre", "fecha_nacimiento"} <= a.keys()
