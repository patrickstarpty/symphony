# Common Test Breakage Patterns — Reference

Quick patterns for failure categorization.

## Locator Breakage (High Confidence)

**Symptoms:**
- "element not found"
- "selector does not match"
- "element is not visible"
- "cannot locate element"

**Root cause:** Element selector changed in implementation (intentional refactor).

**Repair:**
- Extract new selector from diff
- Update test locator to new selector
- Re-run test to verify

**Example:**
```typescript
// Implementation: changed from className to data-testid
- <button className="submit-btn">
+ <button data-testid="submit-btn">

// Test: update locator
- await page.click('.submit-btn')
+ await page.click('[data-testid="submit-btn"]')
```

## Expected Value Breakage (Medium Confidence)

**Symptoms:**
- "expected X, got Y"
- "AssertionError: value mismatch"
- "toBe() failed"
- "Expected: true, Received: false"

**Root cause:** Return value or behavior changed intentionally (feature enhancement, calculation fix).

**Repair:**
- Verify change was intentional (mentioned in PR description/issue)
- Update expected value in test assertion
- Re-run test to verify

**Example:**
```typescript
// Implementation: price calculation changed
- return amount * 1.1;  // 10% markup
+ return amount * 1.2;  // 20% markup (new policy)

// Test: update assertion
- expect(calculateTotal(100)).toBe(110);
+ expect(calculateTotal(100)).toBe(120);
```

## Logic Breakage (Low Confidence)

**Symptoms:**
- TypeError, AttributeError, ReferenceError
- Null/undefined reference
- Exception thrown
- Syntax error in test

**Root cause:** Implementation change broke test logic, not just data.

**Repair:**
- Requires understanding of intent
- May need test logic rewrite, not just data update
- Flag for human review

**Never auto-heal logic breakage.**

## Flaky Test (Not a Breakage)

**Symptoms:**
- Intermittent failure
- Passes on retry
- "timeout waiting for element"
- "element stale reference"

**Root cause:** Test timing issue, not implementation change.

**Action:**
- Not a breakage; handled by `classifying-test-failures`
- Skip healing logic
