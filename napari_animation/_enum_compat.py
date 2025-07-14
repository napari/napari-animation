"""Compatibility layer for enum behavior across Python versions."""

import sys

# Check if enum.member is available (Python 3.11+)
try:
    from enum import member

    _HAS_ENUM_MEMBER = True
except ImportError:
    _HAS_ENUM_MEMBER = False

# Check if enum.member is required (Python 3.13+)
_NEEDS_ENUM_MEMBER = sys.version_info >= (3, 13)


def wrap_enum_member(value):
    """Conditionally wrap a value with enum.member if needed."""
    if _NEEDS_ENUM_MEMBER and _HAS_ENUM_MEMBER:
        return member(value)
    return value
