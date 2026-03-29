---
name: generating-test-data
description: "Generates domain-realistic test fixtures with PII sanitization and validated statistical distributions. Use when writing tests requiring realistic insurance domain data (policy, claim, customer, quote), or before committing fixtures to verify no real PII is present."
---

# generating-test-data

Generate domain-realistic test data with sanitized PII and validated statistical properties. Supports insurance domain entities: policy, claim, customer, quote.

## Quick Reference

**Phase:** during-coding  
**Inputs:**
- `domain` (string, required) — insurance | financial | healthcare
- `entity_type` (string, required) — policy | claim | customer | quote
- `count` (integer, optional) — default 10
- `output_format` (string, optional) — json | yaml | csv (default: json)

**Outputs:**
- `fixtures` — generated test data records
- `pii_audit` — PII scan results
- `distribution_report` — statistical validation of distributions
- `generated_files` — output file paths

**Works better with:** test-driven-development

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
