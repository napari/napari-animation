from qtpy.QtCore import Qt
from qtpy.QtWidgets import QSlider
import numpy as np


class AnimationSliderWidget(QSlider):
    """List of key frames for an animation

    Parameters
    ----------
    animation : napari_animation.Animation
        napari-animation animation to be synced with the GUI.

    Attributes
    ----------
    animation : napari_animation.Animation
        napari-animation animation in sync with the GUI.
    interpol_states : dict
        Dictionary of interpolated states
    keyframe_to_frame : array
        Frame numbers corresponding to each key frames.
    requires_update : bool
        Define if interpolated states should be updated.
    """

    def __init__(self, animation, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation=orientation, parent=parent)

        self.animation = animation
        self.interpol_states = []
        self.keyframe_to_frame = np.array([])
        self.requires_update = True

        self.setToolTip("Scroll through animation")

    def _compute_states(self):
        """Computer interpolation states"""
        self.interpol_states = []
        for state in self.animation._state_generator():
            self.interpol_states.append(state)

        self.keyframe_to_frame = [0]
        steps = [keyframe['steps'] for keyframe in self.animation.key_frames]
        self.keyframe_to_frame += np.cumsum(steps)

        self.setMaximum(len(self.interpol_states)-1)

        self.requires_update = False