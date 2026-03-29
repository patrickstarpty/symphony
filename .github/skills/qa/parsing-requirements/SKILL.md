---
name: parsing-requirements
version: "1.0.0"
description: "Parse issue description into structured AC, detect ambiguities, flag missing information"
category: analysis
phase: pre-coding
platforms: ["all"]
dependencies: []
input_schema:
  - name: "issue_description"
    type: "string"
    required: true
  - name: "issue_metadata"
    type: "object"
    required: false
output_schema:
  - name: "acceptance_criteria"
    type: "array"
  - name: "ambiguities"
    type: "array"
  - name: "missing"
    type: "array"
---

# parsing-requirements

Parse issue descriptions into structured, testable acceptance criteria. Detect ambiguity and flag missing information before coding begins.

## When to Use

Invoke at the start of every issue evaluation — before `test-driven-development` and `validating-acceptance-criteria`. This is the pipeline entry point.

## Instructions

1. Extract observable behavior statements from the issue description. Look for:
   - Explicit AC sections ("Acceptance Criteria", "Requirements", "Expected Behavior")
   - Given-When-Then blocks
   - Bullet points describing behavior
   - Implicit requirements in prose

2. For each extracted statement, assess testability:
   - **Testable:** Contains specific, measurable behavior ("password must be 8-64 characters")
   - **Untestable:** Contains vague qualifiers ("should handle appropriately", "must be fast")

3. Run `scripts/extract-ac.py` on the raw issue text for regex-based extraction as a baseline.

4. Run `scripts/ambiguity-detector.py` on each AC to flag:
   - Vague verbs: "appropriate", "properly", "correctly", "good"
   - Missing thresholds: "large number", "quickly", "many"
   - Undefined terms: "etc.", "and so on", "similar"
   - Implicit assumptions: references to undocumented behavior

5. Identify missing information:
   - No error message specification
   - No rate limiting or performance requirements mentioned
   - No accessibility requirements
   - No edge case handling specified

6. Output structured JSON:
   ```json
   {
     "acceptance_criteria": [
       {"id": "AC-1", "text": "...", "testable": true},
       {"id": "AC-2", "text": "...", "testable": false, "ambiguity": "reason"}
     ],
     "ambiguities": ["AC-2: 'appropriately' needs concrete definition"],
     "missing": ["No error message specification"]
   }
   ```

## Guardrails

- **Never invent requirements.** Flag what's missing, don't fill it in.
- **Flag ambiguity, don't resolve it.** The human decides what "appropriate" means.
- **Zero extractable ACs → output `missing`** rather than fabricating criteria.
- **Preserve original wording** in the `text` field — don't rephrase.

## Consumers

- `test-driven-development` — uses AC list to generate test case matrix
- `validating-acceptance-criteria` — uses structured AC for evidence mapping
- `scoring-risk` (P3) — uses AC complexity for risk assessment
