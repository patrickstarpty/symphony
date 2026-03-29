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
