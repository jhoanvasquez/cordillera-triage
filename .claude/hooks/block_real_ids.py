#!/usr/bin/env python3
"""PreToolUse hook: block writing real-looking identity documents or vehicle
plates into any repository file.

Enforces constitution Principle II (only fictitious data). A bare "3 letters + 3
digits" token or an 8-11 digit run is, on its own, indistinguishable from a
legitimate code identifier (Spec Kit checklist IDs, error codes), a money amount,
a timestamp or a phone number. To stay high-precision, the hook flags such a
value only when it sits next to an identity/plate keyword (documento, cedula,
placa, and their English field-name equivalents) — i.e. when the value is being
used AS an identity or a plate. The mandatory fictitious markers (DOC-FIC-*,
FIC-*) never match the shapes, so a keyed fictitious value passes.

This is the fast prevention layer; the authoritative repo-wide guarantee is the
CI/pre-commit check the constitution also mandates. Blocks with exit code 2 + a
stderr reason. Fail-safe: any error returns 0 so a hook bug never breaks the flow.
"""

import json
import re
import sys

# Up to 20 same-line characters (a separator, quote, or short word) may sit
# between the keyword and the value: covers `"document": "<value>"`,
# `placa: <value>` and `cedula <value>`. `.` does not cross newlines, so a CSV
# header on a separate line does not bind to a data row (left to the CI check).
_GAP = r".{0,20}?"
_DOCUMENT = re.compile(
    r"\b(?i:documento|c[eé]dula|cedula|identificaci[oó]n|nit|dni|document|national_?id)"
    + _GAP
    + r"\b(\d{8,11})\b"
)
_PLATE = re.compile(r"\b(?i:placa|patente|plate|license_?plate)" + _GAP + r"\b([A-Z]{3}[0-9]{3})\b")


def main() -> int:
    try:
        # Read stdin as UTF-8 explicitly: on Windows sys.stdin defaults to the
        # locale codepage (cp1252), which would mangle accented domain keywords
        # like "cédula" in the JSON payload.
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return 0

    ti = data.get("tool_input") or {}
    content = " ".join(str(ti.get(k) or "") for k in ("content", "new_string"))

    match = _PLATE.search(content) or _DOCUMENT.search(content)
    if match:
        print(
            f"block_real_ids: un campo de identidad/placa trae un valor con forma real ({match.group(1)!r}). "
            "Usá marcadores ficticios imposibles por diseño (DOC-FIC-*, FIC-*).",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
