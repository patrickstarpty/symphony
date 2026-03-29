# QA Verification Skills — P2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the 5 P2 QA generation skills (SKILL.md + scripts + references + templates + evals) and 5 P2 rules files (security-standards.md + 4 platform rules), building on P1 core evaluation skills.

**Architecture:** Each skill is a directory under `.github/skills/qa/` following the anthropics/skills structure: `SKILL.md` (agent instructions), `scripts/` (Python helper scripts with minimal deps via per-skill requirements.txt), `references/` (domain knowledge), `templates/` (Liquid templates), `evals/` (test-prompts.yaml + assertions.yaml). Skills are standalone — no shared runtime. Scripts are invoked by the agent via shell. P2 scripts may use external dependencies (numpy, pydantic, etc.) listed in per-skill requirements.txt.

**Tech Stack:** Markdown (SKILL.md), Python 3.12+ (scripts with minimal per-skill deps), YAML (evals, frontmatter), Liquid (templates)

**Spec:** `docs/specs/2026-03-28-qa-skills-quick-win-design.md` §5 (P2 Skills), §7.3 (P2 Rules), §8 (Evals)

**Prerequisite:** P1 skills must be implemented first (parsing-requirements, test-driven-development, analyzing-coverage, validating-acceptance-criteria, classifying-test-failures, generating-qa-report).

---

## File Structure

```
.github/skills/qa/
├── generating-test-data/
│   ├── SKILL.md
│   ├── requirements.txt
│   ├── scripts/
│   │   ├── data-generator.py
│   │   ├── pii-sanitizer.py
│   │   └── distribution-validator.py
│   ├── references/
│   │   ├── insurance-data-schemas.md
│   │   └── pii-patterns.md
│   ├── templates/
│   │   ├── fixture.json.liquid
│   │   ├── factory.ts.liquid
│   │   └── factory.py.liquid
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
├── generating-playwright-tests/
│   ├── SKILL.md
│   ├── requirements.txt
│   ├── scripts/
│   │   ├── selector-strategy.py
│   │   └── page-analyzer.py
│   ├── references/
│   │   ├── playwright-patterns.md
│   │   ├── pom-conventions.md
│   │   └── web-testing-standards.md
│   ├── templates/
│   │   ├── page-object.ts.liquid
│   │   ├── spec.ts.liquid
│   │   └── fixture.ts.liquid
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
├── generating-api-tests/
│   ├── SKILL.md
│   ├── requirements.txt
│   ├── scripts/
│   │   ├── schema-parser.py
│   │   └── endpoint-analyzer.py
│   ├── references/
│   │   ├── api-testing-patterns.md
│   │   └── schema-validation-rules.md
│   ├── templates/
│   │   ├── rest.test.ts.liquid
│   │   ├── graphql.test.ts.liquid
│   │   └── pytest-api.py.liquid
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
├── generating-mobile-tests/
│   ├── SKILL.md
│   ├── requirements.txt
│   ├── scripts/
│   │   ├── platform-detector.py
│   │   └── accessibility-checker.py
│   ├── references/
│   │   ├── appium-patterns.md
│   │   ├── xctest-patterns.md
│   │   └── uiautomator-patterns.md
│   ├── templates/
│   │   ├── appium.test.ts.liquid
│   │   ├── xctest.swift.liquid
│   │   └── espresso.kt.liquid
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
├── generating-perf-tests/
│   ├── SKILL.md
│   ├── requirements.txt
│   ├── scripts/
│   │   ├── load-profile-calculator.py
│   │   └── baseline-collector.py
│   ├── references/
│   │   ├── perf-testing-patterns.md
│   │   └── insurance-load-profiles.md
│   ├── templates/
│   │   ├── k6.test.js.liquid
│   │   ├── locust.py.liquid
│   │   └── gatling.scala.liquid
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
└── rules/
    ├── security-standards.md
    └── platform/
        ├── typescript.md
        ├── python.md
        ├── java.md
        └── go.md
```

**Total files: 59** (5 SKILL.md + 11 scripts + 13 references + 15 templates + 10 eval files + 5 rules + 5 requirements.txt)

---

## Task 1: P2 Rules Files

Create security-standards.md and 4 platform-specific rules. Rules are foundational — skills reference them.

**Files:**
- Create: `.github/skills/qa/rules/security-standards.md`
- Create: `.github/skills/qa/rules/platform/typescript.md`
- Create: `.github/skills/qa/rules/platform/python.md`
- Create: `.github/skills/qa/rules/platform/java.md`
- Create: `.github/skills/qa/rules/platform/go.md`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p .github/skills/qa/rules/platform
```

- [ ] **Step 2: Write security-standards.md**

```markdown
# Security Standards — P2

> Applied during test data generation, API/web/mobile test creation, and performance testing. Referenced by all P2 generation skills.

## Input Validation Testing

- Every text input must have test cases for:
  - Empty string and whitespace-only strings
  - Max length boundaries (test at limit, one past limit)
  - SQL injection patterns: `' OR '1'='1`, `"; DROP TABLE--`, parameterized payloads
  - XSS payloads: `<script>alert(1)</script>`, event handlers (`onclick=`), data URIs
  - Command injection: backticks, `$()`, pipe chains
  - Path traversal: `../`, `..\`, encoded variants
- Test generation must include at least one security-focused test case per input field
- Never commit real security exploit code — use OWASP Top 10 canonical examples only

## Authentication & Authorization Testing

- Login/session tests must cover:
  - Valid credentials → authenticated state
  - Invalid password → rejection with generic error (no username confirmation)
  - Missing credentials → 401 Unauthorized
  - Expired session → redirect to login, no data leak
  - CSRF token validation (if applicable)
  - Token/cookie scope isolation per user
- OAuth/SAML flows: verify state parameter validation, code-exchange attacks, redirect URI whitelisting
- API token tests: verify Bearer token format, invalid format rejection, token expiration
- Permission boundary tests: authenticated user cannot access other user's data

## Secrets Management

- Never generate test credentials with real patterns:
  - Database passwords must be obviously fake ("test_password_123")
  - API keys must be obviously fake ("sk_test_123456789" or similar)
  - Private keys must use dummy RSA/EC keypairs from test fixtures (not real keys)
- Test data files (fixtures, factories) must not be added to git if they contain secrets
- Scripts must never log credentials, tokens, or sensitive parameters
- Environment variable references (`$DB_PASSWORD`) are acceptable; hardcoded values are not

## OWASP Top 10 Coverage

Test generation should include patterns for:
1. **Injection** — SQL, NoSQL, Command, LDAP (covered by Input Validation above)
2. **Broken Authentication** — covered by Authentication & Authorization above
3. **Sensitive Data Exposure** — test HTTPS enforcement, no plaintext PII in logs/responses
4. **XML External Entity (XXE)** — if parsing XML, test DTD XXE, external entity injection
5. **Broken Access Control** — authorization checks, object-level access control
6. **Security Misconfiguration** — CORS policy testing, security headers (CSP, HSTS, X-Frame-Options)
7. **XSS** — covered by Input Validation above
8. **Insecure Deserialization** — if accepting JSON/YAML, test malicious payloads
9. **Using Components with Known Vulnerabilities** — no explicit test requirement (dependency scanning covers this)
10. **Insufficient Logging & Monitoring** — test that security events are logged (login failures, permission denials)

## Test Data Privacy

- Insurance-domain PII must use obviously fake data (§security-standards.md § Test Data Privacy):
  - SSN: "999-99-9999" (clearly invalid format)
  - License: "DL123456" (truncated, non-state format)
  - Phone: "555-0100" (reserved exchange)
  - Address: "123 Test St, Test City, TS 99999"
  - Policy number: "POL-TEST-999999" (clearly marked test)
  - Account number: "ACC-TEST-9999999"
- Dates: use fixed test dates (2000-01-01, 2099-12-31) never current date
- Amounts: use round numbers (100.00, 9999.99) that are obviously test values
- Names: use "Test User", "Jane Doe", "John Smith" — never real employee names

## Rate Limiting & DoS Tests

- API tests must include at least one rate-limit scenario (if applicable to endpoint)
- Performance tests should validate graceful degradation under load (no crash, queuing visible)
- Never run actual stress tests against production-like infrastructure without explicit approval
```

- [ ] **Step 3: Write platform/typescript.md**

```markdown
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
```

- [ ] **Step 4: Write platform/python.md**

```markdown
# Python Testing Rules — P2

> Applied by generating-api-tests and generating-perf-tests when target is Python.

## Type Hints

- All function signatures in test code must include type hints:
  - ✅ `def create_policy(user_id: str, premium: float) -> Policy:`
  - ❌ `def create_policy(user_id, premium):`
- Use `from __future__ import annotations` for forward references
- Return type must be specified:
  - ✅ `def setup() -> None:`
  - ❌ `def setup():`
- Collections must be parameterized:
  - ✅ `list[str]`, `dict[str, int]`
  - ❌ `list`, `dict`

## Docstrings

- Every test class and test function must have a docstring:
  ```python
  def test_policy_renewal_with_valid_dates(policy_fixture):
      """Verify policy renewal succeeds when dates are valid and consecutive.

      Given a policy with expiration date 2024-12-31,
      When renewal is requested for 2024-01-01,
      Then renewal succeeds and new expiration is 2025-12-31.
      """
  ```
- Docstring must describe the Given-When-Then scenario
- Never leave docstrings as `"""..."""` (placeholder)

## Virtual Environment

- All projects must use venv:
  - `python -m venv venv`
  - Activate: `. venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
- requirements.txt or pyproject.toml must pin all test dependencies:
  - ✅ `pytest==7.4.0`
  - ❌ `pytest` (unpinned)
- Test dependencies must be in a separate group (e.g., `[dev]` in pyproject.toml):
  ```toml
  [project.optional-dependencies]
  dev = ["pytest==7.4.0", "pytest-cov==4.1.0"]
  ```

## Import Ordering

- Follow isort convention (stdlib → third-party → local):
  ```python
  import json
  from typing import Any

  import pytest
  from pydantic import BaseModel

  from app.models import Policy
  from app.services import PolicyService
  ```
- No wildcard imports (`from app import *`)

## Async Testing (pytest-asyncio)

- Use `@pytest.mark.asyncio` for async test functions:
  ```python
  @pytest.mark.asyncio
  async def test_async_policy_fetch():
      result = await policy_service.fetch_by_id("123")
      assert result is not None
  ```
- Fixtures that return coroutines must be `async`:
  ```python
  @pytest.fixture
  async def async_client():
      async with AsyncClient() as client:
          yield client
  ```

## Mocking & Fixtures

- Use `pytest` fixtures, not bare setup/teardown:
  - ✅ `@pytest.fixture` with `yield`
  - ❌ `setUp()` / `tearDown()` methods
- Mock external dependencies:
  ```python
  @pytest.fixture
  def mock_email_service(monkeypatch):
      mock = Mock()
      mock.send.return_value = True
      monkeypatch.setattr('app.services.email_service', mock)
      return mock
  ```

## Assertions

- Use `assert` statements (not `self.assertEqual`):
  - ✅ `assert result.status == "active"`
  - ❌ `self.assertEqual(result.status, "active")`
- For complex objects, use `pytest.approx()` for floats:
  - ✅ `assert premium == pytest.approx(199.99, abs=0.01)`
  - ❌ `assert premium == 199.99` (fragile with floats)

## Error Testing

- Use `pytest.raises()` context manager:
  ```python
  with pytest.raises(ValueError, match="Premium must be positive"):
      Policy.create(premium=-100)
  ```
```

- [ ] **Step 5: Write platform/java.md**

```markdown
# Java Testing Rules — P2

> Applied by generating-api-tests when target is Java (JUnit/Mockito/RestAssured).

## Annotations & Junit 5

- Use JUnit 5 annotations (not JUnit 4):
  - ✅ `@Test`, `@BeforeEach`, `@AfterEach`, `@ParameterizedTest`
  - ❌ `@org.junit.Test`, `setUp()`, `tearDown()`
- Test classes must have public scope:
  - ✅ `public class PolicyRenewalTest { }`
  - ❌ `class PolicyRenewalTest { }`
- Test methods must be public and void:
  ```java
  @Test
  public void shouldRenewPolicyWithValidDates() {
      // Arrange, Act, Assert
  }
  ```

## Exception Handling in Tests

- Use `assertThrows()` for exception testing:
  ```java
  InvalidPolicyException thrown = assertThrows(
      InvalidPolicyException.class,
      () -> policy.renew(invalidDate),
      "Premium must be positive"
  );
  assertEquals("Premium must be positive", thrown.getMessage());
  ```
- Never use try-catch to catch expected exceptions

## Stream API Testing

- Test Stream operations in isolation:
  ```java
  @Test
  public void shouldFilterActivePolicies() {
      List<Policy> policies = Arrays.asList(
          new Policy("P1", true),
          new Policy("P2", false),
          new Policy("P3", true)
      );

      List<Policy> active = policies.stream()
          .filter(Policy::isActive)
          .collect(Collectors.toList());

      assertEquals(2, active.size());
  }
  ```
- Use `.toList()` (Java 16+) instead of `collect(Collectors.toList())`

## Spring Test Slicing

- Use `@WebMvcTest` for controller testing (not full context):
  ```java
  @WebMvcTest(PolicyController.class)
  class PolicyControllerTest {
      @MockBean
      private PolicyService policyService;

      @Autowired
      private MockMvc mockMvc;
  }
  ```
- Use `@DataJpaTest` for repository testing (only DB layer, no services)
- Use `@SpringBootTest` only for full integration tests (isolated, not CI/CD)

## Mockito

- Use `@Mock` and `@InjectMocks`:
  ```java
  @Mock
  private PolicyRepository repository;

  @InjectMocks
  private PolicyService service;
  ```
- Verify interactions explicitly:
  ```java
  verify(repository, times(1)).save(any(Policy.class));
  verify(repository, never()).delete(any());
  ```
- Stub return values with `when().thenReturn()`:
  ```java
  when(repository.findById("123"))
      .thenReturn(Optional.of(policy));
  ```

## RestAssured for API Tests

- Use fluent API for readability:
  ```java
  given()
      .contentType(ContentType.JSON)
      .body(createPolicyRequest)
  .when()
      .post("/policies")
  .then()
      .statusCode(201)
      .body("id", notNullValue())
      .body("status", equalTo("active"));
  ```
- Always validate response status code
- Never skip error response validation

## Assertions (AssertJ)

- Use AssertJ for fluent assertions (not Hamcrest in new tests):
  ```java
  assertThat(policy)
      .isNotNull()
      .extracting(Policy::getStatus)
      .isEqualTo("active");
  ```

## Parameterized Tests

- Use `@ParameterizedTest` with `@ValueSource` or `@CsvSource`:
  ```java
  @ParameterizedTest
  @CsvSource({
      "100.00, true",
      "-50.00, false",
      "0.00, false"
  })
  public void shouldValidatePremium(Double premium, boolean expected) {
      assertEquals(expected, Policy.isValidPremium(premium));
  }
  ```
```

- [ ] **Step 6: Write platform/go.md**

```markdown
# Go Testing Rules — P2

> Applied by generating-api-tests when target is Go.

## Table-Driven Tests

- All test cases must use table-driven approach:
  ```go
  func TestPolicyRenewal(t *testing.T) {
      tests := []struct {
          name        string
          policy      *Policy
          expectedErr bool
          expectation string
      }{
          {
              name:        "valid policy renews successfully",
              policy:      &Policy{Premium: 100, Expiry: time.Now().AddDate(1, 0, 0)},
              expectedErr: false,
          },
          {
              name:        "negative premium fails",
              policy:      &Policy{Premium: -50},
              expectedErr: true,
              expectation: "invalid premium",
          },
      }

      for _, tt := range tests {
          t.Run(tt.name, func(t *testing.T) {
              err := tt.policy.Renew()
              if (err != nil) != tt.expectedErr {
                  t.Fatalf("expected error: %v, got: %v", tt.expectedErr, err)
              }
          })
      }
  }
  ```
- One table per logical unit; no nested tables

## Error Handling

- Check errors immediately after function calls:
  ```go
  policy, err := NewPolicy(id)
  if err != nil {
      t.Fatalf("failed to create policy: %v", err)
  }
  ```
- Test both success and failure paths:
  - ✅ Test `err == nil` case AND `err != nil` case
  - ❌ Only test happy path
- Use `t.Errorf()` for non-fatal assertions, `t.Fatalf()` for fatal ones

## Goroutine Testing

- Use channels and context for coordination:
  ```go
  func TestConcurrentPolicyAccess(t *testing.T) {
      results := make(chan error, 2)
      policy := NewPolicy("P1")

      go func() {
          results <- policy.Renew()
      }()
      go func() {
          results <- policy.Cancel()
      }()

      for i := 0; i < 2; i++ {
          if err := <-results; err != nil {
              t.Logf("operation failed: %v", err)
          }
      }
  }
  ```
- Never use `time.Sleep()` to wait for goroutines (use channels or sync.WaitGroup)

## Race Detector

- Run tests with `-race` flag:
  ```bash
  go test -race ./...
  ```
- No data races allowed — use `sync.Mutex` for shared state:
  ```go
  type PolicyService struct {
      mu       sync.RWMutex
      policies map[string]*Policy
  }

  func (s *PolicyService) Get(id string) *Policy {
      s.mu.RLock()
      defer s.mu.RUnlock()
      return s.policies[id]
  }
  ```

## Subtests

- Use `t.Run()` for logical grouping:
  ```go
  t.Run("renewal scenarios", func(t *testing.T) {
      t.Run("valid renewal", func(t *testing.T) { ... })
      t.Run("expired policy", func(t *testing.T) { ... })
  })
  ```
- Names must be descriptive and lowercase

## Mocking (testify/mock)

- Use testify for mock assertions:
  ```go
  mock := new(MockRepository)
  mock.On("Save", mock.MatchedBy(func(p *Policy) bool {
      return p.ID == "P1"
  })).Return(nil)

  // Call code under test
  service := NewPolicyService(mock)
  err := service.RenewPolicy("P1")

  // Verify
  mock.AssertExpectations(t)
  ```

## Benchmarks

- Mark performance-critical tests with `Benchmark` prefix:
  ```go
  func BenchmarkPolicyCreation(b *testing.B) {
      for i := 0; i < b.N; i++ {
          NewPolicy("P1")
      }
  }
  ```
- Run with `go test -bench=.`

## Assertions (testify/assert)

- Use testify for readable assertions:
  ```go
  assert.NotNil(t, policy)
  assert.Equal(t, "active", policy.Status)
  assert.ErrorContains(t, err, "premium must be positive")
  ```
```

- [ ] **Step 7: Commit rules files**

```bash
git add .github/skills/qa/rules/
git commit -m "feat(qa-skills): add P2 rules files

Add security-standards.md (OWASP Top 10, input validation, secrets management).
Add platform-specific rules: typescript.md (strict mode, async patterns), python.md (type hints, venv, docstrings), java.md (annotations, Spring slicing, Mockito), go.md (table-driven tests, goroutines, race detector)."
```

---

## Task 2: generating-test-data skill

Generate domain-realistic test fixtures for insurance domain. Sanitize PII, validate distributions.

**Files:**
- Create: `.github/skills/qa/generating-test-data/SKILL.md`
- Create: `.github/skills/qa/generating-test-data/requirements.txt`
- Create: `.github/skills/qa/generating-test-data/scripts/data-generator.py`
- Create: `.github/skills/qa/generating-test-data/scripts/pii-sanitizer.py`
- Create: `.github/skills/qa/generating-test-data/scripts/distribution-validator.py`
- Create: `.github/skills/qa/generating-test-data/references/insurance-data-schemas.md`
- Create: `.github/skills/qa/generating-test-data/references/pii-patterns.md`
- Create: `.github/skills/qa/generating-test-data/templates/fixture.json.liquid`
- Create: `.github/skills/qa/generating-test-data/templates/factory.ts.liquid`
- Create: `.github/skills/qa/generating-test-data/templates/factory.py.liquid`
- Create: `.github/skills/qa/generating-test-data/evals/test-prompts.yaml`
- Create: `.github/skills/qa/generating-test-data/evals/assertions.yaml`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p .github/skills/qa/generating-test-data/{scripts,references,templates,evals}
```

- [ ] **Step 2: Write requirements.txt**

```
pydantic==2.5.0
faker==20.1.0
pyyaml==6.0.1
```

- [ ] **Step 3: Write SKILL.md**

```markdown
---
name: generating-test-data
version: "1.0.0"
description: "Generate domain-realistic test fixtures with sanitized PII, validated distributions"
category: generation
phase: during-coding
platforms: ["all"]
dependencies: []
soft_dependencies: ["test-driven-development"]
input_schema:
  - name: "domain"
    type: "string"
    required: true
    description: "insurance | financial | healthcare"
  - name: "entity_type"
    type: "string"
    required: true
    description: "policy | claim | customer | quote"
  - name: "count"
    type: "integer"
    required: false
    default: 10
  - name: "output_format"
    type: "string"
    required: false
    description: "json | yaml | csv"
    default: "json"
output_schema:
  - name: "fixtures"
    type: "array"
  - name: "pii_audit"
    type: "object"
    description: "PII scan results"
  - name: "distribution_report"
    type: "object"
    description: "Statistical validation"
  - name: "generated_files"
    type: "array"
---

# generating-test-data

Generate domain-realistic test data with sanitized PII and validated statistical properties. Supports insurance domain entities: policy, claim, customer, quote.

## When to Use

Use during coding when writing tests that require realistic data. Run before committing test fixtures to verify PII sanitization.

## Instructions

1. Identify domain and entity type from the test requirements
2. Run `scripts/data-generator.py` to produce base fixtures with Faker-generated values
3. Run `scripts/pii-sanitizer.py` to scan and replace any real or risky PII patterns
4. Run `scripts/distribution-validator.py` to verify distributions match insurance domain reality (e.g., premiums cluster around typical values, not uniformly random)
5. Optionally render into language-specific factories (TypeScript, Python) using templates
6. Output structured JSON/YAML with audit trail

## Guardrails

- **Zero real customer data.** All fixtures must use obviously fake values.
- **PII scan always runs.** Never skip sanitization.
- **Distribution realism.** Random uniform values (1-10000) are not realistic for premiums; must cluster around mode.
- **Immutability.** Generated fixtures should be read-only in tests (not mutated mid-test).

## Consumers

- `test-driven-development` — enriches test strategy context with schema hints
- Manual test engineers — reference fixtures in hand-written tests
- Integration tests — seed test database with realistic data

## References

- `insurance-data-schemas.md` — entity definitions, field types, valid ranges
- `pii-patterns.md` — patterns that trigger sanitization
```

- [ ] **Step 4: Write scripts/data-generator.py**

```python
#!/usr/bin/env python3
"""Generate domain-realistic test fixtures for insurance domain.

Usage:
  python data-generator.py --domain insurance --entity policy --count 5 --format json

Output: JSON/YAML/CSV with randomly generated fixtures matching entity schema.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Any

from faker import Faker
from pydantic import BaseModel, Field


class PolicyFixture(BaseModel):
    id: str = Field(default_factory=lambda: f"POL-{Faker().numerify('##########')}")
    customer_name: str = ""
    customer_email: str = ""
    policy_number: str = ""
    coverage_type: str = "auto"
    premium_amount: float = Field(default=100.0, ge=0)
    effective_date: str = ""
    expiration_date: str = ""
    status: str = "active"
    deductible: float = Field(default=500.0, ge=0)


class ClaimFixture(BaseModel):
    id: str = Field(default_factory=lambda: f"CLM-{Faker().numerify('##########')}")
    policy_id: str = ""
    claim_number: str = ""
    incident_date: str = ""
    claim_date: str = ""
    claim_type: str = "auto"
    amount_claimed: float = Field(default=500.0, ge=0)
    status: str = "open"
    description: str = ""


class CustomerFixture(BaseModel):
    id: str = Field(default_factory=lambda: f"CUST-{Faker().numerify('########')}")
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    date_of_birth: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""


class QuoteFixture(BaseModel):
    id: str = Field(default_factory=lambda: f"QT-{Faker().numerify('########')}")
    customer_email: str = ""
    coverage_type: str = "auto"
    estimated_premium: float = Field(default=150.0, ge=0)
    quote_date: str = ""
    expiration_date: str = ""
    status: str = "pending"


def generate_policy(fake: Faker) -> PolicyFixture:
    """Generate a realistic insurance policy fixture."""
    start_date = fake.date_between(start_date="-2y", end_date="today")
    end_date = start_date + timedelta(days=365)
    return PolicyFixture(
        id=f"POL-{fake.numerify('##########')}",
        customer_name=f"Test {fake.last_name()}",
        customer_email=f"test_{fake.numerify('####')}@test.example",
        policy_number=f"POL-TEST-{fake.numerify('######')}",
        coverage_type=fake.random_element(["auto", "home", "life"]),
        premium_amount=round(fake.random.uniform(50, 500), 2),
        effective_date=start_date.isoformat(),
        expiration_date=end_date.isoformat(),
        status=fake.random_element(["active", "expired", "cancelled"]),
        deductible=fake.random_element([250.0, 500.0, 1000.0, 2500.0]),
    )


def generate_claim(fake: Faker) -> ClaimFixture:
    """Generate a realistic insurance claim fixture."""
    incident_date = fake.date_between(start_date="-1y", end_date="today")
    claim_date = incident_date + timedelta(days=fake.random_int(0, 30))
    return ClaimFixture(
        id=f"CLM-{fake.numerify('##########')}",
        policy_id=f"POL-{fake.numerify('##########')}",
        claim_number=f"CLM-TEST-{fake.numerify('######')}",
        incident_date=incident_date.isoformat(),
        claim_date=claim_date.isoformat(),
        claim_type=fake.random_element(["auto", "home", "life"]),
        amount_claimed=round(fake.random.uniform(100, 50000), 2),
        status=fake.random_element(["open", "approved", "rejected", "pending_review"]),
        description=fake.sentence(nb_words=8),
    )


def generate_customer(fake: Faker) -> CustomerFixture:
    """Generate a realistic customer fixture."""
    return CustomerFixture(
        id=f"CUST-{fake.numerify('########')}",
        first_name=f"Test{fake.numerify('##')}",
        last_name=fake.last_name(),
        email=f"test_{fake.numerify('####')}@test.example",
        phone="555-0100",
        date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
        address="123 Test St",
        city="Test City",
        state="TS",
        zip_code="99999",
    )


def generate_quote(fake: Faker) -> QuoteFixture:
    """Generate a realistic insurance quote fixture."""
    quote_date = fake.date_between(start_date="-30d", end_date="today")
    exp_date = quote_date + timedelta(days=30)
    return QuoteFixture(
        id=f"QT-{fake.numerify('########')}",
        customer_email=f"test_{fake.numerify('####')}@test.example",
        coverage_type=fake.random_element(["auto", "home", "life"]),
        estimated_premium=round(fake.random.uniform(75, 300), 2),
        quote_date=quote_date.isoformat(),
        expiration_date=exp_date.isoformat(),
        status=fake.random_element(["pending", "accepted", "expired"]),
    )


def main():
    parser = argparse.ArgumentParser(description="Generate domain-realistic test fixtures")
    parser.add_argument("--domain", default="insurance", help="insurance | financial | healthcare")
    parser.add_argument("--entity", default="policy", help="policy | claim | customer | quote")
    parser.add_argument("--count", type=int, default=5, help="Number of fixtures to generate")
    parser.add_argument("--format", default="json", help="json | yaml | csv")
    args = parser.parse_args()

    fake = Faker()
    fixtures = []

    generators = {
        "policy": generate_policy,
        "claim": generate_claim,
        "customer": generate_customer,
        "quote": generate_quote,
    }

    generator = generators.get(args.entity)
    if not generator:
        print(f"Unknown entity: {args.entity}", file=sys.stderr)
        sys.exit(1)

    for _ in range(args.count):
        fixture = generator(fake)
        fixtures.append(fixture.model_dump())

    if args.format == "json":
        json.dump(fixtures, sys.stdout, indent=2, default=str)
    elif args.format == "yaml":
        import yaml
        yaml.dump(fixtures, sys.stdout, default_flow_style=False)
    else:
        print(f"Unsupported format: {args.format}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Write scripts/pii-sanitizer.py**

```python
#!/usr/bin/env python3
"""Scan and sanitize PII in test data.

Usage:
  cat fixtures.json | python pii-sanitizer.py

Input: JSON fixture array
Output: Sanitized JSON + PII audit report
"""

import json
import re
import sys
from typing import Any


PII_PATTERNS = {
    "ssn": (
        r"\b(?!999-99-9999)(?!000-00-0000)\d{3}-\d{2}-\d{4}\b",
        "999-99-9999"
    ),
    "phone": (
        r"\b(?!555-0100)(?!555-0199)[\d]{3}-[\d]{3}-[\d]{4}\b",
        "555-0100"
    ),
    "email_real": (
        r"\b(?!test_|example|localhost)[a-zA-Z0-9._%+-]+@(?!test\.|example\.)[a-zA-Z0-9.-]+\b",
        "test_user@test.example"
    ),
    "credit_card": (
        r"\b(?!4111-1111-1111-1111)(?!5555-5555-5555-5555)\d{4}-?\d{4}-?\d{4}-?\d{4}\b",
        "4111-1111-1111-1111"
    ),
    "license_plate": (
        r"\b[A-Z]{2}[0-9]{5,6}\b",
        "DL123456"
    ),
}


def scan_pii(value: Any) -> list[dict[str, str]]:
    """Scan a value for PII patterns."""
    findings = []
    if not isinstance(value, str):
        return findings

    for pattern_name, (pattern, _) in PII_PATTERNS.items():
        matches = re.finditer(pattern, value, re.IGNORECASE)
        for match in matches:
            findings.append({
                "pattern": pattern_name,
                "found": match.group(0),
                "context": value[:50],
            })
    return findings


def sanitize_pii(obj: Any) -> tuple[Any, list[dict]]:
    """Recursively sanitize PII in object."""
    findings = []

    if isinstance(obj, dict):
        sanitized = {}
        for key, value in obj.items():
            if isinstance(value, str):
                pii_found = scan_pii(value)
                findings.extend(pii_found)

                sanitized_value = value
                for pattern_name, (pattern, replacement) in PII_PATTERNS.items():
                    sanitized_value = re.sub(pattern, replacement, sanitized_value, flags=re.IGNORECASE)
                sanitized[key] = sanitized_value
            elif isinstance(value, (dict, list)):
                sanitized[key], nested_findings = sanitize_pii(value)
                findings.extend(nested_findings)
            else:
                sanitized[key] = value
        return sanitized, findings

    elif isinstance(obj, list):
        sanitized = []
        for item in obj:
            sanitized_item, item_findings = sanitize_pii(item)
            findings.extend(item_findings)
            sanitized.append(sanitized_item)
        return sanitized, findings

    else:
        return obj, findings


def main():
    try:
        fixtures = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(fixtures, list):
        fixtures = [fixtures]

    sanitized_fixtures, all_findings = sanitize_pii(fixtures)

    audit_report = {
        "total_fixtures": len(fixtures),
        "pii_findings": len(all_findings),
        "findings_by_pattern": {},
        "details": all_findings,
    }

    for finding in all_findings:
        pattern = finding["pattern"]
        audit_report["findings_by_pattern"][pattern] = \
            audit_report["findings_by_pattern"].get(pattern, 0) + 1

    output = {
        "fixtures": sanitized_fixtures,
        "pii_audit": audit_report,
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Write scripts/distribution-validator.py**

```python
#!/usr/bin/env python3
"""Validate statistical distribution of test data.

Usage:
  cat fixtures.json | python distribution-validator.py --field premium_amount --expected-mode 150

Input: JSON fixture array, field name
Output: Distribution analysis + verdict (realistic | synthetic)
"""

import argparse
import json
import statistics
import sys
from typing import Any


def extract_numeric_values(fixtures: list[dict], field: str) -> list[float]:
    """Extract numeric field values."""
    values = []
    for fixture in fixtures:
        value = fixture.get(field)
        if isinstance(value, (int, float)):
            values.append(float(value))
    return sorted(values)


def analyze_distribution(values: list[float]) -> dict[str, Any]:
    """Analyze statistical distribution."""
    if not values:
        return {"error": "No numeric values found"}

    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0,
        "quartile_25": sorted(values)[len(values) // 4],
        "quartile_75": sorted(values)[3 * len(values) // 4],
    }


def main():
    parser = argparse.ArgumentParser(description="Validate distribution of test data")
    parser.add_argument("--field", required=True, help="Field name to analyze")
    parser.add_argument("--expected-mode", type=float, help="Expected central tendency")
    parser.add_argument("--expected-range", type=float, help="Expected std deviation")
    args = parser.parse_args()

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        data = [data]

    values = extract_numeric_values(data, args.field)
    analysis = analyze_distribution(values)

    verdict = "realistic"
    warnings = []

    if analysis.get("count", 0) < 5:
        warnings.append("Sample size < 5 (too small for statistical analysis)")

    if args.expected_mode and values:
        distance_from_mode = abs(analysis["mean"] - args.expected_mode)
        if distance_from_mode > args.expected_mode * 0.5:
            warnings.append(f"Mean {analysis['mean']:.2f} far from expected mode {args.expected_mode}")
            verdict = "suspicious"

    if analysis.get("stdev", 0) > 0:
        cv = analysis["stdev"] / analysis["mean"] if analysis["mean"] != 0 else 0
        if cv > 2:
            warnings.append(f"High coefficient of variation {cv:.2f} (possible uniform random)")
            verdict = "synthetic"

    output = {
        "field": args.field,
        "analysis": analysis,
        "verdict": verdict,
        "warnings": warnings,
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
```

- [ ] **Step 7: Write references/insurance-data-schemas.md**

```markdown
# Insurance Domain Data Schemas

Entity definitions, field types, valid ranges, and realistic distributions for test data generation.

## Policy

```json
{
  "id": "string (unique)",
  "policy_number": "string (POL-*)",
  "customer_name": "string",
  "customer_email": "string",
  "coverage_type": "enum: auto|home|life|health",
  "premium_amount": "number (50-5000, mode ~200)",
  "effective_date": "ISO8601 date",
  "expiration_date": "ISO8601 date",
  "status": "enum: active|expired|cancelled|suspended",
  "deductible": "number (250|500|1000|2500)",
  "beneficiary": "string (optional)",
  "claims_history": "array of claim_ids (optional)"
}
```

**Premium Distribution:** Claims cluster around $150-300 for auto, $200-400 for home, $500-1500 for life. Not uniform.

## Claim

```json
{
  "id": "string (unique)",
  "claim_number": "string (CLM-*)",
  "policy_id": "string",
  "incident_date": "ISO8601 date",
  "claim_date": "ISO8601 date",
  "claim_type": "enum: auto|home|life|health|general",
  "amount_claimed": "number (100-50000, mode ~2000)",
  "amount_approved": "number (0 to amount_claimed, optional)",
  "status": "enum: open|approved|denied|pending_review|settled",
  "description": "string",
  "supporting_documents": "array of file_paths (optional)"
}
```

## Customer

```json
{
  "id": "string (unique)",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "date_of_birth": "ISO8601 date (age 18-80)",
  "address": "string",
  "city": "string",
  "state": "string (2-letter code)",
  "zip_code": "string",
  "driver_license_state": "string (optional)",
  "occupation": "string (optional)"
}
```

## Quote

```json
{
  "id": "string (unique)",
  "customer_email": "string",
  "coverage_type": "enum: auto|home|life",
  "estimated_premium": "number (50-1000)",
  "quote_date": "ISO8601 date",
  "expiration_date": "ISO8601 date (quote_date + 30 days)",
  "status": "enum: pending|accepted|expired|rejected",
  "vehicle_info": "object (for auto quotes, optional)",
  "property_info": "object (for home quotes, optional)"
}
```
```

- [ ] **Step 8: Write references/pii-patterns.md**

```markdown
# PII Patterns Reference

Patterns that trigger sanitization in test data. All test fixtures must use obviously fake values.

## Obvious Fake Values (Allowed)

These patterns are allowed in test data and NOT sanitized:
- SSN: `999-99-9999` (invalid check digit)
- Phone: `555-0100`, `555-0199` (reserved for tests)
- Email: `test_*@test.example`, `*@localhost` (fake domain)
- License: `DL123456` (truncated, obviously fake)
- Address: `123 Test St`, `Test City, TS 99999`
- Policy: `POL-TEST-*`
- Claim: `CLM-TEST-*`
- Customer: `Test {LastName}`
- CC: `4111-1111-1111-1111` (Visa test number)

## Patterns Triggering Sanitization

| Type | Pattern | Replacement | Reason |
|------|---------|-------------|--------|
| SSN | `\b(?!999-99-9999)\d{3}-\d{2}-\d{4}\b` | `999-99-9999` | Real SSN format |
| Phone | `\b(?!555-0100)[\d]{3}-[\d]{3}-[\d]{4}\b` | `555-0100` | Real phone format |
| Email | `[a-z]+@(?!test\|example)[a-z.]+` | `test_user@test.example` | Real email domain |
| Credit Card | `\b(?!4111)\d{4}-?\d{4}-?\d{4}-?\d{4}\b` | `4111-1111-1111-1111` | Real CC format |
| License | `[A-Z]{2}\d{6,8}` (state-like) | `DL123456` | Real license format |

## PII Audit Output

All sanitization runs produce an audit report:
```json
{
  "total_fixtures": 10,
  "pii_findings": 2,
  "findings_by_pattern": {
    "email_real": 1,
    "phone": 1
  },
  "details": [
    {
      "pattern": "email_real",
      "found": "john.doe@company.com",
      "context": "customer_email"
    }
  ]
}
```
```

- [ ] **Step 9: Write templates/fixture.json.liquid**

```liquid
{
  "fixtures": [
    {% for fixture in fixtures %}
    {
      "id": "{{ fixture.id }}",
      "entity_type": "{{ entity_type }}",
      "data": {
        {% for key, value in fixture %}
        "{{ key }}": {% if value is string %}"{{ value }}"{% else %}{{ value }}{% endif %}{% unless forloop.last %},{% endunless %}
        {% endfor %}
      },
      "generated_at": "{{ 'now' | date: '%Y-%m-%dT%H:%M:%SZ' }}",
      "sanitized": true
    }{% unless forloop.last %},{% endunless %}
    {% endfor %}
  ],
  "metadata": {
    "domain": "{{ domain }}",
    "entity_type": "{{ entity_type }}",
    "count": {{ fixtures | size }},
    "format": "json"
  }
}
```

- [ ] **Step 10: Write templates/factory.ts.liquid**

```liquid
// AUTO-GENERATED TEST FACTORY — Do not edit
// Entity: {{ entity_type }}

import { Faker } from '@faker-js/faker';

interface {{ entity_type | capitalize }} {
  {% for key, type in schema %}
  {{ key }}: {{ type }};
  {% endfor %}
}

export class {{ entity_type | capitalize }}Factory {
  private faker: Faker;

  constructor(seed?: number) {
    this.faker = new Faker({ seed });
  }

  create(overrides?: Partial<{{ entity_type | capitalize }}>): {{ entity_type | capitalize }} {
    const base: {{ entity_type | capitalize }} = {
      {% for fixture in fixtures limit: 1 %}
      {% for key, value in fixture %}
      {{ key }}: {% if value is string %}'{{ value }}'{% else %}{{ value }}{% endif %},
      {% endfor %}
      {% endfor %}
    };
    return { ...base, ...overrides };
  }

  createMany(count: number, overrides?: Partial<{{ entity_type | capitalize }}>): {{ entity_type | capitalize }}[] {
    return Array.from({ length: count }).map(() => this.create(overrides));
  }
}
```

- [ ] **Step 11: Write templates/factory.py.liquid**

```liquid
# AUTO-GENERATED TEST FACTORY — Do not edit
# Entity: {{ entity_type }}

from dataclasses import dataclass, field, replace
from datetime import date, datetime
from typing import Optional, List
from faker import Faker

@dataclass
class {{ entity_type | capitalize }}:
    """{{ entity_type | capitalize }} fixture class."""
    {% for fixture in fixtures limit: 1 %}
    {% for key, value in fixture %}
    {{ key }}: type = None
    {% endfor %}
    {% endfor %}


class {{ entity_type | capitalize }}Factory:
    """Factory for generating {{ entity_type }} test fixtures."""

    def __init__(self, seed: Optional[int] = None):
        self.faker = Faker()
        if seed:
            Faker.seed(seed)

    def create(self, **overrides) -> {{ entity_type | capitalize }}:
        """Create a single {{ entity_type }} fixture."""
        base = {{ entity_type | capitalize }}(
            {% for fixture in fixtures limit: 1 %}
            {% for key, value in fixture %}
            {{ key }}={% if value is string %}'{{ value }}'{% else %}{{ value }}{% endif %},
            {% endfor %}
            {% endfor %}
        )
        return replace(base, **overrides)

    def create_many(self, count: int, **overrides) -> List[{{ entity_type | capitalize }}]:
        """Create multiple {{ entity_type }} fixtures."""
        return [self.create(**overrides) for _ in range(count)]
```

- [ ] **Step 12: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "gtd-tc-001"
    description: "Generate 5 policy fixtures with insurance domain realism"
    input:
      domain: "insurance"
      entity_type: "policy"
      count: 5
      output_format: "json"
    expected:
      fixture_count: 5
      pii_audit_pass: true
      has_distribution_report: true
      fields_present: ["id", "policy_number", "premium_amount", "status"]

  - id: "gtd-tc-002"
    description: "PII sanitization detects and replaces real email patterns"
    input:
      domain: "insurance"
      entity_type: "customer"
      count: 3
      fixture_with_real_email: "john.smith@company.com"
    expected:
      pii_audit_pass: true
      email_sanitized: "test_*@test.example"
      findings_by_pattern: { "email_real": 1 }

  - id: "gtd-tc-003"
    description: "Distribution validator detects unrealistic uniform random values"
    input:
      domain: "insurance"
      entity_type: "policy"
      count: 20
      field: "premium_amount"
      values: "uniform_random_1_to_10000"
    expected:
      verdict: "synthetic"
      warnings_contain: ["coefficient of variation"]

  - id: "gtd-tc-004"
    description: "TypeScript factory template generates valid code"
    input:
      entity_type: "policy"
      fixture_count: 5
      template: "factory.ts"
    expected:
      output_contains: "PolicyFactory"
      output_contains: "create("
      output_contains: "createMany("
      typescript_valid: true
```

- [ ] **Step 13: Write evals/assertions.yaml**

```yaml
assertions:
  - test_case: "gtd-tc-001"
    checks:
      - { field: "fixtures", operator: "length_equals", value: 5 }
      - { field: "fixtures[0].id", operator: "matches", value: "POL-" }
      - { field: "pii_audit.pii_findings", operator: "equals", value: 0 }
      - { field: "distribution_report", operator: "exists" }

  - test_case: "gtd-tc-002"
    checks:
      - { field: "pii_audit.findings_by_pattern.email_real", operator: "equals", value: 1 }
      - { field: "fixtures[0].customer_email", operator: "matches", value: "test_" }
      - { field: "pii_audit.pii_findings", operator: "gte", value: 1 }

  - test_case: "gtd-tc-003"
    checks:
      - { field: "verdict", operator: "equals", value: "synthetic" }
      - { field: "warnings", operator: "contains", value: "coefficient of variation" }

  - test_case: "gtd-tc-004"
    checks:
      - { field: "output", operator: "contains", value: "class PolicyFactory" }
      - { field: "output", operator: "contains", value: "create(" }
      - { field: "output", operator: "contains", value: "createMany(" }
```

- [ ] **Step 14: Verify file count and structure**

```bash
find .github/skills/qa/generating-test-data -type f | wc -l
# Expected: 11 files

find .github/skills/qa/generating-test-data -name "*.py" -exec python3 -m py_compile {} \;
# Should exit 0 (valid Python)
```

- [ ] **Step 15: Commit**

```bash
git add .github/skills/qa/generating-test-data/
git commit -m "feat(qa-skills): add generating-test-data skill (P2)

SKILL.md with domain/entity_type/count inputs, fixtures/pii_audit/distribution_report outputs.
Scripts: data-generator.py (Faker-based fixture creation), pii-sanitizer.py (scan+replace patterns), distribution-validator.py (realism checks).
References: insurance-data-schemas.md (entity definitions), pii-patterns.md (sanitization rules).
Templates: fixture.json.liquid, factory.ts.liquid, factory.py.liquid.
Evals: 4 test cases covering generation, PII sanitization, distribution validation, template rendering."
```

---

## Task 3: generating-playwright-tests skill

Generate Page Object Model tests for web applications. Analyze DOM, extract selectors, generate assertions.

**Files:**
- Create: `.github/skills/qa/generating-playwright-tests/SKILL.md`
- Create: `.github/skills/qa/generating-playwright-tests/requirements.txt`
- Create: `.github/skills/qa/generating-playwright-tests/scripts/selector-strategy.py`
- Create: `.github/skills/qa/generating-playwright-tests/scripts/page-analyzer.py`
- Create: `.github/skills/qa/generating-playwright-tests/references/playwright-patterns.md`
- Create: `.github/skills/qa/generating-playwright-tests/references/pom-conventions.md`
- Create: `.github/skills/qa/generating-playwright-tests/references/web-testing-standards.md`
- Create: `.github/skills/qa/generating-playwright-tests/templates/page-object.ts.liquid`
- Create: `.github/skills/qa/generating-playwright-tests/templates/spec.ts.liquid`
- Create: `.github/skills/qa/generating-playwright-tests/templates/fixture.ts.liquid`
- Create: `.github/skills/qa/generating-playwright-tests/evals/test-prompts.yaml`
- Create: `.github/skills/qa/generating-playwright-tests/evals/assertions.yaml`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p .github/skills/qa/generating-playwright-tests/{scripts,references,templates,evals}
```

- [ ] **Step 2: Write requirements.txt**

```
playwright==1.40.0
lxml==4.9.3
pydantic==2.5.0
```

- [ ] **Step 3: Write SKILL.md**

```markdown
---
name: generating-playwright-tests
version: "1.0.0"
description: "Generate Page Object Model tests from HTML pages with stable selectors and accessibility assertions"
category: generation
phase: post-coding
platforms: ["web"]
dependencies: ["test-driven-development"]
soft_dependencies: []
input_schema:
  - name: "page_url"
    type: "string"
    required: true
    description: "URL of page to analyze (http:// or file://)"
  - name: "test_scenarios"
    type: "array"
    required: true
    description: "List of test scenarios describing user flows"
  - name: "output_format"
    type: "string"
    required: false
    default: "ts"
    description: "ts | js"
output_schema:
  - name: "page_objects"
    type: "array"
    description: "Generated Page Object Model classes"
  - name: "test_specs"
    type: "array"
    description: "Generated test spec files"
  - name: "selector_audit"
    type: "object"
    description: "Selector stability analysis"
  - name: "accessibility_issues"
    type: "array"
    description: "Found accessibility violations"
---

# generating-playwright-tests

Generate type-safe Playwright tests using Page Object Model pattern. Analyzes HTML, extracts stable selectors, flags fragile DOM patterns, generates spec files with AAA structure.

## When to Use

Use after HTML/UI is stabilized to generate test scaffolds. Run before committing test files to verify selector stability.

## Instructions

1. Provide page URL and list of test scenarios (user flows, assertions)
2. Run `scripts/page-analyzer.py` to extract page structure, interactive elements, ARIA landmarks
3. Run `scripts/selector-strategy.py` to recommend selectors (data-testid > role > css), flag fragile XPath/nth-child
4. Generate Page Object Model using `page-object.ts.liquid` template
5. Generate spec files using `spec.ts.liquid` template with AAA (Arrange/Act/Assert) structure
6. Output includes selector audit and accessibility violations

## Guardrails

- **Stable selectors only.** Prioritize data-testid > aria-label/role > CSS selectors. Flag any XPath on dynamic content.
- **No hardcoded waits.** Use waitForSelector or loadState instead of sleep().
- **Accessibility checks.** Flag missing form labels, color contrast issues, touch targets < 44pt.
- **No credentials in code.** Flag any test data containing passwords or API keys.
- **Cross-browser ready.** Generated code runs on Chromium, Firefox, WebKit.

## Consumers

- `test-driven-development` — provides test strategy context
- E2E test engineers — extend generated Page Objects and specs

## References

- `playwright-patterns.md` — wait strategies, network mocking, debugging techniques
- `pom-conventions.md` — Page Object structure, method naming conventions
- `web-testing-standards.md` — WCAG A11y, responsive design, cross-browser patterns
```

- [ ] **Step 4: Write scripts/selector-strategy.py**

```python
#!/usr/bin/env python3
"""Analyze HTML and recommend stable, fragile selectors.

Usage:
  python selector-strategy.py --html page.html --output selectors.json

Output: JSON with recommended selectors, fragility scores, alternative strategies.
"""

import argparse
import json
import sys
from typing import Any
from html.parser import HTMLParser

from lxml import html as lxml_html
from pydantic import BaseModel


class SelectorRecommendation(BaseModel):
    element: str
    text: str = ""
    recommended: str = ""
    alternatives: list[str] = []
    stability_score: float = 0.0
    issues: list[str] = []


class HTMLAnalyzer(HTMLParser):
    """Extract interactive elements and their contexts."""

    def __init__(self):
        super().__init__()
        self.interactive_elements = []
        self.current_element = None

    def handle_starttag(self, tag, attrs):
        if tag in ['button', 'a', 'input', 'select', 'textarea']:
            attr_dict = dict(attrs)
            self.interactive_elements.append({
                'tag': tag,
                'attrs': attr_dict,
                'text': '',
            })

    def handle_data(self, data):
        if self.interactive_elements:
            self.interactive_elements[-1]['text'] += data


def analyze_with_lxml(html_content: str) -> list[SelectorRecommendation]:
    """Use lxml to analyze DOM structure and recommend selectors."""
    recommendations = []

    try:
        tree = lxml_html.fromstring(html_content)
    except Exception as e:
        print(f"Error parsing HTML: {e}", file=sys.stderr)
        return recommendations

    # Find all interactive elements
    for element in tree.xpath('//button | //a | //input | //select | //textarea'):
        rec = SelectorRecommendation(element=element.tag)

        # Extract text
        text = element.text_content() or ""
        rec.text = text.strip()[:50]

        # Strategy 1: data-testid (most stable)
        data_testid = element.get('data-testid')
        if data_testid:
            rec.recommended = f'[data-testid="{data_testid}"]'
            rec.stability_score = 1.0
        else:
            rec.issues.append("Missing data-testid (most stable selector)")

        # Strategy 2: aria-label + role
        aria_label = element.get('aria-label')
        role = element.get('role') or element.tag
        if aria_label:
            rec.alternatives.append(f'[aria-label="{aria_label}"]')

        # Strategy 3: CSS class (moderate stability)
        class_attr = element.get('class', '')
        if class_attr:
            classes = class_attr.split()
            stable_classes = [c for c in classes if not c.startswith('_')]
            if stable_classes:
                css_selector = '.' + '.'.join(stable_classes[:2])
                rec.alternatives.append(css_selector)
                if not rec.recommended:
                    rec.recommended = css_selector
                    rec.stability_score = 0.7

        # Strategy 4: Text content (fragile for dynamic content)
        if text and not rec.recommended:
            xpath = f'//{element.tag}[contains(text(), "{text[:30]}")]'
            rec.alternatives.append(xpath)
            rec.issues.append(f"Text-based selector fragile if content changes: {text[:30]}")

        # Check for fragile patterns
        if 'nth-child' in (rec.recommended or ''):
            rec.issues.append("XPath with nth-child is fragile (DOM reordering breaks)")
            rec.stability_score = min(rec.stability_score, 0.3)

        if '//' in (rec.recommended or '') and 'testid' not in (rec.recommended or ''):
            rec.issues.append("XPath hard to maintain; prefer CSS or data-testid")

        recommendations.append(rec)

    return recommendations


def main():
    parser = argparse.ArgumentParser(description="Analyze HTML and recommend selectors")
    parser.add_argument("--html", required=True, help="HTML file path")
    parser.add_argument("--output", default="selectors.json", help="Output JSON file")
    args = parser.parse_args()

    try:
        with open(args.html, 'r') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"HTML file not found: {args.html}", file=sys.stderr)
        sys.exit(1)

    recommendations = analyze_with_lxml(html_content)

    audit = {
        "total_elements": len(recommendations),
        "with_data_testid": sum(1 for r in recommendations if 'data-testid' in r.recommended),
        "with_issues": sum(1 for r in recommendations if r.issues),
        "recommendations": [r.model_dump() for r in recommendations],
    }

    with open(args.output, 'w') as f:
        json.dump(audit, f, indent=2)

    print(f"Analysis complete: {args.output}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Write scripts/page-analyzer.py**

```python
#!/usr/bin/env python3
"""Parse page structure, extract interactive elements, group by section.

Usage:
  python page-analyzer.py --html page.html --output structure.json

Output: JSON with page sections, interactive elements, ARIA landmarks.
"""

import argparse
import json
import sys
from typing import Any
from lxml import html as lxml_html


def analyze_page_structure(html_content: str) -> dict[str, Any]:
    """Extract page structure: headers, nav, sections, forms."""
    structure = {
        "page_title": "",
        "landmarks": [],
        "forms": [],
        "interactive_elements": [],
        "sections": [],
    }

    try:
        tree = lxml_html.fromstring(html_content)
    except Exception as e:
        print(f"Error parsing HTML: {e}", file=sys.stderr)
        return structure

    # Extract title
    title_elem = tree.xpath('//title')
    if title_elem:
        structure["page_title"] = title_elem[0].text_content()

    # Extract ARIA landmarks
    for landmark in tree.xpath('//*[@role="main"] | //*[@role="navigation"] | //*[@role="contentinfo"]'):
        structure["landmarks"].append({
            "role": landmark.get("role"),
            "text": landmark.text_content()[:100],
        })

    # Extract forms
    for form in tree.xpath('//form'):
        form_data = {
            "action": form.get("action", ""),
            "method": form.get("method", "GET"),
            "fields": [],
        }
        for field in form.xpath('.//input | .//select | .//textarea'):
            form_data["fields"].append({
                "name": field.get("name", ""),
                "type": field.get("type", "text"),
                "required": field.get("required") is not None,
                "label": field.xpath('preceding::label[1]/text()')[0] if field.xpath('preceding::label[1]/text()') else "",
            })
        structure["forms"].append(form_data)

    # Extract interactive elements
    for elem in tree.xpath('//button | //a | //input[@type="submit"]'):
        structure["interactive_elements"].append({
            "tag": elem.tag,
            "text": elem.text_content().strip()[:50],
            "type": elem.get("type", "button"),
            "data-testid": elem.get("data-testid", ""),
        })

    # Extract sections (divs with role or heading)
    for section in tree.xpath('//div[@role] | //section | //article'):
        structure["sections"].append({
            "role": section.get("role", ""),
            "heading": section.xpath('.//h1/text() | .//h2/text() | .//h3/text()')[0] if section.xpath('.//h1 | .//h2 | .//h3') else "",
        })

    return structure


def main():
    parser = argparse.ArgumentParser(description="Analyze page structure")
    parser.add_argument("--html", required=True, help="HTML file path")
    parser.add_argument("--output", default="structure.json", help="Output JSON file")
    args = parser.parse_args()

    try:
        with open(args.html, 'r') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"HTML file not found: {args.html}", file=sys.stderr)
        sys.exit(1)

    structure = analyze_page_structure(html_content)

    with open(args.output, 'w') as f:
        json.dump(structure, f, indent=2)

    print(f"Structure analysis complete: {args.output}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Write references/playwright-patterns.md**

```markdown
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
```

- [ ] **Step 7: Write references/pom-conventions.md**

```markdown
# Page Object Model Conventions

Structure and naming conventions for Page Objects.

## Class Structure

```typescript
export class LoginPage {
  constructor(readonly page: Page) {}

  // Locators (private, use methods to access)
  private usernameField = () => this.page.locator('[data-testid="username"]');
  private passwordField = () => this.page.locator('[data-testid="password"]');
  private submitButton = () => this.page.locator('button[type="submit"]');

  // Actions (public methods)
  async enterUsername(username: string): Promise<void> {
    await this.usernameField().fill(username);
  }

  async enterPassword(password: string): Promise<void> {
    await this.passwordField().fill(password);
  }

  async clickLogin(): Promise<void> {
    await this.submitButton().click();
  }

  async login(username: string, password: string): Promise<void> {
    await this.enterUsername(username);
    await this.enterPassword(password);
    await this.clickLogin();
  }

  // Assertions (return state/value for chaining)
  async isLoginButtonEnabled(): Promise<boolean> {
    return await this.submitButton().isEnabled();
  }

  async getErrorMessage(): Promise<string> {
    return await this.page.locator('[role="alert"]').textContent();
  }
}
```

## Naming Conventions

- **Locator methods:** snake_case, describe element type: `submitButton()`, `emailInput()`, `submitError()`
- **Action methods:** `click*`, `fill*`, `select*`, `hover*`: `clickSubmit()`, `fillEmail()`, `selectCountry()`
- **Assertion methods:** `is*`, `get*`, `has*`: `isEnabled()`, `getText()`, `hasError()`
- **Navigation methods:** `goto*`, `navigate*`: `gotoLoginPage()`, `navigateTo(url)`

## Encapsulation Rules

1. Locators are private; expose via methods
2. Actions return void or derived Page Object
3. Assertions return values (string, boolean, number)
4. Navigation returns new Page Object or void

```typescript
// Good: Encapsulated
export class CheckoutPage {
  async proceedToPayment(): Promise<PaymentPage> {
    await this.continueButton().click();
    return new PaymentPage(this.page);
  }
}

// Bad: Exposed locator
export class CheckoutPage {
  continueButton = () => this.page.locator('button.continue');
}
```
```

- [ ] **Step 8: Write references/web-testing-standards.md**

```markdown
# Web Testing Standards

Accessibility, responsive design, and cross-browser testing.

## WCAG A11y Checklist

- [ ] Form inputs have associated `<label>` elements
- [ ] Interactive elements have `aria-label` or visible text
- [ ] Color contrast ratio >= 4.5:1 (normal text), 3:1 (large text)
- [ ] Focus indicators visible (outline or custom)
- [ ] Touch targets >= 44x44 px
- [ ] Images have alt text (empty alt for decorative)
- [ ] Links have descriptive text (not "click here")
- [ ] Headings in logical order (h1, h2, h3)
- [ ] ARIA landmarks: main, nav, contentinfo
- [ ] Error messages linked to form fields

## Responsive Design Testing

```typescript
// Test multiple viewports
const viewports = [
  { name: 'mobile', width: 375, height: 667 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1920, height: 1080 },
];

for (const vp of viewports) {
  await page.setViewportSize({ width: vp.width, height: vp.height });
  // Assert layout changes, buttons visible, no overflow
  expect(await page.locator('button').count()).toBeGreaterThan(0);
}
```

## Cross-Browser Compatibility

Test on multiple browsers to catch platform-specific issues:

```typescript
export default {
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
};
```

## Test Data Best Practices

- Use realistic data (test.example email, 555-0100 phone)
- Avoid PII in assertions
- Clean up test data after each suite
- Use fixtures for shared data
```

- [ ] **Step 9: Write templates/page-object.ts.liquid**

```liquid
// AUTO-GENERATED PAGE OBJECT — Do not edit
// Page: {{ page_name }}

import { Page, Locator } from '@playwright/test';

export class {{ page_class_name }} {
  constructor(readonly page: Page) {}

  // Locators
  {% for element in elements %}
  private {{ element.name }}(): Locator {
    return this.page.locator('{{ element.selector }}');
  }
  {% endfor %}

  // Actions
  {% for action in actions %}
  async {{ action.name }}({% if action.param %}{{ action.param_name }}: {{ action.param_type }}{% endif %}): Promise<void> {
    {% if action.action_type == 'fill' %}
    await this.{{ action.locator }}().fill({{ action.param_name }});
    {% elsif action.action_type == 'click' %}
    await this.{{ action.locator }}().click();
    {% elsif action.action_type == 'select' %}
    await this.{{ action.locator }}().selectOption({{ action.param_name }});
    {% endif %}
  }
  {% endfor %}

  // Assertions
  {% for assertion in assertions %}
  async {{ assertion.name }}(): Promise<{{ assertion.return_type }}> {
    return await this.{{ assertion.locator }}().{% if assertion.return_type == 'boolean' %}isVisible(){% elsif assertion.return_type == 'string' %}textContent(){% endif %};
  }
  {% endfor %}
}
```

- [ ] **Step 10: Write templates/spec.ts.liquid**

```liquid
// AUTO-GENERATED TEST SPEC — Do not edit
// Scenario: {{ scenario_name }}

import { test, expect } from '@playwright/test';
import { {{ page_class_name }} } from './{{ page_file }}';

test.describe('{{ scenario_name }}', () => {
  let page: {{ page_class_name }};

  test.beforeEach(async ({ page: rawPage }) => {
    page = new {{ page_class_name }}(rawPage);
    await rawPage.goto('{{ test_url }}');
  });

  {% for test_case in test_cases %}
  test('{{ test_case.description }}', async () => {
    // Arrange
    {% for setup in test_case.arrange %}
    {{ setup }}
    {% endfor %}

    // Act
    {% for action in test_case.act %}
    await page.{{ action }}();
    {% endfor %}

    // Assert
    {% for assertion in test_case.assert %}
    expect({{ assertion }}).toBeTruthy();
    {% endfor %}
  });
  {% endfor %}
});
```

- [ ] **Step 11: Write templates/fixture.ts.liquid**

```liquid
// AUTO-GENERATED TEST FIXTURES — Do not edit

export const test_data = {
  {% for fixture in fixtures %}
  {{ fixture.key }}: {
    {% for field, value in fixture.data %}
    {{ field }}: '{{ value }}',
    {% endfor %}
  },
  {% endfor %}
};

export const mock_responses = {
  {% for mock in mocks %}
  {{ mock.endpoint }}: {
    status: {{ mock.status }},
    body: {{ mock.body | json }},
  },
  {% endfor %}
};
```

- [ ] **Step 12: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "gpt-tc-001"
    description: "Generate Page Object Model for simple login form"
    input:
      page_html: "login_form.html"
      test_scenarios:
        - "User enters valid credentials and submits form"
        - "User sees error message on invalid credentials"
    expected:
      pom_class_count: 1
      has_locators: true
      has_fill_action: true
      has_click_action: true
      selector_audit_pass: true

  - id: "gpt-tc-002"
    description: "Generate spec with AAA structure for form interaction"
    input:
      page_html: "form.html"
      test_scenarios:
        - "User fills email, password, clicks submit, sees success"
    expected:
      test_spec_count: 1
      has_beforeEach: true
      has_arrange_section: true
      has_act_section: true
      has_assert_section: true

  - id: "gpt-tc-003"
    description: "Selector analyzer flags missing data-testid on critical elements"
    input:
      page_html: "checkout.html"
    expected:
      selector_audit_issues: true
      issues_contain: ["data-testid"]
      stability_scores_exist: true

  - id: "gpt-tc-004"
    description: "Generated code uses stable selectors (data-testid > role > css)"
    input:
      page_html: "dashboard.html"
    expected:
      locators_use_data_testid: true
      locators_prioritize_role: false
      no_fragile_xpath: true
```

- [ ] **Step 13: Write evals/assertions.yaml**

```yaml
assertions:
  - test_case: "gpt-tc-001"
    checks:
      - { field: "pom_class_name", operator: "matches", value: "^[A-Z][a-zA-Z]*Page$" }
      - { field: "locators", operator: "length_gte", value: 3 }
      - { field: "locators[0].selector", operator: "matches", value: "\\[data-testid" }
      - { field: "selector_audit.with_data_testid", operator: "gte", value: 1 }

  - test_case: "gpt-tc-002"
    checks:
      - { field: "spec_beforeEach", operator: "exists" }
      - { field: "spec_tests[0].sections.Arrange", operator: "exists" }
      - { field: "spec_tests[0].sections.Act", operator: "exists" }
      - { field: "spec_tests[0].sections.Assert", operator: "exists" }

  - test_case: "gpt-tc-003"
    checks:
      - { field: "selector_audit.with_issues", operator: "gte", value: 1 }
      - { field: "selector_audit.recommendations[*].issues", operator: "contains", value: "data-testid" }

  - test_case: "gpt-tc-004"
    checks:
      - { field: "locators[*].recommended", operator: "all_match", value: "data-testid" }
      - { field: "locators[*].recommended", operator: "not_contains", value: "//" }
      - { field: "locators[*].stability_score", operator: "all_gte", value: 0.8 }
```

- [ ] **Step 14: Verify file count and structure**

```bash
find .github/skills/qa/generating-playwright-tests -type f | wc -l
# Expected: 12 files

find .github/skills/qa/generating-playwright-tests -name "*.py" -exec python3 -m py_compile {} \;
# Should exit 0 (valid Python)

python3 -c "import yaml; yaml.safe_load(open('.github/skills/qa/generating-playwright-tests/evals/test-prompts.yaml'))"
# Should exit 0 (valid YAML)
```

- [ ] **Step 15: Commit**

```bash
git add .github/skills/qa/generating-playwright-tests/
git commit -m "feat(qa-skills): add generating-playwright-tests skill (P2)

SKILL.md with page_url/test_scenarios inputs, page_objects/test_specs/selector_audit outputs.
Scripts: selector-strategy.py (DOM analysis, stable selector recommendations), page-analyzer.py (structure extraction).
References: playwright-patterns.md (wait strategies, mocking), pom-conventions.md (class structure, naming), web-testing-standards.md (a11y, responsive, cross-browser).
Templates: page-object.ts.liquid (typed POM class), spec.ts.liquid (AAA test structure), fixture.ts.liquid (test data).
Evals: 4 test cases covering POM generation, spec structure, selector analysis, stability scoring."
```

---

## Task 4: generating-api-tests skill

Generate API test suites from OpenAPI/GraphQL schemas. Parse endpoints, generate happy path + edge cases.

**Files:**
- Create: `.github/skills/qa/generating-api-tests/SKILL.md`
- Create: `.github/skills/qa/generating-api-tests/requirements.txt`
- Create: `.github/skills/qa/generating-api-tests/scripts/schema-parser.py`
- Create: `.github/skills/qa/generating-api-tests/scripts/endpoint-analyzer.py`
- Create: `.github/skills/qa/generating-api-tests/references/api-testing-patterns.md`
- Create: `.github/skills/qa/generating-api-tests/references/schema-validation-rules.md`
- Create: `.github/skills/qa/generating-api-tests/templates/rest.test.ts.liquid`
- Create: `.github/skills/qa/generating-api-tests/templates/graphql.test.ts.liquid`
- Create: `.github/skills/qa/generating-api-tests/templates/pytest-api.py.liquid`
- Create: `.github/skills/qa/generating-api-tests/evals/test-prompts.yaml`
- Create: `.github/skills/qa/generating-api-tests/evals/assertions.yaml`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p .github/skills/qa/generating-api-tests/{scripts,references,templates,evals}
```

- [ ] **Step 2: Write requirements.txt**

```
pyyaml==6.0.1
jsonschema==4.20.0
pydantic==2.5.0
```

- [ ] **Step 3: Write SKILL.md**

```markdown
---
name: generating-api-tests
version: "1.0.0"
description: "Generate API test suites from OpenAPI 3.x and GraphQL schemas with happy path and edge cases"
category: generation
phase: post-coding
platforms: ["api"]
dependencies: ["test-driven-development"]
soft_dependencies: []
input_schema:
  - name: "schema"
    type: "object|string"
    required: true
    description: "OpenAPI 3.x spec, Swagger 2.0, or GraphQL SDL file path"
  - name: "test_style"
    type: "string"
    required: false
    default: "jest"
    description: "jest | pytest | ts-rest"
  - name: "base_url"
    type: "string"
    required: false
    description: "API base URL for tests (non-production)"
output_schema:
  - name: "test_suites"
    type: "array"
    description: "Generated test files by endpoint"
  - name: "schema_coverage_report"
    type: "object"
    description: "Endpoint coverage, edge case analysis"
  - name: "security_audit"
    type: "object"
    description: "Auth requirements, hardcoded secret detection"
---

# generating-api-tests

Generate comprehensive API test suites from OpenAPI, Swagger, or GraphQL schemas. Produces happy path tests + edge cases (null fields, empty arrays, boundary values). Detects security issues (hardcoded tokens, production URLs).

## When to Use

Use when API schema is finalized and endpoints stable. Run before committing API tests to verify coverage and security.

## Instructions

1. Provide API schema (OpenAPI YAML, Swagger JSON, or GraphQL SDL)
2. Specify test style (Jest for Node/TypeScript, pytest for Python)
3. Run `scripts/schema-parser.py` to extract endpoints, parameters, schemas
4. Run `scripts/endpoint-analyzer.py` to classify operations and generate edge cases
5. Generate test suites using language-specific templates
6. Output includes schema coverage report and security audit

## Guardrails

- **No hardcoded auth tokens.** Flag any API keys, bearer tokens, or credentials in test files.
- **Non-production URLs only.** Verify base_url not production (not api.example.com, only localhost, staging.example.com).
- **Strict schema validation.** Tests must validate response structure against schema, not just status code.
- **Contract testing.** Happy path should document request/response contract; edge cases should test boundaries.
- **Error scenarios.** Include tests for 400 (bad request), 401 (unauthorized), 404 (not found), 500 (server error).

## Consumers

- `test-driven-development` — provides API testing context
- Backend API teams — validate against schemas pre-deployment

## References

- `api-testing-patterns.md` — HTTP mocking, request/response validation, error handling
- `schema-validation-rules.md` — OpenAPI/GraphQL validation rules, response structure checks
```

- [ ] **Step 4: Write scripts/schema-parser.py**

```python
#!/usr/bin/env python3
"""Parse OpenAPI 3.x, Swagger 2.0, GraphQL schemas; extract endpoints and schemas.

Usage:
  python schema-parser.py --schema openapi.yaml --output endpoints.json

Output: JSON with extracted endpoints, parameters, request/response schemas.
"""

import argparse
import json
import sys
from typing import Any
from pathlib import Path

import yaml
from pydantic import BaseModel


class EndpointParameter(BaseModel):
    name: str
    in_: str  # query, path, header, body
    required: bool = False
    schema_ref: str = ""


class EndpointSchema(BaseModel):
    path: str
    method: str  # get, post, put, delete, patch
    summary: str = ""
    parameters: list[EndpointParameter] = []
    request_body_schema: str = ""
    response_schema: str = ""
    auth_required: bool = False


def parse_openapi(spec: dict) -> list[EndpointSchema]:
    """Extract endpoints from OpenAPI 3.x spec."""
    endpoints = []

    paths = spec.get("paths", {})
    for path_str, path_item in paths.items():
        for method_str, operation in path_item.items():
            if method_str.startswith("x-"):
                continue

            endpoint = EndpointSchema(
                path=path_str,
                method=method_str.lower(),
                summary=operation.get("summary", ""),
            )

            # Extract parameters
            for param in operation.get("parameters", []):
                endpoint.parameters.append(
                    EndpointParameter(
                        name=param.get("name", ""),
                        in_=param.get("in", ""),
                        required=param.get("required", False),
                        schema_ref=param.get("schema", {}).get("$ref", ""),
                    )
                )

            # Extract request body schema
            request_body = operation.get("requestBody", {})
            if request_body:
                content = request_body.get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    endpoint.request_body_schema = schema.get("$ref", "")

            # Extract response schema
            responses = operation.get("responses", {})
            if "200" in responses:
                response = responses["200"]
                content = response.get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    endpoint.response_schema = schema.get("$ref", "")

            # Check auth requirement
            security = operation.get("security", [])
            endpoint.auth_required = len(security) > 0

            endpoints.append(endpoint)

    return endpoints


def parse_graphql(sdl: str) -> list[EndpointSchema]:
    """Parse GraphQL SDL; extract queries and mutations."""
    endpoints = []

    # Simple regex-based parsing for SDL
    import re

    # Extract queries
    for match in re.finditer(r'type\s+Query\s*\{([^}]+)\}', sdl):
        query_body = match.group(1)
        for field in re.finditer(r'(\w+)\s*\([^)]*\)\s*:\s*([^,}\n]+)', query_body):
            name, return_type = field.groups()
            endpoints.append(
                EndpointSchema(
                    path=f"/graphql (query {name})",
                    method="post",
                    summary=f"GraphQL query: {name}",
                    response_schema=return_type.strip(),
                )
            )

    # Extract mutations
    for match in re.finditer(r'type\s+Mutation\s*\{([^}]+)\}', sdl):
        mutation_body = match.group(1)
        for field in re.finditer(r'(\w+)\s*\([^)]*\)\s*:\s*([^,}\n]+)', mutation_body):
            name, return_type = field.groups()
            endpoints.append(
                EndpointSchema(
                    path=f"/graphql (mutation {name})",
                    method="post",
                    summary=f"GraphQL mutation: {name}",
                    response_schema=return_type.strip(),
                )
            )

    return endpoints


def main():
    parser = argparse.ArgumentParser(description="Parse API schema and extract endpoints")
    parser.add_argument("--schema", required=True, help="OpenAPI YAML, Swagger JSON, or GraphQL SDL file")
    parser.add_argument("--output", default="endpoints.json", help="Output JSON file")
    args = parser.parse_args()

    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Schema file not found: {args.schema}", file=sys.stderr)
        sys.exit(1)

    with open(schema_path) as f:
        if schema_path.suffix in ['.yaml', '.yml']:
            content = yaml.safe_load(f)
            if isinstance(content, dict) and "openapi" in content:
                endpoints = parse_openapi(content)
            else:
                print(f"Unrecognized YAML schema format", file=sys.stderr)
                sys.exit(1)
        elif schema_path.suffix == '.json':
            content = json.load(f)
            endpoints = parse_openapi(content)
        elif schema_path.suffix == '.graphql':
            sdl = f.read()
            endpoints = parse_graphql(sdl)
        else:
            print(f"Unsupported schema format: {schema_path.suffix}", file=sys.stderr)
            sys.exit(1)

    audit = {
        "total_endpoints": len(endpoints),
        "auth_required_count": sum(1 for e in endpoints if e.auth_required),
        "endpoints": [e.model_dump() for e in endpoints],
    }

    with open(args.output, 'w') as f:
        json.dump(audit, f, indent=2)

    print(f"Schema parsing complete: {args.output}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Write scripts/endpoint-analyzer.py**

```python
#!/usr/bin/env python3
"""Classify endpoints, generate edge case test scenarios.

Usage:
  cat endpoints.json | python endpoint-analyzer.py --output scenarios.json

Output: JSON with CRUD classification, edge case scenarios for each endpoint.
"""

import json
import sys
from typing import Any
from pydantic import BaseModel


class EdgeCaseScenario(BaseModel):
    name: str
    description: str
    inputs: dict[str, Any]
    expected_status: int = 200


class EndpointAnalysis(BaseModel):
    path: str
    method: str
    operation_type: str  # CREATE, READ, UPDATE, DELETE, CUSTOM
    risk_level: str  # low, medium, high, critical
    edge_cases: list[EdgeCaseScenario] = []


def classify_operation(method: str, path: str) -> str:
    """Classify endpoint as CRUD, auth, or custom."""
    method_upper = method.upper()

    if method_upper == "GET":
        return "READ"
    elif method_upper == "POST":
        return "CREATE"
    elif method_upper in ["PUT", "PATCH"]:
        return "UPDATE"
    elif method_upper == "DELETE":
        return "DELETE"
    else:
        return "CUSTOM"


def classify_risk_level(path: str, operation: str) -> str:
    """Classify endpoint risk: auth=high, payment=critical, CRUD=medium."""
    path_lower = path.lower()

    if "auth" in path_lower or "login" in path_lower:
        return "high"
    elif "payment" in path_lower or "billing" in path_lower:
        return "critical"
    elif "claim" in path_lower or "policy" in path_lower:
        return "high"
    elif operation in ["DELETE", "UPDATE"]:
        return "medium"
    else:
        return "low"


def generate_edge_cases(endpoint: dict) -> list[EdgeCaseScenario]:
    """Generate common edge case scenarios."""
    cases = [
        EdgeCaseScenario(
            name="Happy path",
            description="Normal, valid request with valid inputs",
            inputs={"valid": True},
            expected_status=200 if endpoint["method"].upper() != "DELETE" else 204,
        ),
    ]

    # Add method-specific edge cases
    if endpoint["method"].upper() == "GET":
        cases.extend([
            EdgeCaseScenario(
                name="Not found",
                description="Resource does not exist",
                inputs={"id": "nonexistent"},
                expected_status=404,
            ),
            EdgeCaseScenario(
                name="Empty query results",
                description="Query returns empty array",
                inputs={"filter": "never_matches"},
                expected_status=200,
            ),
        ])
    elif endpoint["method"].upper() in ["POST", "PUT", "PATCH"]:
        cases.extend([
            EdgeCaseScenario(
                name="Missing required field",
                description="Request body missing required field",
                inputs={"missing_field": True},
                expected_status=400,
            ),
            EdgeCaseScenario(
                name="Invalid data type",
                description="Field has wrong data type",
                inputs={"email": 12345},
                expected_status=400,
            ),
            EdgeCaseScenario(
                name="Null values",
                description="Optional fields are null",
                inputs={"optional_field": None},
                expected_status=200,
            ),
        ])
    elif endpoint["method"].upper() == "DELETE":
        cases.append(
            EdgeCaseScenario(
                name="Delete nonexistent",
                description="Attempt to delete non-existent resource",
                inputs={"id": "nonexistent"},
                expected_status=404,
            )
        )

    # Add auth-specific cases
    if endpoint.get("auth_required"):
        cases.extend([
            EdgeCaseScenario(
                name="Missing authorization",
                description="Request without auth token",
                inputs={"auth": False},
                expected_status=401,
            ),
            EdgeCaseScenario(
                name="Invalid token",
                description="Request with malformed auth token",
                inputs={"auth": "invalid_token"},
                expected_status=401,
            ),
        ])

    return cases


def main():
    try:
        endpoints_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    analyses = []
    for endpoint in endpoints_data.get("endpoints", []):
        analysis = EndpointAnalysis(
            path=endpoint["path"],
            method=endpoint["method"],
            operation_type=classify_operation(endpoint["method"], endpoint["path"]),
            risk_level=classify_risk_level(endpoint["path"], endpoint["method"]),
            edge_cases=generate_edge_cases(endpoint),
        )
        analyses.append(analysis)

    output = {
        "total_endpoints": len(analyses),
        "high_risk_count": sum(1 for a in analyses if a.risk_level in ["high", "critical"]),
        "analyses": [a.model_dump() for a in analyses],
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Write references/api-testing-patterns.md**

```markdown
# API Testing Patterns

Best practices for REST and GraphQL API testing.

## Happy Path Test Structure

```typescript
test('GET /policies/:id returns policy', async () => {
  // Arrange: Setup test data
  const policyId = 'POL-123';

  // Act: Make API request
  const response = await fetch(`/api/policies/${policyId}`);
  const data = await response.json();

  // Assert: Verify response structure
  expect(response.status).toBe(200);
  expect(data).toHaveProperty('id', policyId);
  expect(data).toHaveProperty('premium_amount');
});
```

## HTTP Mocking

```typescript
import fetchMock from 'jest-fetch-mock';

fetchMock.enableMocks();

beforeEach(() => {
  fetchMock.resetMocks();
});

test('Handle API error', async () => {
  fetchMock.mockRejectOnce(() =>
    Promise.reject(new Error('Network error'))
  );

  // Expect error handling
  expect(async () => {
    await fetchPolicies();
  }).rejects.toThrow();
});
```

## Contract Testing

Validate response against schema:

```typescript
import Ajv from 'ajv';

const ajv = new Ajv();
const policySchema = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    premium_amount: { type: 'number', minimum: 0 },
    status: { enum: ['active', 'expired', 'cancelled'] },
  },
  required: ['id', 'premium_amount'],
};

test('Response validates against policy schema', async () => {
  const response = await fetch('/api/policies/POL-123');
  const data = await response.json();

  const valid = ajv.validate(policySchema, data);
  expect(valid).toBe(true);
});
```

## Error Response Testing

```typescript
test('400 Bad Request includes error details', async () => {
  const response = await fetch('/api/policies', {
    method: 'POST',
    body: JSON.stringify({ /* missing required field */ }),
  });

  expect(response.status).toBe(400);
  const error = await response.json();
  expect(error).toHaveProperty('message');
  expect(error).toHaveProperty('field', 'premium_amount');
});

test('401 Unauthorized without auth token', async () => {
  const response = await fetch('/api/admin/policies');
  expect(response.status).toBe(401);
  expect(response.headers.get('www-authenticate')).toBeDefined();
});
```

## Anti-Patterns

- DON'T: Use `setTimeout()` to wait for responses
- DON'T: Hardcode API keys or credentials
- DON'T: Test against production URL
- DON'T: Skip response validation (only check status 200)
- DO: Mock external APIs
- DO: Validate response structure
- DO: Test error scenarios
- DO: Use fixtures for test data
```

- [ ] **Step 7: Write references/schema-validation-rules.md**

```markdown
# Schema Validation Rules

OpenAPI and GraphQL validation best practices.

## OpenAPI Response Validation

```typescript
import ajv from 'ajv';

const schema = {
  type: 'object',
  properties: {
    id: { type: 'string', pattern: '^POL-[0-9]+$' },
    premium_amount: { type: 'number', minimum: 0, maximum: 100000 },
    status: { enum: ['active', 'expired', 'cancelled'] },
    created_at: { type: 'string', format: 'date-time' },
  },
  required: ['id', 'premium_amount', 'status'],
  additionalProperties: false,
};

const validate = ajv.compile(schema);

test('Response matches schema', async () => {
  const response = await fetch('/api/policies/POL-123');
  const data = await response.json();

  const valid = validate(data);
  expect(valid).toBe(true);
  if (!valid) {
    console.log('Validation errors:', validate.errors);
  }
});
```

## GraphQL Response Validation

```typescript
test('GraphQL query returns expected fields', async () => {
  const query = `{
    policy(id: "POL-123") {
      id
      premiumAmount
      status
    }
  }`;

  const response = await fetch('/graphql', {
    method: 'POST',
    body: JSON.stringify({ query }),
  });

  const { data, errors } = await response.json();
  expect(errors).toBeUndefined();
  expect(data.policy).toHaveProperty('id');
  expect(data.policy.premiumAmount).toBeGreaterThan(0);
});
```

## Error Response Format

All errors should follow this structure:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Premium amount must be greater than 0",
    "details": {
      "field": "premium_amount",
      "value": -100,
      "constraint": "minimum: 0"
    }
  }
}
```

## Auth Header Validation

```typescript
test('Authorization header required', async () => {
  const response = await fetch('/api/admin/policies');
  expect(response.status).toBe(401);

  const authHeader = response.headers.get('www-authenticate');
  expect(authHeader).toMatch(/Bearer realm="API"/);
});
```
```

- [ ] **Step 8: Write templates/rest.test.ts.liquid**

```liquid
// AUTO-GENERATED REST API TEST SUITE — Do not edit
// API: {{ api_name }}

import { test, expect } from '@jest/globals';

const BASE_URL = process.env.API_BASE_URL || 'http://localhost:3000';

describe('REST API: {{ api_name }}', () => {
  {% for endpoint in endpoints %}
  describe('{{ endpoint.method | upcase }} {{ endpoint.path }}', () => {
    {% for scenario in endpoint.scenarios %}
    test('{{ scenario.description }}', async () => {
      // Arrange
      const url = `${BASE_URL}{{ endpoint.path }}`;
      const options = {
        method: '{{ endpoint.method | upcase }}',
        headers: { 'Content-Type': 'application/json' },
      };
      {% if scenario.request_body %}
      options.body = JSON.stringify({{ scenario.request_body | json }});
      {% endif %}

      // Act
      const response = await fetch(url, options);
      const data = await response.json();

      // Assert
      expect(response.status).toBe({{ scenario.expected_status }});
      {% if scenario.assertions %}
      {% for assertion in scenario.assertions %}
      expect(data).toHaveProperty('{{ assertion.property }}');
      {% endfor %}
      {% endif %}
    });
    {% endfor %}
  });
  {% endfor %}
});
```

- [ ] **Step 9: Write templates/graphql.test.ts.liquid**

```liquid
// AUTO-GENERATED GraphQL TEST SUITE — Do not edit

import { test, expect } from '@jest/globals';

const BASE_URL = process.env.GRAPHQL_URL || 'http://localhost:3000/graphql';

describe('GraphQL API', () => {
  {% for operation in operations %}
  test('{{ operation.type }}: {{ operation.name }}', async () => {
    const {{ operation.type | downcase }}Query = `
      {{ operation.type | downcase }} {{ operation.name }} {
        {% for field in operation.fields %}
        {{ field }}
        {% endfor %}
      }
    `;

    const response = await fetch(BASE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: {{ operation.type | downcase }}Query }),
    });

    const { data, errors } = await response.json();
    expect(errors).toBeUndefined();
    expect(data).toBeDefined();
    {% for assertion in operation.assertions %}
    expect(data).toHaveProperty('{{ assertion }}');
    {% endfor %}
  });
  {% endfor %}
});
```

- [ ] **Step 10: Write templates/pytest-api.py.liquid**

```liquid
# AUTO-GENERATED API TEST SUITE (PYTEST) — Do not edit

import os
import pytest
import requests

BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:3000')

{% for endpoint in endpoints %}
class Test{{ endpoint.name | capitalize }}:
    """Tests for {{ endpoint.method | upcase }} {{ endpoint.path }}"""

    {% for scenario in endpoint.scenarios %}
    def test_{{ scenario.name | replace(' ', '_') | downcase }}(self):
        """{{ scenario.description }}"""
        # Arrange
        url = f"{BASE_URL}{{ endpoint.path }}"
        {% if scenario.request_body %}
        payload = {{ scenario.request_body | json }}
        {% endif %}

        # Act
        response = requests.{{ endpoint.method | downcase }}(
            url,
            json=payload if 'payload' in locals() else None,
        )

        # Assert
        assert response.status_code == {{ scenario.expected_status }}
        {% if scenario.assertions %}
        data = response.json()
        {% for assertion in scenario.assertions %}
        assert '{{ assertion.property }}' in data
        {% endfor %}
        {% endif %}
    {% endfor %}
{% endfor %}
```

- [ ] **Step 11: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "gat-tc-001"
    description: "Parse OpenAPI 3.x schema and extract all endpoints"
    input:
      schema_file: "openapi.yaml"
      schema_format: "openapi"
    expected:
      total_endpoints: 5
      auth_required_count: 2
      endpoints_have_paths: true
      endpoints_have_methods: true

  - id: "gat-tc-002"
    description: "Generate REST test suite with happy path and edge cases"
    input:
      endpoints:
        - path: "/api/policies/:id"
          method: "get"
          auth_required: true
    expected:
      test_count: 3
      includes_happy_path: true
      includes_not_found: true
      includes_unauthorized: true

  - id: "gat-tc-003"
    description: "Generate GraphQL query tests from SDL"
    input:
      schema_file: "schema.graphql"
      operations:
        - type: "Query"
          name: "policies"
    expected:
      test_count: 1
      validates_response: true
      no_hardcoded_credentials: true

  - id: "gat-tc-004"
    description: "Analyze endpoints and classify risk level"
    input:
      endpoints:
        - path: "/api/admin/users"
          method: "delete"
        - path: "/api/payment/charge"
          method: "post"
    expected:
      delete_risk: "medium"
      payment_risk: "critical"
      high_risk_count: 1
      critical_risk_count: 1
```

- [ ] **Step 12: Write evals/assertions.yaml**

```yaml
assertions:
  - test_case: "gat-tc-001"
    checks:
      - { field: "endpoints[*].path", operator: "all_exist" }
      - { field: "endpoints[*].method", operator: "all_in", value: ["get", "post", "put", "delete", "patch"] }
      - { field: "auth_required_count", operator: "gte", value: 1 }

  - test_case: "gat-tc-002"
    checks:
      - { field: "tests", operator: "length_gte", value: 3 }
      - { field: "tests[*].scenario", operator: "contains", value: "Happy path" }
      - { field: "tests[*].scenario", operator: "contains", value: "Not found" }

  - test_case: "gat-tc-003"
    checks:
      - { field: "tests[0].query", operator: "contains", value: "query policies" }
      - { field: "tests[0].assertions[0]", operator: "matches", value: "data.policies" }
      - { field: "code", operator: "not_contains", value: "Authorization: Bearer" }

  - test_case: "gat-tc-004"
    checks:
      - { field: "analyses[0].risk_level", operator: "equals", value: "medium" }
      - { field: "analyses[1].risk_level", operator: "equals", value: "critical" }
      - { field: "high_risk_count", operator: "gte", value: 1 }
      - { field: "critical_risk_count", operator: "gte", value: 1 }
```

- [ ] **Step 13: Verify file count and structure**

```bash
find .github/skills/qa/generating-api-tests -type f | wc -l
# Expected: 11 files

python3 -c "import yaml; yaml.safe_load(open('.github/skills/qa/generating-api-tests/evals/test-prompts.yaml'))"
# Should exit 0 (valid YAML)

find .github/skills/qa/generating-api-tests -name "*.py" -exec python3 -m py_compile {} \;
# Should exit 0 (valid Python)
```

- [ ] **Step 14: Commit**

```bash
git add .github/skills/qa/generating-api-tests/
git commit -m "feat(qa-skills): add generating-api-tests skill (P2)

SKILL.md with schema/test_style inputs, test_suites/schema_coverage_report outputs.
Scripts: schema-parser.py (OpenAPI/GraphQL extraction), endpoint-analyzer.py (CRUD classification, edge case generation).
References: api-testing-patterns.md (HTTP mocking, contract validation), schema-validation-rules.md (response structure, auth header checks).
Templates: rest.test.ts.liquid (Jest tests), graphql.test.ts.liquid (GraphQL queries/mutations), pytest-api.py.liquid (Python tests).
Evals: 4 test cases covering schema parsing, test generation, edge cases, risk classification."
```

---

## Task 5: generating-mobile-tests skill

Generate mobile tests for iOS/Android. Detect platform, generate framework-specific code.

**Files:**
- Create: `.github/skills/qa/generating-mobile-tests/SKILL.md`
- Create: `.github/skills/qa/generating-mobile-tests/requirements.txt`
- Create: `.github/skills/qa/generating-mobile-tests/scripts/platform-detector.py`
- Create: `.github/skills/qa/generating-mobile-tests/scripts/accessibility-checker.py`
- Create: `.github/skills/qa/generating-mobile-tests/references/appium-patterns.md`
- Create: `.github/skills/qa/generating-mobile-tests/references/xctest-patterns.md`
- Create: `.github/skills/qa/generating-mobile-tests/references/uiautomator-patterns.md`
- Create: `.github/skills/qa/generating-mobile-tests/templates/appium.test.ts.liquid`
- Create: `.github/skills/qa/generating-mobile-tests/templates/xctest.swift.liquid`
- Create: `.github/skills/qa/generating-mobile-tests/templates/espresso.kt.liquid`
- Create: `.github/skills/qa/generating-mobile-tests/evals/test-prompts.yaml`
- Create: `.github/skills/qa/generating-mobile-tests/evals/assertions.yaml`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p .github/skills/qa/generating-mobile-tests/{scripts,references,templates,evals}
```

- [ ] **Step 2: Write requirements.txt**

```
pyyaml==6.0.1
pydantic==2.5.0
```

- [ ] **Step 3: Write SKILL.md**

```markdown
---
name: generating-mobile-tests
version: "1.0.0"
description: "Generate iOS/Android mobile tests with platform detection and accessibility checks"
category: generation
phase: post-coding
platforms: ["ios", "android"]
dependencies: ["test-driven-development"]
soft_dependencies: []
input_schema:
  - name: "platform"
    type: "string"
    required: false
    description: "ios | android | cross-platform (auto-detect if omitted)"
  - name: "screen_list"
    type: "array"
    required: true
    description: "List of screen names to test"
  - name: "test_scenarios"
    type: "array"
    required: true
    description: "User flows: tap, swipe, input, assertions"
output_schema:
  - name: "test_suites"
    type: "array"
    description: "Generated test files (XCTest, Espresso, or Appium)"
  - name: "accessibility_audit"
    type: "object"
    description: "WCAG A11y violations found"
  - name: "platform_detected"
    type: "string"
    description: "ios | android | flutter"
---

# generating-mobile-tests

Generate native and cross-platform mobile tests. Auto-detects platform from project structure (Xcode, Gradle, flutter.yaml). Produces framework-specific code: XCTest (Swift) for iOS, Espresso (Kotlin) for Android, Appium (TypeScript) for cross-platform. Validates accessibility: VoiceOver labels, touch targets >= 44pt.

## When to Use

Use when mobile app structure is stable. Run before committing mobile tests to verify platform detection and accessibility.

## Instructions

1. Provide list of screen names and test scenarios
2. Run `scripts/platform-detector.py` to identify iOS/Android/Flutter
3. Run `scripts/accessibility-checker.py` to scan for accessibility violations
4. Generate platform-specific tests using corresponding template
5. Output includes accessibility audit and platform detection confidence

## Guardrails

- **No XPath fallback.** Use accessibility ID, content-desc, or image matching; XPath only if no alternative.
- **Rotation tests required.** All tests must handle device rotation (portrait/landscape).
- **Accessibility enabled.** Tests must include VoiceOver/TalkBack labels in assertions.
- **No hardcoded coordinates.** Use element identifiers, not pixel coordinates.
- **Touch targets >= 44pt.** Flag any buttons/clickable < 44x44 dp (iOS) or 48x48 dp (Android).

## Consumers

- `test-driven-development` — provides mobile testing context
- Mobile QA engineers — extend generated tests with platform-specific edge cases

## References

- `appium-patterns.md` — cross-platform element finding, gesture commands
- `xctest-patterns.md` — iOS XCTest API, async patterns, accessibility
- `uiautomator-patterns.md` — Android Espresso, UIAutomator locators
```

- [ ] **Step 4: Write scripts/platform-detector.py**

```python
#!/usr/bin/env python3
"""Detect iOS, Android, or Flutter from project structure.

Usage:
  python platform-detector.py --project-dir . --output platform.json

Output: JSON with detected platform, confidence, framework version.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def detect_platform(project_dir: str) -> dict[str, Any]:
    """Detect platform from project files."""
    project_path = Path(project_dir)

    result = {
        "platform": None,
        "confidence": 0.0,
        "detected_files": [],
        "ios_indicators": [],
        "android_indicators": [],
        "flutter_indicators": [],
    }

    # Check for iOS/Xcode
    ios_files = [
        "ios/Runner.xcworkspace",
        "ios/Runner.xcodeproj",
        "Podfile",
        "ios/Podfile.lock",
    ]
    for f in ios_files:
        if (project_path / f).exists():
            result["ios_indicators"].append(f)
            result["detected_files"].append(f)

    # Check for Android
    android_files = [
        "android/app/build.gradle",
        "android/settings.gradle",
        "android/build.gradle",
        "android/gradle.properties",
    ]
    for f in android_files:
        if (project_path / f).exists():
            result["android_indicators"].append(f)
            result["detected_files"].append(f)

    # Check for Flutter
    flutter_files = [
        "pubspec.yaml",
        "pubspec.lock",
        "flutter.yaml",
    ]
    for f in flutter_files:
        if (project_path / f).exists():
            result["flutter_indicators"].append(f)
            result["detected_files"].append(f)

    # Determine primary platform
    ios_count = len(result["ios_indicators"])
    android_count = len(result["android_indicators"])
    flutter_count = len(result["flutter_indicators"])

    if flutter_count > 0:
        result["platform"] = "flutter"
        result["confidence"] = 0.95 if flutter_count >= 2 else 0.7
    elif ios_count > android_count:
        result["platform"] = "ios"
        result["confidence"] = min(0.95, ios_count / 4.0)
    elif android_count > 0:
        result["platform"] = "android"
        result["confidence"] = min(0.95, android_count / 4.0)
    else:
        result["platform"] = "unknown"
        result["confidence"] = 0.0

    return result


def main():
    parser = argparse.ArgumentParser(description="Detect mobile platform")
    parser.add_argument("--project-dir", default=".", help="Project directory path")
    parser.add_argument("--output", default="platform.json", help="Output JSON file")
    args = parser.parse_args()

    result = detect_platform(args.project_dir)

    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Platform detection complete: {args.output}")
    print(f"Detected: {result['platform']} (confidence: {result['confidence']:.2%})")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Write scripts/accessibility-checker.py**

```python
#!/usr/bin/env python3
"""Check accessibility: VoiceOver labels, touch targets, color contrast.

Usage:
  python accessibility-checker.py --manifest android/app/src/main/AndroidManifest.xml --output a11y.json

Output: JSON with accessibility violations and warnings.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class A11yViolation:
    def __init__(self, severity: str, element: str, issue: str, fix: str):
        self.severity = severity  # error, warning, info
        self.element = element
        self.issue = issue
        self.fix = fix

    def to_dict(self):
        return {
            "severity": self.severity,
            "element": self.element,
            "issue": self.issue,
            "fix": self.fix,
        }


def check_android_manifest(manifest_path: str) -> list[A11yViolation]:
    """Check Android manifest for a11y issues."""
    violations = []

    try:
        with open(manifest_path) as f:
            content = f.read()
    except FileNotFoundError:
        return violations

    # Check for android:contentDescription on ImageView/ImageButton
    if '<ImageView' in content or '<ImageButton' in content:
        if 'android:contentDescription=' not in content:
            violations.append(
                A11yViolation(
                    'error',
                    'ImageView/ImageButton',
                    'Missing android:contentDescription',
                    'Add android:contentDescription="..." to all images'
                )
            )

    # Check for button labels
    if '<Button' in content or '<image-button' in content.lower():
        if 'android:text=' not in content and 'android:contentDescription=' not in content:
            violations.append(
                A11yViolation(
                    'error',
                    'Button',
                    'Button missing text or contentDescription',
                    'Add android:text or android:contentDescription'
                )
            )

    return violations


def check_ios_storyboard(storyboard_path: str) -> list[A11yViolation]:
    """Check iOS storyboard for a11y issues."""
    violations = []

    try:
        with open(storyboard_path) as f:
            content = f.read()
    except FileNotFoundError:
        return violations

    # Check for accessibilityLabel on buttons
    if '<button' in content.lower():
        if 'accessibilityLabel' not in content:
            violations.append(
                A11yViolation(
                    'error',
                    'UIButton',
                    'Button missing accessibilityLabel',
                    'Set accessibilityLabel on all buttons'
                )
            )

    return violations


def main():
    parser = argparse.ArgumentParser(description="Check mobile app accessibility")
    parser.add_argument("--manifest", help="Android manifest file path")
    parser.add_argument("--storyboard", help="iOS storyboard file path")
    parser.add_argument("--output", default="a11y.json", help="Output JSON file")
    args = parser.parse_args()

    violations = []

    if args.manifest:
        violations.extend(check_android_manifest(args.manifest))
    if args.storyboard:
        violations.extend(check_ios_storyboard(args.storyboard))

    audit = {
        "total_violations": len(violations),
        "errors": sum(1 for v in violations if v.severity == 'error'),
        "warnings": sum(1 for v in violations if v.severity == 'warning'),
        "violations": [v.to_dict() for v in violations],
    }

    with open(args.output, 'w') as f:
        json.dump(audit, f, indent=2)

    print(f"Accessibility check complete: {args.output}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Write references/appium-patterns.md**

```markdown
# Appium Cross-Platform Testing Patterns

Best practices for cross-platform mobile automation with Appium.

## Element Locators

Prefer accessibility ID > XPath:

```typescript
// Good: accessibility ID (works iOS & Android)
const loginButton = await driver.elementByAccessibilityId('login-button');

// Good: XPath with predicates (more stable)
const loginButton = await driver.elementByXPath('//XCUIElementTypeButton[@name="Login"]');

// Avoid: position-based or image locators (brittle)
const button = await driver.elementByImage('button.png');
```

## Gestures

```typescript
// Tap
await driver.elementByAccessibilityId('button').click();

// Swipe
const action = new wd.TouchAction(driver);
action.press({ x: 100, y: 100 })
      .moveTo({ x: 100, y: 200 })
      .release();
await action.perform();

// Long press
const action = new wd.TouchAction(driver);
action.longPress({ element: elem })
      .release();
await action.perform();
```

## Cross-Platform Test

```typescript
const platformName = await driver.platformName();

if (platformName === 'iOS') {
  // iOS-specific logic
  const elem = await driver.elementByAccessibilityId('ios-button');
} else if (platformName === 'Android') {
  // Android-specific logic
  const elem = await driver.elementByResourceId('com.example:id/android_button');
}
```

## Wait Strategies

```typescript
// Wait for element visible
await driver.waitForElementByAccessibilityId('content', 5000);

// Wait for condition
await driver.waitForElementByXPath('//XCUIElementTypeStaticText[@value="Loaded"]', 5000);
```
```

- [ ] **Step 7: Write references/xctest-patterns.md**

```markdown
# iOS XCTest Patterns

Best practices for iOS UI testing with XCTest.

## Page Object Structure

```swift
class LoginPage {
    let app: XCUIApplication

    init(_ app: XCUIApplication) {
        self.app = app
    }

    // Locators
    var usernameField: XCUIElement {
        app.textFields.matching(NSPredicate(format: "identifier == 'usernameInput'")).firstMatch
    }

    var passwordField: XCUIElement {
        app.secureTextFields.matching(NSPredicate(format: "identifier == 'passwordInput'")).firstMatch
    }

    var loginButton: XCUIElement {
        app.buttons.matching(NSPredicate(format: "identifier == 'loginBtn'")).firstMatch
    }

    // Actions
    func login(username: String, password: String) {
        usernameField.tap()
        usernameField.typeText(username)

        passwordField.tap()
        passwordField.typeText(password)

        loginButton.tap()
    }
}
```

## Async Wait Patterns

```swift
func testLogin() {
    let app = XCUIApplication()
    app.launch()

    // Wait for element existence
    let predicate = NSPredicate(format: "exists == true")
    expectation(for: predicate, evaluatedWith: app.staticTexts["Welcome"], handler: nil)
    waitForExpectations(timeout: 5)

    // Or explicit wait
    let element = app.staticTexts["Welcome"]
    let waitExpectation = expectation(for: NSPredicate(format: "isHittable == true"), evaluatedWith: element)
    wait(for: [waitExpectation], timeout: 5)
}
```

## Accessibility Testing

```swift
func testAccessibility() {
    let app = XCUIApplication()
    app.launch()

    // Verify accessibility label
    let button = app.buttons.element(matching: NSPredicate(format: "identifier == 'actionBtn'"))
    XCTAssertEqual(button.label, "Confirm Action") // VoiceOver label

    // Check image alternative text
    let icon = app.images["profileIcon"]
    XCTAssert(!icon.label.isEmpty, "Image must have accessibility label")
}
```

## Rotation Handling

```swift
func testPortraitAndLandscape() {
    let app = XCUIApplication()

    // Test in portrait
    XCUIDevice.shared.orientation = .portrait
    app.launch()
    let button = app.buttons["action"]
    XCTAssert(button.exists)

    // Rotate to landscape
    XCUIDevice.shared.orientation = .landscapeRight
    XCTAssert(button.exists, "Button must remain visible after rotation")
}
```
```

- [ ] **Step 8: Write references/uiautomator-patterns.md**

```markdown
# Android Espresso & UIAutomator Patterns

Best practices for Android UI testing.

## Page Object with Espresso

```kotlin
class LoginPageObject(private val device: UiDevice) {

    // Locators using UiSelector
    private val usernameField = device.findObject(
        UiSelector().resourceId("com.example:id/usernameInput")
    )

    private val passwordField = device.findObject(
        UiSelector().resourceId("com.example:id/passwordInput")
    )

    private val loginButton = device.findObject(
        UiSelector().resourceId("com.example:id/loginBtn")
    )

    // Actions
    fun login(username: String, password: String) {
        usernameField.clearTextField()
        usernameField.text = username

        passwordField.clearTextField()
        passwordField.text = password

        loginButton.click()
    }
}
```

## Espresso Matchers

```kotlin
@Test
fun testLogin() {
    onView(withId(R.id.usernameInput))
        .perform(typeText("testuser"))

    onView(withId(R.id.passwordInput))
        .perform(typeText("password123"))

    onView(withId(R.id.loginBtn))
        .perform(click())

    onView(withText("Welcome"))
        .check(matches(isDisplayed()))
}
```

## Content Description (A11y)

```kotlin
@Test
fun testAccessibility() {
    onView(withId(R.id.profilePic))
        .check(matches(hasContentDescription()))

    onView(withContentDescription("User Avatar"))
        .perform(click())
}
```

## Handling Device Rotation

```kotlin
@Test
fun testRotation() {
    // Assume activity survives rotation
    activity.requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
    onView(withId(R.id.button)).check(matches(isDisplayed()))

    // Rotate
    activity.requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
    onView(withId(R.id.button)).check(matches(isDisplayed()))
}
```
```

- [ ] **Step 9: Write templates/appium.test.ts.liquid**

```liquid
// AUTO-GENERATED APPIUM TEST SUITE — Do not edit
// Platform: {{ platform }} | Screens: {{ screen_list | join: ', ' }}

import { remote } from 'webdriverio';

describe('Mobile App: {{ app_name }}', () => {
  let driver;

  before(async () => {
    const opts = {
      platformName: '{{ platform | upcase }}',
      automationName: 'XCUITest', // or 'UIAutomator2' for Android
      deviceName: '{{ device_name }}',
      app: process.env.APP_PATH,
    };
    driver = await remote(opts);
  });

  after(async () => {
    await driver.deleteSession();
  });

  {% for scenario in scenarios %}
  it('{{ scenario.description }}', async () => {
    {% for action in scenario.actions %}
    // {{ action.description }}
    {% if action.type == 'tap' %}
    const element = await driver.$('{{ action.locator }}');
    await element.click();
    {% elsif action.type == 'input' %}
    const input = await driver.$('{{ action.locator }}');
    await input.clearValue();
    await input.addValue('{{ action.value }}');
    {% elsif action.type == 'swipe' %}
    await driver.touchAction([
      { action: 'press', x: {{ action.start_x }}, y: {{ action.start_y }} },
      { action: 'moveTo', x: {{ action.end_x }}, y: {{ action.end_y }} },
      'release'
    ]);
    {% endif %}
    {% endfor %}

    {% for assertion in scenario.assertions %}
    // Assert
    const result = await driver.$('{{ assertion.locator }}');
    expect(await result.isDisplayed()).toBe(true);
    {% endfor %}
  });
  {% endfor %}

  it('should handle device rotation', async () => {
    // Portrait
    await driver.setOrientation('PORTRAIT');
    const portraitElement = await driver.$('accessibility id:mainButton');
    expect(await portraitElement.isDisplayed()).toBe(true);

    // Landscape
    await driver.setOrientation('LANDSCAPE');
    expect(await portraitElement.isDisplayed()).toBe(true);
  });
});
```

- [ ] **Step 10: Write templates/xctest.swift.liquid**

```liquid
// AUTO-GENERATED XCTEST SUITE — Do not edit
// Screens: {{ screen_list | join: ', ' }}

import XCTest

class {{ test_class_name }}: XCTestCase {
    var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }

    override func tearDownWithError() throws {
        app = nil
    }

    {% for scenario in scenarios %}
    func test{{ scenario.name | camelize }}() throws {
        // Arrange
        {% for setup in scenario.arrange %}
        {{ setup }}
        {% endfor %}

        // Act
        {% for action in scenario.act %}
        {% if action.type == 'tap' %}
        let {{ action.var_name }} = app.buttons.matching(NSPredicate(format: "identifier == '{{ action.identifier }}'")).firstMatch
        {{ action.var_name }}.tap()
        {% elsif action.type == 'input' %}
        let {{ action.var_name }} = app.textFields.matching(NSPredicate(format: "identifier == '{{ action.identifier }}'")).firstMatch
        {{ action.var_name }}.tap()
        {{ action.var_name }}.typeText("{{ action.value }}")
        {% endif %}
        {% endfor %}

        // Assert
        {% for assertion in scenario.assertions %}
        let {{ assertion.var_name }} = app.staticTexts["{{ assertion.text }}"]
        let predicate = NSPredicate(format: "exists == true")
        expectation(for: predicate, evaluatedWith: {{ assertion.var_name }}, handler: nil)
        waitForExpectations(timeout: 5)
        {% endfor %}
    }
    {% endfor %}

    func testRotation() throws {
        XCUIDevice.shared.orientation = .portrait
        let button = app.buttons.element(boundBy: 0)
        XCTAssert(button.exists)

        XCUIDevice.shared.orientation = .landscapeRight
        XCTAssert(button.exists)
    }
}
```

- [ ] **Step 11: Write templates/espresso.kt.liquid**

```liquid
// AUTO-GENERATED ESPRESSO TEST SUITE — Do not edit

import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.typeText
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class {{ test_class_name }} {
    {% for scenario in scenarios %}
    @Test
    fun {{ scenario.name | snakeCase }}() {
        // Arrange
        {% for setup in scenario.arrange %}
        {{ setup }}
        {% endfor %}

        // Act
        {% for action in scenario.act %}
        {% if action.type == 'click' %}
        onView(withId(R.id.{{ action.resource_id }}))
            .perform(click())
        {% elsif action.type == 'input' %}
        onView(withId(R.id.{{ action.resource_id }}))
            .perform(typeText("{{ action.value }}"))
        {% endif %}
        {% endfor %}

        // Assert
        {% for assertion in scenario.assertions %}
        onView(withText("{{ assertion.text }}"))
            .check(matches(isDisplayed()))
        {% endfor %}
    }
    {% endfor %}

    @Test
    fun testAccessibility() {
        onView(withId(R.id.profileImage))
            .check(matches(hasContentDescription()))
    }
}
```

- [ ] **Step 12: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "gmt-tc-001"
    description: "Detect iOS platform from Xcode project structure"
    input:
      project_dir: "ios-app"
      has_files:
        - "ios/Runner.xcworkspace"
        - "Podfile"
    expected:
      platform: "ios"
      confidence_gte: 0.8
      detected_files_count: 2

  - id: "gmt-tc-002"
    description: "Generate XCTest suite with rotation handling"
    input:
      platform: "ios"
      screen_list: ["LoginScreen", "HomeScreen"]
      test_scenarios:
        - description: "User logs in and sees home screen"
    expected:
      test_count: 2
      includes_rotation_test: true
      no_hardcoded_coordinates: true

  - id: "gmt-tc-003"
    description: "Generate Espresso tests for Android"
    input:
      platform: "android"
      screen_list: ["LoginActivity", "DashboardActivity"]
      test_scenarios:
        - description: "User enters credentials and submits"
    expected:
      test_count: 2
      uses_resource_ids: true
      includes_accessibility_test: true

  - id: "gmt-tc-004"
    description: "Generate Appium cross-platform tests"
    input:
      platform: "cross-platform"
      screen_list: ["LoginPage"]
    expected:
      test_count: 2
      includes_orientation_test: true
      supports_both_ios_and_android: true
```

- [ ] **Step 13: Write evals/assertions.yaml**

```yaml
assertions:
  - test_case: "gmt-tc-001"
    checks:
      - { field: "platform", operator: "equals", value: "ios" }
      - { field: "confidence", operator: "gte", value: 0.8 }
      - { field: "detected_files", operator: "contains", value: "ios/Runner.xcworkspace" }

  - test_case: "gmt-tc-002"
    checks:
      - { field: "test_count", operator: "gte", value: 2 }
      - { field: "code", operator: "contains", value: "XCUIDevice.shared.orientation" }
      - { field: "code", operator: "not_contains", value: "// hardcoded coordinate" }

  - test_case: "gmt-tc-003"
    checks:
      - { field: "test_count", operator: "gte", value: 2 }
      - { field: "code", operator: "contains", value: "R.id." }
      - { field: "code", operator: "contains", value: "hasContentDescription" }

  - test_case: "gmt-tc-004"
    checks:
      - { field: "test_count", operator: "gte", value: 2 }
      - { field: "code", operator: "contains", value: "setOrientation" }
      - { field: "supports_platforms", operator: "contains", value: "iOS" }
      - { field: "supports_platforms", operator: "contains", value: "Android" }
```

- [ ] **Step 14: Verify file count and structure**

```bash
find .github/skills/qa/generating-mobile-tests -type f | wc -l
# Expected: 12 files

python3 -c "import yaml; yaml.safe_load(open('.github/skills/qa/generating-mobile-tests/evals/test-prompts.yaml'))"
# Should exit 0 (valid YAML)

find .github/skills/qa/generating-mobile-tests -name "*.py" -exec python3 -m py_compile {} \;
# Should exit 0 (valid Python)
```

- [ ] **Step 15: Commit**

```bash
git add .github/skills/qa/generating-mobile-tests/
git commit -m "feat(qa-skills): add generating-mobile-tests skill (P2)

SKILL.md with platform/screen_list/test_scenarios inputs, test_suites/accessibility_audit outputs.
Scripts: platform-detector.py (iOS/Android/Flutter auto-detection), accessibility-checker.py (VoiceOver/TalkBack label validation).
References: appium-patterns.md (cross-platform gestures, locators), xctest-patterns.md (iOS async, rotation), uiautomator-patterns.md (Android Espresso, content-desc).
Templates: appium.test.ts.liquid (TypeScript), xctest.swift.liquid (Swift), espresso.kt.liquid (Kotlin).
Evals: 4 test cases covering platform detection, XCTest generation, Espresso tests, rotation handling."
```

---

## Task 6: generating-perf-tests skill

Generate performance/load tests. Calculate realistic load profiles, generate test code.

**Files:**
- Create: `.github/skills/qa/generating-perf-tests/SKILL.md`
- Create: `.github/skills/qa/generating-perf-tests/requirements.txt`
- Create: `.github/skills/qa/generating-perf-tests/scripts/load-profile-calculator.py`
- Create: `.github/skills/qa/generating-perf-tests/scripts/baseline-collector.py`
- Create: `.github/skills/qa/generating-perf-tests/references/perf-testing-patterns.md`
- Create: `.github/skills/qa/generating-perf-tests/references/insurance-load-profiles.md`
- Create: `.github/skills/qa/generating-perf-tests/templates/k6.test.js.liquid`
- Create: `.github/skills/qa/generating-perf-tests/templates/locust.py.liquid`
- Create: `.github/skills/qa/generating-perf-tests/templates/gatling.scala.liquid`
- Create: `.github/skills/qa/generating-perf-tests/evals/test-prompts.yaml`
- Create: `.github/skills/qa/generating-perf-tests/evals/assertions.yaml`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p .github/skills/qa/generating-perf-tests/{scripts,references,templates,evals}
```

- [ ] **Step 2: Write requirements.txt**

```
pyyaml==6.0.1
pydantic==2.5.0
```

- [ ] **Step 3: Write SKILL.md**

```markdown
---
name: generating-perf-tests
version: "1.0.0"
description: "Generate load tests with realistic user profiles, think times, and SLA assertions"
category: generation
phase: post-coding
platforms: ["all"]
dependencies: []
soft_dependencies: ["test-driven-development"]
input_schema:
  - name: "endpoints"
    type: "array"
    required: true
    description: "List of endpoints to load test"
  - name: "load_profile"
    type: "string"
    required: true
    description: "ramp-up | spike | soak | custom"
  - name: "target_sla"
    type: "object"
    required: true
    description: "SLA targets: p95_latency_ms, error_rate_pct, throughput_rps"
  - name: "test_tool"
    type: "string"
    required: false
    default: "k6"
    description: "k6 | locust | gatling"
output_schema:
  - name: "load_test_code"
    type: "string"
    description: "Generated test script"
  - name: "baseline_metrics"
    type: "object"
    description: "Single-user baseline (latency, CPU, memory)"
  - name: "load_profile_config"
    type: "object"
    description: "VU ramp-up schedule, think times"
---

# generating-perf-tests

Generate load test scripts with realistic user behavior. Converts business SLAs (p95 latency < 200ms, error rate < 0.5%) into load profiles. Includes think time between requests, proper data correlation, and SLA assertions. Supports K6, Locust, and Gatling.

## When to Use

Use when API is production-ready and performance baselines established. Never target production. Always define SLA thresholds before running.

## Instructions

1. Provide list of endpoints and SLA targets
2. Specify load profile (ramp-up, spike, soak) and test tool
3. Run `scripts/load-profile-calculator.py` to convert SLA to VU schedule
4. Run `scripts/baseline-collector.py` to establish single-user baseline
5. Generate load test using tool-specific template
6. Output includes load profile config and baseline metrics

## Guardrails

- **Never target production.** Always verify base_url is staging/localhost, not api.example.com.
- **Define SLAs before running.** Expected p95 latency, error rate, throughput thresholds.
- **Include think time.** Realistic tests include 1-5s delays between requests to mimic user behavior.
- **Proper data correlation.** Extract IDs from responses, reuse in subsequent requests.
- **Monitor resource usage.** Test should include baseline CPU/memory, not just latency.

## Consumers

- Performance engineers — customize ramp-up, thresholds
- DevOps — use baseline metrics for capacity planning

## References

- `perf-testing-patterns.md` — virtual user modeling, think time, data correlation, ramping strategies
- `insurance-load-profiles.md` — typical insurance system loads, peak hours, concurrent user distribution
```

- [ ] **Step 4: Write scripts/load-profile-calculator.py**

```python
#!/usr/bin/env python3
"""Convert business SLAs into load profile (VU ramp schedule).

Usage:
  python load-profile-calculator.py --target-p95-ms 200 --target-rps 100 --profile ramp-up --output profile.json

Output: JSON with VU schedule, think time, expected metrics.
"""

import argparse
import json
import sys
import math
from typing import Any
from pydantic import BaseModel


class VUStage(BaseModel):
    duration_seconds: int
    target_vus: int
    description: str


class LoadProfile(BaseModel):
    profile_type: str  # ramp-up, spike, soak, custom
    total_duration_seconds: int
    stages: list[VUStage]
    think_time_seconds: float
    target_p95_latency_ms: float
    target_error_rate_pct: float
    target_throughput_rps: float


def calculate_ramp_up_profile(
    target_vus: int,
    target_p95_ms: float,
    target_rps: float,
    total_duration_seconds: int = 600,
) -> LoadProfile:
    """Generate ramp-up profile: gradually increase VUs over time."""
    ramp_duration = 300  # 5 minutes to reach target
    stage_count = 5

    stages = []
    for i in range(1, stage_count + 1):
        vus = int(target_vus * (i / stage_count))
        stages.append(
            VUStage(
                duration_seconds=ramp_duration // stage_count,
                target_vus=vus,
                description=f"Ramp-up stage {i}: {vus} VUs"
            )
        )

    # Steady state
    stages.append(
        VUStage(
            duration_seconds=total_duration_seconds - ramp_duration,
            target_vus=target_vus,
            description="Steady state"
        )
    )

    # Think time: estimate from target RPS
    think_time = max(1.0, (target_vus / target_rps) - 0.5)

    return LoadProfile(
        profile_type="ramp-up",
        total_duration_seconds=total_duration_seconds,
        stages=stages,
        think_time_seconds=think_time,
        target_p95_latency_ms=target_p95_ms,
        target_error_rate_pct=1.0,
        target_throughput_rps=target_rps,
    )


def calculate_spike_profile(
    target_vus: int,
    target_p95_ms: float,
    target_rps: float,
) -> LoadProfile:
    """Generate spike profile: sudden jump in load."""
    stages = [
        VUStage(
            duration_seconds=60,
            target_vus=5,
            description="Baseline load (5 VUs)"
        ),
        VUStage(
            duration_seconds=180,
            target_vus=target_vus,
            description=f"Spike: jump to {target_vus} VUs"
        ),
        VUStage(
            duration_seconds=120,
            target_vus=5,
            description="Recovery to baseline"
        ),
    ]

    think_time = max(1.0, (target_vus / target_rps) - 0.5)

    return LoadProfile(
        profile_type="spike",
        total_duration_seconds=360,
        stages=stages,
        think_time_seconds=think_time,
        target_p95_latency_ms=target_p95_ms,
        target_error_rate_pct=1.0,
        target_throughput_rps=target_rps,
    )


def calculate_soak_profile(
    target_vus: int,
    target_p95_ms: float,
    target_rps: float,
) -> LoadProfile:
    """Generate soak profile: sustained load over long time."""
    stages = [
        VUStage(
            duration_seconds=300,
            target_vus=target_vus,
            description=f"Ramp to {target_vus} VUs"
        ),
        VUStage(
            duration_seconds=3600,  # 1 hour
            target_vus=target_vus,
            description="Sustained load (1 hour)"
        ),
    ]

    think_time = max(1.0, (target_vus / target_rps) - 0.5)

    return LoadProfile(
        profile_type="soak",
        total_duration_seconds=3900,
        stages=stages,
        think_time_seconds=think_time,
        target_p95_latency_ms=target_p95_ms,
        target_error_rate_pct=1.0,
        target_throughput_rps=target_rps,
    )


def main():
    parser = argparse.ArgumentParser(description="Calculate load profile from SLA targets")
    parser.add_argument("--target-p95-ms", type=float, required=True, help="Target p95 latency (ms)")
    parser.add_argument("--target-rps", type=float, required=True, help="Target throughput (requests/sec)")
    parser.add_argument("--target-vus", type=int, default=None, help="Target VUs (auto-calc if omitted)")
    parser.add_argument("--profile", default="ramp-up", help="ramp-up | spike | soak")
    parser.add_argument("--output", default="profile.json", help="Output JSON file")
    args = parser.parse_args()

    # Auto-calculate VUs if not provided
    target_vus = args.target_vus or int(args.target_rps * 2)

    if args.profile == "spike":
        profile = calculate_spike_profile(target_vus, args.target_p95_ms, args.target_rps)
    elif args.profile == "soak":
        profile = calculate_soak_profile(target_vus, args.target_p95_ms, args.target_rps)
    else:
        profile = calculate_ramp_up_profile(target_vus, args.target_p95_ms, args.target_rps)

    with open(args.output, 'w') as f:
        json.dump(profile.model_dump(), f, indent=2)

    print(f"Load profile generated: {args.output}")
    print(f"Profile: {profile.profile_type}")
    print(f"Total duration: {profile.total_duration_seconds}s")
    print(f"Max VUs: {profile.stages[-1].target_vus}")
    print(f"Think time: {profile.think_time_seconds:.1f}s")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Write scripts/baseline-collector.py**

```python
#!/usr/bin/env python3
"""Collect single-user baseline metrics (latency, CPU, memory).

Usage:
  python baseline-collector.py --url http://localhost:3000 --requests 100 --output baseline.json

Output: JSON with p50/p95/p99 latencies, CPU/memory utilization, throughput.
"""

import argparse
import json
import sys
import subprocess
import time
from typing import Any
from pydantic import BaseModel


class BaselineMetric(BaseModel):
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    mean_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    throughput_rps: float
    error_count: int
    error_rate_pct: float


def collect_metrics(base_url: str, request_count: int = 100) -> BaselineMetric:
    """Run single-user load test and collect metrics."""
    latencies = []
    error_count = 0

    print(f"Collecting baseline metrics ({request_count} requests)...")

    for i in range(request_count):
        start = time.time()
        try:
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', base_url],
                capture_output=True,
                timeout=10,
            )
            elapsed = (time.time() - start) * 1000  # Convert to ms
            latencies.append(elapsed)

            if result.returncode != 0 or int(result.stdout.decode()) >= 400:
                error_count += 1
        except subprocess.TimeoutExpired:
            error_count += 1
            latencies.append(10000)  # Timeout = 10s

    latencies.sort()

    metric = BaselineMetric(
        p50_latency_ms=latencies[len(latencies) // 2],
        p95_latency_ms=latencies[int(len(latencies) * 0.95)],
        p99_latency_ms=latencies[int(len(latencies) * 0.99)],
        mean_latency_ms=sum(latencies) / len(latencies),
        min_latency_ms=min(latencies),
        max_latency_ms=max(latencies),
        throughput_rps=request_count / (sum(latencies) / 1000) if latencies else 0,
        error_count=error_count,
        error_rate_pct=(error_count / request_count * 100) if request_count > 0 else 0,
    )

    return metric


def main():
    parser = argparse.ArgumentParser(description="Collect baseline performance metrics")
    parser.add_argument("--url", required=True, help="API URL to test")
    parser.add_argument("--requests", type=int, default=100, help="Number of requests")
    parser.add_argument("--output", default="baseline.json", help="Output JSON file")
    args = parser.parse_args()

    metric = collect_metrics(args.url, args.requests)

    with open(args.output, 'w') as f:
        json.dump(metric.model_dump(), f, indent=2)

    print(f"Baseline metrics saved: {args.output}")
    print(f"p95 latency: {metric.p95_latency_ms:.0f}ms")
    print(f"Throughput: {metric.throughput_rps:.1f} rps")
    print(f"Error rate: {metric.error_rate_pct:.2f}%")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Write references/perf-testing-patterns.md**

```markdown
# Performance Testing Patterns

Best practices for realistic load testing.

## Virtual User Modeling

Think time models realistic user behavior:

```javascript
// Constant think time between requests
await page.goto(url);
await sleep(2000);  // 2 second think time
await page.click(button);
```

Vary think time for realism:

```javascript
// Random think time between 1-5 seconds
const thinkTime = Math.random() * 4000 + 1000;
await sleep(thinkTime);
```

## Data Correlation

Extract dynamic IDs from responses and reuse in subsequent requests:

```javascript
// First request returns policy ID
const response = await http.get('/api/policies');
const policyId = response.json('id');

// Use extracted ID in next request
const claimResponse = await http.post(`/api/policies/${policyId}/claims`, {
  amount: 1000,
});
```

## Ramp-Up Strategies

### Linear Ramp-Up

```javascript
// Increase 10 VUs every 1 minute until reaching 100
export const options = {
  stages: [
    { duration: '1m', target: 10 },
    { duration: '1m', target: 20 },
    { duration: '1m', target: 50 },
    { duration: '1m', target: 100 },
  ],
};
```

### Spike Test

```javascript
// Sudden traffic spike
export const options = {
  stages: [
    { duration: '1m', target: 5 },      // Baseline
    { duration: '2m', target: 100 },    // Spike
    { duration: '2m', target: 5 },      // Recovery
  ],
};
```

## SLA Assertions

```javascript
// Assert performance meets SLA
export const options = {
  thresholds: {
    'http_req_duration': ['p(95)<200'],      // p95 latency < 200ms
    'http_req_failed': ['rate<0.01'],        // Error rate < 1%
  },
};
```

## Error Handling

```javascript
// Handle transient errors (retry) vs real errors (fail)
export default function () {
  const response = http.get('/api/endpoint');

  if (response.status === 503) {
    // Service temporarily unavailable, retry is OK
  } else if (response.status >= 400) {
    // Real error, fail the test
    fail(`API error: ${response.status}`);
  }
}
```
```

- [ ] **Step 7: Write references/insurance-load-profiles.md**

```markdown
# Insurance System Load Profiles

Typical load patterns for insurance applications.

## Daily Load Pattern

Insurance systems experience peak load during business hours:

- **Off-peak (midnight-6am):** 5-10 concurrent users
- **Business hours (8am-5pm):** 100-500 concurrent users
- **Peak hours (10am, 2-3pm):** 500-1000 concurrent users
- **Evening (5pm-midnight):** 20-100 concurrent users

## Feature-Specific Load

- **Quote engine:** High load (users shop around), 50 RPS at peak
- **Policy management:** Moderate load, 20 RPS
- **Claims processing:** Spike load (after incidents), 100+ RPS
- **Admin dashboard:** Predictable, 5-10 RPS

## Seasonal Load

- **Open enrollment (Oct-Dec):** 3-5x normal load
- **Year-end (Nov-Dec):** Policy renewal rush, 2x normal
- **Incident season (hurricane, winter):** Claims spike, 10x normal

## Load Profile Examples

### Standard Quote Session
```
1. GET /api/quote-form (fetch form metadata)
2. Think 5s
3. POST /api/quotes (submit form)
4. Think 3s
5. GET /api/quotes/{id} (check status)
6. GET /api/quotes/{id}/download (download PDF)
```

### Claims Filing
```
1. GET /api/claims/new (form)
2. POST /api/claims (submit)
3. Think 10s (user attaches documents)
4. POST /api/claims/{id}/documents (upload)
5. GET /api/claims/{id} (confirm)
```

## Concurrency Sizing

For typical insurance SaaS (1M policies):

| VUs | Concurrent Sessions | Estimated Coverage |
|-----|-------------------|-------------------|
| 10 | 5-10 real users | Development |
| 50 | 25-50 real users | Staging |
| 100 | 50-100 real users | Load test (baseline) |
| 500 | 250-500 real users | Peak hour simulation |
| 2000 | 1000-2000 real users | Open enrollment peak |
```

- [ ] **Step 8: Write templates/k6.test.js.liquid**

```liquid
// AUTO-GENERATED K6 LOAD TEST — Do not edit
// SLA: p95<{{ target_sla.p95_latency_ms }}ms, Error<{{ target_sla.error_rate_pct }}%

import http from 'k6/http';
import { sleep, check } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

export const options = {
  stages: [
    {% for stage in load_profile.stages %}
    { duration: '{{ stage.duration_seconds }}s', target: {{ stage.target_vus }} }, // {{ stage.description }}
    {% endfor %}
  ],
  thresholds: {
    'http_req_duration': ['p(95)<{{ target_sla.p95_latency_ms }}'],
    'http_req_failed': ['rate<{{ target_sla.error_rate_pct / 100 }}'],
  },
};

{% for endpoint in endpoints %}
function test{{ endpoint.name | camelize }}() {
  const res = http.{{ endpoint.method }}(`${BASE_URL}{{ endpoint.path }}`, {
    headers: { 'Content-Type': 'application/json' },
  });

  check(res, {
    '{{ endpoint.name }} status 200': (r) => r.status === 200,
    '{{ endpoint.name }} latency < 500ms': (r) => r.timings.duration < 500,
  });

  sleep({{ load_profile.think_time_seconds }});
}

{% endfor %}

export default function () {
  {% for endpoint in endpoints %}
  test{{ endpoint.name | camelize }}();
  {% endfor %}
}
```

- [ ] **Step 9: Write templates/locust.py.liquid**

```liquid
# AUTO-GENERATED LOCUST LOAD TEST — Do not edit
# SLA: p95<{{ target_sla.p95_latency_ms }}ms, Error<{{ target_sla.error_rate_pct }}%

from locust import HttpUser, task, between
import time

BASE_URL = '{{ base_url | default: "http://localhost:3000" }}'

class InsuranceUser(HttpUser):
    wait_time = between({{ load_profile.think_time_seconds }}, {{ load_profile.think_time_seconds + 2 }})
    host = BASE_URL

    {% for endpoint in endpoints %}
    @task({{ endpoint.weight | default: 1 }})
    def {{ endpoint.name }}(self):
        """{{ endpoint.description }}"""
        self.client.{{ endpoint.method }}('{{ endpoint.path }}', timeout=10)
    {% endfor %}

class LoadTestShape:
    """Custom load shape for ramp-up profile"""

    def tick(self):
        run_time = self.get_run_time()

        {% for stage in load_profile.stages %}
        # {{ stage.description }}
        if run_time < {{ stage.duration_seconds }}:
            return ({{ stage.target_vus }}, 1)

        {% endfor %}
        return None  # Stop test

if __name__ == '__main__':
    # Run: locust -f this_file.py --headless -u {{ load_profile.stages[-1].target_vus }} -r 10
    pass
```

- [ ] **Step 10: Write templates/gatling.scala.liquid**

```liquid
// AUTO-GENERATED GATLING SIMULATION — Do not edit
// SLA: p95<{{ target_sla.p95_latency_ms }}ms, Error<{{ target_sla.error_rate_pct }}%

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class InsuranceLoadTest extends Simulation {

  val httpProtocol = http
    .baseUrl("{{ base_url | default: "http://localhost:3000" }}")
    .acceptHeader("application/json")
    .shareConnections

  val scn = scenario("Insurance Load Test")
    {% for endpoint in endpoints %}
    .exec(http("{{ endpoint.name }}")
      .{{ endpoint.method }}("{{ endpoint.path }}")
      .check(status.is(200)))
    .pause({{ load_profile.think_time_seconds }})
    {% endfor %}

  setUp(
    scn.injectOpen(
      {% for stage in load_profile.stages %}
      rampOpenUsers({{ stage.target_vus }}) during ({{ stage.duration_seconds }} seconds),
      {% endfor %}
    ).protocols(httpProtocol)
  ).assertions(
    global.responseTime.percentile(95).lt({{ target_sla.p95_latency_ms }}),
    global.successfulRequests.percent.gte({{ 100 - target_sla.error_rate_pct }}),
  )
}
```

- [ ] **Step 11: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "gpt-tc-001"
    description: "Calculate ramp-up profile from SLA targets"
    input:
      target_p95_ms: 200
      target_rps: 100
      profile: "ramp-up"
    expected:
      profile_type: "ramp-up"
      stages_count: 6
      max_vus_gte: 100
      think_time_range: [0.5, 5.0]

  - id: "gpt-tc-002"
    description: "Generate K6 load test with SLA assertions"
    input:
      endpoints:
        - path: "/api/quotes"
          method: "post"
      load_profile: "ramp-up"
      target_sla:
        p95_latency_ms: 200
        error_rate_pct: 0.5
    expected:
      code_contains: "stages"
      code_contains: "thresholds"
      code_contains: "p(95)<200"
      no_hardcoded_url: true

  - id: "gpt-tc-003"
    description: "Generate Locust test with realistic think time"
    input:
      endpoints:
        - name: "get_quote"
          path: "/api/quotes"
          method: "get"
        - name: "submit_claim"
          path: "/api/claims"
          method: "post"
      load_profile: "spike"
    expected:
      code_contains: "wait_time"
      code_contains: "@task"
      code_contains: "think_time"

  - id: "gpt-tc-004"
    description: "Collect baseline metrics for SLA comparison"
    input:
      url: "http://localhost:3000/api/quote"
      requests: 100
    expected:
      has_p50_latency: true
      has_p95_latency: true
      has_p99_latency: true
      has_throughput: true
      error_rate_valid: true
```

- [ ] **Step 12: Write evals/assertions.yaml**

```yaml
assertions:
  - test_case: "gpt-tc-001"
    checks:
      - { field: "profile_type", operator: "equals", value: "ramp-up" }
      - { field: "stages", operator: "length_gte", value: 2 }
      - { field: "stages[-1].target_vus", operator: "gte", value: 100 }
      - { field: "think_time_seconds", operator: "gt", value: 0 }
      - { field: "think_time_seconds", operator: "lt", value: 10 }

  - test_case: "gpt-tc-002"
    checks:
      - { field: "code", operator: "contains", value: "stages" }
      - { field: "code", operator: "contains", value: "p(95)<200" }
      - { field: "code", operator: "contains", value: "rate<0" }
      - { field: "code", operator: "not_contains", value: "http://localhost" }

  - test_case: "gpt-tc-003"
    checks:
      - { field: "code", operator: "contains", value: "wait_time = between" }
      - { field: "code", operator: "contains", value: "@task" }
      - { field: "code", operator: "contains", value: "get_quote" }
      - { field: "code", operator: "contains", value: "submit_claim" }

  - test_case: "gpt-tc-004"
    checks:
      - { field: "p50_latency_ms", operator: "gte", value: 0 }
      - { field: "p95_latency_ms", operator: "gte", value: 0 }
      - { field: "p99_latency_ms", operator: "gte", value: 0 }
      - { field: "throughput_rps", operator: "gt", value: 0 }
      - { field: "error_rate_pct", operator: "gte", value: 0 }
      - { field: "error_rate_pct", operator: "lte", value: 100 }
```

- [ ] **Step 13: Verify file count and structure**

```bash
find .github/skills/qa/generating-perf-tests -type f | wc -l
# Expected: 11 files

python3 -c "import yaml; yaml.safe_load(open('.github/skills/qa/generating-perf-tests/evals/test-prompts.yaml'))"
# Should exit 0 (valid YAML)

find .github/skills/qa/generating-perf-tests -name "*.py" -exec python3 -m py_compile {} \;
# Should exit 0 (valid Python)
```

- [ ] **Step 14: Commit**

```bash
git add .github/skills/qa/generating-perf-tests/
git commit -m "feat(qa-skills): add generating-perf-tests skill (P2)

SKILL.md with endpoints/load_profile/target_sla inputs, load_test_code/baseline_metrics outputs.
Scripts: load-profile-calculator.py (SLA→VU ramp schedule), baseline-collector.py (single-user metrics).
References: perf-testing-patterns.md (think time, data correlation, SLA assertions), insurance-load-profiles.md (business hour loads, seasonal patterns).
Templates: k6.test.js.liquid (JavaScript), locust.py.liquid (Python), gatling.scala.liquid (Scala).
Evals: 4 test cases covering profile calculation, K6/Locust/Gatling generation, baseline collection."
```

---

---

## Task 7: Final Verification

Verify all P2 files are present, syntax-valid, and interdependencies correct.

- [ ] **Step 1: File count verification**

```bash
find .github/skills/qa/ -type f -path "*/generating-*/*" | wc -l
# Expected: 55 files (5 SKILL.md + 11 scripts + 13 references + 15 templates + 10 evals + 5 requirements.txt)

find .github/skills/qa/rules -type f | wc -l
# Expected: 5 files (security-standards.md + 4 platform files)
```

- [ ] **Step 2: YAML syntax validation**

```bash
for file in $(find .github/skills/qa -name "*.yaml"); do
  python3 -c "import yaml; yaml.safe_load(open('$file'))" || echo "INVALID: $file"
done

for file in $(find .github/skills/qa -name "SKILL.md"); do
  python3 << 'EOF'
import re
with open('$file') as f:
    content = f.read()
    if not re.match(r'^---\s*\n.*?\n---\n', content, re.DOTALL):
        print(f"MISSING FRONTMATTER: $file")
EOF
done
```

- [ ] **Step 3: Python syntax validation**

```bash
find .github/skills/qa -name "*.py" -exec python3 -m py_compile {} \; \
  || echo "Invalid Python syntax found"
```

- [ ] **Step 4: Dependency graph check**

Verify soft_dependencies are satisfied:

```bash
# generating-test-data (soft depends on test-driven-development)
grep "soft_dependencies" .github/skills/qa/generating-test-data/SKILL.md

# generating-playwright-tests (depends on test-driven-development)
grep "dependencies" .github/skills/qa/generating-playwright-tests/SKILL.md

# generating-api-tests (depends on test-driven-development)
grep "dependencies" .github/skills/qa/generating-api-tests/SKILL.md

# All should reference P1 skills that exist
```

- [ ] **Step 5: Template Liquid syntax check**

```bash
find .github/skills/qa -name "*.liquid" | while read file; do
  # Basic check: ensure {% and %} are balanced
  open_count=$(grep -o '{%' "$file" | wc -l)
  close_count=$(grep -o '%}' "$file" | wc -l)
  if [ "$open_count" -ne "$close_count" ]; then
    echo "UNBALANCED TAGS: $file"
  fi
done
```

- [ ] **Step 6: Verify reference cross-links**

```bash
# Each SKILL.md should reference its own references/ directory
for skill_dir in .github/skills/qa/generating-*/; do
  skill_md="$skill_dir/SKILL.md"
  if [ -f "$skill_md" ]; then
    # Check that references exist and are mentioned in SKILL.md
    ref_files=$(find "$skill_dir/references" -type f 2>/dev/null | wc -l)
    if [ "$ref_files" -eq 0 ]; then
      echo "NO REFERENCES: $skill_dir"
    fi
  fi
done
```

- [ ] **Step 7: Verify eval test cases**

```bash
# Each skill must have >= 2 test cases
for eval_file in .github/skills/qa/generating-*/evals/test-prompts.yaml; do
  if [ -f "$eval_file" ]; then
    test_count=$(grep -c "^  - id:" "$eval_file" || echo 0)
    if [ "$test_count" -lt 2 ]; then
      echo "INSUFFICIENT TESTS ($test_count): $eval_file"
    fi
  fi
done
```

- [ ] **Step 8: Integration verification**

```bash
# Verify no circular dependencies
# (All P2 generation skills soft-depend or depend on P1 evaluation skills, never vice-versa)

for skill_file in .github/skills/qa/generating-*/SKILL.md; do
  if grep -q "parsing-requirements\|test-driven-development\|analyzing-coverage\|validating-acceptance\|classifying-test\|generating-qa-report" "$skill_file"; then
    echo "✓ $(basename $(dirname $skill_file)) correctly depends on P1"
  fi
done
```

- [ ] **Step 9: Total file count audit**

```bash
echo "=== P2 Skills Breakdown ==="
for skill in generating-test-data generating-playwright-tests generating-api-tests generating-mobile-tests generating-perf-tests; do
  skill_dir=".github/skills/qa/$skill"
  if [ -d "$skill_dir" ]; then
    count=$(find "$skill_dir" -type f | wc -l)
    echo "$skill: $count files"
  fi
done

echo "=== Rules Breakdown ==="
rules_count=$(find .github/skills/qa/rules -type f | wc -l)
echo "rules/: $rules_count files"

echo "=== Total ==="
total=$(find .github/skills/qa -type f | wc -l)
echo "Total: $total files"
echo "Expected: 64 files (59 P2 skills + 5 rules)"
```

- [ ] **Step 10: Final commit**

```bash
git status --short | head -20
# Verify all P2 files are staged

git commit -m "feat(qa-skills): complete P2 implementation (5 generation skills + 5 rules)

P2 Skills:
  - generating-test-data: domain-realistic fixtures with PII sanitization
  - generating-playwright-tests: Page Object Model web tests
  - generating-api-tests: REST/GraphQL API tests from schemas
  - generating-mobile-tests: iOS/Android platform-specific tests
  - generating-perf-tests: K6/Locust/Gatling load tests

P2 Rules:
  - security-standards.md: OWASP Top 10, input validation, secrets management
  - platform/typescript.md: strict mode, async patterns, Playwright conventions
  - platform/python.md: type hints, venv, pytest fixtures, async testing
  - platform/java.md: JUnit 5, Spring slicing, Mockito, RestAssured
  - platform/go.md: table-driven tests, goroutines, race detector

All skills follow anthropics/skills structure with SKILL.md frontmatter, scripts, references, templates, evals."
```

---

## Summary

**Total P2 implementation:**
- 5 generation skills (SKILL.md files)
- 11 Python scripts with per-skill dependencies
- 13 reference documents (domain patterns, best practices)
- 15 Liquid templates (language-specific test code generators)
- 10 eval files (test-prompts.yaml + assertions.yaml per skill)
- 5 rules files (security-standards + 4 platform rules)
- 5 requirements.txt files (one per skill)

**Total files: 64** (59 P2 + 5 rules)

**Time estimate:** 4-6 hours with agentic implementation (executing plans task-by-task). Each skill follows identical scaffold pattern, enabling parallel work on scripts/references/templates once structure is understood.

**Next phase:** P3 skills (scoring-risk, reviewing-code-quality, selecting-regressions, healing-broken-tests, analyzing-defects) — deeper integration with code review agents, defect patterns ML, knowledge base persistence.
