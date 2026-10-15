"""JSON fixture loader (read-only) that backs the MCP server."""

import json
from functools import lru_cache
from pathlib import Path

# src/cordillera/mcp_server/ -> src/cordillera/data/
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load(name: str) -> list[dict]:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_insured() -> list[dict]:
    return _load("insured.json")


@lru_cache(maxsize=1)
def load_vehicles() -> list[dict]:
    return _load("vehicles.json")


@lru_cache(maxsize=1)
def load_policies() -> list[dict]:
    return _load("policies.json")
