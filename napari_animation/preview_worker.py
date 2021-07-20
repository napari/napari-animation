from napari.utils.events import Event
from qtpy.QtCore import QObject, QTimer, Signal, Slot


class PreviewWorker(QObject):
    """Preview the animation using the napari viewer.

    Parameters
    ----------
    animation : Animation
        parent animation object
    fps : float
        frames per second
    frame_range : tuple
        range of frames to preview
    """

    frame_requested = Signal(int)
    finished = Signal()
    started = Signal()

    def __init__(self, animation, fps, frame_range):
        super().__init__()
        self.animation = animation
        self.interval = 1000 / abs(fps)
        self.frame_range = frame_range
        self.current_index = frame_range[0]

        # ÷ so that current_frame follows the last set frame index
        self.animation._frames.events._current_index.connect(
            self._on_frame_changed
        )

        self.timer = QTimer()

    @Slot()
    def work(self):
        """Play the animation."""

        self.frame_requested.emit(self.current_index)
        self.timer.singleShot(int(self.interval), self.advance)
        self.advance()
        self.started.emit()

    def advance(self):
        """Advance the current frame in the animation.
        Restricts the animation to the requested frame_range,
        if entered.
        """
        self.current_index += 1

        if self.current_index > self.frame_range[1]:
            return self.finish()

        self.frame_requested.emit(self.current_index)
        self.timer.singleShot(int(self.interval), self.advance)

    @Slot(Event)
    def _on_frame_changed(self, event):
        """Update the current frame if the set frame has changed (from slider or programmatically)."""
        # slot for external events to update the current frame
        self.current_index = event.value

    def finish(self):
        """Emit the finished event signal."""
        self.finished.emit()
