#!/usr/bin/env bash
# Verify TDD rhythm: test files committed before/with implementation files.
# Usage: ./tdd-rhythm-checker.sh [commits_to_check]
# Default: check last 5 commits
# Output: JSON {violations: [...], verdict: "pass"|"fail"}

set -euo pipefail

COMMITS=${1:-5}

violations=()

while IFS= read -r commit_hash; do
    # Get files changed in this commit
    files=$(git diff-tree --no-commit-id --name-only -r "$commit_hash" 2>/dev/null)

    has_src=false
    has_test=false

    while IFS= read -r file; do
        case "$file" in
            *test*|*spec*|*__tests__*|tests/*|test/*)
                has_test=true
                ;;
            src/*|lib/*|app/*|pkg/*)
                has_src=true
                ;;
        esac
    done <<< "$files"

    if $has_src && ! $has_test; then
        msg=$(git log --oneline -1 "$commit_hash" 2>/dev/null)
        violations+=("{\"commit\": \"$msg\", \"issue\": \"implementation-only commit (no test files)\"}")
    fi
done < <(git log --format='%H' -n "$COMMITS" 2>/dev/null)

if [ ${#violations[@]} -eq 0 ]; then
    echo '{"violations": [], "verdict": "pass"}'
else
    joined=$(printf ",%s" "${violations[@]}")
    joined="${joined:1}"
    echo "{\"violations\": [$joined], \"verdict\": \"fail\"}"
fi
