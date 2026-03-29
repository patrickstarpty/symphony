---
name: generating-perf-tests
version: "1.0.0"
description: "Generate load tests with realistic user profiles, think times, and SLA assertions"
category: generation
phase: post-coding
platforms: ["all"]
dependencies: []
soft_dependencies: ["test-driven-development"]
input_schema:
  - name: "endpoints"
    type: "array"
    required: true
    description: "List of endpoints to load test"
  - name: "load_profile"
    type: "string"
    required: true
    description: "ramp-up | spike | soak | custom"
  - name: "target_sla"
    type: "object"
    required: true
    description: "SLA targets: p95_latency_ms, error_rate_pct, throughput_rps"
  - name: "test_tool"
    type: "string"
    required: false
    default: "k6"
    description: "k6 | locust | gatling"
output_schema:
  - name: "load_test_code"
    type: "string"
    description: "Generated test script"
  - name: "baseline_metrics"
    type: "object"
    description: "Single-user baseline (latency, CPU, memory)"
  - name: "load_profile_config"
    type: "object"
    description: "VU ramp-up schedule, think times"
---

# generating-perf-tests

Generate load test scripts with realistic user behavior. Converts business SLAs (p95 latency < 200ms, error rate < 0.5%) into load profiles. Includes think time between requests, proper data correlation, and SLA assertions. Supports K6, Locust, and Gatling.

## When to Use

Use when API is production-ready and performance baselines established. Never target production. Always define SLA thresholds before running.

## Instructions

1. Provide list of endpoints and SLA targets
2. Specify load profile (ramp-up, spike, soak) and test tool
3. Run `scripts/load-profile-calculator.py` to convert SLA to VU schedule
4. Run `scripts/baseline-collector.py` to establish single-user baseline
5. Generate load test using tool-specific template
6. Output includes load profile config and baseline metrics

## Guardrails

- **Never target production.** Always verify base_url is staging/localhost, not api.example.com.
- **Define SLAs before running.** Expected p95 latency, error rate, throughput thresholds.
- **Include think time.** Realistic tests include 1-5s delays between requests to mimic user behavior.
- **Proper data correlation.** Extract IDs from responses, reuse in subsequent requests.
- **Monitor resource usage.** Test should include baseline CPU/memory, not just latency.

## Consumers

- Performance engineers — customize ramp-up, thresholds
- DevOps — use baseline metrics for capacity planning

## References

- `perf-testing-patterns.md` — virtual user modeling, think time, data correlation, ramping strategies
- `insurance-load-profiles.md` — typical insurance system loads, peak hours, concurrent user distribution
