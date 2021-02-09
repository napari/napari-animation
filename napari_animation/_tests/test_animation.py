from unittest.mock import patch

import numpy as np
import pytest

from napari_animation import Animation


@pytest.fixture
def make_napari_viewer():
    from napari import Viewer
    viewers = []

    def actual_factory(*model_args, viewer_class=Viewer, **model_kwargs):
        model_kwargs.setdefault('show', False)
        viewer = viewer_class(*model_args, **model_kwargs)
        viewers.append(viewer)
        return viewer

    yield actual_factory

    for viewer in viewers:
        viewer.close()


@pytest.fixture
def empty_animation(make_napari_viewer):
    viewer = make_napari_viewer()
    animation = Animation(viewer)
    return animation


@pytest.fixture
def animation_with_keyframes(empty_animation):
    for i in range(2):
        empty_animation.capture_keyframe()
        empty_animation.viewer.camera.zoom *= 2
    return empty_animation


@pytest.fixture
def viewer_state(empty_animation):
    return empty_animation._get_viewer_state()


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
    assert 'viewer' in animation.key_frames[0].keys()


def test_set_to_key_frame(animation_with_keyframes):
    """Test Animation.set_to_key_frame()"""
    animation = animation_with_keyframes
    for i in range(2):
        animation.set_to_keyframe(i)
        assert animation.frame == i


def test_get_viewer_state(empty_animation):
    """Test Animation._get_viewer_state()"""
    animation = empty_animation
    state = animation._get_viewer_state()
    assert isinstance(state, dict)
    assert all([item in state.keys() for item in ('camera', 'dims')])

    # check that log transform has been applied to zoom
    assert state['camera']['zoom'] == np.log10(animation.viewer.camera.zoom)


def test_set_viewer_state(animation_with_keyframes, viewer_state):
    """Test Animation._set_viewer_state()"""
    animation = animation_with_keyframes
    current_state = animation._get_viewer_state()
    animation._set_viewer_state(viewer_state)

    animation_dims_state = animation.viewer.dims.asdict()
    animation_camera_state = animation.viewer.camera.asdict()

    assert animation_dims_state == current_state['dims']
    for key in ('center', 'angles', 'interactive'):
        assert animation_camera_state[key] == current_state['camera'][key]

    # check that log transform is undone on zoom
    assert animation_camera_state['zoom'] == np.power(10, current_state['camera']['zoom'])


def test_thumbnail_generation(empty_animation):
    """Test thumbnail generation"""
    animation = empty_animation
    thumbnail = animation._generate_thumbnail()

    assert thumbnail.shape == animation._thumbnail_shape
    assert thumbnail.dtype == np.uint8
    assert thumbnail.max() <= 255
    assert thumbnail.min() >= 0


@patch('napari_animation.animation.imsave')
@patch('imageio.get_writer')
@patch('napari_animation.Animation._frame_generator', return_value=['frame'] * 30)
@pytest.mark.parametrize('ext', ['.mp4', '.mov', ''])
def test_animate_filenames(frame_gen, get_writer, imsave, animation_with_keyframes, ext,
                           tmp_path):
    """Test that Animation.animate() produces files with the correct filenames"""
    output_filename = tmp_path / f'test{ext}'
    animation_with_keyframes.animate(output_filename)
    if ext in ('.mp4', '.mov'):
        expected_filename = output_filename
        saved_filename = get_writer.call_args[0][0]
        assert saved_filename == expected_filename
    elif ext == '':
        expected = [output_filename / f'test_{i}.png' for i in range(30)]
        saved_files = ([call[0][0] for call in imsave.call_args_list])
        assert saved_files == expected
