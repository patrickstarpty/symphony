# QA Agent System — P1 Quick Win Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a demoable QA Evaluator that runs inside a Copilot CLI session, evaluates code on 3 dimensions (Pass Rate, Coverage, Acceptance), writes a structured report to the issue workpad, and auto-transitions the issue state.

**Architecture:** A Python package (`qa-agent`) containing 5 evaluation skills, a verdict engine, and a CLI entry point. Skills are invoked by the Copilot CLI agent during the QA Evaluation Phase defined in WORKFLOW.md. No separate service deployment in P1 — everything runs locally in the agent's workspace.

**Tech Stack:** Python 3.12+, pytest, uv (package manager), Click (CLI), Pydantic (schemas)

**Spec:** `docs/superpowers/specs/2026-03-25-qa-agent-system-design.md`

---

## File Structure

```
qa-agent/
├─ pyproject.toml                          — Package config, dependencies, CLI entry point
├─ src/
│   └─ qa_agent/
│       ├─ __init__.py
│       ├─ cli.py                          — CLI entry point: `qa-agent evaluate`
│       ├─ models.py                       — Pydantic models: EvaluationReport, DimensionResult, Verdict
│       ├─ verdict.py                      — Verdict engine: aggregate 3 dimensions → PASS/FAIL
│       ├─ report.py                       — Report formatter: structured markdown for workpad
│       └─ skills/
│           ├─ __init__.py
│           ├─ base.py                     — Skill base class / protocol
│           ├─ test_runner.py              — Run test suite, parse results, retry flaky
│           ├─ coverage_analyzer.py        — Parse coverage output, compare threshold
│           ├─ acceptance_validator.py     — Compare AC checklist against code changes
│           ├─ failure_classifier.py       — Classify failures: real bug / flaky / env
│           └─ qa_reporter.py             — Aggregate all results into final report
├─ tests/
│   ├─ conftest.py                         — Shared fixtures
│   ├─ test_models.py
│   ├─ test_verdict.py
│   ├─ test_report.py
│   ├─ test_cli.py                         — CLI integration tests via CliRunner
│   └─ skills/
│       ├─ __init__.py
│       ├─ test_test_runner.py
│       ├─ test_coverage_analyzer.py
│       ├─ test_acceptance_validator.py
│       ├─ test_failure_classifier.py
│       └─ test_qa_reporter.py
├─ skill-hub/                              — Skill definitions (prompt + metadata)
│   └─ evaluation/
│       ├─ test-runner/
│       │   ├─ skill.yaml
│       │   └─ prompt.md
│       ├─ coverage-analyzer/
│       │   ├─ skill.yaml
│       │   └─ prompt.md
│       ├─ acceptance-validator/
│       │   ├─ skill.yaml
│       │   └─ prompt.md
│       ├─ failure-classifier/
│       │   ├─ skill.yaml
│       │   └─ prompt.md
│       └─ qa-reporter/
│           ├─ skill.yaml
│           └─ prompt.md
└─ workflow/
    └─ qa-evaluation-phase.md              — WORKFLOW.md QA Evaluation Phase prompt template
```

---

### Task 1: Project Scaffolding

**Files:**
- Create: `qa-agent/pyproject.toml`
- Create: `qa-agent/src/qa_agent/__init__.py`
- Create: `qa-agent/tests/conftest.py`

- [ ] **Step 1: Create project directory**

```bash
mkdir -p qa-agent/src/qa_agent/skills qa-agent/tests/skills qa-agent/skill-hub/evaluation qa-agent/workflow
```

- [ ] **Step 2: Create pyproject.toml**

```toml
[project]
name = "qa-agent"
version = "0.1.0"
description = "QA Evaluator Agent for AI Native SDLC"
requires-python = ">=3.12"
dependencies = [
    "click>=8.1",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
]

[project.scripts]
qa-agent = "qa_agent.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.coverage.run]
source = ["src/qa_agent"]

[tool.coverage.report]
fail_under = 80
```

- [ ] **Step 3: Create __init__.py**

```python
"""QA Agent — Evaluator for AI Native SDLC."""
```

- [ ] **Step 4: Create conftest.py**

```python
"""Shared test fixtures for qa-agent."""
```

- [ ] **Step 5: Initialize and verify**

```bash
cd qa-agent && uv sync && uv run pytest --co -q
```

Expected: `no tests ran` (no test files yet, but setup works)

- [ ] **Step 6: Commit**

```bash
git add qa-agent/
git commit -m "feat: scaffold qa-agent project with pyproject.toml"
```

---

### Task 2: Data Models (Pydantic)

**Files:**
- Create: `qa-agent/src/qa_agent/models.py`
- Create: `qa-agent/tests/test_models.py`

- [ ] **Step 1: Write failing tests for models**

```python
# tests/test_models.py
from qa_agent.models import (
    Dimension,
    DimensionResult,
    DimensionStatus,
    EvaluationReport,
    Verdict,
)


class TestDimensionResult:
    def test_pass_result(self):
        result = DimensionResult(
            dimension=Dimension.PASS_RATE,
            status=DimensionStatus.PASS,
            summary="42/42 tests passed",
            details={"total": 42, "passed": 42, "failed": 0},
        )
        assert result.dimension == Dimension.PASS_RATE
        assert result.status == DimensionStatus.PASS

    def test_fail_result(self):
        result = DimensionResult(
            dimension=Dimension.COVERAGE,
            status=DimensionStatus.FAIL,
            summary="Coverage 65% below threshold 80%",
            details={"coverage_pct": 65.0, "threshold_pct": 80.0},
        )
        assert result.status == DimensionStatus.FAIL

    def test_inconclusive_result(self):
        result = DimensionResult(
            dimension=Dimension.COVERAGE,
            status=DimensionStatus.INCONCLUSIVE,
            summary="Coverage tool unavailable",
        )
        assert result.status == DimensionStatus.INCONCLUSIVE
        assert result.details is None


class TestEvaluationReport:
    def test_report_with_all_pass(self):
        dimensions = [
            DimensionResult(
                dimension=Dimension.PASS_RATE,
                status=DimensionStatus.PASS,
                summary="10/10 passed",
            ),
            DimensionResult(
                dimension=Dimension.COVERAGE,
                status=DimensionStatus.PASS,
                summary="85% coverage",
            ),
            DimensionResult(
                dimension=Dimension.ACCEPTANCE,
                status=DimensionStatus.PASS,
                summary="3/3 AC met",
            ),
        ]
        report = EvaluationReport(
            issue_id="ISSUE-123",
            verdict=Verdict.PASS,
            dimensions=dimensions,
        )
        assert report.verdict == Verdict.PASS
        assert len(report.dimensions) == 3

    def test_report_with_failure(self):
        dimensions = [
            DimensionResult(
                dimension=Dimension.PASS_RATE,
                status=DimensionStatus.FAIL,
                summary="8/10 passed",
            ),
        ]
        report = EvaluationReport(
            issue_id="ISSUE-456",
            verdict=Verdict.FAIL,
            dimensions=dimensions,
        )
        assert report.verdict == Verdict.FAIL
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd qa-agent && uv run pytest tests/test_models.py -v
```

Expected: `ModuleNotFoundError: No module named 'qa_agent.models'`

- [ ] **Step 3: Implement models**

```python
# src/qa_agent/models.py
"""Data models for QA evaluation."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class Dimension(StrEnum):
    PASS_RATE = "pass_rate"
    COVERAGE = "coverage"
    ACCEPTANCE = "acceptance"


class DimensionStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


class Verdict(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"


class DimensionResult(BaseModel):
    dimension: Dimension
    status: DimensionStatus
    summary: str
    details: dict | None = None


class EvaluationReport(BaseModel):
    issue_id: str
    verdict: Verdict
    dimensions: list[DimensionResult]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd qa-agent && uv run pytest tests/test_models.py -v
```

Expected: all PASSED

- [ ] **Step 5: Commit**

```bash
cd qa-agent && git add -A && git commit -m "feat: add Pydantic data models for evaluation dimensions and report"
```

---

### Task 3: Skill Base Protocol

**Files:**
- Create: `qa-agent/src/qa_agent/skills/__init__.py`
- Create: `qa-agent/src/qa_agent/skills/base.py`

- [ ] **Step 1: Create skills __init__.py**

```python
"""QA evaluation skills."""
```

- [ ] **Step 2: Write skill base protocol**

```python
# src/qa_agent/skills/base.py
"""Base protocol for QA evaluation skills."""

from __future__ import annotations

from typing import Protocol

from qa_agent.models import DimensionResult


class EvaluationSkill(Protocol):
    """Protocol that all evaluation skills must implement."""

    def evaluate(self, workspace: str, **kwargs: object) -> DimensionResult:
        """Run evaluation in the given workspace directory.

        Args:
            workspace: Absolute path to the project workspace.
            **kwargs: Skill-specific parameters.

        Returns:
            DimensionResult with status and details.
        """
        ...
```

No test needed — Protocol is a structural type, tested implicitly when concrete skills implement it.

- [ ] **Step 3: Commit**

```bash
cd qa-agent && git add -A && git commit -m "feat: add EvaluationSkill protocol for skill base"
```

---

### Task 4: test-runner Skill

**Files:**
- Create: `qa-agent/src/qa_agent/skills/test_runner.py`
- Create: `qa-agent/tests/skills/test_test_runner.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/skills/test_test_runner.py
"""Tests for test-runner skill."""

import subprocess
from unittest.mock import patch

from qa_agent.models import Dimension, DimensionStatus
from qa_agent.skills.test_runner import TestRunnerSkill


class TestTestRunnerSkill:
    def test_all_tests_pass(self, tmp_path):
        completed = subprocess.CompletedProcess(
            args=["make", "test"],
            returncode=0,
            stdout="10 passed, 0 failed\n",
            stderr="",
        )
        with patch("subprocess.run", return_value=completed):
            skill = TestRunnerSkill(command="make test")
            result = skill.evaluate(workspace=str(tmp_path))

        assert result.dimension == Dimension.PASS_RATE
        assert result.status == DimensionStatus.PASS

    def test_some_tests_fail(self, tmp_path):
        completed = subprocess.CompletedProcess(
            args=["make", "test"],
            returncode=1,
            stdout="8 passed, 2 failed\n",
            stderr="",
        )
        with patch("subprocess.run", return_value=completed):
            skill = TestRunnerSkill(command="make test")
            result = skill.evaluate(workspace=str(tmp_path))

        assert result.dimension == Dimension.PASS_RATE
        assert result.status == DimensionStatus.FAIL

    def test_command_timeout(self, tmp_path):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("make test", 300)):
            skill = TestRunnerSkill(command="make test", timeout=300)
            result = skill.evaluate(workspace=str(tmp_path))

        assert result.dimension == Dimension.PASS_RATE
        assert result.status == DimensionStatus.INCONCLUSIVE
        assert "timeout" in result.summary.lower()

    def test_flaky_retry_passes_on_second_attempt(self, tmp_path):
        fail_result = subprocess.CompletedProcess(
            args=["make", "test"], returncode=1,
            stdout="9 passed, 1 failed\n", stderr="",
        )
        pass_result = subprocess.CompletedProcess(
            args=["make", "test"], returncode=0,
            stdout="10 passed, 0 failed\n", stderr="",
        )
        with patch("subprocess.run", side_effect=[fail_result, pass_result]):
            skill = TestRunnerSkill(command="make test", flaky_retries=2)
            result = skill.evaluate(workspace=str(tmp_path))

        assert result.status == DimensionStatus.PASS
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd qa-agent && uv run pytest tests/skills/test_test_runner.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement test-runner skill**

```python
# src/qa_agent/skills/test_runner.py
"""Test runner skill — execute test suite and report pass rate."""

from __future__ import annotations

import subprocess

from qa_agent.models import Dimension, DimensionResult, DimensionStatus


class TestRunnerSkill:
    def __init__(
        self,
        command: str = "make test",
        timeout: int = 600,
        flaky_retries: int = 0,
    ):
        self.command = command
        self.timeout = timeout
        self.flaky_retries = flaky_retries

    def evaluate(self, workspace: str, **kwargs: object) -> DimensionResult:
        try:
            result = self._run_tests(workspace)
        except subprocess.TimeoutExpired:
            return DimensionResult(
                dimension=Dimension.PASS_RATE,
                status=DimensionStatus.INCONCLUSIVE,
                summary=f"Test command timed out after {self.timeout}s",
            )

        if result.returncode == 0:
            return DimensionResult(
                dimension=Dimension.PASS_RATE,
                status=DimensionStatus.PASS,
                summary=result.stdout.strip(),
                details={"returncode": 0},
            )

        # Retry for flaky tests
        for _ in range(self.flaky_retries):
            try:
                retry = self._run_tests(workspace)
            except subprocess.TimeoutExpired:
                continue
            if retry.returncode == 0:
                return DimensionResult(
                    dimension=Dimension.PASS_RATE,
                    status=DimensionStatus.PASS,
                    summary=f"{retry.stdout.strip()} (passed on retry)",
                    details={"returncode": 0, "retried": True},
                )

        return DimensionResult(
            dimension=Dimension.PASS_RATE,
            status=DimensionStatus.FAIL,
            summary=result.stdout.strip(),
            details={"returncode": result.returncode},
        )

    def _run_tests(self, workspace: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            self.command.split(),
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd qa-agent && uv run pytest tests/skills/test_test_runner.py -v
```

Expected: all PASSED

- [ ] **Step 5: Commit**

```bash
cd qa-agent && git add -A && git commit -m "feat: add test-runner skill with flaky retry support"
```

---

### Task 5: coverage-analyzer Skill

**Files:**
- Create: `qa-agent/src/qa_agent/skills/coverage_analyzer.py`
- Create: `qa-agent/tests/skills/test_coverage_analyzer.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/skills/test_coverage_analyzer.py
"""Tests for coverage-analyzer skill."""

import subprocess
from unittest.mock import patch

from qa_agent.models import Dimension, DimensionStatus
from qa_agent.skills.coverage_analyzer import CoverageAnalyzerSkill


class TestCoverageAnalyzerSkill:
    def test_coverage_above_threshold(self, tmp_path):
        completed = subprocess.CompletedProcess(
            args=["make", "coverage"],
            returncode=0,
            stdout="TOTAL    85%\n",
            stderr="",
        )
        with patch("subprocess.run", return_value=completed):
            skill = CoverageAnalyzerSkill(command="make coverage", threshold=80.0)
            result = skill.evaluate(workspace=str(tmp_path))

        assert result.dimension == Dimension.COVERAGE
        assert result.status == DimensionStatus.PASS
        assert result.details["coverage_pct"] == 85.0

    def test_coverage_below_threshold(self, tmp_path):
        completed = subprocess.CompletedProcess(
            args=["make", "coverage"],
            returncode=0,
            stdout="TOTAL    65%\n",
            stderr="",
        )
        with patch("subprocess.run", return_value=completed):
            skill = CoverageAnalyzerSkill(command="make coverage", threshold=80.0)
            result = skill.evaluate(workspace=str(tmp_path))

        assert result.status == DimensionStatus.FAIL
        assert result.details["coverage_pct"] == 65.0
        assert result.details["threshold_pct"] == 80.0

    def test_coverage_tool_unavailable(self, tmp_path):
        with patch("subprocess.run", side_effect=FileNotFoundError("make not found")):
            skill = CoverageAnalyzerSkill(command="make coverage", threshold=80.0)
            result = skill.evaluate(workspace=str(tmp_path))

        assert result.status == DimensionStatus.INCONCLUSIVE

    def test_parse_pytest_cov_format(self, tmp_path):
        output = """Name                      Stmts   Miss  Cover
---------------------------------------------
src/qa_agent/models.py       25      3    88%
src/qa_agent/verdict.py      18      0   100%
---------------------------------------------
TOTAL                        43      3    93%
"""
        completed = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=output, stderr="",
        )
        with patch("subprocess.run", return_value=completed):
            skill = CoverageAnalyzerSkill(command="make coverage", threshold=80.0)
            result = skill.evaluate(workspace=str(tmp_path))

        assert result.status == DimensionStatus.PASS
        assert result.details["coverage_pct"] == 93.0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd qa-agent && uv run pytest tests/skills/test_coverage_analyzer.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement coverage-analyzer skill**

```python
# src/qa_agent/skills/coverage_analyzer.py
"""Coverage analyzer skill — parse coverage output and compare against threshold."""

from __future__ import annotations

import re
import subprocess

from qa_agent.models import Dimension, DimensionResult, DimensionStatus


class CoverageAnalyzerSkill:
    def __init__(
        self,
        command: str = "make coverage",
        threshold: float = 80.0,
        timeout: int = 300,
    ):
        self.command = command
        self.threshold = threshold
        self.timeout = timeout

    def evaluate(self, workspace: str, **kwargs: object) -> DimensionResult:
        try:
            result = subprocess.run(
                self.command.split(),
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return DimensionResult(
                dimension=Dimension.COVERAGE,
                status=DimensionStatus.INCONCLUSIVE,
                summary=f"Coverage tool unavailable: {e}",
            )

        coverage_pct = self._parse_coverage(result.stdout)
        if coverage_pct is None:
            return DimensionResult(
                dimension=Dimension.COVERAGE,
                status=DimensionStatus.INCONCLUSIVE,
                summary="Could not parse coverage percentage from output",
                details={"raw_output": result.stdout[:500]},
            )

        if coverage_pct >= self.threshold:
            return DimensionResult(
                dimension=Dimension.COVERAGE,
                status=DimensionStatus.PASS,
                summary=f"Coverage {coverage_pct}% meets threshold {self.threshold}%",
                details={"coverage_pct": coverage_pct, "threshold_pct": self.threshold},
            )

        return DimensionResult(
            dimension=Dimension.COVERAGE,
            status=DimensionStatus.FAIL,
            summary=f"Coverage {coverage_pct}% below threshold {self.threshold}%",
            details={"coverage_pct": coverage_pct, "threshold_pct": self.threshold},
        )

    def _parse_coverage(self, output: str) -> float | None:
        """Extract coverage percentage from common tool outputs."""
        # Match "TOTAL ... XX%" pattern (pytest-cov, coverage.py)
        match = re.search(r"TOTAL\s+.*?(\d+)%", output)
        if match:
            return float(match.group(1))
        # Match standalone "XX%" on a line
        match = re.search(r"(\d+(?:\.\d+)?)%", output)
        if match:
            return float(match.group(1))
        return None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd qa-agent && uv run pytest tests/skills/test_coverage_analyzer.py -v
```

Expected: all PASSED

- [ ] **Step 5: Commit**

```bash
cd qa-agent && git add -A && git commit -m "feat: add coverage-analyzer skill with multi-format parsing"
```

---

### Task 6: failure-classifier Skill

**Files:**
- Create: `qa-agent/src/qa_agent/skills/failure_classifier.py`
- Create: `qa-agent/tests/skills/test_failure_classifier.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/skills/test_failure_classifier.py
"""Tests for failure-classifier skill."""

from qa_agent.skills.failure_classifier import FailureCategory, FailureClassifierSkill


class TestFailureClassifierSkill:
    def test_classify_assertion_error_as_real_bug(self):
        skill = FailureClassifierSkill()
        category = skill.classify("AssertionError: expected 5 but got 3")
        assert category == FailureCategory.REAL_BUG

    def test_classify_connection_refused_as_env(self):
        skill = FailureClassifierSkill()
        category = skill.classify("ConnectionRefusedError: [Errno 111] Connection refused")
        assert category == FailureCategory.ENV_ISSUE

    def test_classify_timeout_as_env(self):
        skill = FailureClassifierSkill()
        category = skill.classify("TimeoutError: timed out waiting for element")
        assert category == FailureCategory.ENV_ISSUE

    def test_classify_element_not_found_as_possible_flaky(self):
        skill = FailureClassifierSkill()
        category = skill.classify("NoSuchElementException: Unable to locate element")
        assert category == FailureCategory.POSSIBLE_FLAKY

    def test_classify_unknown_error(self):
        skill = FailureClassifierSkill()
        category = skill.classify("SomeWeirdError: unexpected thing happened")
        assert category == FailureCategory.REAL_BUG  # default to real bug
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd qa-agent && uv run pytest tests/skills/test_failure_classifier.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement failure-classifier skill**

```python
# src/qa_agent/skills/failure_classifier.py
"""Failure classifier skill — categorize test failures by likely root cause."""

from __future__ import annotations

import re
from enum import StrEnum


class FailureCategory(StrEnum):
    REAL_BUG = "real_bug"
    POSSIBLE_FLAKY = "possible_flaky"
    ENV_ISSUE = "env_issue"


# Pattern → category mapping, checked in order
_PATTERNS: list[tuple[re.Pattern, FailureCategory]] = [
    # Environment issues
    (re.compile(r"ConnectionRefused|ConnectionError|ECONNREFUSED", re.I), FailureCategory.ENV_ISSUE),
    (re.compile(r"TimeoutError|timed?\s*out", re.I), FailureCategory.ENV_ISSUE),
    (re.compile(r"DatabaseError.*connection|OperationalError.*server", re.I), FailureCategory.ENV_ISSUE),
    (re.compile(r"ServiceUnavailable|503", re.I), FailureCategory.ENV_ISSUE),
    # Possible flaky
    (re.compile(r"NoSuchElement|ElementNotFound|StaleElement", re.I), FailureCategory.POSSIBLE_FLAKY),
    (re.compile(r"flaky|intermittent|race\s*condition", re.I), FailureCategory.POSSIBLE_FLAKY),
]


class FailureClassifierSkill:
    def classify(self, error_message: str) -> FailureCategory:
        """Classify a test failure error message into a category."""
        for pattern, category in _PATTERNS:
            if pattern.search(error_message):
                return category
        return FailureCategory.REAL_BUG
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd qa-agent && uv run pytest tests/skills/test_failure_classifier.py -v
```

Expected: all PASSED

- [ ] **Step 5: Commit**

```bash
cd qa-agent && git add -A && git commit -m "feat: add failure-classifier skill with pattern-based categorization"
```

---

### Task 7: acceptance-validator Skill

**Files:**
- Create: `qa-agent/src/qa_agent/skills/acceptance_validator.py`
- Create: `qa-agent/tests/skills/test_acceptance_validator.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/skills/test_acceptance_validator.py
"""Tests for acceptance-validator skill."""

from qa_agent.models import Dimension, DimensionStatus
from qa_agent.skills.acceptance_validator import AcceptanceValidatorSkill


class TestAcceptanceValidatorSkill:
    def test_all_ac_met(self):
        acceptance_criteria = [
            "Password must be at least 8 characters",
            "Password must contain a number",
            "Error message shown for invalid password",
        ]
        code_changes = """
        def validate_password(password: str) -> list[str]:
            errors = []
            if len(password) < 8:
                errors.append("Password must be at least 8 characters")
            if not any(c.isdigit() for c in password):
                errors.append("Password must contain a number")
            return errors
        """
        skill = AcceptanceValidatorSkill()
        result = skill.evaluate(
            workspace="/tmp",
            acceptance_criteria=acceptance_criteria,
            code_changes=code_changes,
        )
        assert result.dimension == Dimension.ACCEPTANCE
        # Note: actual LLM-based validation is stubbed in P1
        # This test verifies the skill returns a valid DimensionResult
        assert result.status in (DimensionStatus.PASS, DimensionStatus.INCONCLUSIVE)

    def test_no_acceptance_criteria(self):
        skill = AcceptanceValidatorSkill()
        result = skill.evaluate(
            workspace="/tmp",
            acceptance_criteria=[],
            code_changes="some code",
        )
        assert result.status == DimensionStatus.INCONCLUSIVE
        assert "no acceptance criteria" in result.summary.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd qa-agent && uv run pytest tests/skills/test_acceptance_validator.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement acceptance-validator skill**

P1 implementation uses keyword matching as a simple heuristic. P2/P3 will upgrade to LLM-based validation.

```python
# src/qa_agent/skills/acceptance_validator.py
"""Acceptance validator skill — check if code changes satisfy acceptance criteria."""

from __future__ import annotations

from qa_agent.models import Dimension, DimensionResult, DimensionStatus


class AcceptanceValidatorSkill:
    def evaluate(self, workspace: str, **kwargs: object) -> DimensionResult:
        acceptance_criteria: list[str] = kwargs.get("acceptance_criteria", [])
        code_changes: str = kwargs.get("code_changes", "")

        if not acceptance_criteria:
            return DimensionResult(
                dimension=Dimension.ACCEPTANCE,
                status=DimensionStatus.INCONCLUSIVE,
                summary="No acceptance criteria provided in issue",
            )

        results = []
        for ac in acceptance_criteria:
            # P1: simple keyword heuristic — check if key terms from AC
            # appear in code changes. P2/P3 upgrades to LLM validation.
            key_terms = self._extract_key_terms(ac)
            found = any(term.lower() in code_changes.lower() for term in key_terms)
            results.append({"ac": ac, "likely_met": found})

        met_count = sum(1 for r in results if r["likely_met"])
        total = len(results)

        if met_count == total:
            return DimensionResult(
                dimension=Dimension.ACCEPTANCE,
                status=DimensionStatus.PASS,
                summary=f"{met_count}/{total} acceptance criteria likely met",
                details={"results": results},
            )

        return DimensionResult(
            dimension=Dimension.ACCEPTANCE,
            status=DimensionStatus.FAIL,
            summary=f"{met_count}/{total} acceptance criteria likely met",
            details={"results": results},
        )

    def _extract_key_terms(self, ac: str) -> list[str]:
        """Extract meaningful terms from an acceptance criterion."""
        stop_words = {"must", "should", "the", "a", "an", "be", "is", "are", "for", "and", "or"}
        words = ac.lower().split()
        return [w for w in words if len(w) > 3 and w not in stop_words]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd qa-agent && uv run pytest tests/skills/test_acceptance_validator.py -v
```

Expected: all PASSED

- [ ] **Step 5: Commit**

```bash
cd qa-agent && git add -A && git commit -m "feat: add acceptance-validator skill with keyword heuristic (P1)"
```

---

### Task 8: Verdict Engine

**Files:**
- Create: `qa-agent/src/qa_agent/verdict.py`
- Create: `qa-agent/tests/test_verdict.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_verdict.py
"""Tests for verdict engine."""

from qa_agent.models import Dimension, DimensionResult, DimensionStatus, Verdict
from qa_agent.verdict import compute_verdict


class TestComputeVerdict:
    def test_all_pass(self):
        results = [
            DimensionResult(dimension=Dimension.PASS_RATE, status=DimensionStatus.PASS, summary="ok"),
            DimensionResult(dimension=Dimension.COVERAGE, status=DimensionStatus.PASS, summary="ok"),
            DimensionResult(dimension=Dimension.ACCEPTANCE, status=DimensionStatus.PASS, summary="ok"),
        ]
        assert compute_verdict(results) == Verdict.PASS

    def test_any_fail(self):
        results = [
            DimensionResult(dimension=Dimension.PASS_RATE, status=DimensionStatus.FAIL, summary="fail"),
            DimensionResult(dimension=Dimension.COVERAGE, status=DimensionStatus.PASS, summary="ok"),
            DimensionResult(dimension=Dimension.ACCEPTANCE, status=DimensionStatus.PASS, summary="ok"),
        ]
        assert compute_verdict(results) == Verdict.FAIL

    def test_inconclusive_with_strict_policy(self):
        results = [
            DimensionResult(dimension=Dimension.PASS_RATE, status=DimensionStatus.PASS, summary="ok"),
            DimensionResult(dimension=Dimension.COVERAGE, status=DimensionStatus.INCONCLUSIVE, summary="n/a"),
            DimensionResult(dimension=Dimension.ACCEPTANCE, status=DimensionStatus.PASS, summary="ok"),
        ]
        assert compute_verdict(results, policy="strict") == Verdict.FAIL

    def test_inconclusive_with_advisory_policy(self):
        results = [
            DimensionResult(dimension=Dimension.PASS_RATE, status=DimensionStatus.PASS, summary="ok"),
            DimensionResult(dimension=Dimension.COVERAGE, status=DimensionStatus.INCONCLUSIVE, summary="n/a"),
            DimensionResult(dimension=Dimension.ACCEPTANCE, status=DimensionStatus.PASS, summary="ok"),
        ]
        assert compute_verdict(results, policy="advisory") == Verdict.PASS

    def test_empty_results(self):
        assert compute_verdict([]) == Verdict.FAIL
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd qa-agent && uv run pytest tests/test_verdict.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement verdict engine**

```python
# src/qa_agent/verdict.py
"""Verdict engine — aggregate dimension results into final PASS/FAIL."""

from __future__ import annotations

from qa_agent.models import DimensionResult, DimensionStatus, Verdict


def compute_verdict(
    results: list[DimensionResult],
    policy: str = "strict",
) -> Verdict:
    """Compute overall verdict from dimension results.

    Args:
        results: List of dimension evaluation results.
        policy: "strict" = inconclusive counts as fail.
                "advisory" = inconclusive counts as pass.

    Returns:
        PASS if all dimensions pass, FAIL otherwise.
    """
    if not results:
        return Verdict.FAIL

    for result in results:
        if result.status == DimensionStatus.FAIL:
            return Verdict.FAIL
        if result.status == DimensionStatus.INCONCLUSIVE and policy == "strict":
            return Verdict.FAIL

    return Verdict.PASS
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd qa-agent && uv run pytest tests/test_verdict.py -v
```

Expected: all PASSED

- [ ] **Step 5: Commit**

```bash
cd qa-agent && git add -A && git commit -m "feat: add verdict engine with strict/advisory policy support"
```

---

### Task 9: QA Reporter Skill

**Files:**
- Create: `qa-agent/src/qa_agent/skills/qa_reporter.py`
- Create: `qa-agent/src/qa_agent/report.py`
- Create: `qa-agent/tests/test_report.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_report.py
"""Tests for report formatter."""

from qa_agent.models import (
    Dimension,
    DimensionResult,
    DimensionStatus,
    EvaluationReport,
    Verdict,
)
from qa_agent.report import format_workpad_report


class TestFormatWorkpadReport:
    def test_pass_report(self):
        report = EvaluationReport(
            issue_id="ISSUE-123",
            verdict=Verdict.PASS,
            dimensions=[
                DimensionResult(dimension=Dimension.PASS_RATE, status=DimensionStatus.PASS, summary="42/42 passed"),
                DimensionResult(dimension=Dimension.COVERAGE, status=DimensionStatus.PASS, summary="85% coverage"),
                DimensionResult(dimension=Dimension.ACCEPTANCE, status=DimensionStatus.PASS, summary="3/3 AC met"),
            ],
        )
        md = format_workpad_report(report)
        assert "## QA Report" in md
        assert "PASS" in md
        assert "42/42 passed" in md
        assert "85% coverage" in md

    def test_fail_report_includes_failure_reason(self):
        report = EvaluationReport(
            issue_id="ISSUE-456",
            verdict=Verdict.FAIL,
            dimensions=[
                DimensionResult(dimension=Dimension.PASS_RATE, status=DimensionStatus.FAIL, summary="8/10 passed"),
                DimensionResult(dimension=Dimension.COVERAGE, status=DimensionStatus.PASS, summary="90% coverage"),
                DimensionResult(dimension=Dimension.ACCEPTANCE, status=DimensionStatus.PASS, summary="2/2 AC met"),
            ],
        )
        md = format_workpad_report(report)
        assert "FAIL" in md
        assert "8/10 passed" in md
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd qa-agent && uv run pytest tests/test_report.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement report formatter**

```python
# src/qa_agent/report.py
"""Report formatter — generate structured markdown for issue workpad."""

from __future__ import annotations

from qa_agent.models import DimensionStatus, EvaluationReport


_STATUS_ICON = {
    DimensionStatus.PASS: "PASS",
    DimensionStatus.FAIL: "FAIL",
    DimensionStatus.INCONCLUSIVE: "N/A",
}


def format_workpad_report(report: EvaluationReport) -> str:
    """Format an EvaluationReport as markdown for the issue workpad."""
    lines = [
        "## QA Report",
        "",
        f"**Verdict: {report.verdict.value}**",
        "",
        "| Dimension | Result | Details |",
        "|-----------|--------|---------|",
    ]

    for dim in report.dimensions:
        status = _STATUS_ICON[dim.status]
        lines.append(f"| {dim.dimension.value} | {status} | {dim.summary} |")

    lines.append("")
    lines.append(f"_Evaluated at {report.timestamp.strftime('%Y-%m-%d %H:%M UTC')}_")
    return "\n".join(lines)
```

- [ ] **Step 4: Implement qa-reporter skill**

```python
# src/qa_agent/skills/qa_reporter.py
"""QA reporter skill — aggregate all dimension results into a final report."""

from __future__ import annotations

from qa_agent.models import DimensionResult, EvaluationReport
from qa_agent.report import format_workpad_report
from qa_agent.verdict import compute_verdict


class QAReporterSkill:
    def __init__(self, policy: str = "strict"):
        self.policy = policy

    def generate_report(
        self,
        issue_id: str,
        results: list[DimensionResult],
    ) -> tuple[EvaluationReport, str]:
        """Generate evaluation report and formatted markdown.

        Returns:
            Tuple of (EvaluationReport, markdown string for workpad).
        """
        verdict = compute_verdict(results, policy=self.policy)
        report = EvaluationReport(
            issue_id=issue_id,
            verdict=verdict,
            dimensions=results,
        )
        markdown = format_workpad_report(report)
        return report, markdown
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd qa-agent && uv run pytest tests/test_report.py -v
```

Expected: all PASSED

- [ ] **Step 6: Commit**

```bash
cd qa-agent && git add -A && git commit -m "feat: add qa-reporter skill and workpad report formatter"
```

---

### Task 10: CLI Entry Point

**Files:**
- Create: `qa-agent/src/qa_agent/cli.py`

- [ ] **Step 1: Implement CLI**

```python
# src/qa_agent/cli.py
"""CLI entry point for qa-agent."""

from __future__ import annotations

import json
import sys

import click

from qa_agent.models import Dimension, DimensionResult
from qa_agent.report import format_workpad_report
from qa_agent.skills.acceptance_validator import AcceptanceValidatorSkill
from qa_agent.skills.coverage_analyzer import CoverageAnalyzerSkill
from qa_agent.skills.qa_reporter import QAReporterSkill
from qa_agent.skills.test_runner import TestRunnerSkill


@click.group()
def main():
    """QA Agent — Evaluator for AI Native SDLC."""


@main.command()
@click.option("--workspace", required=True, help="Path to project workspace")
@click.option("--issue-id", required=True, help="Issue identifier (e.g. ISSUE-123)")
@click.option("--test-command", default="make test", help="Command to run tests")
@click.option("--coverage-command", default="make coverage", help="Command to run coverage")
@click.option("--coverage-threshold", default=80.0, help="Minimum coverage percentage")
@click.option("--policy", default="strict", type=click.Choice(["strict", "advisory"]))
@click.option("--acceptance-criteria", default=None, help="JSON array of AC strings")
@click.option("--code-changes", default=None, help="Code changes text or path to diff file")
@click.option("--output", default="text", type=click.Choice(["text", "json"]))
def evaluate(
    workspace: str,
    issue_id: str,
    test_command: str,
    coverage_command: str,
    coverage_threshold: float,
    policy: str,
    acceptance_criteria: str | None,
    code_changes: str | None,
    output: str,
):
    """Run QA evaluation on a workspace."""
    results: list[DimensionResult] = []

    # 1. Pass Rate
    runner = TestRunnerSkill(command=test_command, flaky_retries=2)
    results.append(runner.evaluate(workspace=workspace))

    # 2. Coverage
    analyzer = CoverageAnalyzerSkill(command=coverage_command, threshold=coverage_threshold)
    results.append(analyzer.evaluate(workspace=workspace))

    # 3. Acceptance
    ac_list = json.loads(acceptance_criteria) if acceptance_criteria else []
    changes = code_changes or ""
    validator = AcceptanceValidatorSkill()
    results.append(validator.evaluate(
        workspace=workspace,
        acceptance_criteria=ac_list,
        code_changes=changes,
    ))

    # Generate report
    reporter = QAReporterSkill(policy=policy)
    report, markdown = reporter.generate_report(issue_id=issue_id, results=results)

    if output == "json":
        click.echo(report.model_dump_json(indent=2))
    else:
        click.echo(markdown)

    sys.exit(0 if report.verdict == "PASS" else 1)
```

- [ ] **Step 2: Verify CLI works**

```bash
cd qa-agent && uv run qa-agent evaluate --help
```

Expected: Help text with all options displayed

- [ ] **Step 3: Commit**

```bash
cd qa-agent && git add -A && git commit -m "feat: add CLI entry point for qa-agent evaluate"
```

---

### Task 11: Skill Hub Definitions

**Files:**
- Create: `qa-agent/skill-hub/evaluation/test-runner/skill.yaml`
- Create: `qa-agent/skill-hub/evaluation/test-runner/prompt.md`
- Create: (same structure for other 4 skills)

- [ ] **Step 1: Create test-runner skill definition**

```yaml
# skill-hub/evaluation/test-runner/skill.yaml
name: test-runner
version: "0.1.0"
description: Execute project test suite and report pass rate
dimension: pass_rate
input:
  workspace: { type: string, required: true }
  command: { type: string, default: "make test" }
  timeout: { type: integer, default: 600 }
  flaky_retries: { type: integer, default: 2 }
output:
  dimension_result: { type: DimensionResult }
```

```markdown
<!-- skill-hub/evaluation/test-runner/prompt.md -->
# Test Runner

Run the project's test suite and report pass rate.

## When to use
After code implementation is complete, to verify all tests pass.

## How it works
1. Execute the configured test command in the workspace
2. If tests fail, retry up to N times to detect flaky tests
3. Parse output to determine pass/fail counts
4. Return PASS if all tests pass, FAIL if real failures exist, INCONCLUSIVE on timeout
```

- [ ] **Step 2: Create remaining 4 skill definitions**

Repeat the same `skill.yaml` + `prompt.md` pattern for:
- `skill-hub/evaluation/coverage-analyzer/`
- `skill-hub/evaluation/acceptance-validator/`
- `skill-hub/evaluation/failure-classifier/`
- `skill-hub/evaluation/qa-reporter/`

(Each with appropriate name, description, dimension, input/output schema)

- [ ] **Step 3: Commit**

```bash
cd qa-agent && git add skill-hub/ && git commit -m "feat: add skill hub definitions for 5 P1 evaluation skills"
```

---

### Task 12: WORKFLOW.md QA Evaluation Phase Template

**Files:**
- Create: `qa-agent/workflow/qa-evaluation-phase.md`

- [ ] **Step 1: Write the QA Evaluation Phase prompt template**

```markdown
<!-- workflow/qa-evaluation-phase.md -->
# QA Evaluation Phase

Add this section to your WORKFLOW.md prompt template, after the coding instructions.

---

## QA Evaluation Phase

After completing implementation, you MUST run QA evaluation before transitioning the issue.

### Step 1: Run tests

```bash
qa-agent evaluate \
  --workspace {{ workspace_path }} \
  --issue-id {{ issue.identifier }} \
  --test-command "{{ config.qa.test_command | default: 'make test' }}" \
  --coverage-command "{{ config.qa.coverage_command | default: 'make coverage' }}" \
  --coverage-threshold {{ config.qa.coverage_threshold | default: 80 }} \
  --policy {{ config.qa.gate_policy | default: 'strict' }} \
  --acceptance-criteria '{{ issue.acceptance_criteria | json }}' \
  --output text
```

### Step 2: Update workpad

Copy the QA Report output into the Copilot Workpad comment under a `## QA Report` heading.

### Step 3: Act on verdict

- If **Verdict: PASS** → transition issue to **Human Review**
- If **Verdict: FAIL** → transition issue to **Rework**, include failure details in workpad

**Do NOT skip the QA Evaluation Phase.** If qa-agent is unavailable, note this in the workpad and leave the issue in current state for human triage.
```

- [ ] **Step 2: Commit**

```bash
cd qa-agent && git add workflow/ && git commit -m "feat: add WORKFLOW.md QA Evaluation Phase template"
```

---

### Task 13: Integration Test — Full Evaluation Pipeline

**Files:**
- Create: `qa-agent/tests/test_integration.py`

- [ ] **Step 1: Write integration test**

```python
# tests/test_integration.py
"""Integration test — full evaluation pipeline end-to-end."""

import subprocess
from unittest.mock import patch

from qa_agent.models import Dimension, DimensionStatus, Verdict
from qa_agent.skills.acceptance_validator import AcceptanceValidatorSkill
from qa_agent.skills.coverage_analyzer import CoverageAnalyzerSkill
from qa_agent.skills.qa_reporter import QAReporterSkill
from qa_agent.skills.test_runner import TestRunnerSkill


class TestFullEvaluationPipeline:
    def test_all_pass_pipeline(self, tmp_path):
        """Simulate: tests pass, coverage good, AC met → PASS."""
        test_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="10 passed\n", stderr="",
        )
        cov_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="TOTAL    85%\n", stderr="",
        )

        with patch("subprocess.run", side_effect=[test_result, cov_result]):
            results = []

            runner = TestRunnerSkill(command="make test")
            results.append(runner.evaluate(workspace=str(tmp_path)))

            analyzer = CoverageAnalyzerSkill(command="make coverage", threshold=80.0)
            results.append(analyzer.evaluate(workspace=str(tmp_path)))

            validator = AcceptanceValidatorSkill()
            results.append(validator.evaluate(
                workspace=str(tmp_path),
                acceptance_criteria=["password validation"],
                code_changes="def validate_password(password):",
            ))

        reporter = QAReporterSkill(policy="strict")
        report, markdown = reporter.generate_report("TEST-001", results)

        assert report.verdict == Verdict.PASS
        assert len(report.dimensions) == 3
        assert "## QA Report" in markdown
        assert "PASS" in markdown

    def test_test_failure_pipeline(self, tmp_path):
        """Simulate: tests fail → FAIL regardless of other dimensions."""
        test_result = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="8 passed, 2 failed\n", stderr="",
        )
        cov_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="TOTAL    90%\n", stderr="",
        )

        # flaky_retries=2 means 3 total attempts (1 original + 2 retries)
        fail_results = [test_result] * 3 + [cov_result]
        with patch("subprocess.run", side_effect=fail_results):
            results = []

            runner = TestRunnerSkill(command="make test", flaky_retries=2)
            results.append(runner.evaluate(workspace=str(tmp_path)))

            analyzer = CoverageAnalyzerSkill(command="make coverage", threshold=80.0)
            results.append(analyzer.evaluate(workspace=str(tmp_path)))

            validator = AcceptanceValidatorSkill()
            results.append(validator.evaluate(
                workspace=str(tmp_path),
                acceptance_criteria=[],
                code_changes="",
            ))

        reporter = QAReporterSkill(policy="strict")
        report, _ = reporter.generate_report("TEST-002", results)

        assert report.verdict == Verdict.FAIL
        assert report.dimensions[0].status == DimensionStatus.FAIL
```

- [ ] **Step 2: Run full test suite**

```bash
cd qa-agent && uv run pytest -v --tb=short
```

Expected: all tests PASSED

- [ ] **Step 3: Run coverage check**

```bash
cd qa-agent && uv run pytest --cov=src/qa_agent --cov-report=term-missing
```

Expected: coverage >= 80%

- [ ] **Step 4: Commit**

```bash
cd qa-agent && git add -A && git commit -m "feat: add integration tests for full evaluation pipeline"
```

---

### Task 14: Final Verification

- [ ] **Step 1: Run full test suite with coverage**

```bash
cd qa-agent && uv run pytest -v --cov=src/qa_agent --cov-report=term-missing --cov-fail-under=80
```

Expected: all tests pass, coverage >= 80%

- [ ] **Step 2: Verify CLI end-to-end**

```bash
cd qa-agent && uv run qa-agent evaluate \
  --workspace /tmp \
  --issue-id DEMO-001 \
  --test-command "echo '5 passed'" \
  --coverage-command "echo 'TOTAL    85%'" \
  --coverage-threshold 80 \
  --policy strict \
  --output text
```

Expected: QA Report with PASS verdict

- [ ] **Step 3: Verify JSON output**

```bash
cd qa-agent && uv run qa-agent evaluate \
  --workspace /tmp \
  --issue-id DEMO-001 \
  --test-command "echo '5 passed'" \
  --coverage-command "echo 'TOTAL    85%'" \
  --policy strict \
  --output json
```

Expected: JSON EvaluationReport with verdict "PASS"

- [ ] **Step 4: Final commit**

```bash
cd qa-agent && git add -A && git commit -m "chore: P1 QA Agent complete — 5 skills, verdict engine, CLI, integration tests"
```
