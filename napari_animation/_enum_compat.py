"""Compatibility layer for enum behavior across Python versions.

Python 3.13 introduced stricter enum handling requiring `enum.member()` wrapper for callable values.
This compatibility layer detects Python version and conditionally wraps enum values.
- Python 3.10:
- Python 3.11 added `member`
- Python 3.13+: No wrapper required.

Enum members have a name and a value.
"""

import sys

# Check if member is importable
try:
    from enum import member

    # member is importable (Python 3.11+)
    _HAS_ENUM_MEMBER = True
except ImportError:
    # Python 3.10 has no member support
    _HAS_ENUM_MEMBER = False

# Check if enum.member is required (Python 3.13+)
_NEEDS_ENUM_MEMBER = sys.version_info >= (3, 13)


def wrap_enum_member(value):
    """Conditionally wrap a value with enum.member if needed."""
    if _NEEDS_ENUM_MEMBER:
        if not _HAS_ENUM_MEMBER:
            raise RuntimeError(
                f"Python {sys.version_info[:2]} requires enum.member but it's not available. "
                "Please upgrade your Python installation."
            )
        return member(value)
    return value
