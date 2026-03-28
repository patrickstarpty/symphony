---
name: validating-acceptance-criteria
version: "1.0.0"
description: "Map AC to test evidence, score SATISFIED/PARTIAL/UNMET per criterion"
category: evaluation
phase: post-coding
platforms: ["all"]
dependencies: ["parsing-requirements"]
soft_dependencies: ["analyzing-coverage"]
input_schema:
  - name: "acceptance_criteria"
    type: "array"
    required: true
  - name: "test_results"
    type: "object"
    required: true
  - name: "git_diff"
    type: "string"
    required: true
output_schema:
  - name: "criteria"
    type: "array"
    description: "Per-AC status + evidence"
  - name: "satisfied"
    type: "number"
  - name: "partial"
    type: "number"
  - name: "unmet"
    type: "number"
  - name: "verdict"
    type: "string"
---

# validating-acceptance-criteria

Map each acceptance criterion to concrete test evidence. Score every AC as SATISFIED, PARTIAL, or UNMET. Any non-SATISFIED AC fails the Acceptance dimension.

## When to Use

Post-coding, after tests have run. Requires AC list from `parsing-requirements` and test results. Optionally enriched by `analyzing-coverage` data.

## Instructions

1. For each AC, search for evidence across three sources:
   - **Test names/descriptions:** Semantic alignment between AC text and test descriptions
   - **Git diff:** Implementation logic that addresses the AC
   - **Coverage data** (if available from `analyzing-coverage`): Whether relevant code paths are covered

2. Run `scripts/ac-evidence-mapper.py` for keyword-based matching as a baseline.

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
