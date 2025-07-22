"""Compatibility layer for enum behavior across Python versions.

Python 3.13 introduced stricter enum handling requiring `enum.member()` wrapper for callable values. See https://docs.python.org/3/library/enum.html.
This compatibility layer detects Python version and conditionally wraps enum values.
- Python 3.10:
- Python 3.11 added `member`
- Python 3.13+: EnumDict is added, and member is required. See
  https://docs.python.org/3/whatsnew/3.13.html#enum

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
        # Needed for Python 3.11+
        return member(value)
    # python 3.10 common case
    return value
