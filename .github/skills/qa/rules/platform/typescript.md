# TypeScript Testing Rules — P2

> Applied by generating-playwright-tests and generating-api-tests when target is TypeScript/JavaScript.

## Strict Mode & Type Safety

- Always generate with `"strict": true` in tsconfig for test files
- Type assertions (`as Type`) are acceptable in tests only when bridging to untyped libraries
- Avoid `any` type in test code:
  - Use `unknown` + type guard if bridging untyped libraries
  - Use `Record<string, unknown>` for flexible object maps
- Function parameters in test fixtures must be typed:
  - ✅ `function createUser(name: string, age: number): User { ... }`
  - ❌ `function createUser(name, age) { ... }`

## Async Patterns

- Use `async/await` exclusively (no `.then()` chains in test code)
- All async operations in tests must be awaited:
  - ✅ `await page.goto(url)`
  - ❌ `page.goto(url)` (missing await)
- Test functions must be `async` if they contain `await`:
  - ✅ `it('should log in', async () => { await page.fill(...) })`
  - ❌ `it('should log in', () => { await page.fill(...) })`
- Never suppress unhandled rejection warnings with `.catch()` silently — log/rethrow
- Timeouts for waits must be explicit:
  - ✅ `page.waitForSelector(sel, { timeout: 5000 })`
  - ❌ `page.waitForSelector(sel)` (relying on global default)

## Test Structure (AAA)

- Every test must follow Arrange-Act-Assert:
  ```typescript
  it('should validate email format', async () => {
    // Arrange
    const validator = new EmailValidator();
    const input = 'invalid-email';

    // Act
    const result = validator.validate(input);

    // Assert
    expect(result).toBe(false);
  });
  ```

## Assertion Best Practices

- One logical assertion per test (may have multiple `expect()` calls validating the same assertion)
- Use descriptive matchers:
  - ✅ `expect(response.status).toBe(200)`
  - ❌ `expect(response).toBeTruthy()`
- Test error messages:
  - ✅ `expect(error.message).toContain('Invalid email')`
  - ❌ `expect(error).toBeDefined()` (too vague)

## Playwright-Specific

- Use Page Object Model (POM) for web tests (locators centralized in page classes)
- Selectors must be specific and stable:
  - ✅ `button[data-testid="submit-form"]`
  - ❌ `div.container div button` (fragile)
- Use `data-testid` attributes for test targeting when possible
- Waits must be explicit, not relying on implicit timeouts:
  - ✅ `await page.waitForLoadState('networkidle')`
  - ❌ `await page.waitForTimeout(1000)` (fragile)

## API Testing (Jest/Vitest)

- Mock external HTTP calls (never hit real APIs in tests):
  - ✅ Use `jest.mock()` or MSW (Mock Service Worker)
  - ❌ `await fetch('https://api.example.com/...')`
- Validate both happy path AND error scenarios
- Use matchers for JSON schema validation (e.g., `expect.objectContaining()`)
