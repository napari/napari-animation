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
    _ENUM_MEMBER_AVAILABLE = True
except ImportError:
    # Python 3.10 has no member support
    _ENUM_MEMBER_AVAILABLE = False

# Check if enum.member is required (Python 3.13+)
_ENUM_MEMBER_REQUIRED = sys.version_info >= (3, 13)


def wrap_enum_member(value):
    """Conditionally wrap a value with enum.member if needed."""
    # Enum member is required for Python 3.13+, and available for 3.11+
    if _ENUM_MEMBER_REQUIRED or _ENUM_MEMBER_AVAILABLE:
        return member(value)
    # For python 3.10 and older, just return the value directly
    if not _ENUM_MEMBER_AVAILABLE:
        return value
