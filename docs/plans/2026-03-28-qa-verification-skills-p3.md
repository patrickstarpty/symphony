# QA Verification Skills — P3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the 5 P3 QA advanced skills + review-guidelines.md rules file, enabling risk-based testing, code review support, intelligent regression selection, auto-healing, and organizational learning.

**Architecture:** Each P3 skill is a directory under `.github/skills/qa/` following the anthropics/skills structure: `SKILL.md` (agent instructions), `scripts/` (Python 3.12+ with graceful degradation), `references/` (domain knowledge), `evals/` (test-prompts.yaml + assertions.yaml). P3 skills depend on Knowledge Base MCP (P2 infrastructure) for defect history and component registry, with fallback when unavailable.

**Tech Stack:** Markdown (SKILL.md), Python 3.12+ (scripts with minimal deps via per-skill requirements.txt), YAML (evals, frontmatter)

**Spec:** `docs/specs/2026-03-28-qa-skills-quick-win-design.md` §6 (P3 Skills), §7.3 (P3 Rules), §8 (Evals)

**Prerequisite:** P1 and P2 skills must be implemented. P3 skills depend on Knowledge Base MCP (P2 infrastructure) for defect history and component registry.

---

## File Structure

```
.github/skills/qa/
├── scoring-risk/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── change-scope-analyzer.py
│   │   ├── component-criticality.py
│   │   └── defect-density-calculator.py
│   ├── references/
│   │   ├── risk-scoring-model.md
│   │   └── component-registry.md
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
├── reviewing-code-quality/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── spec-compliance-checker.py
│   │   └── quality-metrics.py
│   ├── references/
│   │   ├── review-checklist.md
│   │   └── code-quality-standards.md
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
├── selecting-regressions/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── change-impact-analyzer.py
│   │   ├── dependency-graph-walker.py
│   │   └── test-selector.py
│   ├── references/
│   │   └── regression-strategies.md
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
├── healing-broken-tests/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── failure-pattern-matcher.py
│   │   ├── locator-updater.py
│   │   └── diff-correlator.py
│   ├── references/
│   │   ├── common-breakage-patterns.md
│   │   └── auto-fix-strategies.md
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
├── analyzing-defects/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── root-cause-classifier.py
│   │   ├── pattern-detector.py
│   │   └── knowledge-base-writer.py
│   ├── references/
│   │   ├── defect-taxonomy.md
│   │   └── root-cause-categories.md
│   └── evals/
│       ├── test-prompts.yaml
│       └── assertions.yaml
└── rules/
    └── review-guidelines.md
```

**Total files:** 5 SKILL.md + 14 scripts + 9 references + 10 eval files + 1 rule = 39 files

---

## Task 1: Directory scaffold and review-guidelines.md rule

Create P3 directory structure and the rules file. The rule is foundational for reviewing-code-quality.

**Files:**
- Create: `.github/skills/qa/scoring-risk/{SKILL.md, scripts, references, evals}`
- Create: `.github/skills/qa/reviewing-code-quality/{SKILL.md, scripts, references, evals}`
- Create: `.github/skills/qa/selecting-regressions/{SKILL.md, scripts, references, evals}`
- Create: `.github/skills/qa/healing-broken-tests/{SKILL.md, scripts, references, evals}`
- Create: `.github/skills/qa/analyzing-defects/{SKILL.md, scripts, references, evals}`
- Create: `.github/skills/qa/rules/review-guidelines.md`

- [ ] **Step 1: Create directory scaffold**

```bash
mkdir -p .github/skills/qa/{scoring-risk/{scripts,references,evals},reviewing-code-quality/{scripts,references,evals},selecting-regressions/{scripts,references,evals},healing-broken-tests/{scripts,references,evals},analyzing-defects/{scripts,references,evals}}
```

- [ ] **Step 2: Verify directory structure**

Run: `find .github/skills/qa -type d | grep -E "^\.github/skills/qa/(scoring|reviewing|selecting|healing|analyzing)" | sort`

Expected: 25 directories (5 skills × 5 subdirs: root, scripts, references, evals, plus rules parent).

- [ ] **Step 3: Write rules/review-guidelines.md**

```markdown
# Code Review Guidelines — P3

> Declarative review standards consumed by Code Reviewer agent (Claude Sonnet 4.6) and reviewing-code-quality skill. Ensures consistent, cross-model objectivity in code quality evaluation.

## Two-Stage Review Process

All code review follows a strict two-stage process to catch spec violations before evaluating code quality.

### Stage 1: Specification Compliance

**Purpose:** Verify the implementation addresses every requirement in the AC/spec.

**Process:**
1. Parse acceptance criteria and spec requirements from issue description
2. For each requirement, search the diff for corresponding implementation
3. Check for:
   - Missing AC coverage (requirement mentioned in spec but not implemented)
   - Incomplete implementation (skeleton only, no business logic)
   - Spec-breaking changes (implementation contradicts AC)

**Verdict:**
- **PASS:** All AC requirements have implementation in the diff
- **FAIL:** One or more AC requirements unimplemented or contradicted

**Action:**
- Stage 1 FAIL → Issue REQUEST_CHANGES immediately, skip Stage 2
- Stage 1 PASS → Proceed to Stage 2

### Stage 2: Code Quality

**Purpose:** Evaluate implementation quality: readability, SOLID principles, performance, pattern consistency.

**Scope:** Only evaluate if Stage 1 passes.

**Evaluation criteria:**
- **Readability:** Function length (max 30 lines for public methods), nesting depth (max 3), meaningful names, self-documenting code
- **SOLID:** Single responsibility, no gods, dependency injection, open/closed principle, Liskov substitution, interface segregation, dependency inversion
- **Performance:** No N+1 queries, no unnecessary full-table scans, caching strategy documented, API response times <500ms p95
- **Patterns:** Consistent with codebase conventions, error handling patterns, logging standards, testing patterns
- **Security:** Input validation at boundaries, no hardcoded credentials, parameterized queries, OWASP Top 10 coverage

**Never evaluate:**
- Linter-catchable style issues (use pre-commit hooks instead)
- Formatting and whitespace
- Variable naming style (convention should be automated)

### Comment Quality Standards

**Actionable:** Every comment must suggest a specific fix.
- ✓ "Add early return to reduce nesting: `if (!condition) return;`"
- ✗ "This could be cleaner"

**Non-blocking:** Mark quality-of-life suggestions as "Optional" or "FYI".
- "Optional: Extract to a helper function for readability"

**Technical debt:** Reference issue/epic for refactoring work.
- "Technical debt [PAY-456]: Consider Query Builder pattern instead of string concat"

**Specific:** Point to exact lines and explain the impact.
- "Line 42: N+1 query in loop. Add `.eager_load(:orders)` to line 10"

## Cross-Model Protocol

**Consumption:** Code Reviewer agent (Claude Sonnet 4.6) uses this guideline as a system prompt supplement to `reviewing-code-quality` skill output.

**Objectivity:** Different model (Sonnet vs Haiku) for implementation vs review prevents self-approval bias.

**Verdict mapping:**
- reviewing-code-quality outputs: APPROVE | REQUEST_CHANGES | COMMENT
- Code Reviewer agent elevates to: ✓ Approved | ⚠ Revisions Requested | → Address Comments → Re-review

**Escalation:** If Code Reviewer disagrees with reviewing-code-quality verdict, provide detailed justification in comments. No silent overrides.

## Guardrails

- Never approve a diff that fails Stage 1 spec compliance
- Comments must be specific and actionable, not subjective
- Don't nitpick automated tool issues (lint, format)
- Quality issues should be flagged with severity:
  - **Critical:** Breaks spec, security issue, will cause production incident
  - **Major:** SOLID violation, significant performance issue
  - **Minor:** Code style inconsistency, non-blocking refactoring opportunity
- When uncertain, ask clarifying questions instead of assuming intent
```

- [ ] **Step 4: Commit scaffold and rule**

```bash
git add .github/skills/qa/
git commit -m "feat(qa-skills): scaffold P3 directory structure and review guidelines

Create .github/skills/qa/ P3 directories for 5 advanced skills.
Add rules/review-guidelines.md (two-stage review, cross-model protocol, comment standards)."
```

---

## Task 2: scoring-risk skill

Risk scoring feeds dynamic coverage thresholds to analyzing-coverage and test selection priorities to selecting-regressions.

**Files:**
- Create: `.github/skills/qa/scoring-risk/SKILL.md`
- Create: `.github/skills/qa/scoring-risk/scripts/change-scope-analyzer.py`
- Create: `.github/skills/qa/scoring-risk/scripts/component-criticality.py`
- Create: `.github/skills/qa/scoring-risk/scripts/defect-density-calculator.py`
- Create: `.github/skills/qa/scoring-risk/references/risk-scoring-model.md`
- Create: `.github/skills/qa/scoring-risk/references/component-registry.md`
- Create: `.github/skills/qa/scoring-risk/evals/test-prompts.yaml`
- Create: `.github/skills/qa/scoring-risk/evals/assertions.yaml`

- [ ] **Step 1: Write SKILL.md**

```markdown
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
```

- [ ] **Step 2: Write scripts/change-scope-analyzer.py**

```python
#!/usr/bin/env python3
"""Analyze change scope: files changed, lines delta, blast radius.

Usage: echo '<git_diff_text>' | python change-scope-analyzer.py
Output: JSON with scope score (0-25) and factors.
"""

import json
import sys
import re


def parse_diff(diff_text: str) -> dict:
    """Parse unified diff format and extract metrics."""
    files = {}
    current_file = None
    additions = 0
    deletions = 0

    for line in diff_text.split('\n'):
        # File header: +++ b/path/to/file or --- a/path/to/file
        if line.startswith('+++'):
            current_file = line.replace('+++ b/', '').strip()
            if current_file and current_file not in files:
                files[current_file] = {'additions': 0, 'deletions': 0}
        elif line.startswith('---') and not line.startswith('--- a/'):
            continue
        elif line.startswith('-') and not line.startswith('---'):
            deletions += 1
            if current_file and current_file in files:
                files[current_file]['deletions'] += 1
        elif line.startswith('+') and not line.startswith('+++'):
            additions += 1
            if current_file and current_file in files:
                files[current_file]['additions'] += 1

    return {
        'files_changed': len(files),
        'total_additions': additions,
        'total_deletions': deletions,
        'total_lines_delta': additions + deletions,
        'files': files
    }


def calculate_scope_score(metrics: dict) -> int:
    """Calculate scope points (0-25) from change metrics.

    Heuristic:
    - 1-3 files, <50 lines → 5 points (small fix)
    - 4-10 files, 50-200 lines → 10 points (feature)
    - 11-30 files, 200-500 lines → 15 points (module refactor)
    - 30+ files, 500+ lines → 25 points (major refactor/infra change)
    """
    files = metrics['files_changed']
    lines = metrics['total_lines_delta']

    if files <= 3 and lines < 50:
        return 5
    elif files <= 10 and lines < 200:
        return 10
    elif files <= 30 and lines < 500:
        return 15
    else:
        return 25


def identify_blast_radius(files: dict) -> list:
    """Identify files modified that suggest broad impact."""
    blast_files = []
    high_risk_patterns = [
        r'package\.json|requirements\.txt|pyproject\.toml',  # deps
        r'tsconfig\.json|babel\.config\.js|setup\.cfg',      # config
        r'\.env\.|secrets\.',                                 # secrets (bad)
        r'utils\.ts?|helpers\.py|shared/',                   # shared code
        r'middleware/|interceptors/',                         # global middleware
    ]

    for filename in files.keys():
        for pattern in high_risk_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                blast_files.append(filename)
                break

    return blast_files


def main():
    diff_text = sys.stdin.read()

    if not diff_text.strip():
        json.dump({
            'scope_score': 0,
            'files_changed': 0,
            'total_lines_delta': 0,
            'blast_radius': [],
            'confidence': 'low'
        }, sys.stdout, indent=2)
        return

    metrics = parse_diff(diff_text)
    scope_score = calculate_scope_score(metrics)
    blast_radius = identify_blast_radius(metrics['files'])

    output = {
        'scope_score': scope_score,
        'files_changed': metrics['files_changed'],
        'total_additions': metrics['total_additions'],
        'total_deletions': metrics['total_deletions'],
        'total_lines_delta': metrics['total_lines_delta'],
        'blast_radius': blast_radius,
        'blast_radius_count': len(blast_radius),
        'confidence': 'high' if metrics['files_changed'] > 0 else 'low'
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
```

- [ ] **Step 3: Write scripts/component-criticality.py**

```python
#!/usr/bin/env python3
"""Determine component criticality from file paths and registry.

Usage: echo '{"files": ["src/payments/processor.ts"], "registry": {...}}' | python component-criticality.py
Output: JSON with criticality_score (0-35) and component tier.
"""

import json
import sys
import re


DEFAULT_REGISTRY = {
    "payment": {"tier": "critical", "score": 35},
    "auth": {"tier": "critical", "score": 30},
    "security": {"tier": "critical", "score": 30},
    "policy": {"tier": "high", "score": 20},
    "claim": {"tier": "high", "score": 20},
    "customer": {"tier": "high", "score": 20},
    "api": {"tier": "high", "score": 20},
    "database": {"tier": "high", "score": 20},
    "util": {"tier": "low", "score": 10},
    "helper": {"tier": "low", "score": 10},
    "test": {"tier": "low", "score": 5},
}


def detect_component(filepath: str, registry: dict) -> dict:
    """Detect component from filepath using registry and heuristics."""
    filepath_lower = filepath.lower()

    # Direct registry lookup
    for component, config in registry.items():
        if re.search(rf'/{component}s?/', filepath_lower) or filepath_lower.startswith(component):
            return config

    # Fallback: directory-based detection
    parts = filepath_lower.split('/')
    if len(parts) > 1:
        dir_name = parts[1]  # assume src/component/...
        for key, config in DEFAULT_REGISTRY.items():
            if dir_name.startswith(key):
                return config

    # Default to low criticality
    return DEFAULT_REGISTRY.get("util", {"tier": "low", "score": 10})


def calculate_max_criticality(files: list, registry: dict) -> dict:
    """Return the highest criticality component found."""
    scores = []

    for filepath in files:
        component = detect_component(filepath, registry)
        scores.append({
            'file': filepath,
            'tier': component.get('tier', 'low'),
            'score': component.get('score', 10)
        })

    if not scores:
        return {
            'criticality_score': 10,
            'tier': 'low',
            'components': [],
            'confidence': 'low'
        }

    max_score = max(scores, key=lambda x: x['score'])

    return {
        'criticality_score': max_score['score'],
        'tier': max_score['tier'],
        'components': scores,
        'confidence': 'medium' if len(scores) > 0 else 'low'
    }


def main():
    data = json.load(sys.stdin)
    files = data.get('files', [])
    registry = data.get('registry', DEFAULT_REGISTRY)

    result = calculate_max_criticality(files, registry)
    json.dump(result, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: Write scripts/defect-density-calculator.py**

```python
#!/usr/bin/env python3
"""Calculate defect density from historical defect data (Knowledge Base).

Usage: echo '{"files": [...], "defect_history": {...}}' | python defect-density-calculator.py
Output: JSON with defect_score (0-25) and history summary.

Graceful degradation: No history available → score = 0 (neutral).
"""

import json
import sys
from collections import defaultdict


def calculate_defect_score(files: list, defect_history: dict) -> int:
    """Calculate defect points (0-25) from historical density.

    Heuristic:
    - No history → 0 (neutral, don't penalize unknowns)
    - <1 defect per 1000 lines → 5 points
    - 1-2 defects per 1000 lines → 10 points
    - 2-5 defects per 1000 lines → 15 points
    - >5 defects per 1000 lines → 25 points (hotspot)
    """
    if not defect_history or not files:
        return 0

    total_defects = 0

    for filepath in files:
        # Normalize path for lookup
        normalized = filepath.lstrip('./')

        file_defects = defect_history.get(normalized, {})
        if isinstance(file_defects, dict):
            total_defects += file_defects.get('count', 0)
        else:
            total_defects += file_defects

    if total_defects == 0:
        return 0

    # Estimate density (defects per file is rough proxy)
    density = total_defects / max(len(files), 1)

    if density < 1:
        return 5
    elif density < 2:
        return 10
    elif density < 5:
        return 15
    else:
        return 25


def main():
    data = json.load(sys.stdin)
    files = data.get('files', [])
    defect_history = data.get('defect_history', {})

    defect_score = calculate_defect_score(files, defect_history)

    # Summarize history for transparency
    file_summaries = {}
    for filepath in files:
        normalized = filepath.lstrip('./')
        if normalized in defect_history:
            file_summaries[normalized] = defect_history[normalized]

    output = {
        'defect_score': defect_score,
        'total_defects': sum(
            d.get('count', 0) if isinstance(d, dict) else d
            for d in defect_history.values()
        ) if defect_history else 0,
        'affected_files_with_history': len(file_summaries),
        'file_summaries': file_summaries,
        'confidence': 'high' if defect_history else 'low'
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
```

- [ ] **Step 5: Write references/risk-scoring-model.md**

```markdown
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
```

- [ ] **Step 6: Write references/component-registry.md**

```markdown
# Component Registry — Project-Specific

> Maintained by tech leads and architects. Defines component criticality for risk scoring. Updated annually or when architecture changes.

## Template

Copy this section per component and customize for your org:

```yaml
components:
  payment:
    tier: critical
    score: 35
    description: "Payment processing, ledger updates, card management"
    paths: ["src/services/payment/", "src/modules/payment/"]
    owners: ["@payment-team"]

  auth:
    tier: critical
    score: 30
    description: "Authentication, JWT, session management"
    paths: ["src/auth/", "src/middleware/auth.ts"]
    owners: ["@security-team"]

  policy:
    tier: high
    score: 20
    description: "Policy operations, underwriting rules"
    paths: ["src/policy/", "src/modules/underwriting/"]
    owners: ["@underwriting-team"]

  api:
    tier: high
    score: 20
    description: "REST/GraphQL API contracts"
    paths: ["src/api/"]
    owners: ["@platform-team"]

  utils:
    tier: low
    score: 10
    description: "Utility functions, helpers"
    paths: ["src/utils/", "src/lib/"]
    owners: ["@platform-team"]
```

## Instructions for Teams

1. List all major components (functional domains)
2. Assign tier based on impact if component fails:
   - **Critical:** Revenue impact, security breach, compliance violation
   - **High:** Operational impact, user experience degradation
   - **Low:** Non-critical features, developer tools
3. Add file paths (glob patterns OK)
4. Assign owning team for escalations
5. Review annually or when architecture changes

## Example (Insurance Domain)

```yaml
components:
  claims:
    tier: critical
    score: 35
    description: "Claims processing, settlements, fraud detection"
    paths: ["src/claims/**", "src/services/claim*.ts"]
    owners: ["@claims-team"]

  underwriting:
    tier: critical
    score: 30
    description: "Risk assessment, policy approval, rating rules"
    paths: ["src/underwriting/**"]
    owners: ["@underwriting-team"]

  billing:
    tier: high
    score: 20
    description: "Premium calculations, invoicing"
    paths: ["src/billing/**"]
    owners: ["@finance-team"]

  customer:
    tier: high
    score: 20
    description: "Customer profiles, communications"
    paths: ["src/customer/**", "src/modules/customer/**"]
    owners: ["@customer-success"]
```
```

- [ ] **Step 7: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "sr-tc-001"
    description: "Critical component, small change scope"
    input:
      git_diff: |
        diff --git a/src/payment/processor.ts b/src/payment/processor.ts
        index abc123..def456 100644
        --- a/src/payment/processor.ts
        +++ b/src/payment/processor.ts
        @@ -10,6 +10,10 @@ export class PaymentProcessor {
           async processPayment(amount: number) {
        +    if (amount < 0) {
        +      throw new Error('Amount must be positive');
        +    }
             return this.gateway.charge(amount);
           }
      issue_metadata:
        component: payment
        title: "Add negative amount validation"
    expected:
      risk_score_gte: 60
      risk_level: "high"
      factors:
        scope_score: 5
        criticality_score: 35
      thresholds:
        coverage_gte: 85

  - id: "sr-tc-002"
    description: "Low-risk utility change, broad scope"
    input:
      git_diff: |
        diff --git a/src/utils/helpers.ts b/src/utils/helpers.ts
        index abc123..def456 100644
        --- a/src/utils/helpers.ts
        +++ b/src/utils/helpers.ts
        @@ -1,50 +1,80 @@
         // Major refactor of utility functions
      issue_metadata:
        title: "Refactor helpers for performance"
    expected:
      risk_score_lte: 30
      risk_level: "low"
      factors:
        criticality_score: 10

  - id: "sr-tc-003"
    description: "High defect history component"
    input:
      git_diff: |
        diff --git a/src/api/legacy-endpoint.ts b/src/api/legacy-endpoint.ts
      issue_metadata:
        title: "Fix legacy API endpoint"
      defect_history:
        "src/api/legacy-endpoint.ts":
          count: 12
          density: 0.08
    expected:
      risk_score_gte: 50
      factors:
        defect_score_gte: 15
```

- [ ] **Step 8: Write evals/assertions.yaml**

```yaml
assertions:
  - test_id: "sr-tc-001"
    checks:
      - path: "risk_score"
        type: "number_range"
        min: 60
        max: 100
      - path: "risk_level"
        type: "equals"
        value: "high"
      - path: "factors[0].score"
        type: "number_range"
        min: 0
        max: 25
      - path: "recommended_thresholds.coverage"
        type: "number_gte"
        value: 85

  - test_id: "sr-tc-002"
    checks:
      - path: "risk_score"
        type: "number_lte"
        value: 30
      - path: "risk_level"
        type: "equals"
        value: "low"

  - test_id: "sr-tc-003"
    checks:
      - path: "risk_score"
        type: "number_gte"
        value: 50
      - path: "factors"
        type: "array_has_where"
        field: "name"
        value: "defect_density"
```

- [ ] **Step 9: Commit scoring-risk skill**

```bash
git add .github/skills/qa/scoring-risk/
git commit -m "feat(qa-skills): implement scoring-risk P3 skill

Adds risk scoring based on change scope, component criticality, defect history, complexity delta.
Produces dynamic coverage thresholds for analyzing-coverage and prioritization for selecting-regressions.

Scripts:
- change-scope-analyzer.py: Files changed, lines delta, blast radius
- component-criticality.py: Component tier detection and scoring
- defect-density-calculator.py: Historical defect density (graceful degradation)

References:
- risk-scoring-model.md: Scoring algorithm, factor weights, thresholds
- component-registry.md: Project-specific component tiers

Evals: 3 test cases (critical/high, low-risk, high-history)."
```

---

## Task 3: reviewing-code-quality skill

Two-stage review for Code Reviewer agent (cross-model objectivity).

**Files:**
- Create: `.github/skills/qa/reviewing-code-quality/SKILL.md`
- Create: `.github/skills/qa/reviewing-code-quality/scripts/spec-compliance-checker.py`
- Create: `.github/skills/qa/reviewing-code-quality/scripts/quality-metrics.py`
- Create: `.github/skills/qa/reviewing-code-quality/references/review-checklist.md`
- Create: `.github/skills/qa/reviewing-code-quality/references/code-quality-standards.md`
- Create: `.github/skills/qa/reviewing-code-quality/evals/test-prompts.yaml`
- Create: `.github/skills/qa/reviewing-code-quality/evals/assertions.yaml`

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: reviewing-code-quality
version: "1.0.0"
description: "Two-stage review: spec compliance first, then code quality"
category: evaluation
phase: post-coding
platforms: ["all"]
dependencies: ["generating-qa-report"]
input_schema:
  - name: "git_diff"
    type: "string"
    required: true
  - name: "qa_report"
    type: "object"
    required: true
    description: "QA report must pass all gates before code review"
  - name: "spec_references"
    type: "array"
    required: false
  - name: "review_focus"
    type: "array"
    required: false
output_schema:
  - name: "stage1_spec_compliance"
    type: "object"
  - name: "stage2_code_quality"
    type: "object"
  - name: "verdict"
    type: "string"
    description: "APPROVE | REQUEST_CHANGES | COMMENT"
  - name: "comments"
    type: "array"
    description: "Line-level review comments"
---

# reviewing-code-quality

Two-stage code review: verify spec compliance first, then evaluate code quality. Consumed by Code Reviewer agent (Claude Sonnet 4.6) for cross-model objectivity.

## When to Use

Invoke after QA report is generated and QA gates PASS. If QA gates fail, do not review code.

**Prerequisites:**
- `generating-qa-report` must complete
- All Pass Rate, Coverage, Acceptance gates must be PASS

## Instructions

### Stage 1: Specification Compliance

**Purpose:** Ensure implementation addresses every AC/spec requirement.

1. Extract acceptance criteria from issue description or QA report
2. For each AC, search diff for corresponding implementation
3. Check for:
   - Missing AC (requirement in spec, not in diff)
   - Incomplete implementation (skeleton only)
   - Spec-breaking changes (contradicts AC)

4. Run `scripts/spec-compliance-checker.py` with diff + AC list
5. Output `stage1_spec_compliance` with verdict: PASS or FAIL

**Stage 1 Verdict Logic:**
- `PASS`: All AC requirements covered in diff
- `FAIL`: Any requirement unimplemented or contradicted

**Action:**
- Stage 1 FAIL → output `verdict: REQUEST_CHANGES`, skip Stage 2
- Stage 1 PASS → proceed to Stage 2

### Stage 2: Code Quality

**Only evaluate if Stage 1 passes.**

1. Run `scripts/quality-metrics.py` on diff to extract metrics:
   - Function length
   - Cyclomatic complexity
   - Nesting depth
   - Code duplication
   - SOLID principle violations

2. Evaluate against references/code-quality-standards.md:
   - Readability (length, names, self-documentation)
   - SOLID principles (SRP, OCP, LSP, ISP, DIP)
   - Performance (N+1, caching, response times)
   - Security (input validation, hardcoded secrets)
   - Patterns (consistency with codebase)

3. Generate actionable comments (see review-guidelines.md § Comment Quality)

4. Output `stage2_code_quality` with:
   - Issues found (array of {severity, location, suggestion})
   - Overall verdict: APPROVE | REQUEST_CHANGES | COMMENT

### Final Verdict

```
if stage1 = FAIL → REQUEST_CHANGES (+ explain spec gaps)
elif stage2 = REQUEST_CHANGES → REQUEST_CHANGES
elif stage2 = COMMENT → COMMENT
else → APPROVE
```

## Consumers

- Code Reviewer agent (Claude Sonnet 4.6) — uses output as review summary, may expand with additional insights

## Guardrails

- Never approve if Stage 1 fails
- Every comment must be actionable and specific (not "could be better")
- Don't flag linter/formatter issues (use hooks instead)
- Quality issues should note severity: Critical | Major | Minor
- When uncertain, ask clarifying questions instead of assuming
```

- [ ] **Step 2: Write scripts/spec-compliance-checker.py**

```python
#!/usr/bin/env python3
"""Check if diff implementation covers all acceptance criteria.

Usage: echo '{"diff": "...", "acceptance_criteria": [...]}' | python spec-compliance-checker.py
Output: JSON with stage1_spec_compliance verdict.
"""

import json
import sys
import re


def extract_ac_keywords(ac_text: str) -> list:
    """Extract keywords from AC for searching in diff."""
    # Remove common words and split on word boundaries
    stopwords = {'the', 'a', 'an', 'is', 'are', 'must', 'should', 'will', 'when', 'then', 'given'}
    words = re.findall(r'\b\w+\b', ac_text.lower())
    return [w for w in words if w not in stopwords and len(w) > 3]


def search_diff_for_ac(diff_text: str, ac_text: str, keywords: list) -> bool:
    """Search diff for evidence of AC implementation."""
    diff_lower = diff_text.lower()

    # Look for exact phrase match
    if ac_text.lower() in diff_lower:
        return True

    # Look for significant keyword matches (>50% of keywords)
    matches = sum(1 for kw in keywords if kw in diff_lower)
    if matches >= len(keywords) * 0.5 and len(keywords) > 0:
        return True

    # Look for variable/function name related to AC
    # e.g., "password validation" → search for "password" or "validate"
    for keyword in keywords:
        if re.search(rf'\b{keyword}s?\b', diff_lower):
            return True

    return False


def check_compliance(diff_text: str, criteria: list) -> dict:
    """Check if diff covers all acceptance criteria."""
    if not criteria:
        return {
            'verdict': 'UNKNOWN',
            'details': 'No acceptance criteria provided',
            'covered': [],
            'uncovered': []
        }

    covered = []
    uncovered = []

    for ac in criteria:
        ac_id = ac.get('id', '?')
        ac_text = ac.get('text', '')

        if not ac_text.strip():
            continue

        keywords = extract_ac_keywords(ac_text)
        is_covered = search_diff_for_ac(diff_text, ac_text, keywords)

        record = {
            'id': ac_id,
            'text': ac_text[:100],  # truncate for output
            'covered': is_covered
        }

        if is_covered:
            covered.append(record)
        else:
            uncovered.append(record)

    verdict = 'PASS' if len(uncovered) == 0 else 'FAIL'

    return {
        'verdict': verdict,
        'coverage_ratio': f"{len(covered)}/{len(criteria)}",
        'covered': covered,
        'uncovered': uncovered
    }


def main():
    data = json.load(sys.stdin)
    diff = data.get('diff', '')
    criteria = data.get('acceptance_criteria', [])

    result = check_compliance(diff, criteria)

    output = {
        'stage1_spec_compliance': result
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
```

- [ ] **Step 3: Write scripts/quality-metrics.py**

```python
#!/usr/bin/env python3
"""Extract code quality metrics from diff.

Usage: echo '{"diff": "...", "language": "typescript"}' | python quality-metrics.py
Output: JSON with function lengths, complexity, nesting depth, duplication flags.
"""

import json
import sys
import re
from collections import defaultdict


def analyze_python_code(code: str) -> dict:
    """Analyze Python code metrics."""
    lines = code.split('\n')
    functions = []
    current_func = None
    indent_stack = []
    max_nesting = 0

    for i, line in enumerate(lines):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # Track indentation (proxy for nesting)
        while indent_stack and indent_stack[-1] >= indent:
            indent_stack.pop()
        indent_stack.append(indent)
        max_nesting = max(max_nesting, len(indent_stack))

        # Detect function definition
        if re.match(r'^\s*(async\s+)?def\s+\w+', line):
            if current_func:
                current_func['end_line'] = i - 1
                functions.append(current_func)
            current_func = {
                'name': re.search(r'def\s+(\w+)', line).group(1),
                'start_line': i,
                'lines': 1
            }
        elif current_func:
            current_func['lines'] += 1

    if current_func:
        functions.append(current_func)

    return {
        'language': 'python',
        'functions': functions,
        'max_nesting': min(max_nesting, 5),  # cap at 5 for reasonableness
        'quality_issues': []
    }


def analyze_typescript_code(code: str) -> dict:
    """Analyze TypeScript code metrics."""
    lines = code.split('\n')
    functions = []
    current_func = None
    bracket_stack = []

    for i, line in enumerate(lines):
        # Detect function definition
        if re.search(r'\b(async\s+)?(function|\w+\s*\(|=>)', line):
            if re.search(r'\bfunction\s+\w+|^\s*\w+\s*\([^)]*\)\s*(?::|=>)', line):
                if current_func:
                    functions.append(current_func)
                func_name = re.search(r'\b(?:function\s+)?(\w+)\s*\(', line)
                current_func = {
                    'name': func_name.group(1) if func_name else 'anonymous',
                    'start_line': i,
                    'lines': 1
                }

        # Count brackets for nesting
        bracket_stack.extend(line.count('{') - line.count('}'))

        if current_func:
            current_func['lines'] += 1

    if current_func:
        functions.append(current_func)

    max_nesting = max(bracket_stack) if bracket_stack else 0

    return {
        'language': 'typescript',
        'functions': functions,
        'max_nesting': min(max_nesting, 5),
        'quality_issues': []
    }


def flag_quality_issues(metrics: dict) -> dict:
    """Flag quality issues based on metrics."""
    issues = []

    for func in metrics.get('functions', []):
        if func.get('lines', 0) > 30:
            issues.append({
                'severity': 'major',
                'type': 'function_too_long',
                'function': func['name'],
                'lines': func['lines'],
                'suggestion': 'Extract to smaller functions (target: <30 lines)'
            })

        if func.get('lines', 0) > 50:
            issues.append({
                'severity': 'critical',
                'type': 'function_too_long',
                'function': func['name'],
                'lines': func['lines'],
                'suggestion': 'Break into multiple functions (<30 lines each)'
            })

    if metrics.get('max_nesting', 0) > 3:
        issues.append({
            'severity': 'major',
            'type': 'deep_nesting',
            'depth': metrics['max_nesting'],
            'suggestion': 'Reduce nesting depth to ≤3 using early returns or extraction'
        })

    return issues


def main():
    data = json.load(sys.stdin)
    diff = data.get('diff', '')
    language = data.get('language', 'unknown').lower()

    # Extract code additions from diff
    code_additions = '\n'.join(
        line[1:] for line in diff.split('\n')
        if line.startswith('+') and not line.startswith('+++')
    )

    if language == 'python':
        metrics = analyze_python_code(code_additions)
    elif language in ('typescript', 'javascript', 'ts', 'js'):
        metrics = analyze_typescript_code(code_additions)
    else:
        metrics = {
            'language': 'unknown',
            'functions': [],
            'max_nesting': 0,
            'quality_issues': []
        }

    # Flag issues
    metrics['quality_issues'] = flag_quality_issues(metrics)

    output = {
        'stage2_code_quality': {
            'metrics': metrics,
            'verdict': 'REQUEST_CHANGES' if metrics['quality_issues'] else 'APPROVE'
        }
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: Write references/review-checklist.md**

```markdown
# Code Review Checklist — Reference

Use this checklist when evaluating code quality (Stage 2).

## Spec Compliance (Stage 1)

- [ ] Every AC requirement has corresponding implementation
- [ ] No conflicting changes to existing AC
- [ ] Edge cases mentioned in spec are covered

## Readability

- [ ] Function names are descriptive (read name, understand purpose)
- [ ] Variable names are meaningful (not single-letter except loop counters)
- [ ] Comments explain WHY, not WHAT (code should be self-documenting)
- [ ] Complex logic has explanatory comments
- [ ] Functions are <30 lines (excluding tests)
- [ ] Nesting depth ≤3 (use early returns to flatten)
- [ ] No dead code or commented-out code

## SOLID Principles

- **Single Responsibility:** Each class/function has one reason to change
- **Open/Closed:** Open for extension, closed for modification
- **Liskov Substitution:** Subtypes are substitutable for base types
- **Interface Segregation:** Clients depend on specific interfaces, not monoliths
- **Dependency Inversion:** Depend on abstractions, not implementations

Flags:
- [ ] Class has 10+ public methods? (SRP violation)
- [ ] Changing one feature breaks unrelated tests? (tight coupling)
- [ ] Function has 5+ parameters? (pass objects instead)
- [ ] Type assertions or casts in logic? (LSP violation)

## Performance

- [ ] No N+1 queries (explicit `.eager_load()` or batch queries)
- [ ] Caching strategy documented for expensive operations
- [ ] No unnecessary full-table scans or large result sets
- [ ] API response times: target <500ms p95
- [ ] No blocking operations on event loop (async/await proper)
- [ ] No deep recursion without base case protection

## Security

- [ ] Input validation at all API boundaries
- [ ] No hardcoded credentials, API keys, tokens
- [ ] Parameterized queries (prevent SQL injection)
- [ ] CORS/CSRF protection enabled
- [ ] Secrets loaded from environment, not code
- [ ] Authentication/authorization verified before sensitive operations
- [ ] PII logged only in debug mode, sanitized in production
- [ ] Dependencies checked for known vulnerabilities

## Testing

- [ ] New code has test coverage (target: >80%)
- [ ] Tests are independent (no shared state)
- [ ] Test names describe the scenario and expected outcome
- [ ] Happy path AND error cases tested

## Error Handling

- [ ] Errors are caught and handled explicitly (not silently ignored)
- [ ] User-facing errors have clear messages
- [ ] System errors logged with context for debugging
- [ ] Graceful degradation on external service failure

## Documentation

- [ ] Public methods have docstrings/JSDoc
- [ ] Complex algorithms explained
- [ ] Breaking changes documented
- [ ] Examples provided for non-obvious APIs
```

- [ ] **Step 5: Write references/code-quality-standards.md**

```markdown
# Code Quality Standards — Reference

## Language-Agnostic Standards

Applied to all code regardless of language.

### Function Length

| Threshold | Severity | Action |
|-----------|----------|--------|
| <20 lines | Ideal | No action |
| 20–30 lines | Acceptable | Monitor |
| 30–50 lines | Warning | Consider extraction |
| >50 lines | Critical | Must refactor |

**Exception:** Generated code, data mappers (>100 lines OK if simple transformations).

### Cyclomatic Complexity

| Score | Meaning |
|-------|---------|
| 1–5 | Good: easily testable |
| 6–10 | Moderate: test thoroughly |
| 11–15 | High: consider refactoring |
| 16+ | Very High: refactor required |

**Calculation:** Count decision points (if, else, switch, catch, loops, && operators, || operators).

### Nesting Depth

| Depth | Example | Comment |
|-------|---------|---------|
| 1–2 | if → logic | Ideal |
| 3–4 | if → if → if → logic | Acceptable, use early returns |
| 5+ | Deep nesting | Refactor: extract helper, guard clauses |

**Technique:** Use early returns to flatten:
```
// Bad: nested logic
function validate(user) {
  if (user) {
    if (user.email) {
      if (user.email.includes('@')) {
        return true;
      }
    }
  }
  return false;
}

// Good: guard clauses
function validate(user) {
  if (!user) return false;
  if (!user.email) return false;
  if (!user.email.includes('@')) return false;
  return true;
}
```

### Code Duplication

- First occurrence: write normally
- Second occurrence: still acceptable (copy-paste might be justified)
- Third occurrence: extract to shared function

**DRY violation threshold:** >2 copies of similar logic.

### Naming Conventions

| Context | Style | Example |
|---------|-------|---------|
| Classes/Types | PascalCase | `PaymentProcessor`, `User` |
| Functions/Methods | camelCase | `processPayment`, `getUserById` |
| Constants | UPPER_SNAKE | `MAX_RETRIES`, `API_ENDPOINT` |
| Variables | camelCase | `userName`, `transactionId` |
| Boolean functions | is/has prefix | `isValid()`, `hasPermission()` |

### Import Ordering

Standard: External → Internal → Relative
```typescript
// External
import express from 'express';
import { Logger } from 'winston';

// Internal
import { PaymentService } from '../services/payment';
import { User } from '../models/user';

// Relative
import { validateEmail } from './validators';
import { config } from './config';
```

## Language-Specific Standards

### TypeScript/JavaScript

- **Strict mode:** Required in tsconfig.json
- **Type assertions:** Minimize `as Type` — prefer proper typing
- **Any type:** Forbidden except for temporary debugging
- **Async patterns:** Always `await` promises, handle errors
- **String templates:** Use backticks for dynamic strings, not `+` concat

### Python

- **Type hints:** Required for all function signatures
- **Docstrings:** All public functions need docstrings (Google/NumPy style)
- **Virtual environments:** Always use venv for isolation
- **Import order:** Standard library → third-party → local (autopep8 compatible)
- **Lint:** Pass flake8/pylint without warnings

### Java

- **Annotations:** Use @Override, @Deprecated, @FunctionalInterface appropriately
- **Exception handling:** Catch specific exceptions, not generic `Exception`
- **Stream API:** Prefer functional style for collections
- **Nullability:** Use @Nullable/@NotNull or Optional<T>

### Go

- **Table-driven tests:** Standard pattern for testing multiple scenarios
- **Error handling:** Explicit `if err != nil` checks (not hidden exceptions)
- **Goroutine testing:** Use `sync.WaitGroup` or channels correctly
- **Race detector:** All concurrent code passes `go test -race`

## Performance Targets

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| API endpoint latency | <200ms p95 | >500ms p99 |
| Database query | <100ms | >500ms |
| Page load | <2s | >5s |
| Test suite | <10 min | >30 min |

## Code Review Comment Quality

### Good Comment
```
Line 42: N+1 query detected. Load orders with posts in single query:
  Post.includes(:orders).where(...)
```

### Bad Comment
```
This could be more efficient
```

### Good Suggestion
```
Optional: Extract this validation logic to a helper method for reusability across endpoints.
Technical debt [TECH-123].
```

### Bad Suggestion
```
Make it better
```
```

- [ ] **Step 6: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "rcq-tc-001"
    description: "Spec compliant, good code quality"
    input:
      git_diff: |
        diff --git a/src/auth/validator.ts
        +++ b/src/auth/validator.ts
        +export function validatePassword(password: string): boolean {
        +  if (!password || password.length < 8) return false;
        +  if (!password.match(/[A-Z]/)) return false;
        +  return password.match(/[0-9]/) !== null;
        +}
      qa_report:
        pass_rate: "PASS"
        coverage: "PASS"
        acceptance: "PASS"
      acceptance_criteria:
        - id: "AC-1"
          text: "Password must be 8-64 characters"
        - id: "AC-2"
          text: "Must contain at least one uppercase letter and one number"
    expected:
      stage1_verdict: "PASS"
      stage2_verdict: "APPROVE"
      final_verdict: "APPROVE"

  - id: "rcq-tc-002"
    description: "Missing AC implementation"
    input:
      git_diff: |
        diff --git a/src/payment/processor.ts
        +++ b/src/payment/processor.ts
        +export async function processPayment(amount: number) {
        +  return this.gateway.charge(amount);
        +}
      qa_report:
        pass_rate: "PASS"
      acceptance_criteria:
        - id: "AC-1"
          text: "Validate amount is positive"
        - id: "AC-2"
          text: "Return transaction ID"
    expected:
      stage1_verdict: "FAIL"
      uncovered:
        - "AC-1"
      final_verdict: "REQUEST_CHANGES"

  - id: "rcq-tc-003"
    description: "High-quality code quality"
    input:
      git_diff: |
        diff --git a/src/utils/helpers.ts
        +++ b/src/utils/helpers.ts
        +function calculateTotal(items: Item[]): number {
        +  return items.reduce((sum, item) => sum + item.price, 0);
        +}
        +
        +function filterActive(items: Item[]): Item[] {
        +  return items.filter(item => item.active);
        +}
      qa_report:
        pass_rate: "PASS"
        coverage: "PASS"
        acceptance: "PASS"
    expected:
      stage2_quality_issues: []
      stage2_verdict: "APPROVE"

  - id: "rcq-tc-004"
    description: "Code quality issues: long function, deep nesting"
    input:
      git_diff: |
        diff --git a/src/logic/complex.ts
        +++ b/src/logic/complex.ts
        +function handleRequest(req) {
        +  if (req.user) {
        +    if (req.user.authenticated) {
        +      if (req.body.data) {
        +        if (req.body.data.length > 0) {
        +          // ... 45 lines of processing logic ...
        +        }
        +      }
        +    }
        +  }
        +}
      qa_report:
        pass_rate: "PASS"
        coverage: "PASS"
        acceptance: "PASS"
    expected:
      stage2_quality_issues_count_gte: 1
      stage2_verdict: "COMMENT"
```

- [ ] **Step 7: Write evals/assertions.yaml**

```yaml
assertions:
  - test_id: "rcq-tc-001"
    checks:
      - path: "stage1_spec_compliance.verdict"
        type: "equals"
        value: "PASS"
      - path: "stage2_code_quality.verdict"
        type: "equals"
        value: "APPROVE"
      - path: "verdict"
        type: "equals"
        value: "APPROVE"

  - test_id: "rcq-tc-002"
    checks:
      - path: "stage1_spec_compliance.verdict"
        type: "equals"
        value: "FAIL"
      - path: "stage1_spec_compliance.uncovered"
        type: "array_length_gte"
        value: 1
      - path: "verdict"
        type: "equals"
        value: "REQUEST_CHANGES"

  - test_id: "rcq-tc-003"
    checks:
      - path: "stage2_code_quality.metrics.quality_issues"
        type: "array_length"
        value: 0
      - path: "stage2_code_quality.verdict"
        type: "equals"
        value: "APPROVE"

  - test_id: "rcq-tc-004"
    checks:
      - path: "stage2_code_quality.metrics.quality_issues"
        type: "array_length_gte"
        value: 1
      - path: "stage2_code_quality.verdict"
        type: "equals"
        value: "REQUEST_CHANGES"
```

- [ ] **Step 8: Commit reviewing-code-quality skill**

```bash
git add .github/skills/qa/reviewing-code-quality/
git commit -m "feat(qa-skills): implement reviewing-code-quality P3 skill

Two-stage review for Code Reviewer agent (cross-model objectivity).

Stage 1: Spec compliance verification (all AC requirements covered?)
Stage 2: Code quality evaluation (readability, SOLID, performance, security)

Scripts:
- spec-compliance-checker.py: AC keyword extraction and diff coverage search
- quality-metrics.py: Function length, complexity, nesting depth analysis

References:
- review-checklist.md: Detailed checklist for Stage 2 evaluation
- code-quality-standards.md: Language-specific and universal standards

Evals: 4 test cases (compliant+good, missing AC, high-quality, quality-issues)."
```

---

## Task 4: selecting-regressions skill

Regression test selection based on change impact analysis and risk scoring.

[Continuing in next message due to length...]

**Files:**
- Create: `.github/skills/qa/selecting-regressions/SKILL.md`
- Create: `.github/skills/qa/selecting-regressions/scripts/change-impact-analyzer.py`
- Create: `.github/skills/qa/selecting-regressions/scripts/dependency-graph-walker.py`
- Create: `.github/skills/qa/selecting-regressions/scripts/test-selector.py`
- Create: `.github/skills/qa/selecting-regressions/references/regression-strategies.md`
- Create: `.github/skills/qa/selecting-regressions/evals/test-prompts.yaml`
- Create: `.github/skills/qa/selecting-regressions/evals/assertions.yaml`

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: selecting-regressions
version: "1.0.0"
description: "Select relevant regression tests from change impact analysis — run only affected tests"
category: execution
phase: post-coding
platforms: ["all"]
dependencies: ["scoring-risk"]
soft_dependencies: ["generating-playwright-tests", "generating-api-tests", "generating-mobile-tests", "generating-perf-tests"]
input_schema:
  - name: "git_diff"
    type: "string"
    required: true
  - name: "test_catalog"
    type: "object"
    required: true
    description: "Inventory of all available tests with metadata"
  - name: "dependency_graph"
    type: "object"
    required: false
    description: "From Knowledge Base MCP or build system"
  - name: "risk_score"
    type: "object"
    required: false
    description: "From scoring-risk skill"
output_schema:
  - name: "selected_tests"
    type: "array"
    description: "Ordered by priority"
  - name: "skipped_tests"
    type: "array"
    description: "With justification"
  - name: "estimated_time"
    type: "number"
  - name: "confidence"
    type: "string"
    description: "high (full graph) | medium (heuristic) | low (filename only)"
---

# selecting-regressions

Select regression tests for the change using change impact analysis. Minimize test execution time while maintaining confidence.

## When to Use

Invoke after coding phase completes but before running tests. Determines which tests to prioritize.

## Instructions

1. Run `scripts/change-impact-analyzer.py` on git diff
   - Output: directly and transitively affected files

2. Run `scripts/dependency-graph-walker.py` to expand transitive dependencies
   - Input: dependency graph (if available from Knowledge Base MCP)
   - Output: full set of affected modules

3. Map affected modules to test files using:
   - Test naming conventions (`src/foo.ts` → `src/__tests__/foo.test.ts`)
   - Import analysis (`import { X } from 'module'`)
   - Config mappings (if available)

4. Run `scripts/test-selector.py`
   - Input: affected tests, risk score (if available), test history
   - Output: prioritized test list with estimated runtime

5. Apply guardrails:
   - Risk=critical/high → add full regression suite as fallback
   - Shared infrastructure change → full suite
   - New code with no dependencies → only new tests
   - Low confidence → warn and recommend full suite

## Confidence Levels

| Level | Condition | Action |
|-------|-----------|--------|
| high | Full dependency graph available + complete test metadata | Trust selection; run selected tests only |
| medium | Heuristic detection (file matching) + partial test metadata | Run selection + smoke test suite |
| low | Filename matching only; no graph | Warn; recommend full test suite |

## Consumers

- CI/CD system — executes selected test list
- QA Evaluator — decides whether to run full suite vs selection

## Guardrails

- Never skip critical-path tests (auth, payments, policy approval)
- Low confidence → warn + suggest full suite
- Shared infrastructure changes (deps, config, middleware) → full regression
- Additive: when in doubt, include a test
- Max 15 min execution time; if exceeded, recommend sampling strategy
```

- [ ] **Step 2: Write scripts/change-impact-analyzer.py**

```python
#!/usr/bin/env python3
"""Analyze which modules are directly affected by a change.

Usage: echo '<git_diff>' | python change-impact-analyzer.py
Output: JSON with directly affected files.
"""

import json
import sys
import re


def parse_changed_files(diff_text: str) -> list:
    """Extract file paths from unified diff."""
    files = set()

    for line in diff_text.split('\n'):
        # Detect file headers: +++ b/path/to/file or --- a/path/to/file
        if line.startswith('+++ b/'):
            files.add(line.replace('+++ b/', '').strip())
        elif line.startswith('--- a/'):
            files.add(line.replace('--- a/', '').strip())

    return sorted(list(files))


def identify_test_files(changed_files: list) -> list:
    """Identify corresponding test files for changed source files."""
    test_files = []

    for filepath in changed_files:
        # Skip if already a test file
        if re.search(r'(__tests__|\.test\.|\.spec\.)', filepath):
            test_files.append(filepath)
            continue

        # Generate probable test paths
        patterns = [
            (r'src/(.*?)(\.ts$|\.js$|\.py$)', r'src/__tests__/\1.test\2'),
            (r'src/(.*?)(\.ts$|\.js$|\.py$)', r'src/\1.spec\2'),
            (r'lib/(.*?)(\.ts$|\.js$)', r'lib/__tests__/\1.test\2'),
            (r'(.*?)(\.ts$|\.js$)', r'\1.test\2'),
        ]

        for pattern, replacement in patterns:
            match = re.search(pattern, filepath)
            if match:
                test_path = re.sub(pattern, replacement, filepath)
                test_files.append(test_path)

    return list(set(test_files))


def main():
    diff_text = sys.stdin.read()

    changed_files = parse_changed_files(diff_text)
    test_files = identify_test_files(changed_files)

    output = {
        'directly_affected_files': changed_files,
        'probable_test_files': test_files,
        'file_count': len(changed_files),
        'confidence': 'high' if changed_files else 'low'
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
```

- [ ] **Step 3: Write scripts/dependency-graph-walker.py**

```python
#!/usr/bin/env python3
"""Walk dependency graph to find transitive dependencies.

Usage: echo '{"affected_files": [...], "dependency_graph": {...}}' | python dependency-graph-walker.py
Output: JSON with transitive affected modules.

Graceful degradation: If no graph available, returns directly affected only.
"""

import json
import sys
from collections import deque


def normalize_path(path: str) -> str:
    """Normalize paths for consistent lookup."""
    return path.lstrip('./').rstrip('/')


def walk_graph(affected: list, graph: dict, max_depth: int = 3) -> set:
    """BFS walk of dependency graph to find transitive dependencies."""
    if not graph:
        return set(affected)

    visited = set(affected)
    queue = deque(affected)
    depth = {affected[0]: 0 for node in affected}

    while queue:
        current = queue.popleft()
        current_depth = depth.get(current, 0)

        if current_depth >= max_depth:
            continue

        # Find modules that import current module
        dependents = graph.get(normalize_path(current), {}).get('imported_by', [])

        for dep in dependents:
            if dep not in visited:
                visited.add(dep)
                queue.append(dep)
                depth[dep] = current_depth + 1

    return visited


def main():
    data = json.load(sys.stdin)
    affected_files = data.get('directly_affected_files', [])
    dependency_graph = data.get('dependency_graph', {})

    if not dependency_graph:
        # No graph available, return directly affected
        output = {
            'transitive_affected': affected_files,
            'confidence': 'low',
            'note': 'No dependency graph available. Recommend full test suite.'
        }
    else:
        transitive = walk_graph(affected_files, dependency_graph)
        output = {
            'transitive_affected': sorted(list(transitive)),
            'direct_count': len(affected_files),
            'transitive_count': len(transitive),
            'confidence': 'high'
        }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: Write scripts/test-selector.py**

```python
#!/usr/bin/env python3
"""Select regression tests to run based on impact analysis and risk.

Usage: echo '{"affected_modules": [...], "risk_score": {...}, "test_catalog": {...}}' | python test-selector.py
Output: JSON with prioritized test selection.
"""

import json
import sys
from typing import Optional


def prioritize_tests(
    affected_modules: list,
    test_catalog: dict,
    risk_score: Optional[dict] = None
) -> dict:
    """Prioritize tests based on affected modules and risk."""

    selected = []
    skipped = []
    total_estimated_time = 0

    # Critical path tests (always run)
    critical_patterns = ['auth', 'payment', 'security', 'policy']
    critical_tests = [
        t for t in test_catalog.get('tests', [])
        if any(p in t.get('tags', []) for p in critical_patterns)
    ]

    risk_level = risk_score.get('risk_level', 'medium') if risk_score else 'medium'

    for test in test_catalog.get('tests', []):
        test_id = test.get('id')
        test_module = test.get('module', '')
        test_time = test.get('estimated_time_ms', 1000)
        tags = test.get('tags', [])

        # Always include critical path tests
        if any(t in tags for t in critical_patterns):
            selected.append(test)
            total_estimated_time += test_time
            continue

        # Include tests for affected modules
        if test_module in affected_modules or any(
            test_module.startswith(m) for m in affected_modules
        ):
            selected.append(test)
            total_estimated_time += test_time
            continue

        # For critical/high risk, add related smoke tests
        if risk_level in ('critical', 'high'):
            if 'smoke' in tags:
                selected.append(test)
                total_estimated_time += test_time
                continue

        # Everything else gets skipped
        skipped.append({
            'id': test_id,
            'module': test_module,
            'reason': 'not affected by change'
        })

    # If total time is high, recommend sampling
    confidence = 'high'
    note = None
    if total_estimated_time > 15 * 60 * 1000:  # >15 min
        confidence = 'medium'
        note = f"Estimated time {total_estimated_time / 1000 / 60:.1f} min. Consider sampling or parallel execution."

    if risk_level == 'low' and not affected_modules:
        confidence = 'low'
        note = 'No affected modules detected. Recommend full regression suite.'

    return {
        'selected_tests': [{'id': t.get('id'), 'module': t.get('module')} for t in selected],
        'skipped_tests': skipped,
        'total_tests': len(test_catalog.get('tests', [])),
        'selected_count': len(selected),
        'estimated_time_ms': total_estimated_time,
        'estimated_time_min': round(total_estimated_time / 1000 / 60, 1),
        'confidence': confidence,
        'note': note,
        'risk_level': risk_level
    }


def main():
    data = json.load(sys.stdin)
    affected_modules = data.get('transitive_affected', data.get('directly_affected_files', []))
    test_catalog = data.get('test_catalog', {})
    risk_score = data.get('risk_score')

    result = prioritize_tests(affected_modules, test_catalog, risk_score)

    json.dump(result, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
```

- [ ] **Step 5: Write references/regression-strategies.md**

```markdown
# Regression Testing Strategies — Reference

## Strategy Selection by Risk

### Low Risk (score 0-24)

**Approach:** Minimal subset
- Only tests for directly affected modules
- Skip smoke/integration tests
- Est. time: <5 min

**When applicable:**
- Small bug fix in isolated utility
- Typo/comment fix
- Single-module feature addition

### Medium Risk (score 25-49)

**Approach:** Smart selection
- Affected modules + direct dependents
- Smoke test suite for system health
- Platform-specific tests if UI changes
- Est. time: 5-15 min

**When applicable:**
- Cross-module feature
- API endpoint change
- Database schema change (non-structural)

### High Risk (score 50-74)

**Approach:** Comprehensive
- Full transitive dependency chain
- Full smoke test suite
- All platform-specific test suites
- Security/auth smoke tests even if unaffected
- Est. time: 15-30 min

**When applicable:**
- Authentication/authorization change
- Dependency upgrade
- Database structural change
- Shared infrastructure modification

### Critical Risk (score 75-100)

**Approach:** Full regression
- Run all tests
- Can parallelize to reduce wall-clock time
- Est. time: 30+ min (60+ parallel)

**When applicable:**
- Payment/billing system change
- Security-critical module
- Policy approval/underwriting change
- Framework/library upgrade

## Test Selection Heuristics

### By File Pattern

```
src/auth/**           → Always include (auth tests critical)
src/payment/**        → Always include
src/policy/**         → Always include if risk ≥ high
src/api/**            → Include affected + smoke tests
src/utils/**          → Include affected only (low risk)
src/__tests__/**      → Include matching src file
```

### By Naming Convention

```
*.critical.test.ts    → Always include
*.smoke.test.ts       → Include for risk ≥ medium
*.integration.test.ts → Include for risk ≥ medium
*.unit.test.ts        → Include only if directly affected
*.e2e.test.ts         → Include for risk ≥ high
```

### Shared Infrastructure Changes

Always run full regression if changes touch:
- `package.json` (deps)
- `tsconfig.json` (compilation)
- `.env.example` (config schema)
- `src/middleware/**` (global middleware)
- `src/config/**` (configuration)
- Database migrations

**Reason:** Config/middleware changes affect all modules transitively.

## Confidence Levels

### High Confidence

✓ Full dependency graph available (from build system or Knowledge Base)
✓ Complete test catalog with accurate file mappings
✓ Risk score computed from change scope + component criticality + defect history

**Action:** Run selected tests only; approve if pass.

### Medium Confidence

⚠ Partial dependency graph (heuristic file matching)
⚠ Some test files may be missing from catalog
⚠ Risk score lacks defect history

**Action:** Run selection + smoke test suite; require manual review if smoke fails.

### Low Confidence

✗ No dependency graph available
✗ Test mappings are filename-based guesses
✗ Large change or unknown risk

**Action:** Warn and recommend full test suite; provide justification for selection.

## Best Practices

1. **Version your dependency graph:** Track imports/dependencies per commit for regression accuracy
2. **Maintain test catalog metadata:** Document test type (unit/integration/e2e), module, tags, estimated time
3. **Baseline smoke suite:** Define minimal smoke tests that must always pass
4. **Critical path coverage:** Ensure auth, payment, policy tests are always included for their changes
5. **Review skipped tests:** Periodically audit skipped tests to validate heuristics
6. **Monitor test reliability:** Track flaky tests separately from selection logic
7. **Parallel execution:** For risk ≥ high, parallelize to maintain reasonable CI time
```

- [ ] **Step 6: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "sr-tc-001"
    description: "Narrow change: single utility function"
    input:
      git_diff: |
        diff --git a/src/utils/validators.ts
        +++ b/src/utils/validators.ts
        +export function isValidEmail(email: string): boolean {
        +  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        +}
      test_catalog:
        tests:
          - id: "test-1"
            module: "src/utils/validators"
            tags: ["unit"]
            estimated_time_ms: 500
          - id: "test-2"
            module: "src/api"
            tags: ["smoke"]
            estimated_time_ms: 5000
      risk_score:
        risk_level: "low"
    expected:
      selected_count: 1
      confidence: "high"
      includes:
        - "test-1"
      skips:
        - "test-2"

  - id: "sr-tc-002"
    description: "Broad infrastructure change: dependency upgrade"
    input:
      git_diff: |
        diff --git a/package.json
        +++ b/package.json
        -"express": "4.17.1"
        +"express": "4.18.0"
      test_catalog:
        tests:
          - id: "test-smoke"
            module: "all"
            tags: ["smoke"]
            estimated_time_ms: 10000
          - id: "test-api"
            module: "src/api"
            tags: ["integration"]
            estimated_time_ms: 5000
          - id: "test-auth"
            module: "src/auth"
            tags: ["critical"]
            estimated_time_ms: 3000
      risk_score:
        risk_level: "high"
    expected:
      selected_count_gte: 2
      confidence: "medium"
      includes:
        - "test-smoke"
        - "test-auth"

  - id: "sr-tc-003"
    description: "Cross-module: payment processor change"
    input:
      git_diff: |
        diff --git a/src/payment/processor.ts
      test_catalog:
        tests:
          - id: "payment-unit"
            module: "src/payment"
            tags: ["unit"]
          - id: "order-integration"
            module: "src/order"
            tags: ["integration"]
          - id: "api-smoke"
            module: "src/api"
            tags: ["smoke"]
      risk_score:
        risk_level: "critical"
    expected:
      selected_count_gte: 2
      confidence: "high"
      includes:
        - "payment-unit"
        - "api-smoke"
```

- [ ] **Step 7: Write evals/assertions.yaml**

```yaml
assertions:
  - test_id: "sr-tc-001"
    checks:
      - path: "selected_count"
        type: "equals"
        value: 1
      - path: "confidence"
        type: "equals"
        value: "high"
      - path: "selected_tests[0].id"
        type: "equals"
        value: "test-1"
      - path: "estimated_time_min"
        type: "number_lte"
        value: 5

  - test_id: "sr-tc-002"
    checks:
      - path: "selected_count"
        type: "number_gte"
        value: 2
      - path: "confidence"
        type: "equals"
        value: "medium"
      - path: "selected_tests"
        type: "array_contains_id"
        value: "test-auth"

  - test_id: "sr-tc-003"
    checks:
      - path: "selected_count"
        type: "number_gte"
        value: 2
      - path: "confidence"
        type: "equals"
        value: "high"
      - path: "selected_tests"
        type: "array_contains_id"
        value: "payment-unit"
```

- [ ] **Step 8: Commit selecting-regressions skill**

```bash
git add .github/skills/qa/selecting-regressions/
git commit -m "feat(qa-skills): implement selecting-regressions P3 skill

Intelligent test selection based on change impact analysis and risk scoring.

Scripts:
- change-impact-analyzer.py: Direct impact from diff (files → test files)
- dependency-graph-walker.py: Transitive dependencies (graceful degradation)
- test-selector.py: Prioritize tests by risk level and module affinity

References:
- regression-strategies.md: Strategy selection by risk, heuristics, confidence levels

Evals: 3 test cases (narrow, broad infra, cross-module)."
```

---

## Task 5: healing-broken-tests skill

Auto-repair tests broken by intentional code changes (locators, expected values).

**Files:**
- Create: `.github/skills/qa/healing-broken-tests/SKILL.md`
- Create: `.github/skills/qa/healing-broken-tests/scripts/failure-pattern-matcher.py`
- Create: `.github/skills/qa/healing-broken-tests/scripts/locator-updater.py`
- Create: `.github/skills/qa/healing-broken-tests/scripts/diff-correlator.py`
- Create: `.github/skills/qa/healing-broken-tests/references/common-breakage-patterns.md`
- Create: `.github/skills/qa/healing-broken-tests/references/auto-fix-strategies.md`
- Create: `.github/skills/qa/healing-broken-tests/evals/test-prompts.yaml`
- Create: `.github/skills/qa/healing-broken-tests/evals/assertions.yaml`

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: healing-broken-tests
version: "1.0.0"
description: "Auto-repair tests broken by intentional code changes — update selectors, fixtures, expected values"
category: execution
phase: post-coding
platforms: ["all"]
dependencies: ["classifying-test-failures"]
soft_dependencies: ["generating-qa-report"]
input_schema:
  - name: "broken_tests"
    type: "array"
    required: true
  - name: "git_diff"
    type: "string"
    required: true
  - name: "intent"
    type: "string"
    required: true
    description: "Intended change description (from issue/PR)"
output_schema:
  - name: "healed_tests"
    type: "array"
  - name: "unhealed_tests"
    type: "array"
  - name: "patches"
    type: "array"
  - name: "confidence"
    type: "string"
    description: "high (locator) | medium (expected value) | low (logic)"
---

# healing-broken-tests

Auto-repair tests broken by intentional code changes. Categorizes breakage type and applies high-confidence fixes only.

## When to Use

Invoke after test failures classified but before reporting to QA gates. Fixes broken tests caused by intentional changes so they don't block the quality gate.

## Instructions

1. Receive list of failing tests from `classifying-test-failures`
2. Run `scripts/failure-pattern-matcher.py` on failure logs
   - Categorize by breakage type: locator | expected_value | logic
3. Run `scripts/diff-correlator.py`
   - Map each failure to specific diff hunks
   - Identify if breakage was intentional (related to PR goal)
4. For high-confidence failures:
   - Run `scripts/locator-updater.py` → find new selector in updated code
   - Update assertion values from diff
5. Apply patches to test files
6. Re-run healed tests to verify they pass
7. Output `healed_tests` (now passing) and `unhealed_tests` (flagged for human review)

## Breakage Types and Repair Strategy

| Type | Detection | Repair | Confidence |
|------|-----------|--------|------------|
| Locator change | "element not found" + Element selector in diff changed | Find new selector in updated code | High |
| Expected value | "expected X got Y" + Return value changed intentionally | Update assertion to match new intentional behavior | Medium |
| Logic change | TypeError, AttributeError, assertion logic broken | Flag for human review — needs intent understanding | Low |

## Confidence Levels

- **High:** Locator updates are mechanical; apply automatically if healed test passes
- **Medium:** Expected value updates require Intent validation; apply with human review
- **Low:** Logic changes; always flag for human review. Never auto-heal.

## Consumers

- CI/CD system — re-run healed tests to verify
- `analyzing-defects` — ingests healed vs unhealed pattern data
- QA report — counts healed tests as resolved, unhealed as true failures

## Guardrails

- Never auto-heal a test detecting a real bug
- High-confidence (locator) can auto-apply if healed test passes
- Medium/low require human review
- Never change test logic (conditionals, loops)
- Only update data: selectors, expected values, fixtures
- If patch fails re-run, report as unhealed
```

- [ ] **Step 2: Write scripts/failure-pattern-matcher.py**

```python
#!/usr/bin/env python3
"""Categorize test failures by breakage type.

Usage: echo '{"failures": [...]}' | python failure-pattern-matcher.py
Output: JSON with categorized failures.
"""

import json
import sys
import re


def categorize_failure(failure_log: str) -> dict:
    """Classify failure into locator|expected_value|logic."""
    log_lower = failure_log.lower()

    # Locator failures: element not found, selector not matching
    if any(x in log_lower for x in [
        'element not found', 'no element matching', 'selector',
        'cannot find', 'element does not exist', 'visibility'
    ]):
        return {
            'type': 'locator',
            'confidence': 'high',
            'pattern': next(
                (x for x in ['element not found', 'selector', 'visibility']
                 if x in log_lower), 'element_not_found'
            )
        }

    # Expected value failures: assertion mismatch, value changed
    if any(x in log_lower for x in [
        'expected', 'assertion', 'equal', 'tobe', 'toequal',
        'got', 'received', 'but was'
    ]):
        return {
            'type': 'expected_value',
            'confidence': 'medium',
            'pattern': 'assertion_mismatch'
        }

    # Logic failures: errors, exceptions, type errors
    if any(x in log_lower for x in [
        'error', 'exception', 'typeerror', 'attributeerror',
        'referenceerror', 'syntaxerror', 'undefined', 'null'
    ]):
        return {
            'type': 'logic',
            'confidence': 'low',
            'pattern': 'runtime_error'
        }

    return {
        'type': 'unknown',
        'confidence': 'low',
        'pattern': 'unknown'
    }


def main():
    data = json.load(sys.stdin)
    failures = data.get('failures', [])

    categorized = []
    for failure in failures:
        test_id = failure.get('test_id', '?')
        log = failure.get('log', '')

        category = categorize_failure(log)
        categorized.append({
            'test_id': test_id,
            'type': category['type'],
            'confidence': category['confidence'],
            'pattern': category['pattern']
        })

    output = {
        'failures': categorized,
        'summary': {
            'locator': sum(1 for f in categorized if f['type'] == 'locator'),
            'expected_value': sum(1 for f in categorized if f['type'] == 'expected_value'),
            'logic': sum(1 for f in categorized if f['type'] == 'logic')
        }
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
```

- [ ] **Step 3: Write scripts/locator-updater.py**

```python
#!/usr/bin/env python3
"""Find new selector in updated code and suggest locator fix.

Usage: echo '{"test_selector": "...", "diff": "...", "framework": "playwright"}' | python locator-updater.py
Output: JSON with suggested new selector.
"""

import json
import sys
import re


def extract_selectors_from_code(code: str, framework: str = 'playwright') -> list:
    """Extract selectors from implementation code."""
    selectors = []

    if framework in ('playwright', 'js', 'typescript'):
        # CSS selectors, data-testid, etc.
        patterns = [
            r"data-testid=['\"]([^'\"]+)['\"]",
            r"querySelector\(['\"]([^'\"]+)['\"]\)",
            r"css: ['\"]([^'\"]+)['\"]",
            r"getByTestId\(['\"]([^'\"]+)['\"]\)",
        ]
    elif framework in ('selenium', 'py', 'python'):
        patterns = [
            r"By\.CSS_SELECTOR, ['\"]([^'\"]+)['\"]",
            r"By\.ID, ['\"]([^'\"]+)['\"]",
            r"By\.CLASS_NAME, ['\"]([^'\"]+)['\"]",
        ]
    else:
        patterns = []

    for pattern in patterns:
        for match in re.finditer(pattern, code):
            selectors.append(match.group(1))

    return list(set(selectors))


def find_new_selector(diff: str, old_selector: str, framework: str) -> str:
    """Find new selector in diff that replaced old one."""
    # Extract added lines (with +)
    added_lines = [
        line[1:] for line in diff.split('\n')
        if line.startswith('+') and not line.startswith('+++')
    ]
    added_code = '\n'.join(added_lines)

    # Find similar new selectors
    new_selectors = extract_selectors_from_code(added_code, framework)

    if not new_selectors:
        return None

    # Return most likely match (first one, or fuzzy match to old)
    # Simple heuristic: prefer selectors that share words with old
    old_words = set(re.findall(r'\w+', old_selector.lower()))

    best_match = None
    best_score = -1

    for selector in new_selectors:
        new_words = set(re.findall(r'\w+', selector.lower()))
        overlap = len(old_words & new_words)
        if overlap > best_score:
            best_match = selector
            best_score = overlap

    return best_match if best_score > 0 else new_selectors[0]


def main():
    data = json.load(sys.stdin)
    test_selector = data.get('test_selector', '')
    diff = data.get('diff', '')
    framework = data.get('framework', 'playwright')

    if not test_selector or not diff:
        json.dump({'error': 'Missing selector or diff'}, sys.stdout)
        return

    new_selector = find_new_selector(diff, test_selector, framework)

    output = {
        'old_selector': test_selector,
        'new_selector': new_selector,
        'confidence': 'high' if new_selector else 'low'
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: Write scripts/diff-correlator.py**

```python
#!/usr/bin/env python3
"""Map failures to specific diff hunks to identify intent.

Usage: echo '{"failures": [...], "diff": "..."}' | python diff-correlator.py
Output: JSON mapping failures to diff hunks and intent.
"""

import json
import sys
import re


def extract_hunks(diff: str) -> list:
    """Extract diff hunks with line numbers."""
    hunks = []
    current_hunk = None

    for line in diff.split('\n'):
        if line.startswith('@@'):
            match = re.search(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@', line)
            if match:
                current_hunk = {
                    'old_start': int(match.group(1)),
                    'old_count': int(match.group(2)),
                    'new_start': int(match.group(3)),
                    'new_count': int(match.group(4)),
                    'changes': []
                }
                hunks.append(current_hunk)
        elif current_hunk and line.startswith(('+', '-')):
            current_hunk['changes'].append(line)

    return hunks


def identify_intent(hunks: list) -> str:
    """Infer intent from diff hunks."""
    all_changes = '\n'.join(
        change for hunk in hunks for change in hunk['changes']
    )

    keywords = {
        'refactor': r'(refactor|extract|consolidate|reorgan)',
        'rename': r'(rename|renam)',
        'ui_change': r'(css|class|id|selector|data-testid)',
        'api_change': r'(endpoint|route|parameter|return)',
        'behavior_change': r'(logic|calculation|validation)',
    }

    scores = {}
    for intent, pattern in keywords.items():
        if re.search(pattern, all_changes.lower()):
            scores[intent] = 1

    return max(scores, key=scores.get) if scores else 'unknown'


def main():
    data = json.load(sys.stdin)
    failures = data.get('failures', [])
    diff = data.get('diff', '')

    hunks = extract_hunks(diff)
    intent = identify_intent(hunks)

    correlated = []
    for failure in failures:
        correlated.append({
            'test_id': failure.get('test_id'),
            'type': failure.get('type'),
            'related_hunks': len(hunks),
            'inferred_intent': intent,
            'is_intentional': 'yes'
        })

    output = {
        'correlated_failures': correlated,
        'inferred_intent': intent,
        'hunk_count': len(hunks)
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
```

- [ ] **Step 5: Write references/common-breakage-patterns.md**

```markdown
# Common Test Breakage Patterns — Reference

Quick patterns for failure categorization.

## Locator Breakage (High Confidence)

**Symptoms:**
- "element not found"
- "selector does not match"
- "element is not visible"
- "cannot locate element"

**Root cause:** Element selector changed in implementation (intentional refactor).

**Repair:**
- Extract new selector from diff
- Update test locator to new selector
- Re-run test to verify

**Example:**
```typescript
// Implementation: changed from className to data-testid
- <button className="submit-btn">
+ <button data-testid="submit-btn">

// Test: update locator
- await page.click('.submit-btn')
+ await page.click('[data-testid="submit-btn"]')
```

## Expected Value Breakage (Medium Confidence)

**Symptoms:**
- "expected X, got Y"
- "AssertionError: value mismatch"
- "toBe() failed"
- "Expected: true, Received: false"

**Root cause:** Return value or behavior changed intentionally (feature enhancement, calculation fix).

**Repair:**
- Verify change was intentional (mentioned in PR description/issue)
- Update expected value in test assertion
- Re-run test to verify

**Example:**
```typescript
// Implementation: price calculation changed
- return amount * 1.1;  // 10% markup
+ return amount * 1.2;  // 20% markup (new policy)

// Test: update assertion
- expect(calculateTotal(100)).toBe(110);
+ expect(calculateTotal(100)).toBe(120);
```

## Logic Breakage (Low Confidence)

**Symptoms:**
- TypeError, AttributeError, ReferenceError
- Null/undefined reference
- Exception thrown
- Syntax error in test

**Root cause:** Implementation change broke test logic, not just data.

**Repair:**
- Requires understanding of intent
- May need test logic rewrite, not just data update
- Flag for human review

**Never auto-heal logic breakage.**

## Flaky Test (Not a Breakage)

**Symptoms:**
- Intermittent failure
- Passes on retry
- "timeout waiting for element"
- "element stale reference"

**Root cause:** Test timing issue, not implementation change.

**Action:**
- Not a breakage; handled by `classifying-test-failures`
- Skip healing logic
```

- [ ] **Step 6: Write references/auto-fix-strategies.md**

```markdown
# Auto-Fix Strategies — Reference

When and how to auto-apply healing patches.

## Locator Fix (High Confidence — Auto-Apply)

**Confidence threshold:** high

**When to apply:** Always, if healed test passes.

**Verification:**
1. Find new selector in code
2. Apply patch to test file
3. Run healed test
4. Verify test passes
5. Commit patch

**Example patch:**
```diff
diff --git a/src/__tests__/login.test.ts
- expect(page.locator('.submit-btn')).toBeVisible();
+ expect(page.locator('[data-testid="submit-btn"]')).toBeVisible();
```

## Expected Value Fix (Medium Confidence — Require Review)

**Confidence threshold:** medium

**When to apply:** With human review in PR comment.

**Verification:**
1. Extract old and new expected values from diff
2. Generate patch
3. Add PR comment explaining change
4. Wait for author approval
5. Apply and re-run

**PR comment template:**
```
🤖 Healing broken test: [test_id]

The expected value changed due to your implementation update:
- Old: `110`
- New: `120`

This change is intentional per your PR. Suggestion:
\`\`\`diff
- expect(result).toBe(110);
+ expect(result).toBe(120);
\`\`\`

Approve with 👍 to auto-heal, or manually fix if different.
```

## Logic Fix (Low Confidence — Human Review Only)

**Confidence threshold:** low

**When to apply:** Never auto-apply.

**Action:**
1. Flag test in `unhealed_tests`
2. Add comment explaining breakage
3. Assign to author for manual fix
4. Block merge until fixed

**Example comment:**
```
⚠️ Cannot auto-heal [test_id]:
- Breakage type: logic (TypeError)
- Message: "Cannot read property 'map' of undefined"
- Confidence: low

The implementation change broke test logic, not just data.
Please review and fix manually.
```

## No-Heal Rules

**Never auto-apply:**
- Logic changes (type errors, exceptions, assertion logic)
- Tests that verify bugs/security issues
- Tests for error handling
- Concurrent/async timing tests

**Always require human review for:**
- Multi-line changes
- Changes to test flow (control flow statements)
- Behavioral changes (not just data)
```

- [ ] **Step 7: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "hbt-tc-001"
    description: "Locator breakage: high confidence auto-heal"
    input:
      broken_tests:
        - test_id: "login-submit"
          error: "element not found: .submit-btn"
      git_diff: |
        diff --git a/src/LoginForm.tsx
        - <button className="submit-btn">
        + <button data-testid="submit-btn">
      intent: "Refactor button selector to data-testid"
    expected:
      healed_count: 1
      unhealed_count: 0
      confidence: "high"
      patches:
        - test: "login-submit"
          old: ".submit-btn"
          new: "submit-btn"

  - id: "hbt-tc-002"
    description: "Expected value breakage: medium confidence"
    input:
      broken_tests:
        - test_id: "price-calc"
          error: "expected 110, got 120"
      git_diff: |
        diff --git a/src/pricing.ts
        - return amount * 1.1;
        + return amount * 1.2;
      intent: "Update markup policy from 10% to 20%"
    expected:
      healed_count: 0
      unhealed_count: 1
      confidence: "medium"
      requires_review: true

  - id: "hbt-tc-003"
    description: "Logic breakage: low confidence, human review only"
    input:
      broken_tests:
        - test_id: "order-filter"
          error: "TypeError: Cannot read property 'map' of undefined"
      git_diff: |
        diff --git a/src/OrderService.ts
        - getOrders() { return this.orders.map(...); }
        + async getOrders() { return this.fetchRemote(); }
      intent: "Refactor to async remote fetch"
    expected:
      healed_count: 0
      unhealed_count: 1
      confidence: "low"
      requires_review: true
```

- [ ] **Step 8: Write evals/assertions.yaml**

```yaml
assertions:
  - test_id: "hbt-tc-001"
    checks:
      - path: "healed_tests"
        type: "array_length"
        value: 1
      - path: "unhealed_tests"
        type: "array_length"
        value: 0
      - path: "confidence"
        type: "equals"
        value: "high"
      - path: "patches[0].new"
        type: "contains"
        value: "submit-btn"

  - test_id: "hbt-tc-002"
    checks:
      - path: "healed_tests"
        type: "array_length"
        value: 0
      - path: "unhealed_tests"
        type: "array_length"
        value: 1
      - path: "confidence"
        type: "equals"
        value: "medium"

  - test_id: "hbt-tc-003"
    checks:
      - path: "unhealed_tests"
        type: "array_length"
        value: 1
      - path: "confidence"
        type: "equals"
        value: "low"
```

- [ ] **Step 9: Commit healing-broken-tests skill**

```bash
git add .github/skills/qa/healing-broken-tests/
git commit -m "feat(qa-skills): implement healing-broken-tests P3 skill

Auto-repair tests broken by intentional code changes.

Categorizes failures: locator (high), expected_value (medium), logic (low).
Auto-applies high-confidence locator fixes only.
Flags medium/low for human review.

Scripts:
- failure-pattern-matcher.py: Categorize failures by type
- locator-updater.py: Find new selector in updated code
- diff-correlator.py: Map failures to hunks and infer intent

References:
- common-breakage-patterns.md: Breakage type patterns and examples
- auto-fix-strategies.md: When/how to auto-apply vs require review

Evals: 3 test cases (locator high, expected medium, logic low)."
```

---

## Task 6: analyzing-defects skill

Root cause analysis and Knowledge Base updates (proposed, human-reviewed).

**Files:**
- Create: `.github/skills/qa/analyzing-defects/SKILL.md`
- Create: `.github/skills/qa/analyzing-defects/scripts/root-cause-classifier.py`
- Create: `.github/skills/qa/analyzing-defects/scripts/pattern-detector.py`
- Create: `.github/skills/qa/analyzing-defects/scripts/knowledge-base-writer.py`
- Create: `.github/skills/qa/analyzing-defects/references/defect-taxonomy.md`
- Create: `.github/skills/qa/analyzing-defects/references/root-cause-categories.md`
- Create: `.github/skills/qa/analyzing-defects/evals/test-prompts.yaml`
- Create: `.github/skills/qa/analyzing-defects/evals/assertions.yaml`

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: analyzing-defects
version: "1.1.0"
description: "Analyze defect root causes, identify patterns, feed insights into Knowledge Base"
category: analysis
phase: post-coding
platforms: ["all"]
dependencies: ["classifying-test-failures", "generating-qa-report", "healing-broken-tests"]
input_schema:
  - name: "defect_data"
    type: "array"
    required: true
    description: "Defect records: issue ID, root cause, component, resolution"
  - name: "time_window"
    type: "string"
    required: false
    description: "30d | 90d | all. Default: 90d."
  - name: "scope"
    type: "string"
    required: false
    description: "team | component | project | organization"
output_schema:
  - name: "patterns"
    type: "array"
  - name: "root_cause_distribution"
    type: "object"
    description: "logic | integration | data | config | concurrency"
  - name: "hotspots"
    type: "array"
    description: "Components with disproportionate defect density"
  - name: "recommendations"
    type: "array"
  - name: "knowledge_base_updates"
    type: "array"
    description: "Proposed updates for human review"
---

# analyzing-defects

Analyze root causes of test failures and defects. Identify patterns and hotspots. Propose Knowledge Base updates for human review.

## When to Use

Invoke after `classifying-test-failures`, `healing-broken-tests`, and `generating-qa-report` complete. Aggregates defect data to drive organizational learning.

## Instructions

1. Receive failure records from `classifying-test-failures` and healed/unhealed from `healing-broken-tests`
2. Run `scripts/root-cause-classifier.py`
   - Categorize each defect: logic | integration | data | config | concurrency
3. Run `scripts/pattern-detector.py`
   - Time-series analysis (freq by root cause, trend)
   - Component clustering (which components have defects)
   - Pattern recognition (recurring issues)
4. Identify hotspots (components with defect density > org average)
5. Generate recommendations:
   - Increase test coverage for hotspot components
   - Architectural changes (if pattern suggests design flaw)
   - Process improvements (if pattern suggests workflow issue)
6. Run `scripts/knowledge-base-writer.py`
   - Format proposals for Knowledge Base (patterns, hotspots, recommendations)
   - Always proposed for human review, never auto-committed
7. Output knowledge_base_updates for review

## Root Cause Categories

| Category | Examples | Prevention |
|----------|----------|-----------|
| Logic | Off-by-one, null handling, state management | Stronger typing, peer review |
| Integration | API contract breaking, async timing, dependency mismatch | Contract testing, integration tests |
| Data | Missing validation, schema mismatch, bad state | Test data factories, schema validation |
| Config | Wrong env vars, hardcoded values, missing settings | Config validation, environment tests |
| Concurrency | Race conditions, deadlock, stale references | Proper locking, async/await patterns |

## Pattern Examples

- **"Password validation never rejects special chars"** → Pattern: validation bypass (logic)
- **"Payment API breaks on amount > 1000"** → Pattern: numeric boundary (data)
- **"Tests pass locally, fail on CI"** → Pattern: environment difference (config)
- **"Flaky tests in parallel execution"** → Pattern: shared state (concurrency)

## Hotspot Identification

A hotspot is a component with defect density significantly above org average.

**Calculation:**
```
org_avg_density = total_defects / total_components
component_density = component_defects / component_age_days
is_hotspot = component_density > (org_avg_density * 1.5)
```

## Guardrails

- Patterns require ≥5 data points for statistical significance
- Recommendations must be specific and actionable
- Never commit Knowledge Base updates; always propose for human review
- Sanitize sensitive data before writing (remove user IDs, passwords, PII)
- Distinguish between local team and org-level patterns
```

- [ ] **Step 2: Write scripts/root-cause-classifier.py**

```python
#!/usr/bin/env python3
"""Classify defects by root cause category.

Usage: echo '{"failures": [...]}' | python root-cause-classifier.py
Output: JSON with classified defects.
"""

import json
import sys
import re


CATEGORY_PATTERNS = {
    'logic': [
        r'(null|undefined|none)',
        r'(off.by.one|boundary|edge.case)',
        r'(state.management|mutation)',
        r'(conditional|if.else)',
    ],
    'integration': [
        r'(api|endpoint|contract)',
        r'(async|promise|timeout)',
        r'(dependency|import)',
        r'(mock|stub)',
    ],
    'data': [
        r'(validation|sanitiz)',
        r'(schema|format)',
        r'(type|casting)',
        r'(boundary|range)',
    ],
    'config': [
        r'(environment|env)',
        r'(config|setting)',
        r'(constant|hardcoded)',
    ],
    'concurrency': [
        r'(race|concurrent)',
        r'(lock|mutex)',
        r'(stale|reference)',
        r'(parallel)',
    ],
}


def classify_defect(error_log: str, component: str = '') -> str:
    """Classify defect into category."""
    text = (error_log + ' ' + component).lower()

    scores = {}
    for category, patterns in CATEGORY_PATTERNS.items():
        matches = sum(1 for p in patterns if re.search(p, text))
        scores[category] = matches

    if not scores or max(scores.values()) == 0:
        return 'unknown'

    return max(scores, key=scores.get)


def main():
    data = json.load(sys.stdin)
    failures = data.get('failures', [])

    classified = []
    for failure in failures:
        error = failure.get('error', '')
        component = failure.get('component', '')
        category = classify_defect(error, component)

        classified.append({
            'defect_id': failure.get('id', failure.get('test_id')),
            'component': component,
            'root_cause': category,
            'error_snippet': error[:100]
        })

    summary = {}
    for defect in classified:
        cause = defect['root_cause']
        summary[cause] = summary.get(cause, 0) + 1

    output = {
        'classified_defects': classified,
        'root_cause_distribution': summary,
        'total': len(classified)
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
```

- [ ] **Step 3: Write scripts/pattern-detector.py**

```python
#!/usr/bin/env python3
"""Detect recurring patterns in defects.

Usage: echo '{"classified_defects": [...], "time_window": "90d"}' | python pattern-detector.py
Output: JSON with patterns and hotspots.
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta


def detect_patterns(defects: list) -> list:
    """Identify recurring patterns across defects."""
    component_causes = defaultdict(lambda: defaultdict(int))

    for defect in defects:
        component = defect.get('component', 'unknown')
        cause = defect.get('root_cause', 'unknown')
        component_causes[component][cause] += 1

    patterns = []
    for component, causes in component_causes.items():
        total = sum(causes.values())
        if total >= 5:  # Require ≥5 data points
            dominant_cause = max(causes, key=causes.get)
            patterns.append({
                'component': component,
                'root_cause': dominant_cause,
                'frequency': total,
                'confidence': min(causes[dominant_cause] / total, 1.0)
            })

    return sorted(patterns, key=lambda x: x['frequency'], reverse=True)


def identify_hotspots(defects: list) -> list:
    """Identify components with high defect density."""
    component_defects = defaultdict(int)

    for defect in defects:
        component = defect.get('component', 'unknown')
        component_defects[component] += 1

    if not component_defects:
        return []

    avg = sum(component_defects.values()) / len(component_defects)

    hotspots = [
        {
            'component': comp,
            'defect_count': count,
            'density_multiplier': round(count / avg, 2)
        }
        for comp, count in component_defects.items()
        if count > (avg * 1.5)
    ]

    return sorted(hotspots, key=lambda x: x['defect_count'], reverse=True)


def main():
    data = json.load(sys.stdin)
    defects = data.get('classified_defects', [])

    patterns = detect_patterns(defects)
    hotspots = identify_hotspots(defects)

    output = {
        'patterns': patterns,
        'hotspots': hotspots,
        'pattern_count': len(patterns),
        'hotspot_count': len(hotspots),
        'defect_count': len(defects)
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: Write scripts/knowledge-base-writer.py**

```python
#!/usr/bin/env python3
"""Format pattern insights for Knowledge Base updates.

Usage: echo '{"patterns": [...], "hotspots": [...]}' | python knowledge-base-writer.py
Output: JSON with proposed Knowledge Base updates (for human review).
"""

import json
import sys
from datetime import datetime


def generate_updates(patterns: list, hotspots: list) -> list:
    """Generate proposed Knowledge Base entries."""
    updates = []

    # Pattern entries
    for pattern in patterns:
        updates.append({
            'type': 'pattern',
            'component': pattern['component'],
            'title': f"Recurring {pattern['root_cause']} issues in {pattern['component']}",
            'description': f"Detected {pattern['frequency']} instances of {pattern['root_cause']} failures",
            'frequency': pattern['frequency'],
            'recommendation': generate_recommendation(pattern['root_cause']),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'pending_review'
        })

    # Hotspot entries
    for hotspot in hotspots:
        updates.append({
            'type': 'hotspot',
            'component': hotspot['component'],
            'title': f"{hotspot['component']} is a defect hotspot",
            'description': f"Defect density {hotspot['density_multiplier']}x org average ({hotspot['defect_count']} defects)",
            'density': hotspot['density_multiplier'],
            'recommendation': "Increase test coverage, review architecture, consider refactoring",
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'pending_review'
        })

    return updates


def generate_recommendation(root_cause: str) -> str:
    """Generate specific recommendation based on root cause."""
    recommendations = {
        'logic': "Review implementation logic, add boundary testing, improve code review for this component",
        'integration': "Add integration tests, verify API contracts, test async timing",
        'data': "Strengthen validation rules, add schema tests, expand test data coverage",
        'config': "Add environment-specific tests, centralize configuration, validate on startup",
        'concurrency': "Add concurrency tests, review locking strategy, test under load",
    }
    return recommendations.get(root_cause, "Review and improve test coverage for this component")


def main():
    data = json.load(sys.stdin)
    patterns = data.get('patterns', [])
    hotspots = data.get('hotspots', [])

    updates = generate_updates(patterns, hotspots)

    output = {
        'knowledge_base_updates': updates,
        'update_count': len(updates),
        'note': 'All updates require human review before committing to Knowledge Base',
        'status': 'pending_review'
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
```

- [ ] **Step 5: Write references/defect-taxonomy.md**

```markdown
# Defect Taxonomy — Reference

Classification system for test failures and production defects.

## Root Cause Categories

### Logic Errors

**Definition:** Bugs in implementation logic (algorithms, conditionals, state management).

**Examples:**
- Off-by-one error in loop
- Null pointer dereference
- Incorrect conditional (if/else)
- State not updated correctly
- Missing edge case handling

**Indicators:**
- Test assertion fails with unexpected value
- Calculation incorrect
- Boundary conditions fail

**Prevention:**
- Type-safe languages + strict mode
- Comprehensive boundary value testing
- Peer code review
- Table-driven test cases

### Integration Errors

**Definition:** Bugs at module/service boundaries (API contracts, async patterns, dependencies).

**Examples:**
- API response format mismatch
- Async promise not awaited
- Missing dependency import
- Mock/stub not matching real behavior
- Service initialization order

**Indicators:**
- Works in isolation, fails in integration
- Timing-dependent failures
- Contract violation messages
- Import/dependency errors

**Prevention:**
- Contract testing (Pact, OpenAPI validation)
- Integration test coverage
- Async/await pattern enforcement
- Dependency injection

### Data Errors

**Definition:** Bugs in data handling (validation, transformation, schema mismatch).

**Examples:**
- Unvalidated user input
- Type mismatch (string vs number)
- Schema version mismatch
- Missing required field
- Invalid data range

**Indicators:**
- Data validation error
- Type assertion failure
- Schema mismatch messages
- Null/undefined where value expected

**Prevention:**
- Input validation at boundaries
- Strong typing (TypeScript, Python type hints)
- Schema validation (JSON Schema, Protobuf)
- Test data factories

### Configuration Errors

**Definition:** Bugs due to environment/runtime configuration.

**Examples:**
- Wrong environment variables
- Hardcoded values in code
- Missing configuration file
- Secrets exposed in code
- Version/compatibility mismatch

**Indicators:**
- Passes locally, fails on CI/production
- Environment-specific failure
- Configuration not found error
- Version incompatibility

**Prevention:**
- Externalize all configuration
- Environment validation on startup
- Secret management (vault, env vars)
- Compatibility testing across versions

### Concurrency Errors

**Definition:** Bugs in concurrent/parallel execution.

**Examples:**
- Race condition (timing-dependent)
- Deadlock
- Stale reference in async chain
- Improper locking
- Shared mutable state

**Indicators:**
- Non-deterministic failures (flaky)
- Failure only in parallel execution
- Stale reference error
- Timeout in deadlock

**Prevention:**
- Immutable data structures
- Proper synchronization primitives (locks, channels)
- Async/await over callbacks
- Race detector tools (go test -race)
```

- [ ] **Step 6: Write references/root-cause-categories.md**

```markdown
# Root Cause Categories — Reference

Detailed categorization for defect analysis and prevention.

## Category: Logic

**Severity:** High (fixes often require code changes)

**Sub-categories:**
- **Boundary logic:** Off-by-one, min/max handling
- **Conditional logic:** if/else conditions wrong
- **Loop logic:** Infinite loops, wrong iteration
- **State management:** State not initialized/updated/cleaned

**Example Detection:**
```
AssertionError: expected 11 but got 10  → Off-by-one
TypeError: Cannot read property 'x' of null  → Null handling
Expected true, got false  → Conditional logic
```

**Fix Pattern:**
```
1. Write failing test with correct expected value
2. Fix implementation logic
3. Verify test passes
4. Review similar patterns in codebase
```

## Category: Integration

**Severity:** Medium (fixes often require coordination)

**Sub-categories:**
- **API contract:** Request/response format mismatch
- **Async timing:** Promise not awaited, timeout
- **Dependency version:** API changed in upgrade
- **Mock/stub:** Test double doesn't match reality

**Example Detection:**
```
Response 404 for /users/:id  → API endpoint wrong
Promise not returned  → Async pattern
Test passes with mock, fails with real service  → Stub mismatch
```

**Fix Pattern:**
```
1. Add integration test with real (or more realistic) service
2. Update service call or mock
3. Verify contract with upstream service
4. Add contract test for future protection
```

## Category: Data

**Severity:** High (fixes often require careful validation)

**Sub-categories:**
- **Input validation:** User input not validated
- **Type mismatch:** String passed where number expected
- **Range violation:** Value outside acceptable bounds
- **Schema change:** Field missing or wrong type

**Example Detection:**
```
Invalid email format  → Validation failure
TypeError: str + int  → Type mismatch
Value must be 0-100  → Range violation
Unknown field 'phone'  → Schema mismatch
```

**Fix Pattern:**
```
1. Add validation at input boundary
2. Strengthen type checking
3. Add test data covering range/edges
4. Validate schema on deserialize
```

## Category: Config

**Severity:** Low to Medium (fixes often environmental)

**Sub-categories:**
- **Environment variables:** Wrong env var or missing
- **Hardcoded values:** Values hardcoded that should be config
- **Secrets exposure:** Secrets in code instead of vault
- **Version incompatibility:** Dependency version mismatch

**Example Detection:**
```
Environment variable not found: API_URL  → Missing env var
localhost hardcoded in code  → Should be config
AWS_SECRET in source code  → Secrets exposure
Module requires v2.0, have v1.5  → Version mismatch
```

**Fix Pattern:**
```
1. Externalize value to environment variable / config file
2. Validate config on startup
3. Test with different config values
4. Never commit secrets (use .gitignore + vault)
```

## Category: Concurrency

**Severity:** Critical (hardest to debug and fix)

**Sub-categories:**
- **Race condition:** Timing-dependent, non-deterministic
- **Deadlock:** Circular locking dependency
- **Stale reference:** Object reference outdated in async chain
- **Shared mutable state:** Multiple threads modify same data

**Example Detection:**
```
Test passes sometimes, fails sometimes  → Race condition
Test hangs, never completes  → Deadlock
'data' is undefined in callback  → Stale reference
'users' changed during iteration  → Shared state mutation
```

**Fix Pattern:**
```
1. Use immutable data structures
2. Apply proper locking (mutex, semaphore)
3. Use async/await instead of callbacks
4. Write concurrency-specific tests
5. Run with race detector enabled
```
```

- [ ] **Step 7: Write evals/test-prompts.yaml**

```yaml
test_cases:
  - id: "ad-tc-001"
    description: "Pattern detection: recurring validation issue"
    input:
      classified_defects:
        - defect_id: "FAIL-001"
          component: "payment"
          root_cause: "data"
          error_snippet: "Invalid amount: must be positive"
        - defect_id: "FAIL-002"
          component: "payment"
          root_cause: "data"
          error_snippet: "Amount validation failed"
        - defect_id: "FAIL-003"
          component: "payment"
          root_cause: "data"
          error_snippet: "Negative amount rejected"
        - defect_id: "FAIL-004"
          component: "payment"
          root_cause: "data"
          error_snippet: "Amount must be > 0"
        - defect_id: "FAIL-005"
          component: "payment"
          root_cause: "data"
          error_snippet: "Range check failed"
    expected:
      patterns_count_gte: 1
      patterns:
        - component: "payment"
          root_cause: "data"
          frequency: 5

  - id: "ad-tc-002"
    description: "Hotspot identification: high defect density"
    input:
      classified_defects:
        - defect_id: "H-001"
          component: "legacy-api"
          root_cause: "integration"
        - defect_id: "H-002"
          component: "legacy-api"
          root_cause: "logic"
        - defect_id: "H-003"
          component: "legacy-api"
          root_cause: "integration"
        - defect_id: "H-004"
          component: "legacy-api"
          root_cause: "config"
        - defect_id: "H-005"
          component: "legacy-api"
          root_cause: "logic"
        - defect_id: "H-006"
          component: "new-service"
          root_cause: "logic"
    expected:
      hotspots_count_gte: 1
      hotspots:
        - component: "legacy-api"
          defect_count: 5

  - id: "ad-tc-003"
    description: "Insufficient data: no patterns (< 5 points)"
    input:
      classified_defects:
        - defect_id: "I-001"
          component: "util"
          root_cause: "logic"
        - defect_id: "I-002"
          component: "util"
          root_cause: "data"
        - defect_id: "I-003"
          component: "other"
          root_cause: "logic"
    expected:
      patterns_count: 0
      note: "Insufficient data points for pattern detection"
```

- [ ] **Step 8: Write evals/assertions.yaml**

```yaml
assertions:
  - test_id: "ad-tc-001"
    checks:
      - path: "patterns"
        type: "array_length_gte"
        value: 1
      - path: "patterns[0].component"
        type: "equals"
        value: "payment"
      - path: "patterns[0].root_cause"
        type: "equals"
        value: "data"
      - path: "patterns[0].frequency"
        type: "number_gte"
        value: 5

  - test_id: "ad-tc-002"
    checks:
      - path: "hotspots"
        type: "array_length_gte"
        value: 1
      - path: "hotspots[0].component"
        type: "equals"
        value: "legacy-api"
      - path: "hotspots[0].defect_count"
        type: "number_gte"
        value: 5

  - test_id: "ad-tc-003"
    checks:
      - path: "patterns"
        type: "array_length"
        value: 0
```

- [ ] **Step 9: Commit analyzing-defects skill**

```bash
git add .github/skills/qa/analyzing-defects/
git commit -m "feat(qa-skills): implement analyzing-defects P3 skill

Root cause analysis and Knowledge Base pattern extraction.

Classifies defects: logic, integration, data, config, concurrency.
Detects patterns (≥5 occurrences) and hotspots (density > org avg).
Proposes Knowledge Base updates for human review (never auto-commits).

Scripts:
- root-cause-classifier.py: Pattern matching for root cause categories
- pattern-detector.py: Time-series and hotspot analysis
- knowledge-base-writer.py: Format proposals for Knowledge Base

References:
- defect-taxonomy.md: Detailed classification system with examples
- root-cause-categories.md: Category-specific indicators and fix patterns

Evals: 3 test cases (pattern detection, hotspot, insufficient data)."
```

---

## Task 7: Final verification

Verify all P3 files created and directory structure complete.

- [ ] **Step 1: Count SKILL.md files**

Run: `find .github/skills/qa -type f -name "SKILL.md" | wc -l`

Expected: 11 (6 P1 + 5 P3)

- [ ] **Step 2: Count Python scripts**

Run: `find .github/skills/qa -type f -name "*.py" | wc -l`

Expected: 14 (P3 scripts only)

- [ ] **Step 3: Count reference files**

Run: `find .github/skills/qa -type f -name "*.md" | grep -v SKILL | wc -l`

Expected: ≥16 (9 P3 references + rules + P1 references)

- [ ] **Step 4: Count eval files**

Run: `find .github/skills/qa -type f -name "test-prompts.yaml" | wc -l`

Expected: 11 (6 P1 + 5 P3)

- [ ] **Step 5: Verify rules directory**

Run: `ls -la .github/skills/qa/rules/`

Expected:
```
qa-standards.md (P1)
tdd-rules.md (P1)
review-guidelines.md (P3)
```

- [ ] **Step 6: Commit final verification**

```bash
git log --oneline -15 | grep qa-skills
```

Expected: 7 commits (1 scaffold + 5 skills + 1 final verification)

- [ ] **Step 7: Create summary commit**

```bash
git add .
git commit -m "docs(qa-skills): P3 comprehensive implementation plan complete

All 5 P3 skills implemented with full code:
- scoring-risk: Risk scoring model (scope, criticality, defect history, complexity)
- reviewing-code-quality: Two-stage review (spec compliance + code quality)
- selecting-regressions: Intelligent test selection (impact analysis + risk-weighted)
- healing-broken-tests: Auto-repair (locator/value fixes, human review for logic)
- analyzing-defects: Root cause analysis (patterns, hotspots, Knowledge Base proposals)

Plus P3 rules file:
- review-guidelines.md: Two-stage review process, cross-model protocol, comment standards

Total: 5 SKILL.md + 14 scripts + 9 references + 10 evals + 1 rules = 39 files

Spec: docs/specs/2026-03-28-qa-skills-quick-win-design.md §6 (P3), §7.3 (rules), §8 (evals)
Plan: docs/plans/2026-03-28-qa-verification-skills-p3.md (this plan)"
```

---

**Progress Tracking:**
- [x] Task 1: Scaffold + review-guidelines.md
- [x] Task 2: scoring-risk skill (9 steps)
- [x] Task 3: reviewing-code-quality skill (8 steps)
- [x] Task 4: selecting-regressions skill (8 steps)
- [x] Task 5: healing-broken-tests skill (9 steps)
- [x] Task 6: analyzing-defects skill (9 steps)
- [x] Task 7: Final verification (7 steps)
