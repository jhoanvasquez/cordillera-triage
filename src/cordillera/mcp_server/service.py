"""Lógica pura de las herramientas MCP.

Separada de la capa FastMCP (`server.py`) para poder probarla sin levantar el servidor.
Las funciones aceptan los datos por parámetro (inyectables en tests) y, si no se pasan,
los cargan desde las fixtures.
"""

from typing import Literal

from . import loader
from .errors import CategoriaError, error_info
from .models import AseguradoResumen, RespuestaBusqueda, RespuestaVerificacion

# Registro reservado para simular una falla transitoria (ver fixtures #1, caso #7).
DOCUMENTO_FLAKY = "DOC-FIC-9999"

PorCriterio = Literal["documento", "nombre", "placa"]


def _coincidencias(
    asegurados: list[dict], vehiculos: list[dict], criterio: str, por: PorCriterio | None
) -> list[dict]:
    c = criterio.lower()
    if por == "documento":
        return [a for a in asegurados if a["documento"] == criterio]
    if por == "nombre":
        return [a for a in asegurados if c in a["nombre"].lower()]
    if por == "placa":
        ids = {v["asegurado_id"] for v in vehiculos if v["placa"] == criterio}
        return [a for a in asegurados if a["id"] in ids]

    # Sin `por`: intenta documento, nombre y placa; deduplica por id conservando orden.
    por_id = {a["id"]: a for a in asegurados}
    encontrados: dict[str, dict] = {}
    for a in asegurados:
        if a["documento"] == criterio or c in a["nombre"].lower():
            encontrados[a["id"]] = a
    for v in vehiculos:
        if v["placa"] == criterio and v["asegurado_id"] in por_id:
            encontrados[v["asegurado_id"]] = por_id[v["asegurado_id"]]
    return list(encontrados.values())


def buscar_asegurado(
    criterio: str,
    por: PorCriterio | None = None,
    *,
    asegurados: list[dict] | None = None,
    vehiculos: list[dict] | None = None,
) -> RespuestaBusqueda:
    """Busca asegurados por documento, nombre o placa. Puede devolver varias coincidencias."""
    asegurados = asegurados if asegurados is not None else loader.cargar_asegurados()
    vehiculos = vehiculos if vehiculos is not None else loader.cargar_vehiculos()

    if not criterio or not criterio.strip():
        return RespuestaBusqueda(
            ok=False,
            error=error_info(
                CategoriaError.VALIDATION, "El criterio de búsqueda no puede estar vacío."
            ),
        )
    criterio = criterio.strip()

    if criterio == DOCUMENTO_FLAKY:
        return RespuestaBusqueda(
            ok=False,
            error=error_info(
                CategoriaError.TRANSIENT,
                "Tiempo de espera agotado consultando el core de la aseguradora.",
            ),
        )

    coincidencias = _coincidencias(asegurados, vehiculos, criterio, por)
    resultados = [
        AseguradoResumen(id=a["id"], documento=a["documento"], nombre=a["nombre"])
        for a in coincidencias
    ]
    return RespuestaBusqueda(ok=True, resultados=resultados, resultCount=len(resultados))


def verificar_identidad(
    documento: str,
    fecha_nacimiento: str,
    *,
    asegurados: list[dict] | None = None,
) -> RespuestaVerificacion:
    """Confirma la identidad con un segundo dato. Solo reporta; la regla 1 la aplica el hook."""
    asegurados = asegurados if asegurados is not None else loader.cargar_asegurados()

    if not documento or not fecha_nacimiento:
        return RespuestaVerificacion(
            ok=False,
            error=error_info(
                CategoriaError.VALIDATION, "Documento y fecha de nacimiento son obligatorios."
            ),
        )

    if documento == DOCUMENTO_FLAKY:
        return RespuestaVerificacion(
            ok=False,
            error=error_info(
                CategoriaError.TRANSIENT,
                "Tiempo de espera agotado consultando el core de la aseguradora.",
            ),
        )

    aseg = next((a for a in asegurados if a["documento"] == documento), None)
    if aseg is None:
        return RespuestaVerificacion(
            ok=False,
            error=error_info(CategoriaError.BUSINESS, "No existe un asegurado con ese documento."),
        )

    verificado = aseg["fecha_nacimiento"] == fecha_nacimiento
    return RespuestaVerificacion(
        ok=True,
        verificado=verificado,
        asegurado_id=aseg["id"] if verificado else None,
    )
