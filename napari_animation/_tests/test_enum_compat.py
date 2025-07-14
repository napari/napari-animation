"""Tests for enum compatibility across Python versions."""

import sys
from functools import partial
from unittest.mock import patch

from napari_animation._enum_compat import (
    _HAS_ENUM_MEMBER,
    _NEEDS_ENUM_MEMBER,
    wrap_enum_member,
)
from napari_animation.easing import Easing
from napari_animation.interpolation.interpolation_constants import (
    Interpolation,
)


def test_enum_member_detection():
    """Test that enum.member availability is correctly detected."""
    if sys.version_info >= (3, 11):
        assert _HAS_ENUM_MEMBER is True
    else:
        assert _HAS_ENUM_MEMBER is False

    if sys.version_info >= (3, 13):
        assert _NEEDS_ENUM_MEMBER is True
    else:
        assert _NEEDS_ENUM_MEMBER is False


def test_wrap_enum_member_basic():
    """Test basic wrap_enum_member functionality."""

    def test_func(x):
        return x * 2

    partial_func = partial(test_func)
    wrapped = wrap_enum_member(partial_func)

    # The wrapped function should behave the same when called through enum
    from enum import Enum

    class TestEnum(Enum):
        TEST = wrapped

        def __call__(self, *args):
            return self.value(*args)

    result = TestEnum.TEST(5)
    assert result == 10


def test_wrap_enum_member_python_310_simulation():
    """Test wrap_enum_member behavior simulating Python 3.10."""

    def test_func(x):
        return x * 2

    partial_func = partial(test_func)

    # Simulate Python 3.10 environment
    with patch(
        "napari_animation._enum_compat._NEEDS_ENUM_MEMBER", False
    ), patch("napari_animation._enum_compat._HAS_ENUM_MEMBER", False):
        wrapped = wrap_enum_member(partial_func)

        # Should return the original partial function
        assert wrapped is partial_func
        assert wrapped(5) == 10


def test_wrap_enum_member_python_313_simulation():
    """Test wrap_enum_member behavior simulating Python 3.13."""

    def test_func(x):
        return x * 2

    partial_func = partial(test_func)

    # Simulate Python 3.13 environment
    with patch(
        "napari_animation._enum_compat._NEEDS_ENUM_MEMBER", True
    ), patch("napari_animation._enum_compat._HAS_ENUM_MEMBER", True):
        # Mock enum.member if not available
        if not _HAS_ENUM_MEMBER:
            with patch("napari_animation._enum_compat.member") as mock_member:
                mock_member.return_value = f"wrapped_{partial_func}"
                wrapped = wrap_enum_member(partial_func)
                mock_member.assert_called_once_with(partial_func)
                assert wrapped == f"wrapped_{partial_func}"
        else:
            wrapped = wrap_enum_member(partial_func)
            # Should return enum.member wrapped version
            assert type(wrapped).__name__ == "member"


def test_easing_enum_functionality():
    """Test that the Easing enum works correctly with the compatibility fix."""
    # Test that all easing functions are callable
    for easing in Easing:
        result = easing(0.5)
        assert isinstance(result, int | float)
        assert (
            0 <= result <= 1.5
        )  # Some easing functions can go slightly above 1

    # Test specific easing functions
    assert Easing.LINEAR(0.5) == 0.5
    assert Easing.LINEAR(0.0) == 0.0
    assert Easing.LINEAR(1.0) == 1.0


def test_interpolation_enum_functionality():
    """Test that the Interpolation enum works correctly with the compatibility fix."""
    # Test DEFAULT interpolation
    result = Interpolation.DEFAULT(0.0, 1.0, 0.5)
    assert result == 0.5

    # Test BOOL interpolation
    result = Interpolation.BOOL(False, True, 0.5)
    assert result is True

    result = Interpolation.BOOL(False, True, 0.0)
    assert result is False


def test_enum_member_access():
    """Test that enum members can be accessed properly."""
    # Test that we can access the underlying partial function
    linear_func = Easing.LINEAR.value
    assert callable(linear_func)
    assert linear_func(0.5) == 0.5

    # Test that enum comparison works
    assert Easing.LINEAR == Easing.LINEAR
    assert Easing.LINEAR != Easing.QUADRATIC

    # Test that enum iteration works
    easing_names = [e.name for e in Easing]
    assert "LINEAR" in easing_names
    assert "QUADRATIC" in easing_names
    assert len(easing_names) == 10


def test_enum_in_collection():
    """Test that enums work correctly in collections."""
    # Test that we can use enums in lists
    easing_list = [Easing.LINEAR, Easing.QUADRATIC]
    assert len(easing_list) == 2
    assert Easing.LINEAR in easing_list

    # Test that we can use enums in dictionaries
    easing_dict = {Easing.LINEAR: "linear", Easing.QUADRATIC: "quadratic"}
    assert easing_dict[Easing.LINEAR] == "linear"
