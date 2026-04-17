from dataclasses import dataclass

import numpy as np

from napari_animation._qt import AnimationTimelineWidget, AnimationWidget


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


def test_animation_timeline_widget(make_napari_viewer, qtbot):
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((28, 28)))
    aw = AnimationTimelineWidget(viewer)
    qtbot.addWidget(aw)

    animation = aw.timeline.animation
    track = animation.add_track('viewer')
    viewer.camera.zoom = 10.0
    animation.add_keyframe_from_state('viewer', 0)
    assert len(track.keyframes) == 1
    viewer.camera.zoom = 20.0
    animation.add_keyframe_from_state('viewer', 10)
    assert len(track.keyframes) == 2
    animation.add_keyframe_from_state('viewer', 20)
    assert len(track.keyframes) == 3

    animation.current_frame = 5
    assert viewer.camera.zoom == 15.0


def test_timeline_custom_track(make_napari_viewer, qtbot):
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((28, 28)))
    aw = AnimationTimelineWidget(viewer)
    qtbot.addWidget(aw)

    @dataclass
    class Thing:
        x: int = 1

    thing = Thing()

    aw.add_custom_track('x', thing, 'x')
    animation = aw.timeline.animation

    track = animation.add_track('x')
    animation.add_keyframe_from_state('x', 0)
    assert track.keyframes[0].t == 0
    assert track.keyframes[0].value == 1
    thing.x = 2
    animation.add_keyframe_from_state('x', 10)
    assert track.keyframes[1].t == 10
    assert track.keyframes[1].value == 2
