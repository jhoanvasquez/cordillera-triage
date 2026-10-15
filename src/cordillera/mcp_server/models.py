"""Modelos Pydantic de entrada/salida de las herramientas MCP.

Los nombres de campo de dominio van en español; el envelope técnico (`ok`, `error`,
`resultCount`) en inglés, según la constitución (Principio IV/VI).
"""

from pydantic import BaseModel

from .errors import ErrorInfo


class AseguradoResumen(BaseModel):
    """Resumen público de un asegurado. NO incluye `fecha_nacimiento`:

    ese es el dato secreto de verificación y no debe filtrarse en la búsqueda.
    """

    id: str
    documento: str
    nombre: str


class RespuestaBusqueda(BaseModel):
    """Resultado de `buscar_asegurado`. Una búsqueda sin resultados es `ok=True`."""

    ok: bool
    resultados: list[AseguradoResumen] = []
    resultCount: int = 0
    error: ErrorInfo | None = None


class RespuestaVerificacion(BaseModel):
    """Resultado de `verificar_identidad`. `verificado` solo reporta; no decide."""

    ok: bool
    verificado: bool | None = None
    asegurado_id: str | None = None
    error: ErrorInfo | None = None
