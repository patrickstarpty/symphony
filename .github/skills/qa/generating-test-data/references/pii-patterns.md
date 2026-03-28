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
