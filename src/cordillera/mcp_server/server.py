"""Servidor MCP `cordillera` (FastMCP sobre stdio).

Capa delgada: registra las herramientas que envuelven la lógica pura de `service.py`.
El tipo de retorno Pydantic hace que FastMCP exponga el resultado como `structuredContent`.
"""

from typing import Literal

from mcp.server.fastmcp import FastMCP

from . import service
from .models import (
    RespuestaBusqueda,
    RespuestaCobertura,
    RespuestaPoliza,
    RespuestaVerificacion,
)

mcp = FastMCP("cordillera")


@mcp.tool()
def buscar_asegurado(
    criterio: str, por: Literal["documento", "nombre", "placa"] | None = None
) -> RespuestaBusqueda:
    """Encuentra al asegurado por documento, nombre o placa. Puede devolver varias coincidencias.

    Una búsqueda sin resultados devuelve ok=true con resultCount=0 (no es un error).
    """
    return service.buscar_asegurado(criterio, por)


@mcp.tool()
def verificar_identidad(documento: str, fecha_nacimiento: str) -> RespuestaVerificacion:
    """Confirma la identidad del asegurado con un dato adicional (fecha de nacimiento).

    Devuelve verificado=true/false; no revela la fecha almacenada.
    """
    return service.verificar_identidad(documento, fecha_nacimiento)


@mcp.tool()
def consultar_poliza(placa: str) -> RespuestaPoliza:
    """Devuelve la póliza COMPLETA de un VEHÍCULO ESPECÍFICO: vigencia, amparos y deducibles.

    Úsala para conocer qué contiene la póliza. Si el asegurado tiene varios vehículos y el
    reporte no dice cuál, PREGUNTA PRIMERO cuál vehículo; no adivines.
    """
    return service.consultar_poliza(placa)


@mcp.tool()
def verificar_cobertura(numero_poliza: str, tipo: str, fecha: str) -> RespuestaCobertura:
    """Responde UNA sola pregunta: ¿el tipo de siniestro está cubierto por la póliza en la fecha?

    Devuelve cubierto: si | no | incierto con un motivo. Úsala antes de abrir un reclamo o de
    responder una duda de cobertura (por ejemplo, la grúa). No devuelve la póliza completa.
    """
    return service.verificar_cobertura(numero_poliza, tipo, fecha)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
