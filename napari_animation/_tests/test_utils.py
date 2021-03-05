import pytest

from ..utils import (
    _interpolate_bool,
    _interpolate_float,
    _interpolate_int,
    interpolate_state,
)


@pytest.mark.parametrize("fraction", [0, 0.2, 0.4, 0.6, 0.8, 1])
def test_interpolate_state(key_frames, fraction):
    """Check that state interpolation works"""
    initial_state = key_frames[0]["viewer"]
    final_state = key_frames[1]["viewer"]
    result = interpolate_state(initial_state, final_state, fraction)
    assert len(result) == len(initial_state)
    if fraction == 0:
        assert result == initial_state
    elif fraction == 1:
        assert result == final_state
    else:
        # zoom is the only property modified in the key_frame fixture, check it
        # has been interpolated properly
        def get_zoom(state):
            return state["camera"]["zoom"]

        initial_zoom, final_zoom, result_zoom = (
            get_zoom(state) for state in (initial_state, final_state, result)
        )
        assert result_zoom == _interpolate_float(
            initial_zoom, final_zoom, fraction
        )  # noqa: E501


@pytest.mark.parametrize("a", [0.0, 0])
@pytest.mark.parametrize("b", [1.0, 1])
@pytest.mark.parametrize("fraction", [0, 0.0, 0.5, 1.0, 1])
def test_interpolate_float(a, b, fraction):
    """Check that interpolation of floats produces valid output"""
    result = _interpolate_float(a, b, fraction)
    assert isinstance(result, float)
    assert result == fraction


@pytest.mark.parametrize("a", [0.0, 0])
@pytest.mark.parametrize("b", [100.0, 100])
@pytest.mark.parametrize("fraction", [0, 0.0, 0.5, 1.0, 1])
def test_interpolate_int(a, b, fraction):
    """Check that integer interpolation produces integers"""
    result = _interpolate_int(a, b, fraction)
    assert isinstance(result, int)
    assert result == fraction * b


@pytest.mark.parametrize("a", [True, False])
@pytest.mark.parametrize("b", [True, False])
@pytest.mark.parametrize("fraction", [0, 0.25, 0.75, 1])
def test_interpolate_bool(a, b, fraction):
    result = _interpolate_bool(a, b, fraction)
    if fraction < 0.5:
        assert result == a
    else:
        assert result == b
