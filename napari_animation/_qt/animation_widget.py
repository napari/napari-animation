from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton

from ..animation import Animation
from .frame_widget import FrameWidget
from .keyframeslist_widget import KeyFramesListWidget
from .keyframelistcontrol_widget import KeyFrameListControlWidget


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

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self._layout.addWidget(QLabel('Animation Wizard', parent=self))

        self._init_capture_button()

        self._layout.addStretch(1)

        self._init_keyframes_list_control_widget()

        self._init_keyframes_list_widget()
        self._init_frame_widget()

        self.pathText = QLineEdit(parent=self)
        self.pathText.setText('demo.mp4')
        self._layout.addWidget(self.pathText)

        self.saveButton = QPushButton('Save Animation', parent=self)
        self.saveButton.clicked.connect(self._save_callback)
        self._layout.addWidget(self.saveButton)

        # establish key bindings
        self._add_keybind_callbacks()

        # establish callbacks
        self._add_callbacks()

    def _add_keybind_callbacks(self):
        """Bind keys"""

        self.animation.viewer.bind_key("Alt-f", self._capture_keyframe_callback)
        self.animation.viewer.bind_key("Alt-r", self._replace_keyframe_callback)
        self.animation.viewer.bind_key("Alt-d", self._delete_keyframe_callback)

        self.animation.viewer.bind_key("Alt-a", self._key_adv_frame)
        self.animation.viewer.bind_key("Alt-b", self._key_back_frame)

    def _add_callbacks(self):
        """Establish callbacks"""
        self.keyframesListControlWidget.keyframeDeleteButton.clicked.connect(
            self._delete_keyframe_callback
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
        self.frameWidget.hide()

    def _init_capture_button(self):
        self.captureButton = QPushButton('Capture Frame', parent=self)
        self.captureButton.clicked.connect(self._capture_keyframe_callback)
        self._layout.addWidget(self.captureButton)

    def _init_keyframes_list_control_widget(self):
        self.keyframesListControlWidget = KeyFrameListControlWidget(
            animation=self.animation, parent=self)
        self._layout.addWidget(self.keyframesListControlWidget)
        self.keyframesListControlWidget.hide()

    def _init_keyframes_list_widget(self):
        self.keyframesListWidget = KeyFramesListWidget(self.animation, parent=self)
        self._layout.addWidget(self.keyframesListWidget)
        self.keyframesListWidget.hide()

    def _get_interpolation_steps(self):
        return int(self.frameWidget.stepsSpinBox.value())

    def _get_easing_function(self):
        return self.frameWidget.get_easing_func()

    def _capture_keyframe_callback(self, event=None):
        """Record current key-frame"""
        self.animation.capture_keyframe(steps=self._get_interpolation_steps(),
                                        ease=self._get_easing_function())
        self.keyframesListWidget._add()
        if len(self.animation.key_frames) == 1:
            self.keyframesListControlWidget.show()
            self.keyframesListWidget.show()
            self.frameWidget.show()

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
            self.keyframesListControlWidget.hide()
            self.keyframesListWidget.hide()
            self.frameWidget.hide()

    def _key_adv_frame(self, event=None):
        """Go forwards in key-frame list"""

        new_frame = (self.animation.frame + 1) % len(self.animation.key_frames)
        self.animation.set_to_keyframe(new_frame)

    def _key_back_frame(self, event=None):
        """Go backwards in key-frame list"""

        new_frame = (self.animation.frame - 1) % len(self.animation.key_frames)
        self.animation.set_to_keyframe(new_frame)

    def _save_callback(self, event=None):
        path = self.pathText.text()
        print('Saving animation to', path)
        self.animation.animate(path)

    def close(self):
        self._release_callbacks()
        super().close()
