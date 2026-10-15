"""Load the versioned system prompt.

The prompt is product content (Spanish) kept in `system_prompt.md` so it is
reviewable on its own. This module is the single source that reads it.
"""

from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "system_prompt.md"


def load_system_prompt() -> str:
    """Return the versioned system prompt read from `system_prompt.md`."""
    return _PROMPT_PATH.read_text(encoding="utf-8")
