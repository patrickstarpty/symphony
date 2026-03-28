#!/usr/bin/env bash
# Retry failed tests individually and capture results.
# Usage: ./retry-failures.sh <test_command> <retry_count> <test_name_1> [test_name_2 ...]
# Output: JSON array of retry results to stdout.

set -euo pipefail

TEST_CMD="${1:?Usage: retry-failures.sh <test_command> <retry_count> <test_name...>}"
RETRY_COUNT="${2:-2}"
shift 2

results="["
first=true

for test_name in "$@"; do
    passes=0
    fails=0
    errors=()

    for ((i=1; i<=RETRY_COUNT; i++)); do
        # Run the specific test — framework-specific filtering
        stderr_file=$(mktemp)
        if eval "$TEST_CMD" --testNamePattern="$test_name" 2>"$stderr_file"; then
            passes=$((passes + 1))
        else
            fails=$((fails + 1))
            err=$(tail -5 "$stderr_file" | tr '\n' ' ' | sed 's/"/\\"/g')
            errors+=("$err")
        fi
        rm -f "$stderr_file"
    done

    if ! $first; then
        results+=","
    fi
    first=false

    # Build error array
    err_json="["
    err_first=true
    for e in "${errors[@]}"; do
        if ! $err_first; then err_json+=","; fi
        err_first=false
        err_json+="\"$e\""
    done
    err_json+="]"

    results+="{\"test\": \"$test_name\", \"passes\": $passes, \"fails\": $fails, \"errors\": $err_json}"
done

results+="]"
echo "$results"
