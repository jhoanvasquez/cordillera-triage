"""Agent core: MCP wiring, the agentic loop, and stop-reason logging.

The loop ends on the SDK's `ResultMessage` (its terminal signal) — never by
counting turns or matching keywords in the text (constitution: "Ciclo agéntico
correcto"). `consume` takes an async stream of messages, not the live client, so
loop termination is testable without the model or the CLI.
"""

from __future__ import annotations

import logging
import sys
from collections.abc import AsyncIterable
from dataclasses import dataclass
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ClaudeSDKError,
    Message,
    ResultMessage,
    TextBlock,
)

from .prompt import load_system_prompt
from .sdk_tools import triage_server

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-opus-4-8"

# The `src/` directory. We put it on the spawned MCP subprocess's PYTHONPATH so
# it can import `cordillera` even when the package is not installed (the repo
# runs from source). The subprocess env below sets only PYTHONPATH and relies on
# the CLI merging it over the parent environment, so PATH/SYSTEMROOT survive; if
# that merge behavior ever changes, the subprocess would lose PATH.
_SRC_DIR = str(Path(__file__).resolve().parents[2])

# The six business tools come from the external `cordillera` server; the triage
# producer is the in-process `triage` server. Names follow Claude Code's
# `mcp__<server>__<tool>` convention.
ALLOWED_TOOLS = [
    "mcp__cordillera__buscar_asegurado",
    "mcp__cordillera__verificar_identidad",
    "mcp__cordillera__consultar_poliza",
    "mcp__cordillera__verificar_cobertura",
    "mcp__cordillera__abrir_reclamo",
    "mcp__cordillera__escalar_a_ajustador",
    "mcp__triage__registrar_triage",
]


@dataclass
class RunResult:
    """Outcome of one agent run: the final text plus the SDK's stop signals."""

    text: str
    stop_reason: str | None
    terminal_reason: str | None
    subtype: str | None
    is_error: bool


def build_options(model: str = DEFAULT_MODEL) -> ClaudeAgentOptions:
    """Build the SDK options: system prompt, the two MCP surfaces, allowed tools."""
    return ClaudeAgentOptions(
        model=model,
        system_prompt=load_system_prompt(),
        mcp_servers={
            "cordillera": {
                "type": "stdio",
                "command": sys.executable,
                "args": ["-m", "cordillera.mcp_server.server"],
                "env": {"PYTHONPATH": _SRC_DIR},
            },
            "triage": triage_server,
        },
        allowed_tools=ALLOWED_TOOLS,
        stderr=lambda line: logger.debug("cli stderr: %s", line),
    )


async def consume(messages: AsyncIterable[Message]) -> RunResult:
    """Consume the message stream until the SDK's `ResultMessage`, logging stop reasons.

    Ends when the `ResultMessage` arrives — not by counting iterations nor by
    matching keywords. Logs the model's stop reason on each assistant turn and
    the terminal reason on the result.
    """
    text_parts: list[str] = []
    last_stop_reason: str | None = None

    async for message in messages:
        if isinstance(message, AssistantMessage):
            if message.stop_reason is not None:
                last_stop_reason = message.stop_reason
                logger.info("turn stop_reason=%s", message.stop_reason)
            for block in message.content:
                if isinstance(block, TextBlock):
                    text_parts.append(block.text)
        elif isinstance(message, ResultMessage):
            logger.info(
                "result subtype=%s terminal_reason=%s stop_reason=%s",
                message.subtype,
                message.terminal_reason,
                message.stop_reason,
            )
            return RunResult(
                text="\n".join(text_parts),
                stop_reason=message.stop_reason or last_stop_reason,
                terminal_reason=message.terminal_reason,
                subtype=message.subtype,
                is_error=message.is_error,
            )

    # The SDK always closes a response with a ResultMessage; reaching here means
    # the stream ended early. Report what we have instead of hanging.
    logger.warning("message stream ended without a ResultMessage")
    return RunResult(
        text="\n".join(text_parts),
        stop_reason=last_stop_reason,
        terminal_reason=None,
        subtype=None,
        is_error=True,
    )


async def run(report: str, *, model: str = DEFAULT_MODEL) -> RunResult:
    """Run the agent against a report: connect, send, consume to the SDK result.

    Raises a clear error if the agent/MCP connection cannot be established, so a
    failure surfaces instead of hanging (FR-008).
    """
    options = build_options(model=model)
    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query(report)
            return await consume(client.receive_response())
    except ClaudeSDKError as exc:
        logger.error("agent run failed to connect or communicate: %s", exc)
        raise RuntimeError(f"agent/MCP connection failed: {exc}") from exc
