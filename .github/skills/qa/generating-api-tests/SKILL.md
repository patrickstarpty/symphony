---
name: generating-api-tests
description: "Generates API test suites from OpenAPI, Swagger, or GraphQL schemas covering happy paths, edge cases, and security. Use when an API schema is finalized and endpoint test coverage is needed, or when hardcoded tokens or production URLs may be present in test files."
---

# generating-api-tests

Generate comprehensive API test suites from OpenAPI, Swagger, or GraphQL schemas. Produces happy path tests + edge cases (null fields, empty arrays, boundary values). Detects security issues (hardcoded tokens, production URLs).

## Quick Reference

**Phase:** post-coding  
**Platforms:** api  
**Inputs:**
- `schema` (object|string, required) — OpenAPI 3.x, Swagger 2.0, or GraphQL SDL file path
- `test_style` (string, optional) — jest | pytest | ts-rest (default: jest)
- `base_url` (string, optional) — non-production API base URL

**Outputs:**
- `test_suites` — generated test files by endpoint
- `schema_coverage_report` — endpoint coverage and edge case analysis
- `security_audit` — auth requirements and hardcoded secret detection

**Depends on:** test-driven-development

## When to Use

Use when API schema is finalized and endpoints stable. Run before committing API tests to verify coverage and security.

## Instructions

1. Provide API schema (OpenAPI JSON, Swagger JSON, or GraphQL SDL)
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

- CI/CD system — executes generated API test suites against staging
- Backend API teams — validate against schemas pre-deployment

## References

- `api-testing-patterns.md` — HTTP mocking, request/response validation, error handling
- `schema-validation-rules.md` — OpenAPI/GraphQL validation rules, response structure checks
