from unittest.mock import patch

import numpy as np
import pytest
from napari._tests.utils import (
    add_layer_by_type,
    assert_layer_state_equal,
    layer_test_data,
)
from napari.layers import Surface

from napari_animation import Animation, ViewerState
from napari_animation.utils import make_thumbnail

CAPTURED_IMAGE_LAYER_ATTRIBUTES = [
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
    for key in ("center", "angles", "mouse_pan", "mouse_zoom"):
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
@pytest.mark.parametrize("ext", [".mp4", ".mov", ".gif", ""])
def test_animate_filenames(
    frame_gen, get_writer, imsave, animation_with_key_frames, ext, tmp_path
):
    """Test that Animation.animate() produces files with correct filenames"""
    output_filename = tmp_path / f"test{ext}"
    animation_with_key_frames.animate(output_filename)
    if ext in (".mp4", ".mov", ".gif"):
        expected_filename = output_filename
        saved_filename = get_writer.call_args[0][0]
        assert saved_filename == expected_filename
    elif ext == "":
        expected = [output_filename / f"test_{i:06d}.png" for i in range(30)]
        saved_files = [call[0][0] for call in imsave.call_args_list]
        assert saved_files == expected


@pytest.mark.parametrize("ext", [".mp4", ".mov", ".avi"])
def test_animation_file_metadata(animation_with_key_frames, tmp_path, ext):
    """Test output video file contians napari version metadata()"""
    animation = animation_with_key_frames
    output_filename = tmp_path / f"test{ext}"
    animation.animate(output_filename)
    # Read metadata back in, and check for napari version information
    # We expect to see a metadata line in the metadata like this:
    # title="napari version 0.4.17 https://napari.org/"
    with open(output_filename, "rb") as f:
        content = f.read()
    assert b"napari version" in content
    assert b"https://napari.org" in content


@pytest.mark.parametrize("attribute", CAPTURED_IMAGE_LAYER_ATTRIBUTES)
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


@pytest.mark.parametrize("layer_class, data, ndim", layer_test_data)
def test_attributes_for_all_layer_types(
    make_napari_viewer, layer_class, data, ndim
):
    """Test that attributes are in the viewer_state for all napari layer types"""
    viewer = make_napari_viewer()
    add_layer_by_type(viewer, layer_class, data, visible=True)
    layer_animation = Animation(viewer)
    # get the state of the layer
    layer_state = viewer.layers[0]._get_state()
    # remove attributes that arn't captured
    layer_state.pop("metadata")
    layer_state.pop("data", None)

    if layer_class == Surface:
        layer_state["normals"]["face"].pop("mode", None)
        layer_state["normals"]["vertex"].pop("mode", None)

    layer_animation.capture_keyframe()
    # get the layer attributes captured to viewer_state
    animation_state = layer_animation.key_frames[0].viewer_state.layers[
        viewer.layers[0].name
    ]

    assert_layer_state_equal(animation_state, layer_state)


@pytest.mark.parametrize("layer_class, data, ndim", layer_test_data)
def test_animating_all_layer_types(
    make_napari_viewer, layer_class, data, ndim
):
    """Test that all napari layer types can be animated"""
    viewer = make_napari_viewer()
    add_layer_by_type(viewer, layer_class, data, visible=True)
    layer_animation = Animation(viewer)
    layer_animation.capture_keyframe()
    layer_animation.viewer.camera.zoom *= 2
    layer_animation.capture_keyframe()
    # advance the movie frame, simulating slider movement
    layer_animation.set_movie_frame_index(1)
