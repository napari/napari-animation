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
    """

    def __init__(self, animation, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation=orientation, parent=parent)

        self.animation = animation
        self.requires_update = True
        self.setToolTip("Scroll through animation")

    def _compute_states(self):
        """Computer interpolation states"""
        self.interpol_states = []
        for state in self.animation._state_generator():
            self.interpol_states.append(state)
        self.setMaximum(len(self.interpol_states)-1)
        self.requires_update = False