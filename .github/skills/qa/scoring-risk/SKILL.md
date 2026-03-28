---
name: scoring-risk
version: "1.0.0"
description: "Score issue risk from change scope, component criticality, defect history — feed dynamic thresholds"
category: analysis
phase: pre-coding
platforms: ["all"]
dependencies: []
input_schema:
  - name: "git_diff"
    type: "string"
    required: true
  - name: "issue_metadata"
    type: "object"
    required: false
  - name: "component_registry"
    type: "object"
    required: false
  - name: "defect_history"
    type: "object"
    required: false
    description: "From Knowledge Base MCP"
output_schema:
  - name: "risk_score"
    type: "number"
    description: "0-100"
  - name: "risk_level"
    type: "string"
    description: "critical | high | medium | low"
  - name: "factors"
    type: "array"
  - name: "recommended_thresholds"
    type: "object"
---

# scoring-risk

Score the risk of a change based on scope, component criticality, historical defect density, and complexity delta. Output risk level and dynamic coverage thresholds.

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
