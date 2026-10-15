"""Cargador de las fixtures JSON (solo lectura) que respaldan el servidor MCP."""

import json
from functools import lru_cache
from pathlib import Path

# src/cordillera/mcp_server/ -> src/cordillera/data/
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load(nombre: str) -> list[dict]:
    return json.loads((DATA_DIR / nombre).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def cargar_asegurados() -> list[dict]:
    return _load("asegurados.json")


@lru_cache(maxsize=1)
def cargar_vehiculos() -> list[dict]:
    return _load("vehiculos.json")


@lru_cache(maxsize=1)
def cargar_polizas() -> list[dict]:
    return _load("polizas.json")
