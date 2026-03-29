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
