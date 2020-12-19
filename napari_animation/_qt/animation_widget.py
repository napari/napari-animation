from qtpy.QtWidgets import QWidget, QLabel, QVBoxLayout

from ..animation import Animation
from .frame_widget import FrameWidget


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
    def __init__(self, viewer, parent=None):
        super().__init__(parent=parent)

        
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self._layout.addWidget(QLabel('Animation Wizard', parent=self))
        self._layout.addWidget(FrameWidget(parent=self))
        self._layout.addStretch(1)

        # Create animation
        self.animation = Animation(viewer)

        # establish key bindings
        self._add_callbacks()

    def _add_callbacks(self):
        """Bind keys"""

        self.animation.viewer.bind_key("Alt-f", self._capture_keyframe_callback)
        self.animation.viewer.bind_key("Alt-r", self._replace_keyframe_callback)
        self.animation.viewer.bind_key("Alt-d", self._delete_keyframe_callback)

        self.animation.viewer.bind_key("Alt-a", self._key_adv_frame)
        self.animation.viewer.bind_key("Alt-b", self._key_back_frame)

    def _release_callbacks(self):
        """Release keys"""

        self.animation.viewer.bind_key("Alt-f", None)
        self.animation.viewer.bind_key("Alt-r", None)
        self.animation.viewer.bind_key("Alt-d", None)

        self.animation.viewer.bind_key("Alt-a", None)
        self.animation.viewer.bind_key("Alt-b", None)

    def _capture_keyframe_callback(self, viewer):
        """Record current key-frame"""
        self.animation.capture_keyframe()

    def _replace_keyframe_callback(self, viewer):
        """Replace current key-frame with new view"""
        self.animation.capture_keyframe(insert=False)

    def _delete_keyframe_callback(self, viewer):
        """Delete current key-frame"""

        self.animation.key_frames.pop(self.animation.frame)
        self.animation.frame = (self.animation.frame - 1) % len(self.animation.key_frames)
        self._set_to_keyframe(self.animation.frame)

    def _key_adv_frame(self, viewer):
        """Go forwards in key-frame list"""

        new_frame = (self.animation.frame + 1) % len(self.animation.key_frames)
        self._set_to_keyframe(new_frame)
        print('current frame', self.animation.frame)

    def _key_back_frame(self, viewer):
        """Go backwards in key-frame list"""

        new_frame = (self.animation.frame - 1) % len(self.animation.key_frames)
        self._set_to_keyframe(new_frame)
        print('current frame', self.animation.frame)

    def close():
        self._release_callbacks()
        super().close()