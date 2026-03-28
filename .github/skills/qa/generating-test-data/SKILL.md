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
2. Run `scripts/data-generator.py` to produce base fixtures with generated values
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
