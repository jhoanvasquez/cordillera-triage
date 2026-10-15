"""Servidor MCP `cordillera` (FastMCP sobre stdio).

Capa delgada: registra las herramientas que envuelven la lógica pura de `service.py`.
El tipo de retorno Pydantic hace que FastMCP exponga el resultado como `structuredContent`.
"""

from typing import Literal

from mcp.server.fastmcp import FastMCP

from . import service
from .models import (
    ClaimResponse,
    CoverageResponse,
    EscalationResponse,
    Handoff,
    PolicyResponse,
    SearchResponse,
    Triage,
    VerificationResponse,
)

mcp = FastMCP("cordillera")


@mcp.tool()
def buscar_asegurado(
    criterio: str, por: Literal["documento", "nombre", "placa"] | None = None
) -> SearchResponse:
    """Encuentra al asegurado por documento, nombre o placa. Puede devolver varias coincidencias.

    Una búsqueda sin resultados devuelve ok=true con resultCount=0 (no es un error).
    """
    return service.search_insured(criterio, por)


@mcp.tool()
def verificar_identidad(documento: str, fecha_nacimiento: str) -> VerificationResponse:
    """Confirma la identidad del asegurado con un dato adicional (fecha de nacimiento).

    Devuelve verificado=true/false; no revela la fecha almacenada.
    """
    return service.verify_identity(documento, fecha_nacimiento)


@mcp.tool()
def consultar_poliza(placa: str) -> PolicyResponse:
    """Devuelve la póliza COMPLETA de un VEHÍCULO ESPECÍFICO: vigencia, amparos y deducibles.

    Úsala para conocer qué contiene la póliza. Si el asegurado tiene varios vehículos y el
    reporte no dice cuál, PREGUNTA PRIMERO cuál vehículo; no adivines.
    """
    return service.get_policy(placa)


@mcp.tool()
def verificar_cobertura(numero_poliza: str, tipo: str, fecha: str) -> CoverageResponse:
    """Responde UNA sola pregunta: ¿el tipo de siniestro está cubierto por la póliza en la fecha?

    Devuelve cubierto: si | no | incierto con un motivo. Úsala antes de abrir un reclamo o de
    responder una duda de cobertura (por ejemplo, la grúa). No devuelve la póliza completa.
    """
    return service.check_coverage(numero_poliza, tipo, fecha)


@mcp.tool()
def abrir_reclamo(documento: str, numero_poliza: str, triage: Triage) -> ClaimResponse:
    """Abre un reclamo con el triage estructurado del siniestro.

    Requiere identidad verificada y póliza vigente en la fecha del siniestro (defensa en
    profundidad de la regla 1). Si no se cumplen, devuelve un error de negocio.
    """
    return service.open_claim(documento, numero_poliza, triage)


@mcp.tool()
def escalar_a_ajustador(handoff: Handoff) -> EscalationResponse:
    """Pasa el caso a un ajustador humano con un resumen estructurado y una prioridad.

    El resumen debe permitir actuar a un ajustador que no tiene acceso a la conversación.
    """
    return service.escalate_to_adjuster(handoff)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
