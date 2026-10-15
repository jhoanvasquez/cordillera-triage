"""Light server test: all tools are registered in FastMCP with their Spanish names."""

import asyncio

from cordillera.mcp_server import server


def test_tools_registered():
    tools = asyncio.run(server.mcp.list_tools())
    names = {h.name for h in tools}
    assert {"buscar_asegurado", "verificar_identidad"} <= names
