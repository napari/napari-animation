import numpy as np
import pytest

from napari_animation.easing import Easing


@pytest.mark.parametrize('easing_func', [e.value for e in Easing
                                         if e.name not in ('ELASTIC', 'BACK', 'SINE')])
def test_limits(easing_func):
    """Check that easing functions produce output between 0 and 1 for input in the same range
    """
    inputs = np.linspace(0, 1, 50, endpoint=True)
    result = [easing_func(x) for x in inputs]
    tolerance = 1e-7
    assert np.min(result) >= 0 - tolerance
    assert np.max(result) <= 1 + tolerance

