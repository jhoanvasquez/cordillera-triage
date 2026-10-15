"""Modelos Pydantic de entrada/salida de las herramientas MCP.

Los nombres de campo de dominio van en español; el envelope técnico (`ok`, `error`,
`resultCount`) en inglés, según la constitución (Principio IV/VI).
"""

from typing import Literal

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


class AmparoDetalle(BaseModel):
    """Amparo (cobertura) contratado dentro de una póliza."""

    tipo: str
    cubierto: Literal["si", "no", "incierto"]
    condiciones: str = ""


class PolizaDetalle(BaseModel):
    """Póliza completa de un vehículo: vigencia, amparos y deducible."""

    id: str
    numero: str
    asegurado_id: str
    vehiculo_id: str
    vigencia_desde: str
    vigencia_hasta: str
    deducible: int
    amparos: list[AmparoDetalle] = []


class RespuestaPoliza(BaseModel):
    """Resultado de `consultar_poliza`. Un vehículo sin póliza es `ok=True` con `poliza=None`."""

    ok: bool
    poliza: PolizaDetalle | None = None
    error: ErrorInfo | None = None


class RespuestaCobertura(BaseModel):
    """Resultado de `verificar_cobertura`. `cubierto` solo reporta; no decide el escalamiento."""

    ok: bool
    cubierto: Literal["si", "no", "incierto"] | None = None
    motivo: str | None = None
    deducible: int | None = None
    error: ErrorInfo | None = None
