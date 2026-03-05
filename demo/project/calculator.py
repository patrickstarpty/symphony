"""A simple calculator module.

This module intentionally has bugs and missing features for
Symphony agents to fix.
"""

from __future__ import annotations


def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide a by b.

    BUG: Does not handle division by zero!
    """
    return a / b


# TODO: Add a `power(base, exponent)` function
# TODO: Add a `factorial(n)` function
