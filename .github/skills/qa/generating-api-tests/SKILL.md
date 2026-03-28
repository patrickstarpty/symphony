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

- `test-driven-development` — provides API testing context
- Backend API teams — validate against schemas pre-deployment

## References

- `api-testing-patterns.md` — HTTP mocking, request/response validation, error handling
- `schema-validation-rules.md` — OpenAPI/GraphQL validation rules, response structure checks
