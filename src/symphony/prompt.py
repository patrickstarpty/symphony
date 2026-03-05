"""Prompt renderer using Liquid templates.

Renders the workflow prompt template with issue and attempt context.
Uses python-liquid in strict mode.
"""

from __future__ import annotations

from typing import Any

from liquid import Environment as LiquidEnvironment

from symphony.log import get_logger
from symphony.models import Issue

log = get_logger(__name__)


class PromptError(Exception):
    """Raised when prompt rendering fails."""


def render_prompt(
    template_str: str,
    issue: Issue,
    attempt: int = 1,
    extra_vars: dict[str, Any] | None = None,
) -> str:
    """Render a Liquid template with issue and attempt context.

    Available template variables:
    - ``issue.id``, ``issue.identifier``, ``issue.title``, ``issue.description``
    - ``issue.state``, ``issue.labels``, ``issue.priority``, ``issue.url``
    - ``attempt`` — current attempt number (1-based)
    - Any extra variables passed via ``extra_vars``

    Args:
        template_str: Liquid template string.
        issue: The issue to render context for.
        attempt: Current attempt number.
        extra_vars: Additional template variables.

    Returns:
        Rendered prompt string.

    Raises:
        PromptError: If template rendering fails.
    """
    env = LiquidEnvironment()

    context: dict[str, Any] = {
        "issue": {
            "id": issue.id,
            "identifier": issue.identifier,
            "title": issue.title,
            "description": issue.description,
            "state": issue.state.value,
            "labels": issue.labels,
            "priority": issue.priority,
            "url": issue.url,
            "blocked_by": issue.blocked_by,
        },
        "attempt": attempt,
    }

    if extra_vars:
        context.update(extra_vars)

    try:
        template = env.from_string(template_str)
        result = template.render(**context)
    except Exception as exc:
        raise PromptError(f"Failed to render prompt template: {exc}") from exc

    log.debug("prompt_rendered", length=len(result), issue_id=issue.id, attempt=attempt)
    return result
