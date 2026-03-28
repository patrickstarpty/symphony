# Code Quality Standards — Reference

## Language-Agnostic Standards

Applied to all code regardless of language.

### Function Length

| Threshold | Severity | Action |
|-----------|----------|--------|
| <20 lines | Ideal | No action |
| 20–30 lines | Acceptable | Monitor |
| 30–50 lines | Warning | Consider extraction |
| >50 lines | Critical | Must refactor |

**Exception:** Generated code, data mappers (>100 lines OK if simple transformations).

### Cyclomatic Complexity

| Score | Meaning |
|-------|---------|
| 1–5 | Good: easily testable |
| 6–10 | Moderate: test thoroughly |
| 11–15 | High: consider refactoring |
| 16+ | Very High: refactor required |

**Calculation:** Count decision points (if, else, switch, catch, loops, && operators, || operators).

### Nesting Depth

| Depth | Example | Comment |
|-------|---------|---------|
| 1–2 | if → logic | Ideal |
| 3–4 | if → if → if → logic | Acceptable, use early returns |
| 5+ | Deep nesting | Refactor: extract helper, guard clauses |

**Technique:** Use early returns to flatten:
```
// Bad: nested logic
function validate(user) {
  if (user) {
    if (user.email) {
      if (user.email.includes('@')) {
        return true;
      }
    }
  }
  return false;
}

// Good: guard clauses
function validate(user) {
  if (!user) return false;
  if (!user.email) return false;
  if (!user.email.includes('@')) return false;
  return true;
}
```

### Code Duplication

- First occurrence: write normally
- Second occurrence: still acceptable (copy-paste might be justified)
- Third occurrence: extract to shared function

**DRY violation threshold:** >2 copies of similar logic.

### Naming Conventions

| Context | Style | Example |
|---------|-------|---------|
| Classes/Types | PascalCase | `PaymentProcessor`, `User` |
| Functions/Methods | camelCase | `processPayment`, `getUserById` |
| Constants | UPPER_SNAKE | `MAX_RETRIES`, `API_ENDPOINT` |
| Variables | camelCase | `userName`, `transactionId` |
| Boolean functions | is/has prefix | `isValid()`, `hasPermission()` |

### Import Ordering

Standard: External → Internal → Relative
```typescript
// External
import express from 'express';
import { Logger } from 'winston';

// Internal
import { PaymentService } from '../services/payment';
import { User } from '../models/user';

// Relative
import { validateEmail } from './validators';
import { config } from './config';
```

## Language-Specific Standards

### TypeScript/JavaScript

- **Strict mode:** Required in tsconfig.json
- **Type assertions:** Minimize `as Type` — prefer proper typing
- **Any type:** Forbidden except for temporary debugging
- **Async patterns:** Always `await` promises, handle errors
- **String templates:** Use backticks for dynamic strings, not `+` concat

### Python

- **Type hints:** Required for all function signatures
- **Docstrings:** All public functions need docstrings (Google/NumPy style)
- **Virtual environments:** Always use venv for isolation
- **Import order:** Standard library → third-party → local (autopep8 compatible)
- **Lint:** Pass flake8/pylint without warnings

### Java

- **Annotations:** Use @Override, @Deprecated, @FunctionalInterface appropriately
- **Exception handling:** Catch specific exceptions, not generic `Exception`
- **Stream API:** Prefer functional style for collections
- **Nullability:** Use @Nullable/@NotNull or Optional<T>

### Go

- **Table-driven tests:** Standard pattern for testing multiple scenarios
- **Error handling:** Explicit `if err != nil` checks (not hidden exceptions)
- **Goroutine testing:** Use `sync.WaitGroup` or channels correctly
- **Race detector:** All concurrent code passes `go test -race`

## Performance Targets

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| API endpoint latency | <200ms p95 | >500ms p99 |
| Database query | <100ms | >500ms |
| Page load | <2s | >5s |
| Test suite | <10 min | >30 min |

## Code Review Comment Quality

### Good Comment
```
Line 42: N+1 query detected. Load orders with posts in single query:
  Post.includes(:orders).where(...)
```

### Bad Comment
```
This could be more efficient
```

### Good Suggestion
```
Optional: Extract this validation logic to a helper method for reusability across endpoints.
Technical debt [TECH-123].
```

### Bad Suggestion
```
Make it better
```
