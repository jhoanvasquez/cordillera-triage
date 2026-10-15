"""Envelope de error estructurado, compartido por todas las herramientas MCP.

Decisión (ver plan 002): FastMCP v1 no permite `isError: true` junto con
`structuredContent`. Por eso el estado de dominio viaja siempre en `structuredContent`
con una bandera `ok`; `errorCategory`/`isRetryable` quedan legibles para los hooks (#7).
Las claves del envelope van en inglés (capa de transporte); los valores de dominio, en español.
"""

from enum import Enum

from pydantic import BaseModel


class CategoriaError(str, Enum):
    """Categorías de error del enunciado (behavior #4)."""

    TRANSIENT = "transient"
    VALIDATION = "validation"
    BUSINESS = "business"
    PERMISSIONS = "permissions"


# Solo los errores transitorios se reintentan.
_REINTENTABLES = {CategoriaError.TRANSIENT}


class ErrorInfo(BaseModel):
    """Descriptor de error que viaja dentro del envelope."""

    errorCategory: CategoriaError
    isRetryable: bool
    description: str


def error_info(categoria: CategoriaError, description: str) -> ErrorInfo:
    """Construye un ErrorInfo con el `isRetryable` derivado de la categoría."""
    return ErrorInfo(
        errorCategory=categoria,
        isRetryable=categoria in _REINTENTABLES,
        description=description,
    )
