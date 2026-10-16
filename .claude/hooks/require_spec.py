#!/usr/bin/env python3
"""PreToolUse hook: block Write/Edit under src/** unless the branch has a spec.

Enforces constitution Principle III (no production code in src/** without
specs/<branch>/spec.md). Blocks with exit code 2 + a stderr reason. Fail-safe:
any unexpected error returns 0 so a hook bug never breaks the workflow.
"""

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    try:
        # Read stdin as UTF-8 explicitly (Windows stdin defaults to cp1252).
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return 0

    file_path = (data.get("tool_input") or {}).get("file_path") or ""
    norm = file_path.replace("\\", "/")

    # Only guard production code under src/.
    if not (norm.startswith("src/") or "/src/" in norm):
        return 0

    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
        # Resolve the repo root so the spec lookup does not depend on the hook's
        # working directory (git itself walks up to find .git from any subdir).
        root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
    except Exception:
        return 0
    if not branch or not root:
        return 0

    spec = Path(root) / "specs" / branch / "spec.md"
    if spec.exists():
        return 0

    print(
        f"require_spec: bloqueada escritura bajo src/ — falta {spec.as_posix()}. "
        "Creá la especificación (SDD, Principio III) antes de escribir código de producción.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
