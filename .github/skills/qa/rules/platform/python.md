# Python Testing Rules — P2

> Applied by generating-api-tests and generating-perf-tests when target is Python.

## Type Hints

- All function signatures in test code must include type hints:
  - ✅ `def create_policy(user_id: str, premium: float) -> Policy:`
  - ❌ `def create_policy(user_id, premium):`
- Use `from __future__ import annotations` for forward references
- Return type must be specified:
  - ✅ `def setup() -> None:`
  - ❌ `def setup():`
- Collections must be parameterized:
  - ✅ `list[str]`, `dict[str, int]`
  - ❌ `list`, `dict`

## Docstrings

- Every test class and test function must have a docstring:
  ```python
  def test_policy_renewal_with_valid_dates(policy_fixture):
      """Verify policy renewal succeeds when dates are valid and consecutive.

      Given a policy with expiration date 2024-12-31,
      When renewal is requested for 2024-01-01,
      Then renewal succeeds and new expiration is 2025-12-31.
      """
  ```
- Docstring must describe the Given-When-Then scenario
- Never leave docstrings as `"""..."""` (placeholder)

## Virtual Environment

- All projects must use venv:
  - `python -m venv venv`
  - Activate: `. venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
- requirements.txt or pyproject.toml must pin all test dependencies:
  - ✅ `pytest==7.4.0`
  - ❌ `pytest` (unpinned)
- Test dependencies must be in a separate group (e.g., `[dev]` in pyproject.toml):
  ```toml
  [project.optional-dependencies]
  dev = ["pytest==7.4.0", "pytest-cov==4.1.0"]
  ```

## Import Ordering

- Follow isort convention (stdlib → third-party → local):
  ```python
  import json
  from typing import Any

  import pytest
  from pydantic import BaseModel

  from app.models import Policy
  from app.services import PolicyService
  ```
- No wildcard imports (`from app import *`)

## Async Testing (pytest-asyncio)

- Use `@pytest.mark.asyncio` for async test functions:
  ```python
  @pytest.mark.asyncio
  async def test_async_policy_fetch():
      result = await policy_service.fetch_by_id("123")
      assert result is not None
  ```
- Fixtures that return coroutines must be `async`:
  ```python
  @pytest.fixture
  async def async_client():
      async with AsyncClient() as client:
          yield client
  ```

## Mocking & Fixtures

- Use `pytest` fixtures, not bare setup/teardown:
  - ✅ `@pytest.fixture` with `yield`
  - ❌ `setUp()` / `tearDown()` methods
- Mock external dependencies:
  ```python
  @pytest.fixture
  def mock_email_service(monkeypatch):
      mock = Mock()
      mock.send.return_value = True
      monkeypatch.setattr('app.services.email_service', mock)
      return mock
  ```

## Assertions

- Use `assert` statements (not `self.assertEqual`):
  - ✅ `assert result.status == "active"`
  - ❌ `self.assertEqual(result.status, "active")`
- For complex objects, use `pytest.approx()` for floats:
  - ✅ `assert premium == pytest.approx(199.99, abs=0.01)`
  - ❌ `assert premium == 199.99` (fragile with floats)

## Error Testing

- Use `pytest.raises()` context manager:
  ```python
  with pytest.raises(ValueError, match="Premium must be positive"):
      Policy.create(premium=-100)
  ```
