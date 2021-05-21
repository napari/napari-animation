from pathlib import Path

from napari import Viewer
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QErrorMessage,
    QFileDialog,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..animation import Animation
from .animationslider_widget import AnimationSliderWidget
from .frame_widget import FrameWidget
from .keyframelistcontrol_widget import KeyFrameListControlWidget
from .keyframeslist_widget import KeyFramesListWidget


class AnimationWidget(QWidget):
    """Widget for interatviely making animations using the napari viewer.

    Parameters
    ----------
    viewer : napari.Viewer
        napari viewer.

    Attributes
    ----------
    viewer : napari.Viewer
        napari viewer.
    animation : napari_animation.Animation
        napari-animation animation in sync with the GUI.
    """

    def __init__(self, viewer: Viewer, parent=None):
        super().__init__(parent=parent)

        # Store reference to viewer and create animation
        self.viewer = viewer
        self.animation = Animation(self.viewer)

        # Initialise User Interface
        self.keyframesListControlWidget = KeyFrameListControlWidget(
            animation=self.animation, parent=self
        )
        self.keyframesListWidget = KeyFramesListWidget(
            self.animation.key_frames, parent=self
        )
        self.frameWidget = FrameWidget(parent=self)
        self.saveButton = QPushButton("Save Animation", parent=self)
        self.animationsliderWidget = AnimationSliderWidget(
            self.animation, orientation=Qt.Horizontal, parent=self
        )

        # Create layout
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.keyframesListControlWidget)
        self.layout().addWidget(self.keyframesListWidget)
        self.layout().addWidget(self.frameWidget)
        self.layout().addWidget(self.saveButton)
        self.layout().addWidget(self.animationsliderWidget)

        # establish key bindings and callbacks
        self._add_keybind_callbacks()
        self._add_callbacks()

    def _add_keybind_callbacks(self):
        """Bind keys"""
        self._keybindings = [
            ("Alt-f", self._capture_keyframe_callback),
            ("Alt-r", self._replace_keyframe_callback),
            ("Alt-d", self._delete_keyframe_callback),
            ("Alt-a", lambda e: self.animation.key_frames.select_next()),
            ("Alt-b", lambda e: self.animation.key_frames.select_previous()),
        ]
        for key, cb in self._keybindings:
            self.viewer.bind_key(key, cb)

    def _add_callbacks(self):
        """Establish callbacks"""
        self.keyframesListControlWidget.deleteButton.clicked.connect(
            self._delete_keyframe_callback
        )
        self.keyframesListControlWidget.captureButton.clicked.connect(
            self._capture_keyframe_callback
        )
        self.saveButton.clicked.connect(self._save_callback)
        self.animationsliderWidget.valueChanged.connect(
            self._move_animationslider_callback
        )

        keyframe_list = self.animation.key_frames
        keyframe_list.events.inserted.connect(self._on_keyframes_changed)
        keyframe_list.events.removed.connect(self._on_keyframes_changed)

    def _input_state(self):
        """Get current state of input widgets as {key->value} parameters."""
        return {
            "steps": int(self.frameWidget.stepsSpinBox.value()),
            "ease": self.frameWidget.get_easing_func(),
        }

    def _capture_keyframe_callback(self, event=None):
        """Record current key-frame"""
        self.animation.capture_keyframe(**self._input_state())

    def _replace_keyframe_callback(self, event=None):
        """Replace current key-frame with new view"""
        self.animation.capture_keyframe(**self._input_state(), insert=False)
        self.animationsliderWidget.requires_update = True

    def _delete_keyframe_callback(self, event=None):
        """Delete current key-frame"""
        self.animation.key_frames.remove_selected()

    def _on_keyframes_changed(self, event=None):
        has_frames = bool(self.animation.key_frames)

        self.keyframesListControlWidget.deleteButton.setEnabled(has_frames)
        self.keyframesListWidget.setEnabled(has_frames)
        self.frameWidget.setEnabled(has_frames)
        self.animationsliderWidget.requires_update = True

    def _save_callback(self, event=None):

        if len(self.animation.key_frames) < 2:
            error_dialog = QErrorMessage()
            error_dialog.showMessage(
                f"You need at least two key frames to generate \
                an animation. Your only have {len(self.animation.key_frames)}"
            )
            error_dialog.exec_()

        else:
            filters = (
                "Video files (*.mp4 *.gif *.mov *.avi *.mpg *.mpeg *.mkv *.wmv)"
                ";;Folder of PNGs (*)"  # sep filters with ";;"
            )
            filename, _filter = QFileDialog.getSaveFileName(
                self, "Save animation", str(Path.home()), filters
            )
            if filename:
                self.animation.animate(filename)

    def _move_animationslider_callback(self, new_frame):
        """Scroll through interpolated states. Computes states if key-frames changed"""
        self.animationsliderWidget.synchronise()
        self.animation._set_viewer_state(
            self.animationsliderWidget.interpol_states[new_frame]
        )

        # This gets the index of the first key frame whose frame count is above new_frame
        n_frames = self.animationsliderWidget.cumulative_frame_count
        active_index = (n_frames > new_frame).argmax() - 1
        active_frame = self.animation.key_frames[active_index]
        self.animation.key_frames.selection.active = active_frame

    def closeEvent(self, ev) -> None:
        # release callbacks
        for key, _ in self._keybindings:
            self.viewer.bind_key(key, None)
        return super().closeEvent(ev)
