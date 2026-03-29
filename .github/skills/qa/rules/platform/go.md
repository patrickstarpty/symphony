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
