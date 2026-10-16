"""Deterministic tests for the agent core — no LLM, no CLI (FR-010).

Covers: the versioned prompt loader, the in-process `registrar_triage` tool,
the MCP wiring in `build_options`, and loop termination in `consume`.
"""

import asyncio
import json
import logging
import sys

from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock

from ..mcp_server.models import Triage
from .core import ALLOWED_TOOLS, DEFAULT_MODEL, RunResult, build_options, consume
from .prompt import load_system_prompt
from .sdk_tools import registrar_triage_tool, triage_server

# --- US2: versioned system prompt ------------------------------------------


def test_load_system_prompt_has_triage_and_orchestration_guidance():
    prompt = load_system_prompt()
    assert prompt.strip()
    # triage guidance
    assert "nulo" in prompt  # "lo que el reporte no menciona queda nulo"
    assert "registrar_triage" in prompt
    assert "severidad" in prompt.lower()
    # orchestration guidance
    assert "cobertura" in prompt.lower()
    assert "vehículo" in prompt or "vehiculo" in prompt


# --- US3: registrar_triage as an in-process SDK tool -----------------------


def test_registrar_triage_tool_valid_returns_validated_triage():
    out = asyncio.run(
        registrar_triage_tool.handler({"severity": "leve", "incident_date": "2026-01-10"})
    )
    assert out.get("is_error", False) is False
    data = json.loads(out["content"][0]["text"])
    assert data["severity"] == "leve"
    assert data["claim_type"] is None  # not mentioned -> stays null


def test_registrar_triage_tool_handler_maps_validation_error():
    # Defense-in-depth: the handler converts a Pydantic ValidationError into a
    # structured ErrorInfo. In production the SDK bridge validates arguments
    # against the JSON schema BEFORE the handler, so this branch is only reached
    # for errors the schema cannot express (e.g. future cross-field validators
    # on Triage). We call the handler directly to cover that mapping.
    out = asyncio.run(registrar_triage_tool.handler({"severity": "catastrofica"}))
    assert out["is_error"] is True
    err = json.loads(out["content"][0]["text"])
    assert err["errorCategory"] == "validation"


def test_triage_tool_input_schema_is_the_triage_model():
    assert triage_server is not None
    assert registrar_triage_tool.name == "registrar_triage"
    # The tool's input schema IS the Triage model (spec 006), not just any object.
    assert registrar_triage_tool.input_schema == Triage.model_json_schema()


# --- US1: MCP wiring --------------------------------------------------------


def test_build_options_wires_both_mcp_surfaces_and_tools():
    opts = build_options()
    assert opts.model == DEFAULT_MODEL
    assert opts.system_prompt == load_system_prompt()

    servers = opts.mcp_servers
    assert {"cordillera", "triage"} <= set(servers.keys())

    cordillera = servers["cordillera"]
    assert cordillera["type"] == "stdio"
    assert cordillera["command"] == sys.executable
    assert cordillera["args"] == ["-m", "cordillera.mcp_server.server"]

    assert servers["triage"] is triage_server

    mcp_tools = {
        "mcp__cordillera__buscar_asegurado",
        "mcp__cordillera__verificar_identidad",
        "mcp__cordillera__consultar_poliza",
        "mcp__cordillera__verificar_cobertura",
        "mcp__cordillera__abrir_reclamo",
        "mcp__cordillera__escalar_a_ajustador",
        "mcp__triage__registrar_triage",
    }
    assert mcp_tools <= set(ALLOWED_TOOLS)
    assert "Agent" in ALLOWED_TOOLS  # delegation to revisor-cobertura (#8)


# --- US1: loop termination by the SDK result (no count, no keywords) --------


async def _stream(messages):
    for message in messages:
        yield message


def _assistant(text: str, stop_reason: str) -> AssistantMessage:
    return AssistantMessage(
        content=[TextBlock(text=text)], model=DEFAULT_MODEL, stop_reason=stop_reason
    )


def _result(stop_reason: str, terminal_reason: str) -> ResultMessage:
    return ResultMessage(
        subtype="success",
        duration_ms=1,
        duration_api_ms=1,
        is_error=False,
        num_turns=2,
        session_id="session-test",
        stop_reason=stop_reason,
        terminal_reason=terminal_reason,
    )


def test_consume_terminates_on_result_message(caplog):
    caplog.set_level(logging.INFO)
    messages = [
        _assistant("hola", "tool_use"),
        _assistant("listo", "end_turn"),
        _result("end_turn", "completed"),
        _assistant("NO DEBE CONSUMIRSE", "x"),  # after the ResultMessage
    ]

    result = asyncio.run(consume(_stream(messages)))

    assert isinstance(result, RunResult)
    assert result.subtype == "success"
    assert result.terminal_reason == "completed"
    assert result.stop_reason == "end_turn"
    assert result.is_error is False
    assert "hola" in result.text and "listo" in result.text
    # Proves termination is by the ResultMessage, not by iterating the whole stream.
    assert "NO DEBE CONSUMIRSE" not in result.text
    # Logs the stop reason each turn.
    assert "stop_reason=end_turn" in caplog.text


def test_consume_without_result_message_does_not_hang():
    messages = [_assistant("solo texto", "end_turn")]
    result = asyncio.run(consume(_stream(messages)))
    assert result.is_error is True
    assert "solo texto" in result.text
