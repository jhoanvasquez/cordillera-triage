#!/usr/bin/env bash
# Guards the Option-A packaging decision: the plugin bundles curated COPIES of
# pieces that also live natively in .claude/. This asserts the copies have not
# drifted from their originals (byte-identical). Run in CI / pre-commit so a
# future edit to the original fails loudly instead of silently diverging.
set -euo pipefail
cd "$(dirname "$0")/.."

pairs=(
  ".claude/agents/code-reviewer.md|plugins/cordillera-devkit/agents/code-reviewer.md"
  ".claude/skills/design-review/SKILL.md|plugins/cordillera-devkit/skills/design-review/SKILL.md"
  ".claude/hooks/format.sh|plugins/cordillera-devkit/hooks/format.sh"
)

status=0
for pair in "${pairs[@]}"; do
  original="${pair%%|*}"
  copy="${pair##*|}"
  if cmp -s "$original" "$copy"; then
    echo "OK  $copy == $original"
  else
    echo "DRIFT  $copy != $original"
    status=1
  fi
done
exit "$status"
