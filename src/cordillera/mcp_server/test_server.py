"""Prueba ligera del servidor: las dos herramientas quedan registradas en FastMCP."""

import asyncio

from cordillera.mcp_server import server


def test_herramientas_registradas():
    herramientas = asyncio.run(server.mcp.list_tools())
    nombres = {h.name for h in herramientas}
    assert {"buscar_asegurado", "verificar_identidad"} <= nombres
