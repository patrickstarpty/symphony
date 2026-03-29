---
name: scoring-risk
description: "Scores change risk (0–100) from scope, component criticality, defect history, and complexity to produce dynamic coverage thresholds. Use when beginning an issue before coding starts, or when analyzing-coverage thresholds need calibration based on payment, auth, or business logic changes."
---

# scoring-risk

Score the risk of a change based on scope, component criticality, historical defect density, and complexity delta. Output risk level and dynamic coverage thresholds.

## Quick Reference

**Phase:** pre-coding  
**Inputs:**
- `git_diff` (string, required)
- `issue_metadata` (object, optional)
- `component_registry` (object, optional)
- `defect_history` (object, optional) — from Knowledge Base MCP

**Outputs:**
- `risk_score` — 0–100 numeric score
- `risk_level` — critical | high | medium | low
- `factors` — contributing factor breakdown
- `recommended_thresholds` — dynamic coverage thresholds per component

## When to Use

Invoke at issue start, before coding begins. Feeds two consumers:
- `analyzing-coverage` — thresholds for Pass Rate gate
- `selecting-regressions` — prioritization weights

## Instructions

1. Run `scripts/change-scope-analyzer.py` on git diff → files changed, lines delta, change magnitude
2. Run `scripts/component-criticality.py` → component tier and base criticality score
3. Run `scripts/defect-density-calculator.py` → historical defect count + density for affected files
4. Calculate overall risk score (0-100) using the model in references/risk-scoring-model.md
5. Map score to risk_level and recommended coverage thresholds
6. Output JSON with all factors and thresholds

## Risk Scoring Model

**Four factors, total 100 points:**

| Factor | Points | What It Measures |
|--------|--------|-----------------|
| Change scope | 0–25 | Files changed, lines delta, blast radius |
| Component criticality | 0–35 | payment (35) > auth (30) > business logic (20) > utility (10) |
| Defect history | 0–25 | Historical defect density for affected files (Knowledge Base) |
| Complexity delta | 0–15 | Cyclomatic complexity increase in modified functions |

**Scoring logic:**
```
risk_score = (scope_points + criticality_points + defect_points + complexity_points)
```

**Risk levels and thresholds:**

| Level | Score | Coverage | Gate | Action |
|-------|-------|----------|------|--------|
| critical | 75–100 | ≥95% | strict + mandatory review | Block merge without human approval |
| high | 50–74 | ≥85% | strict | Automatic gate, human review optional |
| medium | 25–49 | ≥80% | advisory | Warn on coverage gap, allow proceed |
| low | 0–24 | ≥70% | advisory | Informational only |

**Graceful degradation:**
- No component registry → assume all components = medium (20 points)
- No defect history (Knowledge Base unavailable) → defect factor = 0 (neutral)
- No complexity analysis tool → complexity factor = 0 (neutral)
- Low confidence → output `confidence: "low"` and suggest manual review

## Consumers

- `analyzing-coverage` — applies dynamic thresholds to Pass Rate calculation
- `selecting-regressions` — weights test selection by risk score

## Guardrails

- Risk scoring is advisory only — never auto-approve based on low score
- Component registry maintained by humans, not auto-generated
- Without defect history, assume neutral (don't penalize unknown components)
- Never block a change solely on score — only inform thresholds
