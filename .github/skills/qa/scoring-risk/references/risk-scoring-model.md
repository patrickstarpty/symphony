# Risk Scoring Model — Reference

## Overview

Risk scoring quantifies change risk to determine dynamic coverage thresholds and test selection priorities. Four factors contribute equally to a 0-100 scale.

## Scoring Factors

### 1. Change Scope (0–25 points)

Measures the breadth and magnitude of changes.

**Metrics:**
- Files changed (count)
- Lines delta (additions + deletions)
- Affected modules (from dependency analysis)

**Scoring:**
- 1-3 files, <50 lines → 5 points (surgical fix)
- 4-10 files, 50-200 lines → 10 points (typical feature)
- 11-30 files, 200-500 lines → 15 points (module refactor)
- 30+ files, 500+ lines → 25 points (major refactor/infrastructure)

**Blast radius multiplier:**
- Changes to package.json, tsconfig.json, .env → +5 to scope
- Changes to shared utils, middleware → +3 to scope
- Changes to database schema → +5 to scope

### 2. Component Criticality (0–35 points)

Risk is higher in safety-critical and revenue-critical components.

**Component Tiers:**

| Tier | Components | Score |
|------|-----------|-------|
| Critical | Payment processing, authentication, authorization, security | 30–35 |
| High | Policy operations, claims, customer data, API contracts | 15–20 |
| Low | Utilities, helpers, test infrastructure | 5–10 |

**Project-specific registry:**

Teams maintain `.github/skills/qa/scoring-risk/references/component-registry.md` listing components and their tiers. Updated annually by tech leads.

**Scoring:**
- If any modified file is critical → use critical score (35)
- If any modified file is high → use high score (20)
- Otherwise → use low score (10)

### 3. Defect History (0–25 points)

High-defect components warrant tighter testing.

**Data source:** Knowledge Base MCP (from previous 90 days by default).

**Metrics:**
- Historical defect count for each file
- Defect density (defects per file over time window)
- Trend (increasing/stable/decreasing)

**Scoring:**
- No history available → 0 points (neutral; never penalize unknown components)
- <1 defect per file (avg) → 5 points
- 1–2 defects per file → 10 points
- 2–5 defects per file → 15 points
- 5+ defects per file → 25 points (hotspot)

### 4. Complexity Delta (0–15 points)

Increased complexity increases defect risk.

**Metrics:**
- Cyclomatic complexity increase in modified functions
- New function count in diff
- Average function length delta

**Scoring:**
- Complexity decrease or no change → 0 points
- Complexity +1 to +5 → 3 points
- Complexity +6 to +10 → 8 points
- Complexity +11+ → 15 points

**Tool:** Requires language-specific analyzer (ast module for Python, esprima for JS, etc.).

## Final Score Calculation

```
risk_score = scope + criticality + defect_history + complexity_delta
risk_score = min(risk_score, 100)
risk_level = {
  75-100: "critical",
  50-74: "high",
  25-49: "medium",
  0-24: "low"
}
```

## Dynamic Thresholds

Risk levels determine coverage thresholds for analyzing-coverage:

| Risk Level | Required Coverage | Gate Type | Actions |
|-----------|------------------|-----------|---------|
| critical | ≥95% | strict | Block merge; mandatory human review |
| high | ≥85% | strict | Automatic gate enforced |
| medium | ≥80% | advisory | Warn on gap; allow proceed |
| low | ≥70% | advisory | Informational only |

## Confidence Levels

Output indicates confidence in the score:

| Confidence | Condition | Action |
|-----------|-----------|--------|
| high | All data available (scope + criticality + defect history) | Trust score; enforce thresholds |
| medium | Scope + criticality available; defect history incomplete | Use score with caution; suggest manual review |
| low | Limited data (only scope, or no diff) | Don't enforce; recommend manual risk assessment |

## Graceful Degradation

When Knowledge Base MCP is unavailable:
- Defect history factor → 0 (neutral)
- Complexity analysis unavailable → complexity factor → 0 (neutral)
- Result: score based on scope + criticality only

When component registry is unavailable:
- All components → medium criticality (20)
- Result: uniform baseline, no tuning
