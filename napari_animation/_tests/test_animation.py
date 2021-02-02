import pytest
from napari_animation import Animation


@pytest.fixture
def make_napari_viewer(qtbot, request):
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


def test_animation(make_napari_viewer):
    """Test creation of an animation class."""
    viewer = make_napari_viewer()
    animation = Animation(viewer)
    assert animation is not None
