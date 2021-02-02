from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton

from ..animation import Animation
from .frame_widget import FrameWidget
from .keyframeslist_widget import KeyFramesListWidget
from .keyframelistcontrol_widget import KeyFrameListControlWidget
from .dialogs import SaveAnimationDialog


class AnimationWidget(QWidget):
    """Widget for interatviely making animations using the napari viewer.

    Parameters
    ----------
    viewer : napari.Viewer
        napari viewer.

    Attributes
    ----------
    key_frames : list of dict
        List of viewer state dictionaries.
    frame : int
        Currently shown key frame.
    """

    def __init__(self, viewer: 'napari.viewer.Viewer', parent=None):
        super().__init__(parent=parent)

        # Create animation
        self.animation = Animation(viewer)

        # Initialise UI
        self._init_ui()

        # establish key bindings and callbacks
        self._add_keybind_callbacks()
        self._add_callbacks()

    def _init_ui(self):
        """Initialise user interface"""
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self._layout.addWidget(QLabel('Animation Wizard', parent=self))

        self._init_keyframes_list_control_widget()
        self._init_keyframes_list_widget()
        self._init_frame_widget()
        self._init_save_button()

    def _add_keybind_callbacks(self):
        """Bind keys"""

        self.animation.viewer.bind_key("Alt-f", self._capture_keyframe_callback)
        self.animation.viewer.bind_key("Alt-r", self._replace_keyframe_callback)
        self.animation.viewer.bind_key("Alt-d", self._delete_keyframe_callback)

        self.animation.viewer.bind_key("Alt-a", self._key_adv_frame)
        self.animation.viewer.bind_key("Alt-b", self._key_back_frame)

    def _add_callbacks(self):
        """Establish callbacks"""
        self.keyframesListControlWidget.deleteButton.clicked.connect(
            self._delete_keyframe_callback
        )
        self.keyframesListControlWidget.captureButton.clicked.connect(
            self._capture_keyframe_callback)
        self.saveButton.clicked.connect(self._save_callback)

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
        self.frameWidget.setEnabled(False)

    def _init_keyframes_list_control_widget(self):
        self.keyframesListControlWidget = KeyFrameListControlWidget(
            animation=self.animation, parent=self)
        self._layout.addWidget(self.keyframesListControlWidget)
        self.keyframesListControlWidget.deleteButton.setEnabled(False)

    def _init_keyframes_list_widget(self):
        self.keyframesListWidget = KeyFramesListWidget(self.animation, parent=self)
        self._layout.addWidget(self.keyframesListWidget)
        self.keyframesListWidget.setEnabled(False)

    def _init_save_button(self):
        self.saveButton = QPushButton('Save Animation', parent=self)
        self._layout.addWidget(self.saveButton)

    def _get_interpolation_steps(self):
        return int(self.frameWidget.stepsSpinBox.value())

    def _get_easing_function(self):
        return self.frameWidget.get_easing_func()

    def _capture_keyframe_callback(self, event=None):
        """Record current key-frame"""
        self.animation.capture_keyframe(steps=self._get_interpolation_steps(),
                                        ease=self._get_easing_function())
        if len(self.animation.key_frames) == 1:
            self.keyframesListControlWidget.deleteButton.setEnabled(True)
            self.keyframesListWidget.setEnabled(True)
            self.frameWidget.setEnabled(True)

    def _update_frame_widget_from_animation(self):
        self.frameWidget.update_from_animation()

    def _replace_keyframe_callback(self, event=None):
        """Replace current key-frame with new view"""
        self.animation.capture_keyframe(steps=self._get_interpolation_steps(),
                                        ease=self._get_easing_function(), insert=False)

    def _delete_keyframe_callback(self, event=None):
        """Delete current key-frame"""
        if len(self.animation.key_frames) > 0:
            self.animation.key_frames.pop(self.animation.frame)
        if len(self.animation.key_frames) == 0:
            self.keyframesListControlWidget.deleteButton.setEnabled(False)
            self.keyframesListWidget.setEnabled(False)
            self.frameWidget.setEnabled(False)

    def _key_adv_frame(self, event=None):
        """Go forwards in key-frame list"""

        new_frame = (self.animation.frame + 1) % len(self.animation.key_frames)
        self.animation.set_to_keyframe(new_frame)

    def _key_back_frame(self, event=None):
        """Go backwards in key-frame list"""

        new_frame = (self.animation.frame - 1) % len(self.animation.key_frames)
        self.animation.set_to_keyframe(new_frame)

    def _save_callback(self, event=None):
        SaveAnimationDialog(self.animation.animate, parent=self).exec_()

    def _update_theme(self, event=None):
        """Update from the napari GUI theme"""
        from napari.utils.theme import get_theme, template

        # get theme and raw stylesheet from napari viewer
        theme = get_theme(self.viewer.theme)
        raw_stylesheet = self.viewer.window.qt_viewer.raw_stylesheet

        # template and apply the primary stylesheet
        templated_stylesheet = template(raw_stylesheet, **theme)
        self.setStyleSheet(templated_stylesheet)

        # update styling of KeyFramesListWidget
        self.keyframesListWidget._update_theme(theme)

    def close(self):
        self._release_callbacks()
        self.viewer.events.theme.disconnect(self._update_theme)
        super().close()
