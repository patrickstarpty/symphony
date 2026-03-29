# Auto-Fix Strategies — Reference

When and how to auto-apply healing patches.

## Locator Fix (High Confidence — Auto-Apply)

**Confidence threshold:** high

**When to apply:** Always, if healed test passes.

**Verification:**
1. Find new selector in code
2. Apply patch to test file
3. Run healed test
4. Verify test passes
5. Commit patch

**Example patch:**
```diff
diff --git a/src/__tests__/login.test.ts
- expect(page.locator('.submit-btn')).toBeVisible();
+ expect(page.locator('[data-testid="submit-btn"]')).toBeVisible();
```

## Expected Value Fix (Medium Confidence — Require Review)

**Confidence threshold:** medium

**When to apply:** With human review in PR comment.

**Verification:**
1. Extract old and new expected values from diff
2. Generate patch
3. Add PR comment explaining change
4. Wait for author approval
5. Apply and re-run

**PR comment template:**
```
🤖 Healing broken test: [test_id]

The expected value changed due to your implementation update:
- Old: `110`
- New: `120`

This change is intentional per your PR. Suggestion:
```diff
- expect(result).toBe(110);
+ expect(result).toBe(120);
```

Approve with 👍 to auto-heal, or manually fix if different.
```

## Logic Fix (Low Confidence — Human Review Only)

**Confidence threshold:** low

**When to apply:** Never auto-apply.

**Action:**
1. Flag test in `unhealed_tests`
2. Add comment explaining breakage
3. Assign to author for manual fix
4. Block merge until fixed

**Example comment:**
```
⚠️ Cannot auto-heal [test_id]:
- Breakage type: logic (TypeError)
- Message: "Cannot read property 'map' of undefined"
- Confidence: low

The implementation change broke test logic, not just data.
Please review and fix manually.
```

## No-Heal Rules

**Never auto-apply:**
- Logic changes (type errors, exceptions, assertion logic)
- Tests that verify bugs/security issues
- Tests for error handling
- Concurrent/async timing tests

**Always require human review for:**
- Multi-line changes
- Changes to test flow (control flow statements)
- Behavioral changes (not just data)
