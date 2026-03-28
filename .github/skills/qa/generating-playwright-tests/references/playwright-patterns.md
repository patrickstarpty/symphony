# Playwright Testing Patterns

Best practices for reliable, maintainable Playwright tests.

## Wait Strategies

### Page Load
```typescript
// Wait for network idle
await page.waitForLoadState('networkidle');

// Wait for specific element
await page.waitForSelector('[data-testid="content"]');

// Wait for function
await page.waitForFunction(() => window.APP_READY === true);
```

### Dynamic Content
```typescript
// Wait for element visibility
await page.locator('[data-testid="modal"]').waitFor({ state: 'visible' });

// Poll for condition
await page.waitForFunction(() => {
  const count = document.querySelectorAll('.item').length;
  return count > 0;
});
```

## Network Mocking

```typescript
// Intercept and mock API
await page.route('**/api/quotes/**', route => {
  route.abort('blockedbyclient');
});

// Mock with custom response
await page.route('**/api/users/**', route => {
  route.continue({
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ id: 1, name: 'Test User' }),
  });
});
```

## Debugging

```typescript
// Trace API calls
await page.route('**/*', route => {
  console.log('>>>', route.request().method(), route.request().url());
  route.continue();
});

// Screenshot on failure
await page.screenshot({ path: 'debug.png' });

// Get page state
const text = await page.textContent('body');
console.log(text);
```

## Anti-Patterns

- DON'T: `await page.waitForTimeout(1000)` (flaky, slow)
- DON'T: Hardcoded waits in POM methods
- DON'T: Rely on timing for element visibility
- DO: Use `waitForSelector`, `waitForLoadState`, `waitForFunction`
- DO: Make wait time configurable per environment
