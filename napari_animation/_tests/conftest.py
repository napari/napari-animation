"""Test configuration for sharing fixtures across multiple files with automatic
discovery at test time.
https://docs.pytest.org/en/stable/fixture.html
"""
import numpy as np
import pytest

from napari_animation import Animation, ViewerState


@pytest.fixture
def empty_animation(make_napari_viewer):
    # make_napari_viewer fixture is provided by napari
    viewer = make_napari_viewer()
    animation = Animation(viewer)
    return animation


@pytest.fixture
def animation_with_key_frames(empty_animation):
    for i in range(2):
        empty_animation.capture_keyframe()
        empty_animation.viewer.camera.zoom *= 2
    return empty_animation


@pytest.fixture
def viewer_state(empty_animation):
    return ViewerState.from_viewer(empty_animation.viewer)


@pytest.fixture
def key_frames(animation_with_key_frames):
    return animation_with_key_frames.key_frames


@pytest.fixture
def frame_sequence(animation_with_key_frames):
    return animation_with_key_frames._frames


@pytest.fixture
def image_animation(make_napari_viewer):
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((28, 28)))
    return Animation(viewer)


@pytest.fixture
def layer_state(image_animation: Animation):
    image_animation.capture_keyframe()
    return image_animation.key_frames[0].viewer_state.layers
