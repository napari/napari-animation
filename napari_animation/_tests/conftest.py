"""Test configuration for sharing fixtures across multiple files with automatic
discovery at test time.
https://docs.pytest.org/en/stable/fixture.html
"""
import pytest
import numpy as np

from napari_animation import Animation


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
    return empty_animation._get_viewer_state()


@pytest.fixture
def key_frames(animation_with_key_frames):
    return animation_with_key_frames.key_frames


@pytest.fixture
def image_animation(make_napari_viewer):
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((28, 28)))
    animation = Animation(viewer)
    return animation


@pytest.fixture
def layer_state(image_animation):
    image_animation.capture_keyframe()
    return image_animation.key_frames[0]['viewer']['layers']





