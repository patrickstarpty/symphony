#!/usr/bin/env bash
# Compare coverage before and after a change.
# Usage: ./test-coverage-delta.sh <before_coverage_json> <after_coverage_json>
# Input: Two JSON files with {lines: N, branches: N, functions: N} percentages.
# Output: JSON {delta: {lines, branches, functions}, regression: bool}

set -euo pipefail

BEFORE="${1:?Usage: test-coverage-delta.sh <before.json> <after.json>}"
AFTER="${2:?Usage: test-coverage-delta.sh <before.json> <after.json>}"

python3 -c "
import json, sys

with open('$BEFORE') as f:
    before = json.load(f)
with open('$AFTER') as f:
    after = json.load(f)

delta = {}
regression = False
for key in ['lines', 'branches', 'functions']:
    b = before.get(key, 0)
    a = after.get(key, 0)
    delta[key] = round(a - b, 2)
    if a < b:
        regression = True

result = {'delta': delta, 'regression': regression}
if regression:
    result['warning'] = 'Coverage decreased — review refactoring step'

json.dump(result, sys.stdout, indent=2)
"
