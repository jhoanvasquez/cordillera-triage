"""Deterministic tests for the coverage-review subagent — no LLM, no CLI (FR-007).

Covers: the CoverageVerdict schema and parser, the revisor-cobertura AgentDefinition
(tools restricted to the two coverage tools), and the wiring into build_options.
"""

import json

import pytest
from pydantic import ValidationError

from .core import build_options
from .coverage import (
    COVERAGE_TOOLS,
    CoverageVerdict,
    build_coverage_reviewer,
    parse_coverage_verdict,
)
from .prompt import load_coverage_reviewer_prompt, load_system_prompt

# --- US2: structured verdict + parser ---------------------------------------


def test_parse_coverage_verdict_valid_including_incierto():
    for covered in ("si", "no", "incierto"):
        verdict = parse_coverage_verdict(json.dumps({"covered": covered}))
        assert isinstance(verdict, CoverageVerdict)
        assert verdict.covered == covered
        assert verdict.tow_covered is None  # not mentioned -> stays null


def test_parse_coverage_verdict_full_shape():
    verdict = parse_coverage_verdict(
        {
            "covered": "si",
            "coverage_type": "colisión",
            "deductible": 500000,
            "tow_covered": True,
            "reason": "Amparo de colisión vigente.",
        }
    )
    assert verdict.covered == "si"
    assert verdict.tow_covered is True
    assert verdict.deductible == 500000


def test_parse_coverage_verdict_rejects_invalid_covered():
    with pytest.raises(ValidationError):
        parse_coverage_verdict({"covered": "total"})  # dict path
    with pytest.raises(ValidationError):
        parse_coverage_verdict('{"covered": "total"}')  # JSON-text path


def test_parse_coverage_verdict_rejects_malformed_json():
    with pytest.raises(ValueError):
        parse_coverage_verdict("not json")


# --- US1: subagent with restricted tools ------------------------------------


def test_build_coverage_reviewer_restricts_tools():
    reviewer = build_coverage_reviewer()
    assert reviewer.tools == COVERAGE_TOOLS
    assert set(reviewer.tools) == {
        "mcp__cordillera__consultar_poliza",
        "mcp__cordillera__verificar_cobertura",
    }
    assert reviewer.description.strip()
    assert reviewer.prompt.strip()


def test_coverage_reviewer_prompt_loaded_from_file():
    prompt = load_coverage_reviewer_prompt()
    assert "cobertura" in prompt.lower()
    assert "incierto" in prompt
    assert prompt == build_coverage_reviewer().prompt


# --- US3: delegation guidance in the main system prompt ---------------------


def test_system_prompt_has_delegation_and_incierto_guidance():
    prompt = load_system_prompt()
    assert "revisor-cobertura" in prompt
    assert "incierto" in prompt
    # the context the subagent must receive
    assert "póliza" in prompt.lower()
    assert "fecha" in prompt.lower()


# --- wiring -----------------------------------------------------------------


def test_build_options_registers_subagent_and_delegation_tool():
    opts = build_options()
    assert opts.agents is not None
    assert "revisor-cobertura" in opts.agents
    assert opts.agents["revisor-cobertura"].tools == COVERAGE_TOOLS
    assert "Agent" in opts.allowed_tools
    assert "mcp__cordillera__consultar_poliza" in opts.allowed_tools
    assert "mcp__cordillera__verificar_cobertura" in opts.allowed_tools
