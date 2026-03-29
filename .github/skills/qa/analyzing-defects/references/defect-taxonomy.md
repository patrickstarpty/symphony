# Defect Taxonomy — Reference

Classification system for test failures and production defects.

## Root Cause Categories

### Logic Errors

**Definition:** Bugs in implementation logic (algorithms, conditionals, state management).

**Examples:**
- Off-by-one error in loop
- Null pointer dereference
- Incorrect conditional (if/else)
- State not updated correctly
- Missing edge case handling

**Indicators:**
- Test assertion fails with unexpected value
- Calculation incorrect
- Boundary conditions fail

**Prevention:**
- Type-safe languages + strict mode
- Comprehensive boundary value testing
- Peer code review
- Table-driven test cases

### Integration Errors

**Definition:** Bugs at module/service boundaries (API contracts, async patterns, dependencies).

**Examples:**
- API response format mismatch
- Async promise not awaited
- Missing dependency import
- Mock/stub not matching real behavior
- Service initialization order

**Indicators:**
- Works in isolation, fails in integration
- Timing-dependent failures
- Contract violation messages
- Import/dependency errors

**Prevention:**
- Contract testing (Pact, OpenAPI validation)
- Integration test coverage
- Async/await pattern enforcement
- Dependency injection

### Data Errors

**Definition:** Bugs in data handling (validation, transformation, schema mismatch).

**Examples:**
- Unvalidated user input
- Type mismatch (string vs number)
- Schema version mismatch
- Missing required field
- Invalid data range

**Indicators:**
- Data validation error
- Type assertion failure
- Schema mismatch messages
- Null/undefined where value expected

**Prevention:**
- Input validation at boundaries
- Strong typing (TypeScript, Python type hints)
- Schema validation (JSON Schema, Protobuf)
- Test data factories

### Configuration Errors

**Definition:** Bugs due to environment/runtime configuration.

**Examples:**
- Wrong environment variables
- Hardcoded values in code
- Missing configuration file
- Secrets exposed in code
- Version/compatibility mismatch

**Indicators:**
- Passes locally, fails on CI/production
- Environment-specific failure
- Configuration not found error
- Version incompatibility

**Prevention:**
- Externalize all configuration
- Environment validation on startup
- Secret management (vault, env vars)
- Compatibility testing across versions

### Concurrency Errors

**Definition:** Bugs in concurrent/parallel execution.

**Examples:**
- Race condition (timing-dependent)
- Deadlock
- Stale reference in async chain
- Improper locking
- Shared mutable state

**Indicators:**
- Non-deterministic failures (flaky)
- Failure only in parallel execution
- Stale reference error
- Timeout in deadlock

**Prevention:**
- Immutable data structures
- Proper synchronization primitives (locks, channels)
- Async/await over callbacks
- Race detector tools (go test -race)
