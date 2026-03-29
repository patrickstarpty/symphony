# Code Review Checklist — Reference

Use this checklist when evaluating code quality (Stage 2).

## Spec Compliance (Stage 1)

- [ ] Every AC requirement has corresponding implementation
- [ ] No conflicting changes to existing AC
- [ ] Edge cases mentioned in spec are covered

## Readability

- [ ] Function names are descriptive (read name, understand purpose)
- [ ] Variable names are meaningful (not single-letter except loop counters)
- [ ] Comments explain WHY, not WHAT (code should be self-documenting)
- [ ] Complex logic has explanatory comments
- [ ] Functions are <30 lines (excluding tests)
- [ ] Nesting depth ≤3 (use early returns to flatten)
- [ ] No dead code or commented-out code

## SOLID Principles

- **Single Responsibility:** Each class/function has one reason to change
- **Open/Closed:** Open for extension, closed for modification
- **Liskov Substitution:** Subtypes are substitutable for base types
- **Interface Segregation:** Clients depend on specific interfaces, not monoliths
- **Dependency Inversion:** Depend on abstractions, not implementations

Flags:
- [ ] Class has 10+ public methods? (SRP violation)
- [ ] Changing one feature breaks unrelated tests? (tight coupling)
- [ ] Function has 5+ parameters? (pass objects instead)
- [ ] Type assertions or casts in logic? (LSP violation)

## Performance

- [ ] No N+1 queries (explicit `.eager_load()` or batch queries)
- [ ] Caching strategy documented for expensive operations
- [ ] No unnecessary full-table scans or large result sets
- [ ] API response times: target <500ms p95
- [ ] No blocking operations on event loop (async/await proper)
- [ ] No deep recursion without base case protection

## Security

- [ ] Input validation at all API boundaries
- [ ] No hardcoded credentials, API keys, tokens
- [ ] Parameterized queries (prevent SQL injection)
- [ ] CORS/CSRF protection enabled
- [ ] Secrets loaded from environment, not code
- [ ] Authentication/authorization verified before sensitive operations
- [ ] PII logged only in debug mode, sanitized in production
- [ ] Dependencies checked for known vulnerabilities

## Testing

- [ ] New code has test coverage (target: >80%)
- [ ] Tests are independent (no shared state)
- [ ] Test names describe the scenario and expected outcome
- [ ] Happy path AND error cases tested

## Error Handling

- [ ] Errors are caught and handled explicitly (not silently ignored)
- [ ] User-facing errors have clear messages
- [ ] System errors logged with context for debugging
- [ ] Graceful degradation on external service failure

## Documentation

- [ ] Public methods have docstrings/JSDoc
- [ ] Complex algorithms explained
- [ ] Breaking changes documented
- [ ] Examples provided for non-obvious APIs
