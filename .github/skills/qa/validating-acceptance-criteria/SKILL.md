---
name: validating-acceptance-criteria
description: "Maps each acceptance criterion to concrete test evidence and scores it SATISFIED, PARTIAL, or UNMET. Use when tests have run and AC are available from parsing-requirements, or when a traceability matrix and Acceptance dimension verdict are needed."
---

# validating-acceptance-criteria

Map each acceptance criterion to concrete test evidence. Score every AC as SATISFIED, PARTIAL, or UNMET. Any non-SATISFIED AC fails the Acceptance dimension.

## Quick Reference

**Phase:** post-coding  
**Inputs:**
- `acceptance_criteria` (array, required) — from parsing-requirements
- `test_results` (object, required) — test runner output
- `git_diff` (string, required) — diff for implementation evidence

**Outputs:**
- `criteria` — per-AC status and evidence map
- `satisfied` / `partial` / `unmet` — counts per status
- `verdict` — PASS | FAIL

**Depends on:** parsing-requirements  
**Works better with:** analyzing-coverage (enriches coverage evidence per AC)

**Load before starting:** `rules/qa-standards.md` — AC traceability requirements and test independence rules

## When to Use

Post-coding, after tests have run. Requires AC list from `parsing-requirements` and test results. Optionally enriched by `analyzing-coverage` data.

## Instructions

1. For each AC, search for evidence across three sources:
   - **Test names/descriptions:** Semantic alignment between AC text and test descriptions
   - **Git diff:** Implementation logic that addresses the AC
   - **Coverage data** (if available from `analyzing-coverage`): Whether relevant code paths are covered

2. Run `scripts/ac-evidence-mapper.py` for keyword-based matching as a baseline.
   **Script unavailable:** manually read each AC and search the test files for test names or assertions that correspond to each criterion. Assign SATISFIED/PARTIAL/UNMET by inspection.

3. Score each AC:
   - **SATISFIED:** Test exists AND passes that directly validates this criterion
   - **PARTIAL:** Code exists that addresses the AC but no test covers it, OR test exists but is skipped/failing
   - **UNMET:** No evidence of implementation or testing

4. Determine verdict:
   - Any PARTIAL or UNMET → **FAIL**
   - All SATISFIED → **PASS**

5. Output evidence map for reviewer traceability:
   ```json
   {
     "criteria": [
       {
         "id": "AC-1",
         "text": "Password must be 8-64 characters",
         "status": "SATISFIED",
         "evidence": {
           "tests": ["test_password_min_length", "test_password_max_length"],
           "diff_files": ["src/auth/validate.ts"],
           "coverage": 92.0
         }
       }
     ],
     "satisfied": 3,
     "partial": 1,
     "unmet": 0,
     "verdict": "FAIL"
   }
   ```

## Guardrails

- **Keyword match ≠ coverage.** A test named "test_password" doesn't mean it tests the right thing — read the test body.
- **PARTIAL is not a soft pass.** It counts as a gap in the Acceptance dimension.
- **Never SATISFIED on code-only evidence.** Implementation without a passing test is PARTIAL at best.
- **Preserve AC text exactly.** Don't rephrase criteria in the output.

## Output

Write AC validation results to the `## Copilot Workpad` issue comment:
```markdown
### QA: acceptance-criteria
verdict: PASS | FAIL
satisfied: N | partial: N | unmet: N
[per-AC breakdown with evidence test names]
```

## Consumers

- `generating-qa-report` — receives Acceptance dimension verdict and per-AC evidence map
