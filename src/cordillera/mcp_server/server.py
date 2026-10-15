"""Servidor MCP `cordillera` (FastMCP sobre stdio).

Capa delgada: registra las herramientas que envuelven la lógica pura de `service.py`.
El tipo de retorno Pydantic hace que FastMCP exponga el resultado como `structuredContent`.
"""

from typing import Literal

from mcp.server.fastmcp import FastMCP

from . import service
from .models import RespuestaBusqueda, RespuestaVerificacion

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


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
