"""End-to-end scenario harness: run a conversation script against the real agent.

Runs the full stack (#6-#9) — `ClaudeSDKClient` + the cordillera MCP server + the
business-rule hooks + the coverage subagent — and captures the tool-call trace, the
final `SessionState`, and the agent text. Scenario tests assert on this behavior
(trace + outcome), never on wording, so they tolerate model nondeterminism.

This module needs the real model (auth + Claude Agent CLI) and is imported only by the
opt-in e2e tests.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)

from .core import DEFAULT_MODEL, build_options
from .state import SessionState


@dataclass
class ScenarioResult:
    """Observable outcome of a scenario run: what tools were called and what happened."""

    tool_trace: list[str] = field(default_factory=list)
    state: SessionState = field(default_factory=SessionState)
    text: str = ""


def called(trace: list[str], tool: str) -> bool:
    """True if a tool whose name ends with `tool` was called (robust to the mcp__ prefix)."""
    return any(name.endswith(tool) for name in trace)


def delegated(trace: list[str]) -> bool:
    """True if the agent delegated to a subagent (the delegation tool is Agent/Task)."""
    return "Agent" in trace or "Task" in trace


async def run_scenario(messages: Iterable[str], *, model: str = DEFAULT_MODEL) -> ScenarioResult:
    """Run the agent over a scripted conversation, capturing trace + state + text."""
    state = SessionState()
    options = build_options(model=model, state=state)
    trace: list[str] = []
    texts: list[str] = []
    async with ClaudeSDKClient(options=options) as client:
        for message in messages:
            await client.query(message)
            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, ToolUseBlock):
                            trace.append(block.name)
                        elif isinstance(block, TextBlock):
                            texts.append(block.text)
                elif isinstance(msg, ResultMessage):
                    # receive_response() self-terminates after the ResultMessage;
                    # this break just makes the per-turn boundary explicit.
                    break
    return ScenarioResult(tool_trace=trace, state=state, text="\n".join(texts))
