# Ambiguity Signals Reference

Quick-reference for the agent when evaluating AC quality.

## Red-Flag Words

| Category | Examples | Why It's Ambiguous |
|----------|----------|--------------------|
| Vague qualifiers | appropriate, proper, correct, good | No measurable definition |
| Missing thresholds | large, many, quickly, soon, often | No numeric bound |
| Undefined scope | etc., and so on, similar, related | Open-ended list |
| Implicit behavior | as needed, if necessary, when applicable | Trigger undefined |
| Subjective quality | user-friendly, intuitive, clean, elegant | Observer-dependent |

## Common Missing Requirements

- Error messages: What text? What format? What HTTP status?
- Rate limiting: How many requests? Per what window?
- Accessibility: WCAG level? Screen reader support?
- Performance: Latency target? Throughput? Under what load?
- Edge cases: Empty input? Max length? Concurrent access?
- Security: Authentication? Authorization? Input validation?

## Testability Checklist

An AC is testable if you can answer YES to all:
1. Can I write an automated assertion for this? (observable output)
2. Is the expected result unambiguous? (one correct answer)
3. Can I set up the preconditions? (reproducible)
4. Can I run it independently? (no external dependencies implied)
