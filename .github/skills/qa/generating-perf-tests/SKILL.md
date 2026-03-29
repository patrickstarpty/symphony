---
name: generating-perf-tests
description: "Generates load test scripts (K6, Locust, Gatling) with realistic user profiles, think times, and SLA assertions. Use when API is production-ready and performance baselines need establishing, or when converting SLAs into ramp-up, spike, or soak test configurations."
---

# generating-perf-tests

Generate load test scripts with realistic user behavior. Converts business SLAs (p95 latency < 200ms, error rate < 0.5%) into load profiles. Includes think time between requests, proper data correlation, and SLA assertions. Supports K6, Locust, and Gatling.

## Quick Reference

**Phase:** post-coding  
**Inputs:**
- `endpoints` (array, required) — endpoints to load test
- `load_profile` (string, required) — ramp-up | spike | soak | custom
- `target_sla` (object, required) — p95_latency_ms, error_rate_pct, throughput_rps
- `test_tool` (string, optional) — k6 | locust | gatling (default: k6)

**Outputs:**
- `load_test_code` — generated test script
- `baseline_metrics` — single-user baseline (latency, CPU, memory)
- `load_profile_config` — VU ramp-up schedule and think times

**Works better with:** test-driven-development

## When to Use

Use when API is production-ready and performance baselines established.

## Instructions

1. Accept `endpoints`, `target_sla`, `load_profile`, and `test_tool` from caller inputs.
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
