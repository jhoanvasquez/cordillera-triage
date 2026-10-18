#!/usr/bin/env bash
# PostToolUse hook: run `ruff format` on the edited .py file.
# Enforces "code formatted after each edit" (constitution). Invoked via
# `bash .claude/hooks/format.sh` (a bare .sh is not executable on Windows).
# Parses stdin with python (no jq dependency). Always exits 0 (post-edit never blocks).

input="$(cat)"
file="$(printf '%s' "$input" | python -c "import json,sys; d=json.load(sys.stdin); print((d.get('tool_input') or {}).get('file_path') or '')" 2>/dev/null)"

case "$file" in
  *.py)
    # Prefer the project venv's ruff (system python usually lacks it); then fall back.
    {
      .venv/Scripts/python.exe -m ruff format "$file" \
      || .venv/bin/python -m ruff format "$file" \
      || python -m ruff format "$file" \
      || ruff format "$file"
    } >/dev/null 2>&1 || true
    ;;
esac

exit 0
