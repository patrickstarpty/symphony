# Code Review Guidelines — P3

> Declarative review standards consumed by Code Reviewer agent (Claude Sonnet 4.6) and reviewing-code-quality skill. Ensures consistent, cross-model objectivity in code quality evaluation.

## Two-Stage Review Process

All code review follows a strict two-stage process to catch spec violations before evaluating code quality.

### Stage 1: Specification Compliance

**Purpose:** Verify the implementation addresses every requirement in the AC/spec.

**Process:**
1. Parse acceptance criteria and spec requirements from issue description
2. For each requirement, search the diff for corresponding implementation
3. Check for:
   - Missing AC coverage (requirement mentioned in spec but not implemented)
   - Incomplete implementation (skeleton only, no business logic)
   - Spec-breaking changes (implementation contradicts AC)

**Verdict:**
- **PASS:** All AC requirements have implementation in the diff
- **FAIL:** One or more AC requirements unimplemented or contradicted

**Action:**
- Stage 1 FAIL → Issue REQUEST_CHANGES immediately, skip Stage 2
- Stage 1 PASS → Proceed to Stage 2

### Stage 2: Code Quality

**Purpose:** Evaluate implementation quality: readability, SOLID principles, performance, pattern consistency.

**Scope:** Only evaluate if Stage 1 passes.

**Evaluation criteria:**
- **Readability:** Function length (max 30 lines for public methods), nesting depth (max 3), meaningful names, self-documenting code
- **SOLID:** Single responsibility, no gods, dependency injection, open/closed principle, Liskov substitution, interface segregation, dependency inversion
- **Performance:** No N+1 queries, no unnecessary full-table scans, caching strategy documented, API response times <500ms p95
- **Patterns:** Consistent with codebase conventions, error handling patterns, logging standards, testing patterns
- **Security:** Input validation at boundaries, no hardcoded credentials, parameterized queries, OWASP Top 10 coverage

**Never evaluate:**
- Linter-catchable style issues (use pre-commit hooks instead)
- Formatting and whitespace
- Variable naming style (convention should be automated)

### Comment Quality Standards

**Actionable:** Every comment must suggest a specific fix.
- ✓ "Add early return to reduce nesting: `if (!condition) return;`"
- ✗ "This could be cleaner"

**Non-blocking:** Mark quality-of-life suggestions as "Optional" or "FYI".
- "Optional: Extract to a helper function for readability"

**Technical debt:** Reference issue/epic for refactoring work.
- "Technical debt [PAY-456]: Consider Query Builder pattern instead of string concat"

**Specific:** Point to exact lines and explain the impact.
- "Line 42: N+1 query in loop. Add `.eager_load(:orders)` to line 10"

## Cross-Model Protocol

**Consumption:** Code Reviewer agent (Claude Sonnet 4.6) uses this guideline as a system prompt supplement to `reviewing-code-quality` skill output.

**Objectivity:** Different model (Sonnet vs Haiku) for implementation vs review prevents self-approval bias.

**Verdict mapping:**
- reviewing-code-quality outputs: APPROVE | REQUEST_CHANGES | COMMENT
- Code Reviewer agent elevates to: ✓ Approved | ⚠ Revisions Requested | → Address Comments → Re-review

**Escalation:** If Code Reviewer disagrees with reviewing-code-quality verdict, provide detailed justification in comments. No silent overrides.

## Guardrails

- Never approve a diff that fails Stage 1 spec compliance
- Comments must be specific and actionable, not subjective
- Don't nitpick automated tool issues (lint, format)
- Quality issues should be flagged with severity:
  - **Critical:** Breaks spec, security issue, will cause production incident
  - **Major:** SOLID violation, significant performance issue
  - **Minor:** Code style inconsistency, non-blocking refactoring opportunity
- When uncertain, ask clarifying questions instead of assuming intent
