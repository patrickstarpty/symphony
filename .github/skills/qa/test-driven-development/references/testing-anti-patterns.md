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
