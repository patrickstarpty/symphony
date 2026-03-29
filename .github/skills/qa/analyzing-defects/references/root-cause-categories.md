# Root Cause Categories — Reference

Detailed categorization for defect analysis and prevention.

## Category: Logic

**Severity:** High (fixes often require code changes)

**Sub-categories:**
- **Boundary logic:** Off-by-one, min/max handling
- **Conditional logic:** if/else conditions wrong
- **Loop logic:** Infinite loops, wrong iteration
- **State management:** State not initialized/updated/cleaned

**Example Detection:**
```
AssertionError: expected 11 but got 10  → Off-by-one
TypeError: Cannot read property 'x' of null  → Null handling
Expected true, got false  → Conditional logic
```

**Fix Pattern:**
```
1. Write failing test with correct expected value
2. Fix implementation logic
3. Verify test passes
4. Review similar patterns in codebase
```

## Category: Integration

**Severity:** Medium (fixes often require coordination)

**Sub-categories:**
- **API contract:** Request/response format mismatch
- **Async timing:** Promise not awaited, timeout
- **Dependency version:** API changed in upgrade
- **Mock/stub:** Test double doesn't match reality

**Example Detection:**
```
Response 404 for /users/:id  → API endpoint wrong
Promise not returned  → Async pattern
Test passes with mock, fails with real service  → Stub mismatch
```

**Fix Pattern:**
```
1. Add integration test with real (or more realistic) service
2. Update service call or mock
3. Verify contract with upstream service
4. Add contract test for future protection
```

## Category: Data

**Severity:** High (fixes often require careful validation)

**Sub-categories:**
- **Input validation:** User input not validated
- **Type mismatch:** String passed where number expected
- **Range violation:** Value outside acceptable bounds
- **Schema change:** Field missing or wrong type

**Example Detection:**
```
Invalid email format  → Validation failure
TypeError: str + int  → Type mismatch
Value must be 0-100  → Range violation
Unknown field 'phone'  → Schema mismatch
```

**Fix Pattern:**
```
1. Add validation at input boundary
2. Strengthen type checking
3. Add test data covering range/edges
4. Validate schema on deserialize
```

## Category: Config

**Severity:** Low to Medium (fixes often environmental)

**Sub-categories:**
- **Environment variables:** Wrong env var or missing
- **Hardcoded values:** Values hardcoded that should be config
- **Secrets exposure:** Secrets in code instead of vault
- **Version incompatibility:** Dependency version mismatch

**Example Detection:**
```
Environment variable not found: API_URL  → Missing env var
localhost hardcoded in code  → Should be config
AWS_SECRET in source code  → Secrets exposure
Module requires v2.0, have v1.5  → Version mismatch
```

**Fix Pattern:**
```
1. Externalize value to environment variable / config file
2. Validate config on startup
3. Test with different config values
4. Never commit secrets (use .gitignore + vault)
```

## Category: Concurrency

**Severity:** Critical (hardest to debug and fix)

**Sub-categories:**
- **Race condition:** Timing-dependent, non-deterministic
- **Deadlock:** Circular locking dependency
- **Stale reference:** Object reference outdated in async chain
- **Shared mutable state:** Multiple threads modify same data

**Example Detection:**
```
Test passes sometimes, fails sometimes  → Race condition
Test hangs, never completes  → Deadlock
'data' is undefined in callback  → Stale reference
'users' changed during iteration  → Shared state mutation
```

**Fix Pattern:**
```
1. Use immutable data structures
2. Apply proper locking (mutex, semaphore)
3. Use async/await instead of callbacks
4. Write concurrency-specific tests
5. Run with race detector enabled
```
