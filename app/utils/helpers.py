"""
Utility functions — timing decorators, JSON helpers, code sanitization.
"""

from __future__ import annotations

import json
import time
from functools import wraps
from typing import Any, Callable


def timed_execution(func: Callable) -> Callable:
    """Decorator that measures and logs function execution time."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return result

    return wrapper


def safe_json_parse(text: str, default: Any = None) -> Any:
    """Safely parse a JSON string, returning default on failure."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}


def truncate_code(code: str, max_length: int = 50000) -> str:
    """Truncate code to maximum length with indicator."""
    if len(code) <= max_length:
        return code
    return code[:max_length] + "\n\n# ... (truncated)"


def count_code_lines(code: str) -> int:
    """Count non-empty lines in code."""
    return sum(1 for line in code.splitlines() if line.strip())


def sanitize_code_input(code: str) -> str:
    """Sanitize code input by removing null bytes and normalizing newlines."""
    code = code.replace("\x00", "")
    code = code.replace("\r\n", "\n")
    return code.strip()


def format_latency(ms: float) -> str:
    """Format latency for display."""
    if ms < 1:
        return f"{ms * 1000:.0f}µs"
    elif ms < 1000:
        return f"{ms:.1f}ms"
    else:
        return f"{ms / 1000:.2f}s"
