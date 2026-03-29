---
name: reviewing-code-quality
description: "Performs two-stage code review: spec compliance first, then code quality (SOLID, complexity, security). Use when QA gates pass and a structured APPROVE/REQUEST_CHANGES/COMMENT verdict with line-level comments is needed."
---

# reviewing-code-quality

Two-stage code review: verify spec compliance first, then evaluate code quality.

## Quick Reference

**Phase:** post-coding  
**Inputs:**
- `git_diff` (string, required)
- `qa_report` (object, required) — all QA gates must pass before review proceeds
- `spec_references` (array, optional)
- `review_focus` (array, optional)

**Outputs:**
- `stage1_spec_compliance` — spec compliance result
- `stage2_code_quality` — code quality metrics and issues
- `verdict` — APPROVE | REQUEST_CHANGES | COMMENT
- `comments` — line-level review comments

**Depends on:** generating-qa-report

## When to Use

Invoke after QA report is generated and QA gates PASS. If QA gates fail, do not review code.

**Prerequisites:**
- `generating-qa-report` must complete
- All Pass Rate, Coverage, Acceptance gates must be PASS

## Instructions

### Stage 1: Specification Compliance

**Purpose:** Ensure implementation addresses every AC/spec requirement.

1. Extract acceptance criteria from issue description or QA report
2. For each AC, search diff for corresponding implementation
3. Check for:
   - Missing AC (requirement in spec, not in diff)
   - Incomplete implementation (skeleton only)
   - Spec-breaking changes (contradicts AC)

4. Run `scripts/spec-compliance-checker.py` with diff + AC list
5. Output `stage1_spec_compliance` with verdict: PASS or FAIL

**Stage 1 Verdict Logic:**
- `PASS`: All AC requirements covered in diff
- `FAIL`: Any requirement unimplemented or contradicted

**Action:**
- Stage 1 FAIL → output `verdict: REQUEST_CHANGES`, skip Stage 2
- Stage 1 PASS → proceed to Stage 2

### Stage 2: Code Quality

**Only evaluate if Stage 1 passes.**

1. Run `scripts/quality-metrics.py` on diff to extract metrics:
   - Function length
   - Cyclomatic complexity
   - Nesting depth
   - Code duplication
   - SOLID principle violations

2. Evaluate against references/code-quality-standards.md:
   - Readability (length, names, self-documentation)
   - SOLID principles (SRP, OCP, LSP, ISP, DIP)
   - Performance (N+1, caching, response times)
   - Security (input validation, hardcoded secrets)
   - Patterns (consistency with codebase)

3. Generate actionable comments (see review-guidelines.md § Comment Quality)

4. Output `stage2_code_quality` with:
   - Issues found (array of {severity, location, suggestion})
   - Overall verdict: APPROVE | REQUEST_CHANGES | COMMENT

### Final Verdict

```
if stage1 = FAIL → REQUEST_CHANGES (+ explain spec gaps)
elif stage2 = REQUEST_CHANGES → REQUEST_CHANGES
elif stage2 = COMMENT → COMMENT
else → APPROVE
```

## Consumers

- Code Reviewer agent — uses output as review summary, may expand with additional insights

## Guardrails

- Never approve if Stage 1 fails
- Every comment must be actionable and specific (not "could be better")
- Don't flag linter/formatter issues (use hooks instead)
- Quality issues should note severity: Critical | Major | Minor
- When uncertain, ask clarifying questions instead of assuming
