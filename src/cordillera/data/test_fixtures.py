"""Pruebas deterministas de los fixtures: formatos ficticios, integridad y cobertura.

No requieren modelo ni servidor: validan solo los datos (necesidad #3 del enunciado).
"""

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent
FECHA_SINIESTRO = "2026-10-10"  # fecha de referencia del escenario (ver plan.md)


def _load(nombre: str) -> list[dict]:
    return json.loads((DATA_DIR / nombre).read_text(encoding="utf-8"))


ASEGURADOS = _load("asegurados.json")
VEHICULOS = _load("vehiculos.json")
POLIZAS = _load("polizas.json")


def _poliza_vigente(poliza: dict, fecha: str) -> bool:
    return poliza["vigencia_desde"] <= fecha <= poliza["vigencia_hasta"]


# --- Historia de usuario 1: integridad y cobertura de los 8 casos ---


def test_integridad_referencial():
    ids_aseg = {a["id"] for a in ASEGURADOS}
    ids_veh = {v["id"] for v in VEHICULOS}
    ids_pol = {p["id"] for p in POLIZAS}
    for v in VEHICULOS:
        assert v["asegurado_id"] in ids_aseg, v
        assert v["poliza_id"] in ids_pol, v
    for p in POLIZAS:
        assert p["asegurado_id"] in ids_aseg, p
        assert p["vehiculo_id"] in ids_veh, p


def test_cobertura_casos():
    # Casos 1 y 2: A-001 con póliza vigente y amparo de grúa.
    p1 = next(p for p in POLIZAS if p["asegurado_id"] == "A-001")
    assert _poliza_vigente(p1, FECHA_SINIESTRO)
    assert any(a["tipo"] == "grua" and a["cubierto"] == "si" for a in p1["amparos"])

    # Caso 4: A-002 con dos vehículos, ambos con póliza vigente.
    veh_a2 = [v for v in VEHICULOS if v["asegurado_id"] == "A-002"]
    assert len(veh_a2) == 2
    for v in veh_a2:
        p = next(p for p in POLIZAS if p["id"] == v["poliza_id"])
        assert _poliza_vigente(p, FECHA_SINIESTRO)

    # Caso 5: A-003 con póliza vencida en la fecha del siniestro.
    p_a3 = next(p for p in POLIZAS if p["asegurado_id"] == "A-003")
    assert not _poliza_vigente(p_a3, FECHA_SINIESTRO)

    # Caso 8: A-004 uso particular con amparo incierto (domicilios).
    v_a4 = next(v for v in VEHICULOS if v["asegurado_id"] == "A-004")
    assert v_a4["uso"] == "particular"
    p_a4 = next(p for p in POLIZAS if p["asegurado_id"] == "A-004")
    assert any(a["cubierto"] == "incierto" for a in p_a4["amparos"])


# --- Historia de usuario 2: datos inequívocamente ficticios ---

RE_DOC = re.compile(r"^DOC-FIC-\d{4}$")
RE_PLACA = re.compile(r"^FIC-\d{2}[A-Z]$")
RE_POL = re.compile(r"^POL-FIC-\d{4}$")


def test_formatos_ficticios():
    for a in ASEGURADOS:
        assert RE_DOC.match(a["documento"]), a["documento"]
    for v in VEHICULOS:
        assert RE_PLACA.match(v["placa"]), v["placa"]
    for p in POLIZAS:
        assert RE_POL.match(p["numero"]), p["numero"]


# Formas reales colombianas que NINGÚN valor puede tener.
RE_CEDULA_REAL = re.compile(r"\b\d{8,10}\b")
RE_PLACA_REAL = re.compile(r"\b[A-Z]{3}\d{3}\b")


def test_sin_datos_reales():
    for nombre in ("asegurados.json", "vehiculos.json", "polizas.json"):
        texto = (DATA_DIR / nombre).read_text(encoding="utf-8")
        assert not RE_CEDULA_REAL.search(texto), f"posible cédula real en {nombre}"
        assert not RE_PLACA_REAL.search(texto), f"posible placa real en {nombre}"


# --- Historia de usuario 3: búsqueda y verificación de identidad ---


def test_coincidencias_multiples():
    marias = [a for a in ASEGURADOS if a["nombre"] == "María Gómez"]
    assert len(marias) >= 2
    assert len({a["documento"] for a in marias}) == len(marias)


def test_segundo_dato_identidad():
    for a in ASEGURADOS:
        assert a.get("fecha_nacimiento")


# --- Historia de usuario 4: falla transitoria ---


def test_registro_flaky_presente():
    flaky = [a for a in ASEGURADOS if a["documento"] == "DOC-FIC-9999"]
    assert len(flaky) == 1
    assert flaky[0].get("flaky") is True
