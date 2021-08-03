from contextlib import contextmanager

import numpy as np
import pytest
from napari._qt._constants import LoopMode

from napari_animation._qt import AnimationWidget
from napari_animation._qt.frameslider_widget import AnimationMovieWorker


@pytest.fixture()
def animation_widget(qtbot, make_napari_viewer):
    """basic AnimationWidget with data that we will use a few times"""
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((28, 28)))
    aw = AnimationWidget(viewer)
    qtbot.addWidget(aw)

    aw.animation.capture_keyframe()
    nz = 8
    aw.animation.capture_keyframe(steps=nz - 1)
    aw.animation._frames._current_index = 0

    return aw


@contextmanager
def make_worker(
    qtbot,
    animation_widget,
    nframes=8,
    fps=20,
    frame_range=None,
    loop_mode=LoopMode.LOOP,
):
    # sets up an AnimationMovieWorker ready for testing, and breaks down when done

    aw = animation_widget

    slider_widget = aw.frameSliderWidget
    slider_widget.loop_mode = loop_mode
    slider_widget.fps = fps
    slider_widget.frame_range = frame_range

    worker = AnimationMovieWorker(slider_widget)
    worker._count = 0
    worker.nz = len(aw.animation._frames)

    def bump(*args):
        if worker._count < nframes:
            worker._count += 1
        else:
            worker.finish()

    def count_reached():
        assert worker._count >= nframes

    def go():
        worker.work()
        qtbot.waitUntil(count_reached, timeout=6000)
        return worker.current

    worker.frame_requested.connect(bump)
    worker.go = go

    yield worker


# Each tuple represents different arguments we will pass to make_thread
# frames, fps, mode, frame_range, expected_result(nframes, nz)
CONDITIONS = [
    # regular nframes < nz
    (5, 10, LoopMode.LOOP, None, lambda x, y: x),
    # loops around to the beginning
    (10, 10, LoopMode.LOOP, None, lambda x, y: x % y),
    # loops correctly with frame_range specified
    (10, 10, LoopMode.LOOP, (2, 6), lambda x, y: x % y),
    # loops correctly going backwards
    (10, -10, LoopMode.LOOP, None, lambda x, y: y - (x % y)),
    # loops back and forth
    (10, 10, LoopMode.BACK_AND_FORTH, None, lambda x, y: x - y + 2),
    # loops back and forth, with negative fps
    (10, -10, LoopMode.BACK_AND_FORTH, None, lambda x, y: y - (x % y) - 2),
]


@pytest.mark.parametrize("nframes,fps,mode,rng,result", CONDITIONS)
def test_animation_thread_variants(
    qtbot, animation_widget, nframes, fps, mode, rng, result
):
    """This is mostly testing that AnimationMovieWorker.advance works as expected"""
    with make_worker(
        qtbot,
        animation_widget,
        fps=fps,
        nframes=nframes,
        frame_range=rng,
        loop_mode=mode,
    ) as worker:
        current = worker.go()
    if rng:
        nrange = rng[1] - rng[0] + 1
        expected = rng[0] + result(nframes, nrange)
        assert expected - 1 <= current <= expected + 1
    else:
        expected = result(nframes, worker.nz)
        # assert current == expected
        # relaxing for CI OSX tests
        assert expected - 1 <= current <= expected + 1


def test_animation_thread_once(qtbot, animation_widget):
    """Single shot animation should stop when it reaches the last frame"""
    nframes = 13
    with make_worker(
        qtbot, animation_widget, nframes=nframes, loop_mode=LoopMode.ONCE
    ) as worker:
        with qtbot.waitSignal(worker.finished, timeout=8000):
            worker.work()
    assert worker.current == worker.nz


def test_play_raises_index_errors(qtbot, animation_widget):

    # data doesn't have 20 frames
    with pytest.raises(IndexError):
        animation_widget.frameSliderWidget._play(20, frame_range=[2, 20])
        qtbot.wait(20)
        animation_widget.frameSliderWidget._stop()


def test_play_raises_value_errors(qtbot, animation_widget):
    # frame_range[1] not > frame_range[0]
    with pytest.raises(ValueError):
        animation_widget.frameSliderWidget._play(20, frame_range=[2, 2])
        qtbot.wait(20)
        animation_widget.frameSliderWidget._stop()

    # that's not a valid loop_mode
    with pytest.raises(ValueError):
        animation_widget.frameSliderWidget._play(20, loop_mode=5)
        qtbot.wait(20)
        animation_widget.frameSliderWidget._stop()
