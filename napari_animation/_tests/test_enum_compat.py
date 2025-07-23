"""Tests for enum compatibility across Python versions."""

import sys
from functools import partial

from napari_animation._enum_compat import (
    _ENUM_MEMBER_AVAILABLE,
    _ENUM_MEMBER_REQUIRED,
    wrap_enum_member,
)
from napari_animation.easing import Easing
from napari_animation.interpolation.interpolation_constants import (
    Interpolation,
)


def test_enum_member_detection():
    """Test that enum.member availability is correctly detected."""
    if sys.version_info >= (3, 11):
        assert _ENUM_MEMBER_AVAILABLE is True
    else:
        assert _ENUM_MEMBER_AVAILABLE is False

    if sys.version_info >= (3, 13):
        assert _ENUM_MEMBER_REQUIRED is True
    else:
        assert _ENUM_MEMBER_REQUIRED is False


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
