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
