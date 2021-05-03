import numpy as np
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QSlider


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
    cumulative_frame_count : array
        The cumulative frame count of self.animation.key_frames
    requires_update : bool
        Define if interpolated states should be updated.
    """

    def __init__(self, animation, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation=orientation, parent=parent)

        self.animation = animation
        self.interpol_states = []
        self.cumulative_frame_count = np.array([])
        self.requires_update = True

        self.setToolTip("Scroll through animation")

    def synchronise(self):
        """Synchronise the AnimationSliderWidget with the Animation object"""
        if self.requires_update:
            self._compute_states()
            self._compute_cumulative_frame_count()

    def _compute_states(self):
        """Compute interpolation states"""
        self.interpol_states = []
        for state in self.animation._state_generator():
            self.interpol_states.append(state)
        self.setMaximum(len(self.interpol_states) - 1)
        self.requires_update = False

    def _compute_cumulative_frame_count(self):
        """Compute cumulative frame count"""
        steps = [keyframe["steps"] for keyframe in self.animation.key_frames]
        self.cumulative_frame_count = np.insert(np.cumsum(steps), 0, 0)
