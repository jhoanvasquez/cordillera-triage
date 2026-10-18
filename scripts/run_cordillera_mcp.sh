#!/usr/bin/env bash
# Launcher for the `cordillera` MCP stdio server.
# Picks the project venv interpreter (which has mcp/pydantic) rather than a bare
# `python` from PATH, which — when Claude Code starts without the venv active —
# would be the system interpreter and fail with ModuleNotFoundError: mcp.
# Mirrors the venv cascade in .claude/hooks/format.sh. Portable Windows/Unix.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"

if [ -x ".venv/Scripts/python.exe" ]; then
  exec .venv/Scripts/python.exe -m cordillera.mcp_server.server
elif [ -x ".venv/bin/python" ]; then
  exec .venv/bin/python -m cordillera.mcp_server.server
else
  exec python -m cordillera.mcp_server.server
fi
