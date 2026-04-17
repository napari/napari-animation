import numpy as np

from napari_animation._qt import AnimationWidget


def test_animation_widget(make_napari_viewer, qtbot):
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((28, 28)))
    aw = AnimationWidget(viewer)
    qtbot.addWidget(aw)

    aw._capture_keyframe_callback()
    assert len(aw.animation.key_frames) == 1
    aw._capture_keyframe_callback()
    assert len(aw.animation.key_frames) == 2
    aw._replace_keyframe_callback()
    assert len(aw.animation.key_frames) == 2
    aw._delete_keyframe_callback()
    assert len(aw.animation.key_frames) == 1
