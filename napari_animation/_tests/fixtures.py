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
