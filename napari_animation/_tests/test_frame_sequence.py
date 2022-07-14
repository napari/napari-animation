from unittest.mock import patch

import numpy as np
import pytest

from napari_animation.frame_sequence import FrameSequence


def test_frame_seq(frame_sequence: FrameSequence):
    """Test basic indexing and length of FrameSequence."""
    # this fixture has two keyframes, with 15 steps in between
    assert len(frame_sequence) == 16

    # first and last frames are just the keyframes
    assert frame_sequence[0] == frame_sequence._key_frames[0].viewer_state
    # negative indexing works
    assert frame_sequence[-1] == frame_sequence._key_frames[-1].viewer_state

    with pytest.raises(IndexError):
        frame_sequence[1000]


def test_frame_seq_caching(frame_sequence: FrameSequence):
    """Test that we only interpolate on demand, and cache results."""
    fs = frame_sequence
    # index into the sequence and watch whether interpolate is called
    with patch(
        "napari_animation.frame_sequence.interpolate_viewer_state",
    ) as mock:
        _ = fs[5]

        # it should have been called once, and a 2 frames cached (the initial one too)
        mock.assert_called_once()

    assert len(fs._cache) == 2

    # indexing the same frame again will not require re-interpolation
    with patch(
        "napari_animation.frame_sequence.interpolate_viewer_state"
    ) as mock:
        _ = fs[5]
        mock.assert_not_called()

    fs._rebuild_keyframe_index()
    assert len(fs._cache) == 0


def test_iterframes(animation_with_key_frames, frame_sequence: FrameSequence):
    """Test that we can render frames."""

    viewer = animation_with_key_frames.viewer
    fs = frame_sequence

    for n, i in enumerate(fs.iter_frames(viewer)):
        assert isinstance(i, np.ndarray)
        _shape = i.shape
        assert _shape[-1] == 4
        if n > 4:
            break

    for n, i in enumerate(fs.iter_frames(viewer, scale_factor=0.5)):
        assert isinstance(i, np.ndarray)
        assert i.shape[:2] == (_shape[0] // 2, _shape[1] // 2)
        assert i.dtype == np.uint8
        if n > 4:
            break
