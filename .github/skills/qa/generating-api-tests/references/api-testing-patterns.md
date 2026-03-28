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
