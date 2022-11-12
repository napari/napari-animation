from unittest.mock import patch

import numpy as np
import pytest

from napari_animation import Animation, ViewerState
from napari_animation.utils import make_thumbnail

CAPTURED_LAYER_ATTRIBUTES = [
    "name",
    "scale",
    "translate",
    "rotate",
    "shear",
    "opacity",
    "blending",
    "visible",
]


def test_animation(make_napari_viewer):
    """Test creation of an animation class."""
    viewer = make_napari_viewer()
    animation = Animation(viewer)
    assert animation is not None


def test_capture_key_frame(empty_animation):
    """Test capture of key-frame"""
    animation = empty_animation
    assert len(animation.key_frames) == 0
    animation.capture_keyframe()
    assert len(animation.key_frames) == 1
    assert animation.key_frames[0].ease


def test_set_to_key_frame(animation_with_key_frames):
    """Test Animation.set_to_key_frame()"""
    animation = animation_with_key_frames
    for i in range(2):
        animation.set_key_frame_index(i)
        assert animation.key_frames.selection.active == animation.key_frames[i]


def test_replace_keyframe(animation_with_key_frames):
    """Test Animation.set_to_key_frame()"""
    animation = animation_with_key_frames
    assert len(animation.key_frames) == 2
    animation.capture_keyframe(insert=False)
    animation.capture_keyframe(insert=False)
    animation.capture_keyframe(insert=False)
    assert len(animation.key_frames) == 2


def test_get_viewer_state(empty_animation):
    """Test ViewerState.from_viewer()"""
    animation = empty_animation
    state = ViewerState.from_viewer(animation.viewer)
    assert isinstance(state, ViewerState)


def test_set_viewer_state(animation_with_key_frames, viewer_state):
    """Test Animation._set_viewer_state()"""
    animation: Animation = animation_with_key_frames
    current_state = ViewerState.from_viewer(animation.viewer)
    viewer_state.apply(animation.viewer)

    animation_dims_state = animation.viewer.dims.dict()
    animation_camera_state = animation.viewer.camera.dict()

    assert animation_dims_state == current_state.dims
    for key in ("center", "angles", "interactive"):
        assert animation_camera_state[key] == current_state.camera[key]


def test_thumbnail_generation(empty_animation):
    """Test thumbnail generation"""
    animation = empty_animation
    shape = (32, 32, 4)
    thumbnail = make_thumbnail(
        animation.viewer.screenshot(canvas_only=True), shape
    )

    assert thumbnail.shape == shape
    assert thumbnail.dtype == np.uint8
    assert thumbnail.max() <= 255
    assert thumbnail.min() >= 0


@patch("napari_animation.animation.imsave")
@patch("imageio.get_writer")
@patch(
    "napari_animation.frame_sequence.FrameSequence.iter_frames",
    return_value=["frame"] * 30,
)
@pytest.mark.parametrize("ext", [".mp4", ".mov", ""])
def test_animate_filenames(
    frame_gen, get_writer, imsave, animation_with_key_frames, ext, tmp_path
):
    """Test that Animation.animate() produces files with correct filenames"""
    output_filename = tmp_path / f"test{ext}"
    animation_with_key_frames.animate(output_filename)
    if ext in (".mp4", ".mov"):
        expected_filename = output_filename
        saved_filename = get_writer.call_args[0][0]
        assert saved_filename == expected_filename
    elif ext == "":
        expected = [output_filename / f"test_{i:06d}.png" for i in range(30)]
        saved_files = [call[0][0] for call in imsave.call_args_list]
        assert saved_files == expected


@pytest.mark.parametrize("attribute", CAPTURED_LAYER_ATTRIBUTES)
def test_layer_attribute_capture(layer_state, attribute):
    """Test that 'attribute' is captured in the layer state dictionary"""
    for layer_state_dict in layer_state.values():
        assert attribute in layer_state_dict.keys()


def test_end_state_reached(image_animation):
    """Check that animation ends in the same state as the final key-frame"""
    image_animation.capture_keyframe()
    image_animation.viewer.dims.current_step = (28, 0)
    image_animation.capture_keyframe(steps=2)
    last_state = image_animation._frames[-1]
    assert last_state == image_animation.key_frames[-1].viewer_state
