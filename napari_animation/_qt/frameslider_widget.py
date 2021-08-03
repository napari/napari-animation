from typing import Optional, Tuple

from napari._qt._constants import LoopMode
from napari._qt.qthreading import _new_worker_qthread
from napari._qt.widgets.qt_scrollbar import ModifiedScrollBar
from napari.utils.translations import trans
from qtpy.QtCore import QObject, Qt, QTimer, Signal, Slot
from qtpy.QtWidgets import QFrame, QHBoxLayout, QWidget

from .playbutton_widget import QtPlayButton


class QtFrameSliderWidget(QWidget):
    """Compound widget to hold the label, slider and play button for a frame sequence."""

    fps_changed = Signal(float)
    mode_changed = Signal(str)
    range_changed = Signal(tuple)
    play_started = Signal()
    play_stopped = Signal()

    def __init__(self, parent: QWidget, frames, viewer):
        super().__init__(parent=parent)
        self.viewer = viewer
        self.frames = frames
        self.slider = None
        self.play_button = None

        sep = QFrame(self)
        sep.setFixedSize(1, 14)

        self._fps = 20
        self._loop_mode = LoopMode.ONCE

        self._minframe = None
        self._maxframe = None

        self._thread = None
        self._worker = None

        layout = QHBoxLayout()

        self._create_range_slider_widget()
        self._update_range()
        self.frames.events.nframes.connect(self._nframes_changed)
        self._create_play_button_widget()

        layout.addWidget(self.play_button)
        layout.addWidget(self.slider, stretch=1)
        layout.addWidget(sep)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignVCenter)
        self.setLayout(layout)

    def _value_changed(self, value):
        """Slider changed to this new value.
        We split this out as a separate function for perfmon.
        """
        self.frames.set_movie_frame_index(self.viewer, value)

    def _nframes_changed(self, event):
        self._update_range()
        frame_range = None if event.value <= 1 else (0, event.value - 1)
        self.frame_range = frame_range

    def _create_range_slider_widget(self):
        """Creates a range slider widget:"""
        slider = ModifiedScrollBar(Qt.Horizontal)
        slider.setFocusPolicy(Qt.NoFocus)
        slider.setMinimum(0)
        slider.setMaximum(max(self.nframes - 1, 0))
        slider.setSingleStep(1)
        slider.setPageStep(1)
        slider.setToolTip("Scroll through animation")
        slider.setValue(self.frames._current_index)

        # Listener to be used for sending events back to model:
        slider.valueChanged.connect(self._value_changed)
        self.frames.events._current_index.connect(
            lambda x: self._update_slider()
        )

        self.slider = slider

    def _create_play_button_widget(self):
        """Creates the actual play button, which has the modal popup."""
        self.play_button = QtPlayButton(fps=self._fps, mode=self._loop_mode)

        self.play_button.mode_combo.activated[str].connect(
            lambda x: self.__class__.loop_mode.fset(
                self, LoopMode(x.replace(" ", "_"))
            )
        )

        def fps_listener(*args):
            fps = self.play_button.fpsspin.value()
            fps *= -1 if self.play_button.reverse_check.isChecked() else 1
            self.__class__.fps.fset(self, fps)

        self.play_button.fpsspin.editingFinished.connect(fps_listener)
        self.play_button.reverse_check.stateChanged.connect(fps_listener)
        self.play_button.play_requested.connect(self._play)
        self.play_button.stop_requested.connect(self._stop)
        self.play_stopped.connect(self.play_button._handle_stop)
        self.play_started.connect(self.play_button._handle_start)

    def _update_range(self):
        """Updates range for slider."""

        nsteps = self.nframes - 1

        if nsteps <= 0:
            self.hide()
        else:
            self.show()
            self.slider.setMinimum(0)
            self.slider.setMaximum(nsteps)
            self.slider.setSingleStep(1)
            self.slider.setPageStep(1)
            self.slider.setValue(self.frames._current_index)

    def _update_slider(self):
        """Update slider."""
        self.slider.blockSignals(True)
        self.slider.setValue(self.frames._current_index)
        self.slider.blockSignals(False)

    @property
    def nframes(self):
        return len(self.frames)

    @property
    def frame_range(self):
        """Frame range for animation, as (minimum_frame, maximum_frame)."""
        frame_range = (self._minframe, self._maxframe)
        frame_range = frame_range if any(frame_range) else None
        return frame_range

    @frame_range.setter
    def frame_range(self, frame_range):
        """Frame range for animation, as (minimum_frame, maximum_frame).
        Parameters
        ----------
        frame_range : tuple(int, int)
            Frame range as tuple/list with range (minimum_frame, maximum_frame)
        """
        if not isinstance(frame_range, (tuple, list, type(None))):
            raise TypeError(
                trans._("frame_range value must be a list or tuple")
            )

        if frame_range and not len(frame_range) == 2:
            raise ValueError(trans._("frame_range must have a length of 2"))

        if frame_range is None:
            frame_range = (None, None)

        else:
            if frame_range[0] >= frame_range[1]:
                raise ValueError(
                    trans._("frame_range[0] must be <= frame_range[1]")
                )
            if frame_range[0] < 0:
                raise IndexError(trans._("frame_range[0] out of range"))
            if frame_range[1] > self.nframes - 1:
                raise IndexError(trans._("frame_range[1] out of range"))

        self._minframe, self._maxframe = frame_range
        self.range_changed.emit(tuple(frame_range))

    @property
    def fps(self):
        """Frames per second for animation."""
        return self._fps

    @fps.setter
    def fps(self, value):
        """Frames per second for animation.
        Parameters
        ----------
        value : float
            Frames per second for animation.
        """
        self._fps = value
        self.play_button.fpsspin.setValue(abs(value))
        self.play_button.reverse_check.setChecked(value < 0)
        self.fps_changed.emit(value)

    @property
    def loop_mode(self):
        """Loop mode for animation.
        Loop mode enumeration from napari._qt._constants.LoopMode
        Available options for the loop mode string enumeration are:
        - LoopMode.ONCE
            Animation will stop once movie reaches the max frame
            (if fps > 0) or the first frame (if fps < 0).
        - LoopMode.LOOP
            Movie will return to the first frame after reaching
            the last frame, looping continuously until stopped.
        - LoopMode.BACK_AND_FORTH
            Movie will loop continuously until stopped,
            reversing direction when the maximum or minimum frame
            has been reached.
        """
        return self._loop_mode

    @loop_mode.setter
    def loop_mode(self, value):
        """Loop mode for animation.
        Parameters
        ----------
        value : napari._qt._constants.LoopMode
            Loop mode for animation.
            Available options for the loop mode string enumeration are:
            - LoopMode.ONCE
                Animation will stop once movie reaches the max frame
                (if fps > 0) or the first frame (if fps < 0).
            - LoopMode.LOOP
                Movie will return to the first frame after reaching
                the last frame, looping continuously until stopped.
            - LoopMode.BACK_AND_FORTH
                Movie will loop continuously until stopped,
                reversing direction when the maximum or minimum frame
                has been reached.
        """
        if value is not None:
            _modes = LoopMode.keys()
            if value not in LoopMode and value not in _modes:
                raise ValueError(
                    trans._(
                        "loop_mode must be one of {_modes}. Got: {loop_mode}",
                        _modes=_modes,
                        loop_mode=value,
                    )
                )

            loop_mode = LoopMode(value)

        self._loop_mode = loop_mode
        self.play_button.mode_combo.setCurrentText(
            str(value).replace("_", " ")
        )
        self.mode_changed.emit(str(value))

    def _update_play_settings(self, fps, loop_mode, frame_range):
        """Update settings for animation.
        Parameters
        ----------
        fps : float
            Frames per second to play the animation.
        loop_mode : napari._qt._constants.LoopMode
            Loop mode for animation.
            Available options for the loop mode string enumeration are:
            - LoopMode.ONCE
                Animation will stop once movie reaches the max frame
                (if fps > 0) or the first frame (if fps < 0).
            - LoopMode.LOOP
                Movie will return to the first frame after reaching
                the last frame, looping continuously until stopped.
            - LoopMode.BACK_AND_FORTH
                Movie will loop continuously until stopped,
                reversing direction when the maximum or minimum frame
                has been reached.
        frame_range : tuple(int, int)
            Frame range as tuple/list with range (minimum_frame, maximum_frame)
        """
        if fps is not None:
            self.fps = fps
        if loop_mode is not None:
            self.loop_mode = loop_mode
        if frame_range is not None:
            self.frame_range = frame_range

    def _play(
        self,
        fps: Optional[float] = None,
        loop_mode: Optional[str] = None,
        frame_range: Optional[Tuple[int, int]] = None,
    ):
        """Animate (play) axis.

        Parameters
        ----------
        fps : float
            Frames per second for animation.
        loop_mode : napari._qt._constants.LoopMode
            Loop mode for animation.
            Available options for the loop mode string enumeration are:
            - LoopMode.ONCE
                Animation will stop once movie reaches the max frame
                (if fps > 0) or the first frame (if fps < 0).
            - LoopMode.LOOP
                Movie will return to the first frame after reaching
                the last frame, looping continuously until stopped.
            - LoopMode.BACK_AND_FORTH
                Movie will loop continuously until stopped,
                reversing direction when the maximum or minimum frame
                has been reached.
        frame_range : tuple(int, int)
            Frame range as tuple/list with range (minimum_frame, maximum_frame)
        """

        self._update_play_settings(fps, loop_mode, frame_range)

        # setting fps to 0 just stops the animation
        if self.fps == 0:
            return

        worker, thread = _new_worker_qthread(
            AnimationMovieWorker,
            self,
            _start_thread=True,
            _connect={
                "frame_requested": lambda x: self.frames.set_movie_frame_index(
                    self.viewer, x
                )
            },
        )

        thread.finished.connect(self._stop)
        self._worker = worker
        self._thread = thread
        self.play_started.emit()

        return worker, thread

    def _stop(self):
        """Stop animation"""

        if self._thread:
            self._thread.quit()
            self._thread.wait()
        self._thread = None
        self._worker = None
        self.play_stopped.emit()


class AnimationMovieWorker(QObject):
    """A thread to keep the animation timer independent of the main event loop.
    This prevents mouseovers and other events from causing animation lag.
    """

    frame_requested = Signal(int)  # frame
    finished = Signal()
    started = Signal()

    def __init__(self, slider):
        super().__init__()

        self.loop_mode = slider.loop_mode
        slider.fps_changed.connect(self.set_fps)
        slider.mode_changed.connect(self.set_loop_mode)
        slider.range_changed.connect(self.set_frame_range)
        slider.frames.events._current_index.connect(self._on_slider_moved)

        self.slider = slider
        self.set_fps(slider.fps)
        self.set_frame_range(slider.frame_range)

        self.current = max(self.slider.frames._current_index, self.min_point)
        self.current = min(self.current, self.max_point)
        self.timer = QTimer()

    @Slot()
    def work(self):
        """Play the animation."""
        # if loop_mode is once and we are already on the last frame,
        # return to the first frame... (so the user can keep hitting once)

        if self.loop_mode == LoopMode.ONCE:
            if self.step > 0 and self.current >= self.max_point - 1:
                self.frame_requested.emit(self.min_point)
            elif self.step < 0 and self.current <= self.min_point + 1:
                self.frame_requested.emit(self.max_point)
            self.timer.singleShot(int(self.interval), self.advance)
        else:
            # immediately advance one frame
            self.advance()
        self.started.emit()

    @Slot(float)
    def set_fps(self, fps):
        """Set the frames per second value for the animation.
        Parameters
        ----------
        fps : float
            Frames per second for the animation.
        """
        if fps == 0:
            return self.finish()
        self.step = 1 if fps > 0 else -1  # negative fps plays in reverse
        self.interval = 1000 / abs(fps)

    @Slot(tuple)
    def set_frame_range(self, frame_range):
        """Frame range for animation, as (minimum_frame, maximum_frame).
        Parameters
        ----------
        frame_range : tuple(int, int)
            Frame range as tuple/list with range (minimum_frame, maximum_frame)
        """
        self.nframes = self.slider.nframes
        self.frame_range = frame_range

        if self.frame_range is not None:
            self.min_point, self.max_point = self.frame_range
        else:
            self.min_point = 0
            self.max_point = int(self.nframes - 1)
        self.max_point += 1  # range is inclusive

    @Slot(str)
    def set_loop_mode(self, mode):
        """Set the loop mode for the animation.
        Parameters
        ----------
        mode : str
            Loop mode for animation.
            Available options for the loop mode string enumeration are:
            - LoopMode.ONCE
                Animation will stop once movie reaches the max frame
                (if fps > 0) or the first frame (if fps < 0).
            - LoopMode.LOOP
                Movie will return to the first frame after reaching
                the last frame, looping continuously until stopped.
            - LoopMode.BACK_AND_FORTH
                Movie will loop continuously until stopped,
                reversing direction when the maximum or minimum frame
                has been reached.
        """
        self.loop_mode = LoopMode(mode)

    def advance(self):
        """Advance the current frame in the animation.
        Takes the total number of frames into account and restricts the animation to the
        requested frame_range, if entered.
        """
        self.current += self.step

        if self.current < self.min_point:
            if (
                self.loop_mode == LoopMode.BACK_AND_FORTH
            ):  # 'loop_back_and_forth'
                self.step *= -1
                self.current = self.min_point + self.step
            elif self.loop_mode == LoopMode.LOOP:  # 'loop'
                self.current = self.max_point + self.current - self.min_point
            else:  # loop_mode == 'once'
                return self.finish()
        elif self.current >= self.max_point:
            if (
                self.loop_mode == LoopMode.BACK_AND_FORTH
            ):  # 'loop_back_and_forth'
                self.step *= -1
                self.current = self.max_point + 2 * self.step
            elif self.loop_mode == LoopMode.LOOP:  # 'loop'
                self.current = self.min_point + self.current - self.max_point
            else:  # loop_mode == 'once'
                return self.finish()
        with self.slider.frames.events._current_index.blocker(
            self._on_slider_moved
        ):
            self.frame_requested.emit(self.current)

        # using a singleShot timer here instead of timer.start() because
        # it makes it easier to update the interval using signals/slots
        self.timer.singleShot(int(self.interval), self.advance)

    def finish(self):
        """Emit the finished event signal."""
        self.finished.emit()

    def _on_slider_moved(self, event):
        """Update the current frame if the user moved the slider."""
        # slot for external events to update the current frame
        self.current = self.slider.frames._current_index
