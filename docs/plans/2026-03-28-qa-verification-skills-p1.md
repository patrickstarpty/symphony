# QA Verification Skills — P1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the 6 P1 QA verification skills (SKILL.md + scripts + references + evals) and 2 rules files, ready for use by the QA Evaluator agent inside Copilot CLI sessions.

**Architecture:** Each skill is a directory under `.github/skills/qa/` following the anthropics/skills structure: `SKILL.md` (agent instructions), `scripts/` (Python stdlib helper scripts), `references/` (domain knowledge), `templates/` (Liquid templates), `evals/` (test-prompts.yaml + assertions.yaml). Skills are standalone — no shared runtime, no package install. Scripts are invoked by the agent via shell. The QA TDD extension lives at a separate path from the Superpowers TDD skill and loads in addition to it.

**Tech Stack:** Markdown (SKILL.md), Python 3.12+ stdlib only (scripts), YAML (evals, frontmatter), Liquid (templates)

**Spec:** `docs/specs/2026-03-28-qa-skills-quick-win-design.md` §4 (P1 Skills), §7 (Rules), §8 (Evals)

---

## File Structure

```
.github/skills/qa/
├── parsing-requirements/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── extract-ac.py
│   │   └── ambiguity-detector.py
│   ├── references/
│   │   └── ambiguity-signals.md
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
├── test-driven-development/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── tdd-rhythm-checker.sh
│   │   └── test-coverage-delta.sh
│   ├── references/
│   │   ├── test-design-techniques.md
│   │   ├── insurance-domain-patterns.md
│   │   └── testing-anti-patterns.md
│   ├── templates/
│   │   ├── jest.test.ts.liquid
│   │   ├── pytest.py.liquid
│   │   ├── playwright.spec.ts.liquid
│   │   └── junit.java.liquid
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
├── analyzing-coverage/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── coverage-report.py
│   │   └── coverage-gap-analyzer.py
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
├── validating-acceptance-criteria/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── ac-evidence-mapper.py
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
├── classifying-test-failures/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── retry-failures.sh
│   │   └── classify-failure.py
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
├── generating-qa-report/
│   ├── SKILL.md
│   ├── templates/
│   │   └── qa-report.md.liquid
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
└── rules/
    ├── qa-standards.md
    └── tdd-rules.md
```

**Total files: 38** (6 SKILL.md + 10 scripts + 3 references + 5 templates + 12 eval files + 2 rules)

---

## Task 1: Directory scaffold and rules files

Create the directory tree and the two P1 rules files. Rules are foundational — skills reference them.

**Files:**
- Create: `.github/skills/qa/rules/qa-standards.md`
- Create: `.github/skills/qa/rules/tdd-rules.md`

- [ ] **Step 1: Create directory scaffold**

```bash
mkdir -p .github/skills/qa/{parsing-requirements/{scripts,references,evals},test-driven-development/{scripts,references,templates,evals},analyzing-coverage/{scripts,evals},validating-acceptance-criteria/{scripts,evals},classifying-test-failures/{scripts,evals},generating-qa-report/{templates,evals},rules}
```

- [ ] **Step 2: Verify directory structure**

Run: `find .github/skills/qa -type d | sort`

Expected: 20 directories matching the file structure above.

- [ ] **Step 3: Write qa-standards.md**

```markdown
# QA Standards

> Injected into agent context during QA evaluation. Declarative quality principles — skills implement the procedures.

## Test Quality

- Every public function/method must have at least one test.
- Tests must be independent — no shared mutable state, no ordering dependencies.
- Follow AAA (Arrange-Act-Assert) structure. One logical assertion per test.
- Test names describe the behavior under test: `test_<unit>_<scenario>_<expected>`.
- No test should take longer than 5 seconds in isolation (excluding integration tests).

## Coverage

- Default threshold: ≥80% line coverage.
- Error handling paths are mandatory coverage targets for Critical and High components.
- Coverage is a signal, not a goal — don't inflate with trivial tests.
- Missing coverage data → verdict "unavailable", not silent pass.

## Acceptance Criteria

- Every AC must be traceable to at least one test.
- Untestable ACs (vague, ambiguous) must be flagged, not silently skipped.
- SATISFIED requires both implementation AND passing test evidence.
- PARTIAL is not a soft pass — it counts as a gap.

## Test Data

- Never use real customer data in any test environment.
- PII in test data must be obviously fake ("Jane Doe", "555-0100", "123 Test St").
- Insurance policy numbers must not match real carrier formats.
- Test data should cover realistic distributions, not just happy paths.

## Failure Handling

- Flaky tests are reported but do not block the quality gate.
- Environment issues (ECONNREFUSED, ETIMEDOUT, OOM) are distinct from real bugs.
- Only consistent assertion failures count toward FAIL verdict.
- Max 2 retries per failed test in P1.
```

- [ ] **Step 4: Write tdd-rules.md**

```markdown
# TDD Rules

> Enforced during coding phase. QA extension supplements — never contradicts — Superpowers TDD.

## Red-Green-Refactor Cycle

1. **Red:** Write a failing test that describes the desired behavior.
2. **Verify Red:** Run the test. Confirm it fails for the expected reason (not a syntax error).
3. **Green:** Write the minimum implementation to make the test pass.
4. **Verify Green:** Run the test. Confirm it passes.
5. **Refactor:** Improve structure while keeping all tests green.

## Enforcement

- Test files must be committed before or alongside implementation files — never after.
- No implementation-only commits (commits touching `src/` must also touch `tests/` or `test/`).
- The Red phase is never skippable — writing a test after the implementation defeats TDD's design benefit.

## Test Design Techniques

- **Equivalence Partitioning:** Group inputs into classes that should behave identically. One test per class.
- **Boundary Value Analysis:** Test at exact boundaries (min, min+1, max-1, max) plus one step outside.
- **Decision Tables:** For multi-condition logic, enumerate input combinations systematically.

## Exceptions

These do NOT require TDD:
- Configuration files (`.env`, `config.yaml`, `tsconfig.json`)
- Database migrations (schema-only DDL)
- Third-party wrapper functions with no business logic
- Generated code (protobuf stubs, OpenAPI clients)

## Framework Detection

Auto-detect from project files:
- `package.json` with `jest` or `vitest` → Jest/Vitest templates
- `pyproject.toml` or `setup.py` with `pytest` → pytest templates
- `playwright.config.ts` → Playwright templates
- `pom.xml` or `build.gradle` with JUnit → JUnit templates
```

- [ ] **Step 5: Commit**

```bash
git add .github/skills/qa/
git commit -m "feat(qa-skills): scaffold P1 directory structure and rules files

Create .github/skills/qa/ tree for 6 P1 skills plus rules/.
Add qa-standards.md (test quality, coverage, AC, test data, failure handling).
Add tdd-rules.md (Red-Green-Refactor cycle, enforcement, techniques, exceptions)."
```

---

## Task 2: parsing-requirements skill

The pipeline entry point. Extracts structured ACs from issue descriptions, detects ambiguity, flags missing info.

**Files:**
- Create: `.github/skills/qa/parsing-requirements/SKILL.md`
- Create: `.github/skills/qa/parsing-requirements/scripts/extract-ac.py`
- Create: `.github/skills/qa/parsing-requirements/scripts/ambiguity-detector.py`
- Create: `.github/skills/qa/parsing-requirements/references/ambiguity-signals.md`
- Create: `.github/skills/qa/parsing-requirements/evals/test-prompts.yaml`
- Create: `.github/skills/qa/parsing-requirements/evals/assertions.yaml`

- [ ] **Step 1: Write SKILL.md**

```markdown
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
```

- [ ] **Step 2: Write scripts/extract-ac.py**

```python
#!/usr/bin/env python3
"""Extract acceptance criteria from issue descriptions using regex + heuristics.

Usage: python extract-ac.py < issue_description.txt
Output: JSON array of {id, text, source} objects to stdout.

Supports formats:
- Markdown bullet lists under AC headers
- Given-When-Then blocks
- Numbered requirements
- JIRA-style "h3. Acceptance Criteria" sections
"""

import json
import re
import sys


def extract_ac_sections(text: str) -> list[str]:
    """Find sections likely to contain acceptance criteria."""
    patterns = [
        # Markdown headers
        r"(?:^|\n)#{1,3}\s*(?:acceptance\s+criteria|requirements|expected\s+behavior|ac)\s*\n([\s\S]*?)(?=\n#{1,3}\s|\Z)",
        # JIRA headers
        r"(?:^|\n)h[1-3]\.\s*(?:acceptance\s+criteria|requirements)\s*\n([\s\S]*?)(?=\nh[1-3]\.|\Z)",
    ]
    sections = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            sections.append(match.group(1).strip())
    return sections if sections else [text]


def extract_bullets(text: str) -> list[str]:
    """Extract bullet points and numbered items."""
    items = []
    for line in text.split("\n"):
        stripped = line.strip()
        # Markdown bullets: - item, * item, + item
        bullet_match = re.match(r"^[-*+]\s+(.+)$", stripped)
        if bullet_match:
            items.append(bullet_match.group(1).strip())
            continue
        # Numbered: 1. item, 1) item
        num_match = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if num_match:
            items.append(num_match.group(1).strip())
            continue
    return items


def extract_gwt(text: str) -> list[str]:
    """Extract Given-When-Then blocks as single AC strings."""
    pattern = r"(Given\s+.+?\s+When\s+.+?\s+Then\s+.+?)(?=\n\s*Given|\n\s*\n|\Z)"
    matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
    return [re.sub(r"\s+", " ", m).strip() for m in matches]


def deduplicate(items: list[str]) -> list[str]:
    """Remove near-duplicate items (case-insensitive)."""
    seen = set()
    result = []
    for item in items:
        normalized = item.lower().strip().rstrip(".")
        if normalized not in seen and len(normalized) > 5:
            seen.add(normalized)
            result.append(item)
    return result


def main():
    text = sys.stdin.read()
    if not text.strip():
        json.dump([], sys.stdout, indent=2)
        return

    all_items = []
    for section in extract_ac_sections(text):
        all_items.extend(extract_bullets(section))
        all_items.extend(extract_gwt(section))

    # Fallback: if no structured items found, split sentences
    if not all_items:
        sentences = re.split(r"[.!]\s+", text)
        all_items = [s.strip() for s in sentences if len(s.strip()) > 10]

    items = deduplicate(all_items)
    output = []
    for i, item in enumerate(items, 1):
        output.append({
            "id": f"AC-{i}",
            "text": item,
            "source": "gwt" if item.lower().startswith("given") else "bullet",
        })

    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Write scripts/ambiguity-detector.py**

```python
#!/usr/bin/env python3
"""Detect ambiguity signals in acceptance criteria text.

Usage: echo '{"criteria": [...]}' | python ambiguity-detector.py
Input: JSON with "criteria" array of {id, text} objects.
Output: JSON with "flags" array of {id, signal, category, suggestion}.
"""

import json
import re
import sys

VAGUE_VERBS = [
    ("appropriate", "Define specific behavior or values"),
    ("proper", "Specify exact requirements"),
    ("correct", "Define expected output precisely"),
    ("good", "Quantify with measurable criteria"),
    ("nice", "Specify visual/UX requirements"),
    ("fast", "Define latency threshold (e.g., <200ms p95)"),
    ("efficient", "Define resource budget (memory, CPU, time)"),
    ("secure", "List specific security requirements (OWASP)"),
    ("robust", "Define failure scenarios and expected handling"),
    ("user-friendly", "Specify usability criteria or standards"),
    ("intuitive", "Define expected user workflow steps"),
    ("reasonable", "Provide specific numeric bounds"),
    ("adequate", "Provide specific numeric bounds"),
    ("sufficient", "Provide specific numeric bounds"),
    ("handle.*gracefully", "Define error response format and status codes"),
]

MISSING_THRESHOLDS = [
    (r"\blarge\s+(?:number|amount|volume)\b", "Specify exact quantity or range"),
    (r"\bmany\b", "Specify exact count"),
    (r"\bquickly\b", "Specify time threshold"),
    (r"\bsoon\b", "Specify time threshold"),
    (r"\boften\b", "Specify frequency"),
    (r"\bmost\b", "Specify percentage or count"),
    (r"\bsome\b", "Specify exact count or percentage"),
    (r"\bfew\b", "Specify exact count"),
    (r"\bseveral\b", "Specify exact count"),
    (r"\bminimal\b", "Specify exact threshold"),
]

UNDEFINED_TERMS = [
    (r"\betc\.?\b", "List all items explicitly"),
    (r"\band\s+so\s+on\b", "List all items explicitly"),
    (r"\bsimilar\b", "Define similarity criteria"),
    (r"\bsuch\s+as\b.*$", "Provide exhaustive list or define boundary"),
    (r"\brelated\b", "Define the relationship explicitly"),
    (r"\bas\s+needed\b", "Define trigger conditions"),
    (r"\bif\s+(?:necessary|applicable)\b", "Define when it applies"),
]


def detect(criteria: list[dict]) -> list[dict]:
    flags = []
    for ac in criteria:
        ac_id = ac.get("id", "?")
        text = ac.get("text", "")
        text_lower = text.lower()

        for pattern, suggestion in VAGUE_VERBS:
            if re.search(rf"\b{pattern}\b", text_lower):
                flags.append({
                    "id": ac_id,
                    "signal": pattern.replace(".*", " "),
                    "category": "vague_verb",
                    "suggestion": suggestion,
                })

        for pattern, suggestion in MISSING_THRESHOLDS:
            if re.search(pattern, text_lower):
                match = re.search(pattern, text_lower)
                flags.append({
                    "id": ac_id,
                    "signal": match.group(0) if match else pattern,
                    "category": "missing_threshold",
                    "suggestion": suggestion,
                })

        for pattern, suggestion in UNDEFINED_TERMS:
            if re.search(pattern, text_lower):
                match = re.search(pattern, text_lower)
                flags.append({
                    "id": ac_id,
                    "signal": match.group(0) if match else pattern,
                    "category": "undefined_term",
                    "suggestion": suggestion,
                })

    return flags


def main():
    data = json.load(sys.stdin)
    criteria = data.get("criteria", [])
    flags = detect(criteria)
    json.dump({"flags": flags, "total": len(flags)}, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Write references/ambiguity-signals.md**

```markdown
# Ambiguity Signals Reference

Quick-reference for the agent when evaluating AC quality.

## Red-Flag Words

| Category | Examples | Why It's Ambiguous |
|----------|----------|--------------------|
| Vague qualifiers | appropriate, proper, correct, good | No measurable definition |
| Missing thresholds | large, many, quickly, soon, often | No numeric bound |
| Undefined scope | etc., and so on, similar, related | Open-ended list |
| Implicit behavior | as needed, if necessary, when applicable | Trigger undefined |
| Subjective quality | user-friendly, intuitive, clean, elegant | Observer-dependent |

## Common Missing Requirements

- Error messages: What text? What format? What HTTP status?
- Rate limiting: How many requests? Per what window?
- Accessibility: WCAG level? Screen reader support?
- Performance: Latency target? Throughput? Under what load?
- Edge cases: Empty input? Max length? Concurrent access?
- Security: Authentication? Authorization? Input validation?

## Testability Checklist

An AC is testable if you can answer YES to all:
1. Can I write an automated assertion for this? (observable output)
2. Is the expected result unambiguous? (one correct answer)
3. Can I set up the preconditions? (reproducible)
4. Can I run it independently? (no external dependencies implied)
```

- [ ] **Step 5: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "pr-tc-001"
    description: "Password validation with one ambiguous criterion"
    input:
      issue_description: |
        Add password validation to the signup form.
        - Password must be 8-64 characters
        - Must contain at least one uppercase letter and one number
        - Should display appropriate error messages
        - Must not allow previously breached passwords (HaveIBeenPwned API)
    expected:
      acceptance_criteria_count: 4
      testable_count: 3
      ambiguity_flags: ["AC-3: 'appropriate' is vague"]

  - id: "pr-tc-002"
    description: "Clear well-structured AC with no ambiguity"
    input:
      issue_description: |
        ## Acceptance Criteria
        - Given a user on the login page, when they enter valid credentials, then they are redirected to /dashboard
        - Given a user on the login page, when they enter invalid credentials, then they see "Invalid email or password" error
        - Given a user who is already logged in, when they visit /login, then they are redirected to /dashboard
    expected:
      acceptance_criteria_count: 3
      testable_count: 3
      ambiguity_flags: []

  - id: "pr-tc-003"
    description: "Issue with critical missing information"
    input:
      issue_description: |
        Implement the payment processing feature. Users should be able to pay with credit cards and the system should handle errors gracefully.
    expected:
      acceptance_criteria_count_gte: 1
      ambiguity_flags_contain: ["gracefully"]
      missing_contain: ["error message specification", "rate limiting"]

  - id: "pr-tc-004"
    description: "Empty issue description"
    input:
      issue_description: ""
    expected:
      acceptance_criteria_count: 0
      missing_contain: ["No acceptance criteria found"]
```

- [ ] **Step 6: Write evals/assertions.yaml**

```yaml
assertions:
  - test_case: "pr-tc-001"
    checks:
      - { field: "acceptance_criteria", operator: "length_equals", value: 4 }
      - { field: "acceptance_criteria[2].testable", operator: "equals", value: false }
      - { field: "ambiguities", operator: "length_gte", value: 1 }
      - { field: "ambiguities[0]", operator: "contains", value: "appropriate" }

  - test_case: "pr-tc-002"
    checks:
      - { field: "acceptance_criteria", operator: "length_equals", value: 3 }
      - { field: "ambiguities", operator: "length_equals", value: 0 }
      - { field: "acceptance_criteria[0].text", operator: "contains", value: "Given" }

  - test_case: "pr-tc-003"
    checks:
      - { field: "acceptance_criteria", operator: "length_gte", value: 1 }
      - { field: "ambiguities", operator: "length_gte", value: 1 }
      - { field: "missing", operator: "length_gte", value: 1 }

  - test_case: "pr-tc-004"
    checks:
      - { field: "acceptance_criteria", operator: "length_equals", value: 0 }
      - { field: "missing", operator: "length_gte", value: 1 }
```

- [ ] **Step 7: Verify file count**

Run: `find .github/skills/qa/parsing-requirements -type f | wc -l`

Expected: 6 files

- [ ] **Step 8: Commit**

```bash
git add .github/skills/qa/parsing-requirements/
git commit -m "feat(qa-skills): add parsing-requirements skill (P1)

SKILL.md with full frontmatter, instructions, guardrails.
Scripts: extract-ac.py (regex+heuristic AC extraction), ambiguity-detector.py (vague verb/threshold/term flagging).
Reference: ambiguity-signals.md.
Evals: 4 test cases covering clear AC, ambiguity, missing info, empty input."
```

---

## Task 3: test-driven-development QA extension

QA extension to the existing Superpowers TDD skill. Lives at a different path, loads in addition to Superpowers TDD, never contradicts it.

**Files:**
- Create: `.github/skills/qa/test-driven-development/SKILL.md`
- Create: `.github/skills/qa/test-driven-development/scripts/tdd-rhythm-checker.sh`
- Create: `.github/skills/qa/test-driven-development/scripts/test-coverage-delta.sh`
- Create: `.github/skills/qa/test-driven-development/references/test-design-techniques.md`
- Create: `.github/skills/qa/test-driven-development/references/insurance-domain-patterns.md`
- Create: `.github/skills/qa/test-driven-development/references/testing-anti-patterns.md`
- Create: `.github/skills/qa/test-driven-development/templates/jest.test.ts.liquid`
- Create: `.github/skills/qa/test-driven-development/templates/pytest.py.liquid`
- Create: `.github/skills/qa/test-driven-development/templates/playwright.spec.ts.liquid`
- Create: `.github/skills/qa/test-driven-development/templates/junit.java.liquid`
- Create: `.github/skills/qa/test-driven-development/evals/test-prompts.yaml`
- Create: `.github/skills/qa/test-driven-development/evals/assertions.yaml`

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: test-driven-development
version: "1.0.0-qa"
description: "Enforce TDD Red-Green-Refactor: generate test cases from AC, write failing tests, implement, verify"
category: enforcement
phase: during-coding
platforms: ["all"]
dependencies: ["parsing-requirements"]
extends: "../test-driven-development/SKILL.md"
input_schema:
  - name: "acceptance_criteria"
    type: "array"
    required: true
  - name: "framework"
    type: "string"
    required: false
    description: "jest | pytest | playwright | junit. Auto-detected if omitted."
output_schema:
  - name: "test_cases"
    type: "array"
  - name: "test_files"
    type: "array"
  - name: "tdd_log"
    type: "array"
---

# test-driven-development (QA Extension)

> **Loading:** This extension loads *in addition to* the Superpowers TDD skill at `.github/skills/test-driven-development/`. On conflict, Superpowers wins. This skill only adds net-new content under `## QA Enhancements` headers.

## QA Enhancements

### 1. Test Case Generation from AC

For each acceptance criterion from `parsing-requirements`, generate test cases using:

**Equivalence Partitioning:**
- Group inputs into classes that should produce identical behavior
- One test per equivalence class (valid + invalid partitions)
- Example: age validation → {negative, 0, 1-17, 18-120, 121+}

**Boundary Value Analysis:**
- Test at exact boundaries: min, min+1, max-1, max
- Test one step outside: min-1, max+1
- Example: 8-64 char password → test at 7, 8, 9, 63, 64, 65

**Decision Tables:**
- For multi-condition logic, enumerate input combinations
- Each row = one test case
- Example: discount eligibility (member? coupon? min-order?) → 8 combinations

### 2. Enhanced TDD Flow

1. **Analyze AC** → build test case matrix using techniques above
2. **Red** → generate test skeleton from `templates/<framework>.liquid` (AAA structure)
3. **Verify Red** → run test, confirm expected failure reason (not syntax error)
4. **Green** → write minimum implementation to pass
5. **Verify Green** → run all tests, confirm pass
6. **Refactor** → improve structure, run tests again

### 3. Framework Detection

Auto-detect from project files (see `tdd-rules.md § Framework Detection`). If ambiguous, ask. Generate from matching template in `templates/`.

### 4. Rhythm Verification

Run `scripts/tdd-rhythm-checker.sh` after each cycle to verify:
- Test file committed before or with implementation
- No implementation-only commits
- Red phase was not skipped (test existed before passing)

Run `scripts/test-coverage-delta.sh` to verify:
- Coverage increased or held steady after Green phase
- No coverage regression after Refactor phase

## Domain Patterns

Load `references/insurance-domain-patterns.md` for insurance-specific test patterns:
- Policy lifecycle (quote → bind → endorse → renew → cancel)
- Claims processing (FNOL → investigation → adjudication → payment)
- Premium calculation (rating factors, tiered pricing, minimum premium)
- Regulatory compliance (state-specific rules, filing requirements)

## Guardrails

- **Never skip Red phase.** Writing a test after implementation defeats TDD's design benefit.
- **No tests for exceptions** listed in `tdd-rules.md § Exceptions`.
- **Never contradict Superpowers TDD** core principles. QA adds, never overrides.
- **One assertion per test** (logical assertion — multiple `expect()` for one behavior is fine).
```

- [ ] **Step 2: Write scripts/tdd-rhythm-checker.sh**

```bash
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
```

- [ ] **Step 3: Write scripts/test-coverage-delta.sh**

```bash
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
```

- [ ] **Step 4: Write references/test-design-techniques.md**

```markdown
# Test Design Techniques

## Equivalence Partitioning (EP)

Divide input domain into classes where all values in a class should produce the same behavior.

**How to apply:**
1. Identify input parameters
2. For each parameter, define valid and invalid partitions
3. Write one test per partition

**Example — age validation (18-65):**
| Partition | Range | Expected | Test Value |
|-----------|-------|----------|------------|
| Below minimum (invalid) | < 18 | reject | 10 |
| Valid range | 18-65 | accept | 30 |
| Above maximum (invalid) | > 65 | reject | 80 |

## Boundary Value Analysis (BVA)

Test at exact boundaries where behavior changes.

**How to apply:**
1. Identify boundaries from EP partitions
2. Test: min-1, min, min+1, max-1, max, max+1

**Example — age validation (18-65):**
| Point | Value | Expected |
|-------|-------|----------|
| min-1 | 17 | reject |
| min | 18 | accept |
| min+1 | 19 | accept |
| max-1 | 64 | accept |
| max | 65 | accept |
| max+1 | 66 | reject |

## Decision Tables

For logic with multiple conditions, enumerate combinations.

**Example — discount eligibility:**
| Member? | Coupon? | Order > $50? | Discount |
|---------|---------|--------------|----------|
| Y | Y | Y | 20% |
| Y | Y | N | 15% |
| Y | N | Y | 10% |
| Y | N | N | 5% |
| N | Y | Y | 10% |
| N | Y | N | 5% |
| N | N | Y | 0% |
| N | N | N | 0% |

## State Transition Testing

For stateful systems, test all valid transitions and reject invalid ones.

**How to apply:**
1. Draw state diagram
2. Test every valid transition
3. Test at least one invalid transition per state
```

- [ ] **Step 5: Write references/insurance-domain-patterns.md**

```markdown
# Insurance Domain Test Patterns

## Policy Lifecycle

Test the complete state machine:
```
Quote → Application → Underwriting → Bind → Active → Endorse → Renew → Cancel
                         ↓
                      Decline
```

**Key test scenarios:**
- Quote-to-bind happy path
- Mid-term endorsement (coverage change, address change)
- Renewal with premium change
- Cancellation with pro-rata refund calculation
- Reinstatement after lapse
- Declined application (underwriting rules)

## Claims Processing

```
FNOL → Assignment → Investigation → Adjudication → Payment → Close
  ↓                                      ↓
Duplicate                             Denial → Appeal
```

**Key test scenarios:**
- FNOL with all required fields
- Duplicate claim detection
- Subrogation identification
- Reserve calculation and adjustment
- Payment with deductible application
- Denial with required notice generation

## Premium Calculation

**Rating factors to test:**
- Base rate by coverage type
- Territory/location modifier
- Claims history modifier (0-claim discount, surcharge for at-fault)
- Multi-policy discount
- Deductible credit
- Minimum premium floor
- State-specific surcharges and fees

**Edge cases:**
- Minimum premium applies (calculated < floor)
- Maximum discount cap
- Overlapping discount rules
- Mid-term rate change effective dating
- Leap year handling in pro-rata calculations

## Regulatory Compliance

- State-specific cancellation notice periods (10/30/60 days)
- Required form filings by state
- Rate filing effective dates
- Surplus lines tax calculations
- Residual market mechanisms
```

- [ ] **Step 6: Write references/testing-anti-patterns.md**

```markdown
# Testing Anti-Patterns

Patterns that reduce test value. The QA agent should flag these during review.

## Structural Anti-Patterns

**The Giant Test:** Single test with 20+ assertions testing multiple behaviors. Split into focused tests.

**Shared Mutable State:** Tests depend on execution order because they share data. Each test must set up its own state.

**The Liar:** Test that always passes regardless of implementation. Usually a missing assertion or a tautological check (`expect(true).toBe(true)`).

**Test-Per-Method:** Mechanical 1:1 mapping of tests to methods. Test behaviors, not methods.

## Data Anti-Patterns

**Magic Numbers:** `expect(result).toBe(42)` — where does 42 come from? Use named constants or derive from inputs.

**Hardcoded Dates:** `new Date("2024-01-15")` breaks when timezone changes or year rolls over. Use relative dates or freeze time.

**Production Data in Tests:** Real customer data in fixtures. Use obviously fake data.

## Process Anti-Patterns

**Implementation-First Testing:** Writing tests after code. Defeats TDD design benefits and tends to test implementation rather than behavior.

**Testing Private Methods:** Reaching into internals. Test the public interface instead.

**Flaky Acceptance:** Accepting intermittent failures as "known flaky." Either fix the flakiness or delete the test.

**Coverage Gaming:** Adding trivial tests (`toString()`, getters/setters) to hit a number. Coverage should reflect meaningful test scenarios.
```

- [ ] **Step 7: Write templates/jest.test.ts.liquid**

```
// {{ test_name }}
// Generated by QA TDD skill — {{ skill_version }}
// AC: {{ ac_id }} — {{ ac_text }}

import { {{ subject }} } from '{{ module_path }}';

describe('{{ describe_block }}', () => {
  {% for tc in test_cases %}
  it('{{ tc.description }}', () => {
    // Arrange
    {{ tc.arrange }}

    // Act
    {{ tc.act }}

    // Assert
    {{ tc.assert }}
  });
  {% endfor %}
});
```

- [ ] **Step 8: Write templates/pytest.py.liquid**

```
"""{{ test_name }}

Generated by QA TDD skill — {{ skill_version }}
AC: {{ ac_id }} — {{ ac_text }}
"""

import pytest
from {{ module_path }} import {{ subject }}


class Test{{ class_name }}:
    {% for tc in test_cases %}
    def test_{{ tc.name }}(self):
        # Arrange
        {{ tc.arrange }}

        # Act
        {{ tc.act }}

        # Assert
        {{ tc.assert }}
    {% endfor %}
```

- [ ] **Step 9: Write templates/playwright.spec.ts.liquid**

```
// {{ test_name }}
// Generated by QA TDD skill — {{ skill_version }}
// AC: {{ ac_id }} — {{ ac_text }}

import { test, expect } from '@playwright/test';

test.describe('{{ describe_block }}', () => {
  {% for tc in test_cases %}
  test('{{ tc.description }}', async ({ page }) => {
    // Arrange
    {{ tc.arrange }}

    // Act
    {{ tc.act }}

    // Assert
    {{ tc.assert }}
  });
  {% endfor %}
});
```

- [ ] **Step 10: Write templates/junit.java.liquid**

```
// {{ test_name }}
// Generated by QA TDD skill — {{ skill_version }}
// AC: {{ ac_id }} — {{ ac_text }}

package {{ package }};

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

@DisplayName("{{ describe_block }}")
class {{ class_name }}Test {
    {% for tc in test_cases %}
    @Test
    @DisplayName("{{ tc.description }}")
    void {{ tc.method_name }}() {
        // Arrange
        {{ tc.arrange }}

        // Act
        {{ tc.act }}

        // Assert
        {{ tc.assert }}
    }
    {% endfor %}
}
```

- [ ] **Step 11: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "tdd-tc-001"
    description: "Simple single-AC feature: password length validation"
    input:
      acceptance_criteria:
        - { id: "AC-1", text: "Password must be 8-64 characters", testable: true }
      framework: "jest"
    expected:
      test_cases_count_gte: 4
      techniques_used: ["boundary_value_analysis"]
      boundaries: [7, 8, 64, 65]
      tdd_phases: ["red", "verify_red", "green", "verify_green", "refactor"]

  - id: "tdd-tc-002"
    description: "Multi-AC feature: login flow with 3 criteria"
    input:
      acceptance_criteria:
        - { id: "AC-1", text: "Valid credentials redirect to /dashboard", testable: true }
        - { id: "AC-2", text: "Invalid credentials show error message", testable: true }
        - { id: "AC-3", text: "Already logged-in user redirected from /login", testable: true }
      framework: "playwright"
    expected:
      test_cases_count_gte: 3
      test_files_count_gte: 1
      all_ac_covered: true

  - id: "tdd-tc-003"
    description: "Boundary-heavy feature: age-based insurance discount"
    input:
      acceptance_criteria:
        - { id: "AC-1", text: "Customers aged 25-65 get standard rate", testable: true }
        - { id: "AC-2", text: "Customers under 25 pay 15% surcharge", testable: true }
        - { id: "AC-3", text: "Customers over 65 pay 10% surcharge", testable: true }
      framework: "pytest"
    expected:
      test_cases_count_gte: 8
      techniques_used: ["equivalence_partitioning", "boundary_value_analysis"]
      boundaries: [24, 25, 65, 66]
```

- [ ] **Step 12: Write evals/assertions.yaml**

```yaml
assertions:
  - test_case: "tdd-tc-001"
    checks:
      - { field: "test_cases", operator: "length_gte", value: 4 }
      - { field: "test_cases[*].technique", operator: "contains_any", value: "boundary_value_analysis" }
      - { field: "tdd_log", operator: "length_gte", value: 1 }
      - { field: "tdd_log[0].phase", operator: "equals", value: "red" }

  - test_case: "tdd-tc-002"
    checks:
      - { field: "test_cases", operator: "length_gte", value: 3 }
      - { field: "test_files", operator: "length_gte", value: 1 }
      - { field: "test_files[0]", operator: "contains", value: ".spec.ts" }

  - test_case: "tdd-tc-003"
    checks:
      - { field: "test_cases", operator: "length_gte", value: 8 }
      - { field: "test_cases[*].technique", operator: "contains_any", value: ["equivalence_partitioning", "boundary_value_analysis"] }
```

- [ ] **Step 13: Verify file count**

Run: `find .github/skills/qa/test-driven-development -type f | wc -l`

Expected: 12 files

- [ ] **Step 14: Commit**

```bash
git add .github/skills/qa/test-driven-development/
git commit -m "feat(qa-skills): add test-driven-development QA extension (P1)

SKILL.md extending Superpowers TDD with AC-based test generation,
equivalence partitioning, BVA, decision tables, insurance domain patterns.
Scripts: tdd-rhythm-checker.sh, test-coverage-delta.sh.
References: test-design-techniques.md, insurance-domain-patterns.md, testing-anti-patterns.md.
Templates: jest, pytest, playwright, junit (Liquid).
Evals: 3 test cases."
```

---

## Task 4: analyzing-coverage skill

Interprets coverage reports beyond simple threshold checks — assesses risk per uncovered path.

**Files:**
- Create: `.github/skills/qa/analyzing-coverage/SKILL.md`
- Create: `.github/skills/qa/analyzing-coverage/scripts/coverage-report.py`
- Create: `.github/skills/qa/analyzing-coverage/scripts/coverage-gap-analyzer.py`
- Create: `.github/skills/qa/analyzing-coverage/evals/test-prompts.yaml`
- Create: `.github/skills/qa/analyzing-coverage/evals/assertions.yaml`

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: analyzing-coverage
version: "1.0.0"
description: "Interpret coverage gaps, assess risk, suggest which untested paths matter most"
category: evaluation
phase: post-coding
platforms: ["all"]
dependencies: []
soft_dependencies: ["scoring-risk"]
input_schema:
  - name: "coverage_data"
    type: "object"
    required: true
  - name: "threshold"
    type: "number"
    required: false
    description: "Default: 80"
  - name: "component_criticality"
    type: "string"
    required: false
    description: "critical | high | medium | low"
output_schema:
  - name: "summary"
    type: "object"
    description: "Lines, branches, functions percentages"
  - name: "verdict"
    type: "string"
  - name: "gaps"
    type: "array"
    description: "Uncovered paths with risk and suggestions"
---

# analyzing-coverage

Interpret coverage reports beyond "is the number above threshold." Assess which uncovered paths carry the most risk and suggest where to add tests.

## When to Use

After test execution completes (post-coding). Feeds into `generating-qa-report` (Coverage dimension) and optionally enriches `validating-acceptance-criteria`.

## Instructions

1. Parse coverage data using `scripts/coverage-report.py`:
   - Accepts Istanbul (JSON), JaCoCo (XML), coverage.py (JSON), lcov formats
   - Outputs standardized JSON: `{lines: N, branches: N, functions: N, files: [...]}`

2. Compare line/branch/function against threshold (default 80%, override via input or `scoring-risk` P3 dynamic thresholds).

3. Per uncovered file, assess risk:
   - **Critical:** Error handling, security-sensitive, payment/auth logic
   - **High:** User-facing features, data mutation, API endpoints
   - **Medium:** Business logic, internal services
   - **Low:** Utilities, helpers, formatters

4. Run `scripts/coverage-gap-analyzer.py` for specific untested paths — identifies uncovered branches, error handlers, edge cases.

5. Suggest concrete test cases for high-risk gaps (description only, not code).

6. Output:
   ```json
   {
     "summary": {"lines": 85.2, "branches": 72.1, "functions": 91.0},
     "verdict": "PASS",
     "gaps": [
       {"file": "src/payments/retry.ts", "risk": "critical", "uncovered": "catch block L45-52", "suggestion": "Test payment timeout retry logic"}
     ]
   }
   ```

## Guardrails

- **Coverage is a signal, not a goal.** Don't suggest trivial tests to inflate numbers.
- **No data → "unavailable" verdict.** Never silently pass when coverage data is missing.
- **Don't inflate.** Suggesting tests for getters/setters/toString to hit threshold is an anti-pattern.
- **P3 enhancement:** When `scoring-risk` output is available, use dynamic thresholds (critical=95%, high=85%, medium=80%, low=70%).
```

- [ ] **Step 2: Write scripts/coverage-report.py**

```python
#!/usr/bin/env python3
"""Parse coverage reports from multiple tools into standardized JSON.

Usage: python coverage-report.py <format> < coverage_data
Formats: istanbul, jacoco, coverage-py, lcov
Output: Standardized JSON to stdout.
"""

import json
import re
import sys
import xml.etree.ElementTree as ET


def parse_istanbul(data: dict) -> dict:
    """Parse Istanbul/NYC JSON coverage format."""
    total_lines = 0
    covered_lines = 0
    total_branches = 0
    covered_branches = 0
    total_functions = 0
    covered_functions = 0
    files = []

    for filepath, file_data in data.items():
        s = file_data.get("s", {})
        b = file_data.get("b", {})
        f = file_data.get("f", {})

        file_lines = len(s)
        file_covered = sum(1 for v in s.values() if v > 0)
        file_branches = sum(len(arr) for arr in b.values())
        file_branch_covered = sum(1 for arr in b.values() for v in arr if v > 0)
        file_funcs = len(f)
        file_func_covered = sum(1 for v in f.values() if v > 0)

        total_lines += file_lines
        covered_lines += file_covered
        total_branches += file_branches
        covered_branches += file_branch_covered
        total_functions += file_funcs
        covered_functions += file_func_covered

        if file_lines > 0:
            pct = round(file_covered / file_lines * 100, 1)
            files.append({"path": filepath, "lines": pct})

    return {
        "lines": round(covered_lines / total_lines * 100, 1) if total_lines else 0,
        "branches": round(covered_branches / total_branches * 100, 1) if total_branches else 0,
        "functions": round(covered_functions / total_functions * 100, 1) if total_functions else 0,
        "files": sorted(files, key=lambda f: f["lines"]),
    }


def parse_lcov(text: str) -> dict:
    """Parse LCOV .info format."""
    total_lines = 0
    covered_lines = 0
    total_branches = 0
    covered_branches = 0
    total_functions = 0
    covered_functions = 0
    files = []
    current_file = None
    file_total = 0
    file_covered = 0

    for line in text.strip().split("\n"):
        if line.startswith("SF:"):
            current_file = line[3:]
            file_total = 0
            file_covered = 0
        elif line.startswith("LF:"):
            file_total = int(line[3:])
            total_lines += file_total
        elif line.startswith("LH:"):
            file_covered = int(line[3:])
            covered_lines += file_covered
        elif line.startswith("BRF:"):
            total_branches += int(line[4:])
        elif line.startswith("BRH:"):
            covered_branches += int(line[4:])
        elif line.startswith("FNF:"):
            total_functions += int(line[4:])
        elif line.startswith("FNH:"):
            covered_functions += int(line[4:])
        elif line.startswith("end_of_record"):
            if current_file and file_total > 0:
                pct = round(file_covered / file_total * 100, 1)
                files.append({"path": current_file, "lines": pct})

    return {
        "lines": round(covered_lines / total_lines * 100, 1) if total_lines else 0,
        "branches": round(covered_branches / total_branches * 100, 1) if total_branches else 0,
        "functions": round(covered_functions / total_functions * 100, 1) if total_functions else 0,
        "files": sorted(files, key=lambda f: f["lines"]),
    }


def parse_coverage_py(data: dict) -> dict:
    """Parse coverage.py JSON format."""
    totals = data.get("totals", {})
    files_data = data.get("files", {})
    files = []

    for filepath, file_data in files_data.items():
        summary = file_data.get("summary", {})
        pct = summary.get("percent_covered", 0)
        files.append({"path": filepath, "lines": round(pct, 1)})

    return {
        "lines": round(totals.get("percent_covered", 0), 1),
        "branches": round(totals.get("percent_covered_branches", 0), 1),
        "functions": 0,  # coverage.py doesn't track function coverage
        "files": sorted(files, key=lambda f: f["lines"]),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: coverage-report.py <istanbul|jacoco|coverage-py|lcov>", file=sys.stderr)
        sys.exit(1)

    fmt = sys.argv[1]
    raw = sys.stdin.read()

    if fmt == "istanbul":
        data = json.loads(raw)
        result = parse_istanbul(data)
    elif fmt == "lcov":
        result = parse_lcov(raw)
    elif fmt == "coverage-py":
        data = json.loads(raw)
        result = parse_coverage_py(data)
    elif fmt == "jacoco":
        # JaCoCo XML parsing
        root = ET.fromstring(raw)
        counters = {}
        for counter in root.findall(".//counter"):
            ctype = counter.get("type", "").lower()
            missed = int(counter.get("missed", 0))
            covered = int(counter.get("covered", 0))
            if ctype in counters:
                counters[ctype]["missed"] += missed
                counters[ctype]["covered"] += covered
            else:
                counters[ctype] = {"missed": missed, "covered": covered}

        def pct(key):
            c = counters.get(key, {"missed": 0, "covered": 0})
            total = c["missed"] + c["covered"]
            return round(c["covered"] / total * 100, 1) if total else 0

        result = {
            "lines": pct("line"),
            "branches": pct("branch"),
            "functions": pct("method"),
            "files": [],
        }
    else:
        print(f"Unknown format: {fmt}", file=sys.stderr)
        sys.exit(1)

    json.dump(result, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Write scripts/coverage-gap-analyzer.py**

```python
#!/usr/bin/env python3
"""Analyze coverage gaps and categorize by risk.

Usage: echo '{"files": [...], "threshold": 80}' | python coverage-gap-analyzer.py
Input: JSON with standardized coverage files array and threshold.
Output: JSON with gaps categorized by risk.
"""

import json
import re
import sys

# Path patterns indicating higher risk
CRITICAL_PATTERNS = [
    r"(?:payment|billing|charge|refund|transaction)",
    r"(?:auth|login|session|token|credential|password|oauth)",
    r"(?:encrypt|decrypt|hash|sign|verify|secret)",
]

HIGH_PATTERNS = [
    r"(?:api|endpoint|route|controller|handler)",
    r"(?:user|account|profile|registration)",
    r"(?:claim|policy|premium|underwriting)",
    r"(?:mutation|write|update|delete|create)",
]

MEDIUM_PATTERNS = [
    r"(?:service|repository|domain|model|entity)",
    r"(?:validation|sanitize|parse|transform)",
]

LOW_PATTERNS = [
    r"(?:util|helper|format|convert|constant|config)",
    r"(?:logger|debug|trace|metric)",
    r"(?:type|interface|enum|dto|schema)",
]


def classify_risk(filepath: str) -> str:
    """Classify file risk based on path patterns."""
    path_lower = filepath.lower()
    for pattern in CRITICAL_PATTERNS:
        if re.search(pattern, path_lower):
            return "critical"
    for pattern in HIGH_PATTERNS:
        if re.search(pattern, path_lower):
            return "high"
    for pattern in MEDIUM_PATTERNS:
        if re.search(pattern, path_lower):
            return "medium"
    return "low"


def main():
    data = json.load(sys.stdin)
    files = data.get("files", [])
    threshold = data.get("threshold", 80)

    gaps = []
    for f in files:
        path = f.get("path", "")
        lines = f.get("lines", 100)

        if lines < threshold:
            risk = classify_risk(path)
            gap = {
                "file": path,
                "coverage": lines,
                "shortfall": round(threshold - lines, 1),
                "risk": risk,
            }
            gaps.append(gap)

    # Sort: critical first, then by shortfall descending
    risk_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    gaps.sort(key=lambda g: (risk_order.get(g["risk"], 4), -g["shortfall"]))

    json.dump({
        "gaps": gaps,
        "total_below_threshold": len(gaps),
        "critical_gaps": sum(1 for g in gaps if g["risk"] == "critical"),
        "high_gaps": sum(1 for g in gaps if g["risk"] == "high"),
    }, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "cov-tc-001"
    description: "High coverage — should PASS"
    input:
      coverage_data:
        lines: 92.5
        branches: 85.0
        functions: 95.0
        files:
          - { path: "src/payments/process.ts", lines: 88.0 }
          - { path: "src/utils/format.ts", lines: 98.0 }
      threshold: 80
    expected:
      verdict: "PASS"
      gaps_count: 0

  - id: "cov-tc-002"
    description: "Low coverage — should FAIL with gaps"
    input:
      coverage_data:
        lines: 62.0
        branches: 45.0
        functions: 70.0
        files:
          - { path: "src/auth/login.ts", lines: 40.0 }
          - { path: "src/payments/refund.ts", lines: 55.0 }
          - { path: "src/utils/logger.ts", lines: 72.0 }
      threshold: 80
    expected:
      verdict: "FAIL"
      gaps_count_gte: 2
      critical_or_high_gap_exists: true

  - id: "cov-tc-003"
    description: "Medium coverage on critical component — risk-aware verdict"
    input:
      coverage_data:
        lines: 78.0
        branches: 65.0
        functions: 82.0
        files:
          - { path: "src/payments/charge.ts", lines: 75.0 }
          - { path: "src/auth/oauth.ts", lines: 68.0 }
      threshold: 80
      component_criticality: "critical"
    expected:
      verdict: "FAIL"
      gaps_contain_risk: "critical"
```

- [ ] **Step 5: Write evals/assertions.yaml**

```yaml
assertions:
  - test_case: "cov-tc-001"
    checks:
      - { field: "verdict", operator: "equals", value: "PASS" }
      - { field: "summary.lines", operator: "gte", value: 80 }

  - test_case: "cov-tc-002"
    checks:
      - { field: "verdict", operator: "equals", value: "FAIL" }
      - { field: "gaps", operator: "length_gte", value: 2 }
      - { field: "gaps[0].risk", operator: "in", value: ["critical", "high"] }

  - test_case: "cov-tc-003"
    checks:
      - { field: "verdict", operator: "equals", value: "FAIL" }
      - { field: "gaps", operator: "length_gte", value: 1 }
```

- [ ] **Step 6: Verify file count**

Run: `find .github/skills/qa/analyzing-coverage -type f | wc -l`

Expected: 5 files

- [ ] **Step 7: Commit**

```bash
git add .github/skills/qa/analyzing-coverage/
git commit -m "feat(qa-skills): add analyzing-coverage skill (P1)

SKILL.md with risk-aware coverage interpretation.
Scripts: coverage-report.py (Istanbul/JaCoCo/coverage.py/lcov parser),
coverage-gap-analyzer.py (risk classification by file path patterns).
Evals: 3 test cases (high pass, low fail, critical component)."
```

---

## Task 5: validating-acceptance-criteria skill

Maps ACs to test evidence and scores each as SATISFIED/PARTIAL/UNMET.

**Files:**
- Create: `.github/skills/qa/validating-acceptance-criteria/SKILL.md`
- Create: `.github/skills/qa/validating-acceptance-criteria/scripts/ac-evidence-mapper.py`
- Create: `.github/skills/qa/validating-acceptance-criteria/evals/test-prompts.yaml`
- Create: `.github/skills/qa/validating-acceptance-criteria/evals/assertions.yaml`

- [ ] **Step 1: Write SKILL.md**

```markdown
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
```

- [ ] **Step 2: Write scripts/ac-evidence-mapper.py**

```python
#!/usr/bin/env python3
"""Map acceptance criteria to test evidence using keyword extraction and fuzzy matching.

Usage: echo '{"criteria": [...], "test_names": [...], "diff_files": [...]}' | python ac-evidence-mapper.py
Input: JSON with criteria array, test_names array, diff_files array.
Output: JSON with mappings per AC.
"""

import json
import re
import sys
from collections import defaultdict


def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from text, ignoring stop words."""
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "must", "need", "to", "of",
        "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
        "and", "or", "but", "not", "no", "if", "then", "when", "that", "this",
        "it", "its", "they", "them", "their", "we", "our", "you", "your",
    }
    # Split on non-alphanumeric, lowercase
    words = re.findall(r"[a-z]+", text.lower())
    return {w for w in words if w not in stop_words and len(w) > 2}


def normalize_test_name(name: str) -> str:
    """Convert test name patterns to space-separated words."""
    # camelCase → space-separated
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    # snake_case → space-separated
    name = name.replace("_", " ").replace("-", " ")
    return name.lower()


def match_score(ac_keywords: set[str], target_keywords: set[str]) -> float:
    """Calculate overlap score between keyword sets."""
    if not ac_keywords or not target_keywords:
        return 0.0
    intersection = ac_keywords & target_keywords
    return len(intersection) / len(ac_keywords)


def main():
    data = json.load(sys.stdin)
    criteria = data.get("criteria", [])
    test_names = data.get("test_names", [])
    diff_files = data.get("diff_files", [])

    # Pre-process test names
    test_keyword_map = {}
    for name in test_names:
        normalized = normalize_test_name(name)
        test_keyword_map[name] = extract_keywords(normalized)

    # Pre-process diff files
    file_keyword_map = {}
    for path in diff_files:
        filename = path.split("/")[-1].split(".")[0]
        normalized = normalize_test_name(filename)
        file_keyword_map[path] = extract_keywords(normalized)

    mappings = []
    for ac in criteria:
        ac_keywords = extract_keywords(ac.get("text", ""))
        ac_id = ac.get("id", "?")

        # Find matching tests
        matched_tests = []
        for test_name, test_keywords in test_keyword_map.items():
            score = match_score(ac_keywords, test_keywords)
            if score >= 0.3:  # 30% keyword overlap threshold
                matched_tests.append({"name": test_name, "score": round(score, 2)})

        matched_tests.sort(key=lambda t: t["score"], reverse=True)

        # Find matching diff files
        matched_files = []
        for filepath, file_keywords in file_keyword_map.items():
            score = match_score(ac_keywords, file_keywords)
            if score >= 0.2:  # Lower threshold for files
                matched_files.append({"path": filepath, "score": round(score, 2)})

        matched_files.sort(key=lambda f: f["score"], reverse=True)

        mappings.append({
            "id": ac_id,
            "keywords": sorted(ac_keywords),
            "matched_tests": matched_tests[:5],
            "matched_files": matched_files[:5],
            "has_test_evidence": len(matched_tests) > 0,
            "has_code_evidence": len(matched_files) > 0,
        })

    json.dump({"mappings": mappings}, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "vac-tc-001"
    description: "All AC satisfied with full test evidence"
    input:
      acceptance_criteria:
        - { id: "AC-1", text: "Password must be 8-64 characters", testable: true }
        - { id: "AC-2", text: "Must contain uppercase letter and number", testable: true }
      test_results:
        passed: ["test_password_min_length", "test_password_max_length", "test_password_uppercase_required", "test_password_number_required"]
        failed: []
      git_diff: "diff --git a/src/auth/validate.ts ..."
    expected:
      satisfied: 2
      partial: 0
      unmet: 0
      verdict: "PASS"

  - id: "vac-tc-002"
    description: "Mixed results — one PARTIAL (code but no test)"
    input:
      acceptance_criteria:
        - { id: "AC-1", text: "Password must be 8-64 characters", testable: true }
        - { id: "AC-2", text: "Must show error for breached passwords", testable: true }
      test_results:
        passed: ["test_password_length"]
        failed: []
      git_diff: "diff --git a/src/auth/validate.ts ... +checkBreachedPassword()"
    expected:
      satisfied: 1
      partial: 1
      unmet: 0
      verdict: "FAIL"

  - id: "vac-tc-003"
    description: "Keyword match but wrong test body — should not be SATISFIED"
    input:
      acceptance_criteria:
        - { id: "AC-1", text: "User can reset password via email link", testable: true }
      test_results:
        passed: ["test_password_validation"]
        failed: []
      git_diff: "diff --git a/src/auth/validate.ts ..."
    expected:
      verdict: "FAIL"
      note: "test_password_validation tests validation, not reset flow — keyword overlap is misleading"

  - id: "vac-tc-004"
    description: "Zero test evidence — all UNMET"
    input:
      acceptance_criteria:
        - { id: "AC-1", text: "Dashboard loads within 2 seconds", testable: true }
        - { id: "AC-2", text: "Dashboard shows user's recent activity", testable: true }
      test_results:
        passed: []
        failed: []
      git_diff: ""
    expected:
      satisfied: 0
      unmet: 2
      verdict: "FAIL"
```

- [ ] **Step 4: Write evals/assertions.yaml**

```yaml
assertions:
  - test_case: "vac-tc-001"
    checks:
      - { field: "verdict", operator: "equals", value: "PASS" }
      - { field: "satisfied", operator: "equals", value: 2 }
      - { field: "partial", operator: "equals", value: 0 }

  - test_case: "vac-tc-002"
    checks:
      - { field: "verdict", operator: "equals", value: "FAIL" }
      - { field: "partial", operator: "gte", value: 1 }

  - test_case: "vac-tc-003"
    checks:
      - { field: "verdict", operator: "equals", value: "FAIL" }
      - { field: "criteria[0].status", operator: "not_equals", value: "SATISFIED" }

  - test_case: "vac-tc-004"
    checks:
      - { field: "verdict", operator: "equals", value: "FAIL" }
      - { field: "unmet", operator: "equals", value: 2 }
      - { field: "satisfied", operator: "equals", value: 0 }
```

- [ ] **Step 5: Verify and commit**

Run: `find .github/skills/qa/validating-acceptance-criteria -type f | wc -l`

Expected: 4 files

```bash
git add .github/skills/qa/validating-acceptance-criteria/
git commit -m "feat(qa-skills): add validating-acceptance-criteria skill (P1)

SKILL.md with SATISFIED/PARTIAL/UNMET scoring per AC.
Script: ac-evidence-mapper.py (keyword extraction + fuzzy matching).
Evals: 4 test cases (all pass, mixed, keyword-mislead, zero evidence)."
```

---

## Task 6: classifying-test-failures skill

Classifies failures as real-bug, flaky, or environment-issue via retry and pattern analysis.

**Files:**
- Create: `.github/skills/qa/classifying-test-failures/SKILL.md`
- Create: `.github/skills/qa/classifying-test-failures/scripts/retry-failures.sh`
- Create: `.github/skills/qa/classifying-test-failures/scripts/classify-failure.py`
- Create: `.github/skills/qa/classifying-test-failures/evals/test-prompts.yaml`
- Create: `.github/skills/qa/classifying-test-failures/evals/assertions.yaml`

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: classifying-test-failures
version: "1.0.0"
description: "Classify failures as real-bug, flaky, or environment-issue via retry and pattern analysis"
category: evaluation
phase: post-coding
platforms: ["all"]
dependencies: []
input_schema:
  - name: "failed_tests"
    type: "array"
    required: true
  - name: "test_command"
    type: "string"
    required: true
  - name: "retry_count"
    type: "number"
    required: false
    description: "Default: 2"
output_schema:
  - name: "classifications"
    type: "array"
  - name: "real_bugs"
    type: "number"
  - name: "flaky"
    type: "number"
  - name: "env_issues"
    type: "number"
  - name: "verdict"
    type: "string"
    description: "PASS if zero real-bugs"
---

# classifying-test-failures

Classify test failures into actionable categories: real bugs that need fixing, flaky tests that need stabilization, and environment issues that need infrastructure attention.

## When to Use

Post-coding, when test execution has failures. Feeds the Pass Rate dimension into `generating-qa-report`. Also consumed by `healing-broken-tests` (P3).

## Instructions

1. Run `scripts/retry-failures.sh` for each failed test (up to retry_count, default 2):
   - Re-runs each failed test in isolation
   - Captures exit code and stderr for each attempt

2. Classify based on retry results and error patterns:
   - **real-bug:** Consistent assertion error with identical stack trace across all retries
   - **flaky:** Passes on retry, or fails with different error messages across retries
   - **env-issue:** Error matches environment patterns (connection refused, timeout, OOM, port conflict)

3. Run `scripts/classify-failure.py` for pattern-based error matching as a secondary signal.

4. Determine verdict:
   - **PASS:** Zero real-bugs (flaky and env-issues reported but don't block)
   - **FAIL:** One or more real-bugs

5. Output:
   ```json
   {
     "classifications": [
       {
         "test": "test_payment_retry",
         "category": "real-bug",
         "error": "AssertionError: Expected 3 got 0",
         "retries": 2,
         "consistent": true
       },
       {
         "test": "test_ws_reconnect",
         "category": "flaky",
         "error": "Timeout: 5000ms",
         "retries": 2,
         "passed_on_retry": true
       }
     ],
     "real_bugs": 1,
     "flaky": 1,
     "env_issues": 0,
     "verdict": "FAIL"
   }
   ```

## Guardrails

- **Max 2 retries in P1.** Don't burn CI time with excessive retries.
- **Passing on retry = flaky, not fixed.** Don't silently promote to passing.
- **Identical assertion across all retries = real bug.** Don't classify as flaky just because it's intermittent.
- **P3 enhancement:** Historical pass rate analysis via Knowledge Base replaces simple retry heuristics.
```

- [ ] **Step 2: Write scripts/retry-failures.sh**

```bash
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
```

- [ ] **Step 3: Write scripts/classify-failure.py**

```python
#!/usr/bin/env python3
"""Classify test failure errors by pattern matching.

Usage: echo '{"failures": [...]}' | python classify-failure.py
Input: JSON with failures array of {test, error} objects.
Output: JSON with classifications.
"""

import json
import re
import sys

ENV_PATTERNS = [
    (r"ECONNREFUSED", "Connection refused — service not running"),
    (r"ETIMEDOUT", "Connection timeout — network or service issue"),
    (r"ECONNRESET", "Connection reset — service crashed or restarted"),
    (r"EADDRINUSE", "Port already in use — cleanup needed"),
    (r"ENOMEM|OOM|out of memory", "Out of memory — resource constraint"),
    (r"ENOSPC", "No disk space — cleanup needed"),
    (r"EPERM|EACCES|permission denied", "Permission denied — filesystem issue"),
    (r"docker.*not found|container.*not running", "Docker container not available"),
    (r"could not connect to.*database", "Database connection failed"),
    (r"redis.*connection.*refused", "Redis not available"),
]

FLAKY_PATTERNS = [
    (r"timeout.*\d+ms|timed?\s*out", "Timeout — possibly flaky under load"),
    (r"race\s*condition|data\s*race", "Race condition detected"),
    (r"stale\s*element|element.*detached", "DOM element detached — timing issue"),
    (r"socket\s*hang\s*up", "Socket hang up — intermittent network"),
]

REAL_BUG_PATTERNS = [
    (r"AssertionError|AssertError|assert.*fail", "assertion"),
    (r"Expected.*(?:got|received|but was)", "assertion"),
    (r"TypeError|ReferenceError|AttributeError", "type_error"),
    (r"NameError|ImportError|ModuleNotFoundError", "import_error"),
    (r"NullPointerException|null.*reference", "null_reference"),
    (r"IndexError|ArrayIndexOutOfBoundsException", "bounds_error"),
    (r"KeyError|NoSuchElementException", "missing_key"),
]


def classify(error: str) -> tuple[str, str]:
    """Return (category, reason) for an error string."""
    for pattern, reason in ENV_PATTERNS:
        if re.search(pattern, error, re.IGNORECASE):
            return ("env-issue", reason)

    for pattern, reason in FLAKY_PATTERNS:
        if re.search(pattern, error, re.IGNORECASE):
            return ("flaky", reason)

    for pattern, reason in REAL_BUG_PATTERNS:
        if re.search(pattern, error, re.IGNORECASE):
            return ("real-bug", reason)

    return ("unknown", "No matching pattern — manual review needed")


def main():
    data = json.load(sys.stdin)
    failures = data.get("failures", [])

    classifications = []
    for f in failures:
        test = f.get("test", "unknown")
        error = f.get("error", "")
        category, reason = classify(error)
        classifications.append({
            "test": test,
            "category": category,
            "reason": reason,
            "error_snippet": error[:200],
        })

    counts = {"real-bug": 0, "flaky": 0, "env-issue": 0, "unknown": 0}
    for c in classifications:
        counts[c["category"]] = counts.get(c["category"], 0) + 1

    json.dump({
        "classifications": classifications,
        "real_bugs": counts["real-bug"],
        "flaky": counts["flaky"],
        "env_issues": counts["env-issue"],
        "unknown": counts["unknown"],
    }, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "cf-tc-001"
    description: "Three failures: real bug + flaky + env issue"
    input:
      failed_tests:
        - { name: "test_payment_retry", error: "AssertionError: Expected 3 got 0" }
        - { name: "test_ws_reconnect", error: "Timeout: 5000ms" }
        - { name: "test_db_rollback", error: "ECONNREFUSED 127.0.0.1:5432" }
      test_command: "npm test"
      retry_count: 2
    expected:
      real_bugs: 1
      flaky: 1
      env_issues: 1
      verdict: "FAIL"

  - id: "cf-tc-002"
    description: "All failures are environment issues — should PASS"
    input:
      failed_tests:
        - { name: "test_api_integration", error: "ECONNREFUSED 127.0.0.1:8080" }
        - { name: "test_redis_cache", error: "redis connection refused" }
      test_command: "pytest"
      retry_count: 2
    expected:
      real_bugs: 0
      env_issues: 2
      verdict: "PASS"

  - id: "cf-tc-003"
    description: "Flaky test that passes on retry"
    input:
      failed_tests:
        - { name: "test_concurrent_writes", error: "Timeout: 10000ms" }
      test_command: "jest --runInBand"
      retry_count: 2
    expected:
      flaky: 1
      real_bugs: 0
      verdict: "PASS"
```

- [ ] **Step 5: Write evals/assertions.yaml**

```yaml
assertions:
  - test_case: "cf-tc-001"
    checks:
      - { field: "verdict", operator: "equals", value: "FAIL" }
      - { field: "real_bugs", operator: "equals", value: 1 }
      - { field: "flaky", operator: "gte", value: 1 }
      - { field: "env_issues", operator: "gte", value: 1 }

  - test_case: "cf-tc-002"
    checks:
      - { field: "verdict", operator: "equals", value: "PASS" }
      - { field: "real_bugs", operator: "equals", value: 0 }
      - { field: "env_issues", operator: "equals", value: 2 }

  - test_case: "cf-tc-003"
    checks:
      - { field: "verdict", operator: "equals", value: "PASS" }
      - { field: "flaky", operator: "gte", value: 1 }
      - { field: "real_bugs", operator: "equals", value: 0 }
```

- [ ] **Step 6: Verify and commit**

Run: `find .github/skills/qa/classifying-test-failures -type f | wc -l`

Expected: 5 files

```bash
git add .github/skills/qa/classifying-test-failures/
git commit -m "feat(qa-skills): add classifying-test-failures skill (P1)

SKILL.md with retry-based classification: real-bug, flaky, env-issue.
Scripts: retry-failures.sh (isolated reruns), classify-failure.py (pattern matching).
Evals: 3 test cases (mixed, env-only, flaky-retry)."
```

---

## Task 7: generating-qa-report skill

Aggregates the three evaluation dimensions into a single QA Report with quality gate verdict.

**Files:**
- Create: `.github/skills/qa/generating-qa-report/SKILL.md`
- Create: `.github/skills/qa/generating-qa-report/templates/qa-report.md.liquid`
- Create: `.github/skills/qa/generating-qa-report/evals/test-prompts.yaml`
- Create: `.github/skills/qa/generating-qa-report/evals/assertions.yaml`

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: generating-qa-report
version: "1.0.0"
description: "Aggregate evaluation dimensions into structured QA Report for issue workpad"
category: evaluation
phase: post-coding
platforms: ["all"]
dependencies: ["analyzing-coverage", "validating-acceptance-criteria", "classifying-test-failures"]
input_schema:
  - name: "coverage_result"
    type: "object"
    required: true
  - name: "acceptance_result"
    type: "object"
    required: true
  - name: "failure_result"
    type: "object"
    required: true
  - name: "issue_id"
    type: "string"
    required: true
  - name: "gate_policy"
    type: "string"
    required: false
    description: "strict | advisory (default: advisory)"
output_schema:
  - name: "report_markdown"
    type: "string"
  - name: "verdict"
    type: "string"
  - name: "dimensions"
    type: "array"
---

# generating-qa-report

Aggregate the three evaluation dimensions (Pass Rate, Coverage, Acceptance) into a single QA Report. This is the quality gate decision point.

## When to Use

After all three P1 evaluation skills have produced their outputs. This is the final aggregation step before the verdict is written to the issue workpad.

## Instructions

1. Collect outputs from the three evaluation skills:
   - **Pass Rate** from `classifying-test-failures`: verdict + real_bugs count
   - **Coverage** from `analyzing-coverage`: verdict + summary percentages
   - **Acceptance** from `validating-acceptance-criteria`: verdict + satisfied/partial/unmet counts

2. Apply gate policy:
   - **strict:** ALL three dimensions must PASS → overall PASS. Any FAIL → overall FAIL.
   - **advisory** (default): Report all dimensions. No blocking — verdict is informational.

3. Generate markdown report from `templates/qa-report.md.liquid`:
   - Header: issue ID, evaluator, overall verdict
   - Dimension table: score, threshold, status per dimension
   - Details: test summary, coverage gaps, AC traceability matrix
   - Advisory note: if advisory mode, state what would fail under strict

4. Output markdown + structured verdict for programmatic consumption.

## Gate Policy Behavior

| Policy | PASS condition | FAIL behavior |
|--------|---------------|---------------|
| strict | All 3 dimensions PASS | Blocks issue transition |
| advisory | Report only | Warns but does not block |

## Guardrails

- **Reproducible given same inputs.** Same dimension results → same report, always.
- **Never omit a failing dimension.** Even in advisory mode, all dimensions are shown.
- **Advisory mode still states what would fail under strict.** Visibility is non-negotiable.
- **Don't editorialize.** Report facts, don't add subjective commentary.

## Consumers

- Issue workpad (written as markdown comment)
- `reviewing-code-quality` (P3) — QA gates must pass before code review
- `healing-broken-tests` (P3) — prioritizes which failures to address
- `analyzing-defects` (P3) — aggregate quality trends
```

- [ ] **Step 2: Write templates/qa-report.md.liquid**

```
## QA Evaluation Report

**Issue:** {{ issue_id }}  |  **Evaluator:** QA Agent (Gemini 3 Pro)  |  **Verdict: {{ verdict }} {{ verdict_icon }}**
{% if gate_policy == "advisory" %}
> **Mode:** Advisory — results are informational. Under strict policy: {{ strict_verdict }}.
{% endif %}

| Dimension | Score | Threshold | Status |
|-----------|-------|-----------|--------|
| Pass Rate | {{ pass_rate_score }} | 100% (zero real bugs) | {{ pass_rate_status }} |
| Coverage | {{ coverage_score }} | {{ coverage_threshold }}% | {{ coverage_status }} |
| Acceptance | {{ acceptance_score }} | 100% AC satisfied | {{ acceptance_status }} |

{% if has_failures %}
### Test Failures

| Test | Category | Error |
|------|----------|-------|
{% for f in failures %}
| `{{ f.test }}` | {{ f.category }} | {{ f.error_snippet }} |
{% endfor %}

- **Real bugs:** {{ real_bugs }} (must fix)
- **Flaky:** {{ flaky }} (stabilize)
- **Environment:** {{ env_issues }} (infrastructure)
{% endif %}

{% if has_coverage_gaps %}
### Coverage Gaps

| File | Coverage | Risk | Suggestion |
|------|----------|------|------------|
{% for g in coverage_gaps %}
| `{{ g.file }}` | {{ g.coverage }}% | {{ g.risk }} | {{ g.suggestion }} |
{% endfor %}
{% endif %}

{% if has_ac_details %}
### Acceptance Criteria Traceability

| AC | Status | Evidence |
|----|--------|----------|
{% for ac in criteria %}
| {{ ac.id }}: {{ ac.text }} | {{ ac.status }} | {{ ac.evidence_summary }} |
{% endfor %}

**Satisfied:** {{ satisfied }}/{{ total_ac }}  |  **Partial:** {{ partial }}  |  **Unmet:** {{ unmet }}
{% endif %}

---
*Generated by Symphony QA Skills v1.0.0*
```

- [ ] **Step 3: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "qr-tc-001"
    description: "All dimensions pass — clean report"
    input:
      coverage_result:
        verdict: "PASS"
        summary: { lines: 92.0, branches: 85.0, functions: 95.0 }
        gaps: []
      acceptance_result:
        verdict: "PASS"
        satisfied: 4
        partial: 0
        unmet: 0
        criteria:
          - { id: "AC-1", status: "SATISFIED" }
          - { id: "AC-2", status: "SATISFIED" }
          - { id: "AC-3", status: "SATISFIED" }
          - { id: "AC-4", status: "SATISFIED" }
      failure_result:
        verdict: "PASS"
        real_bugs: 0
        flaky: 1
        env_issues: 0
        classifications:
          - { test: "test_ws", category: "flaky" }
      issue_id: "PAY-123"
      gate_policy: "strict"
    expected:
      verdict: "PASS"
      dimensions_count: 3
      report_contains: ["PAY-123", "PASS"]

  - id: "qr-tc-002"
    description: "Mixed failures — coverage and acceptance fail"
    input:
      coverage_result:
        verdict: "FAIL"
        summary: { lines: 62.0, branches: 45.0, functions: 70.0 }
        gaps:
          - { file: "src/auth/login.ts", coverage: 40.0, risk: "critical" }
      acceptance_result:
        verdict: "FAIL"
        satisfied: 2
        partial: 1
        unmet: 1
      failure_result:
        verdict: "PASS"
        real_bugs: 0
        flaky: 0
        env_issues: 0
      issue_id: "AUTH-456"
      gate_policy: "strict"
    expected:
      verdict: "FAIL"
      failing_dimensions: ["Coverage", "Acceptance"]

  - id: "qr-tc-003"
    description: "Advisory mode — would fail strict but reports as advisory"
    input:
      coverage_result:
        verdict: "FAIL"
        summary: { lines: 72.0, branches: 60.0, functions: 80.0 }
        gaps: []
      acceptance_result:
        verdict: "PASS"
        satisfied: 3
        partial: 0
        unmet: 0
      failure_result:
        verdict: "PASS"
        real_bugs: 0
        flaky: 0
        env_issues: 0
      issue_id: "FEAT-789"
      gate_policy: "advisory"
    expected:
      verdict: "ADVISORY"
      report_contains: ["Under strict policy"]
```

- [ ] **Step 4: Write evals/assertions.yaml**

```yaml
assertions:
  - test_case: "qr-tc-001"
    checks:
      - { field: "verdict", operator: "equals", value: "PASS" }
      - { field: "dimensions", operator: "length_equals", value: 3 }
      - { field: "report_markdown", operator: "contains", value: "PAY-123" }

  - test_case: "qr-tc-002"
    checks:
      - { field: "verdict", operator: "equals", value: "FAIL" }
      - { field: "report_markdown", operator: "contains", value: "AUTH-456" }
      - { field: "report_markdown", operator: "contains", value: "critical" }

  - test_case: "qr-tc-003"
    checks:
      - { field: "report_markdown", operator: "contains", value: "Advisory" }
      - { field: "report_markdown", operator: "contains", value: "strict" }
```

- [ ] **Step 5: Verify and commit**

Run: `find .github/skills/qa/generating-qa-report -type f | wc -l`

Expected: 4 files

```bash
git add .github/skills/qa/generating-qa-report/
git commit -m "feat(qa-skills): add generating-qa-report skill (P1)

SKILL.md aggregating 3 evaluation dimensions into quality gate verdict.
Template: qa-report.md.liquid (dimension table, failures, gaps, AC traceability).
Evals: 3 test cases (all-pass, mixed-fail, advisory-mode)."
```

---

## Task 8: Final verification

Verify the complete P1 skill set is consistent and matches the spec.

- [ ] **Step 1: Verify total file count**

Run: `find .github/skills/qa -type f | wc -l`

Expected: 38 files total

- [ ] **Step 2: Verify directory structure matches spec §3**

Run: `find .github/skills/qa -type f | sort`

Compare against the file tree in the spec's §3 File Structure. Every file listed in §3 for P1 skills must exist.

- [ ] **Step 3: Verify all scripts are executable**

```bash
chmod +x .github/skills/qa/*/scripts/*.py .github/skills/qa/*/scripts/*.sh
find .github/skills/qa -name "*.py" -o -name "*.sh" | xargs ls -la
```

- [ ] **Step 4: Verify Python scripts have no syntax errors**

```bash
find .github/skills/qa -name "*.py" -exec python3 -c "import ast; ast.parse(open('{}').read()); print('OK: {}')" \;
```

Expected: "OK" for each .py file, no syntax errors.

- [ ] **Step 5: Verify YAML files parse correctly**

```bash
python3 -c "
import yaml, glob, sys
for path in sorted(glob.glob('.github/skills/qa/**//*.yaml', recursive=True)):
    try:
        with open(path) as f:
            yaml.safe_load(f)
        print(f'OK: {path}')
    except Exception as e:
        print(f'FAIL: {path} — {e}')
        sys.exit(1)
"
```

Expected: "OK" for each .yaml file.

- [ ] **Step 6: Verify SKILL.md frontmatter consistency**

Check that each SKILL.md has `name`, `version`, `description`, `category`, `phase`, `platforms`, `dependencies`, `input_schema`, `output_schema` in frontmatter. Verify `name` matches directory name for all skills except `test-driven-development` (which has version suffix `-qa`).

```bash
for skill_dir in .github/skills/qa/*/; do
    skill_name=$(basename "$skill_dir")
    skill_file="$skill_dir/SKILL.md"
    if [ -f "$skill_file" ]; then
        echo "--- $skill_name ---"
        head -30 "$skill_file" | grep -E "^(name|version|description|category|phase|dependencies):"
    fi
done
```

- [ ] **Step 7: Verify dependency references are valid**

Check that every skill referenced in `dependencies` arrays actually exists as a directory under `.github/skills/qa/`:

```bash
python3 -c "
import yaml, glob, os

skills = set()
for d in glob.glob('.github/skills/qa/*/'):
    skills.add(os.path.basename(d.rstrip('/')))

for path in sorted(glob.glob('.github/skills/qa/*/SKILL.md')):
    with open(path) as f:
        content = f.read()
    # Extract YAML frontmatter
    if content.startswith('---'):
        end = content.index('---', 3)
        fm = yaml.safe_load(content[3:end])
        deps = fm.get('dependencies', [])
        soft = fm.get('soft_dependencies', [])
        name = fm.get('name', '?')
        for dep in deps + soft:
            if dep not in skills:
                print(f'MISSING: {name} depends on \"{dep}\" which is not in P1 skills (OK if P2/P3)')
            else:
                print(f'OK: {name} → {dep}')
"
```

- [ ] **Step 8: Final commit (make scripts executable)**

```bash
git add .github/skills/qa/
git commit -m "chore(qa-skills): make all P1 scripts executable"
```

- [ ] **Step 9: Summary output**

```bash
echo "=== P1 QA Skills Summary ==="
echo "Skills: $(find .github/skills/qa -name 'SKILL.md' | wc -l)"
echo "Scripts: $(find .github/skills/qa -name '*.py' -o -name '*.sh' | wc -l)"
echo "References: $(find .github/skills/qa/*/references -type f 2>/dev/null | wc -l)"
echo "Templates: $(find .github/skills/qa/*/templates -type f 2>/dev/null | wc -l)"
echo "Eval files: $(find .github/skills/qa/*/evals -type f 2>/dev/null | wc -l)"
echo "Rules: $(find .github/skills/qa/rules -type f 2>/dev/null | wc -l)"
echo "Total: $(find .github/skills/qa -type f | wc -l)"
```

Expected:
```
Skills: 6
Scripts: 10
References: 3
Templates: 5
Eval files: 12
Rules: 2
Total: 38
```
