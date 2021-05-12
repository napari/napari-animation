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

        # Initialise UI
        self._init_ui()

        # establish key bindings and callbacks
        self._add_keybind_callbacks()
        self._add_callbacks()

    def _init_ui(self):
        """Initialise user interface"""
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self._init_keyframes_list_control_widget()
        self._init_keyframes_list_widget()
        self._init_frame_widget()
        self._init_save_button()
        self._init_animation_slider_widget()

    def _add_keybind_callbacks(self):
        """Bind keys"""

        self.animation.viewer.bind_key(
            "Alt-f", self._capture_keyframe_callback
        )
        self.animation.viewer.bind_key(
            "Alt-r", self._replace_keyframe_callback
        )
        self.animation.viewer.bind_key("Alt-d", self._delete_keyframe_callback)

        self.animation.viewer.bind_key("Alt-a", self._key_adv_frame)
        self.animation.viewer.bind_key("Alt-b", self._key_back_frame)

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
        self.viewer.events.theme.connect(
            lambda e: self.keyframesListWidget._update_theme(e.value)
        )

    def _release_callbacks(self):
        """Release keys"""

        self.animation.viewer.bind_key("Alt-f", None)
        self.animation.viewer.bind_key("Alt-r", None)
        self.animation.viewer.bind_key("Alt-d", None)

        self.animation.viewer.bind_key("Alt-a", None)
        self.animation.viewer.bind_key("Alt-b", None)

    def _init_frame_widget(self):
        self.frameWidget = FrameWidget(parent=self)
        self._layout.addWidget(self.frameWidget)

    def _init_keyframes_list_control_widget(self):
        self.keyframesListControlWidget = KeyFrameListControlWidget(
            animation=self.animation, parent=self
        )
        self._layout.addWidget(self.keyframesListControlWidget)

    def _init_keyframes_list_widget(self):
        self.keyframesListWidget = KeyFramesListWidget(
            self.animation, parent=self
        )
        self.keyframesListWidget._update_theme(self.viewer.theme)
        self._layout.addWidget(self.keyframesListWidget)

    def _init_save_button(self):
        self.saveButton = QPushButton("Save Animation", parent=self)
        self._layout.addWidget(self.saveButton)

    def _init_animation_slider_widget(self):
        self.animationsliderWidget = AnimationSliderWidget(
            self.animation, orientation=Qt.Horizontal, parent=self
        )
        self._layout.addWidget(self.animationsliderWidget)

    def _get_interpolation_steps(self):
        return int(self.frameWidget.stepsSpinBox.value())

    def _get_easing_function(self):
        return self.frameWidget.get_easing_func()

    def _capture_keyframe_callback(self, event=None):
        """Record current key-frame"""
        self.animation.capture_keyframe(
            steps=self._get_interpolation_steps(),
            ease=self._get_easing_function(),
        )
        if len(self.animation.key_frames) == 1:
            self.keyframesListControlWidget.deleteButton.setEnabled(True)
            self.keyframesListWidget.setEnabled(True)
            self.frameWidget.setEnabled(True)
        self.animationsliderWidget.requires_update = True

    def _update_frame_widget_from_animation(self):
        self.frameWidget.update_from_animation()

    def _replace_keyframe_callback(self, event=None):
        """Replace current key-frame with new view"""
        self.animation.capture_keyframe(
            steps=self._get_interpolation_steps(),
            ease=self._get_easing_function(),
            insert=False,
        )
        self.animationsliderWidget.requires_update = True

    def _delete_keyframe_callback(self, event=None):
        """Delete current key-frame"""
        if len(self.animation.key_frames) > 0:
            self.animation.key_frames.pop(self.animation.frame)
        if len(self.animation.key_frames) == 0:
            self.keyframesListControlWidget.deleteButton.setEnabled(False)
            self.keyframesListWidget.setEnabled(False)
            self.frameWidget.setEnabled(False)
        self.animationsliderWidget.requires_update = True

    def _key_adv_frame(self, event=None):
        """Go forwards in key-frame list"""

        new_frame = (self.animation.frame + 1) % len(self.animation.key_frames)
        self.animation.set_to_keyframe(new_frame)
        self.keyframesListWidget.setCurrentRow(new_frame)

    def _key_back_frame(self, event=None):
        """Go backwards in key-frame list"""

        new_frame = (self.animation.frame - 1) % len(self.animation.key_frames)
        self.animation.set_to_keyframe(new_frame)
        self.keyframesListWidget.setCurrentRow(new_frame)

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

    def _move_animationslider_callback(self, event=None):
        """Scroll through interpolated states. Computes states if key-frames changed"""
        self.animationsliderWidget.synchronise()
        new_frame = self.animationsliderWidget.value()
        self.animation._set_viewer_state(
            self.animationsliderWidget.interpol_states[new_frame]
        )

        # This gets the index of the first key frame whose frame count is above new_frame
        new_key_frame = (
            self.animationsliderWidget.cumulative_frame_count > new_frame
        ).argmax()
        new_key_frame -= 1  # to get the previous key frame
        new_key_frame = int(new_key_frame)  # to enable slicing a list with it
        self.keyframesListWidget.setCurrentRowBlockingSignals(new_key_frame)
        self.animation.frame = new_key_frame

    def close(self):
        self._release_callbacks()
        super().close()
