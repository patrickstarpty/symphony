# TDD Rules

> Enforced during coding phase. QA extension supplements — never contradicts — Superpowers TDD.

## Red-Green-Refactor Cycle

1. **Red:** Write a failing test that describes the desired behavior.
2. **Verify Red:** Run the test. Confirm it fails for the expected reason (not a syntax error).
3. **Green:** Write the minimum implementation to make the test pass.
4. **Verify Green:** Run the test. Confirm it passes.
5. **Refactor:** Improve structure while keeping all tests green.

## Enforcement

- Test files must be committed before or alongside implementation files — never after.
- No implementation-only commits (commits touching `src/` must also touch `tests/` or `test/`).
- The Red phase is never skippable — writing a test after the implementation defeats TDD's design benefit.

## Test Design Techniques

- **Equivalence Partitioning:** Group inputs into classes that should behave identically. One test per class.
- **Boundary Value Analysis:** Test at exact boundaries (min, min+1, max-1, max) plus one step outside.
- **Decision Tables:** For multi-condition logic, enumerate input combinations systematically.

## Exceptions

These do NOT require TDD:
- Configuration files (`.env`, `config.yaml`, `tsconfig.json`)
- Database migrations (schema-only DDL)
- Third-party wrapper functions with no business logic
- Generated code (protobuf stubs, OpenAPI clients)

## Framework Detection

Auto-detect from project files:
- `package.json` with `jest` or `vitest` → Jest/Vitest templates
- `pyproject.toml` or `setup.py` with `pytest` → pytest templates
- `playwright.config.ts` → Playwright templates
- `pom.xml` or `build.gradle` with JUnit → JUnit templates
