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
