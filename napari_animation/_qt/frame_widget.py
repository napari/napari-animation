from qtpy.QtCore import Qt
from qtpy.QtWidgets import QComboBox, QFormLayout, QSpinBox, QWidget

from ..easing import Easing


class FrameWidget(QWidget):
    """Widget for interatviely making animations using the napari viewer."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.animation = self.parentWidget().animation

        # init steps
        self.stepsSpinBox = QSpinBox()
        self.stepsSpinBox.setRange(1, 100000)
        self.stepsSpinBox.setValue(15)

        # init ease
        self.easeComboBox = QComboBox()
        self.easeComboBox.addItems([e.name.lower() for e in Easing])
        self.easeComboBox.setCurrentText("linear")

        # add callbacks
        self.stepsSpinBox.valueChanged.connect(self._update_animation_steps)
        self.easeComboBox.currentIndexChanged.connect(
            self._update_animation_ease
        )

        # layout
        self.setLayout(QFormLayout())
        self.layout().addRow("Steps", self.stepsSpinBox)
        self.layout().addRow("Ease", self.easeComboBox)

    def get_easing_func(self):
        return Easing[self.easeComboBox.currentText().upper()]

    def update_from_animation(self):
        """update state of self to reflect animation state at current key frame"""
        self._update_steps_spin_box()
        self._update_ease_combo_box()

    def _update_steps_spin_box(self):
        """update state of steps spin box to reflect animation state at current key frame"""
        if self.animation.current_key_frame:
            self.stepsSpinBox.setValue(self.animation.current_key_frame.steps)

    def _update_animation_steps(self, event):
        """update state of 'steps' at current key-frame to reflect GUI state"""
        self.animation.current_key_frame.steps = self.stepsSpinBox.value()

    def _update_ease_combo_box(self):
        """update state of ease combo box to reflect animation state at current key frame"""
        if self.animation.current_key_frame:
            ease = self.animation.current_key_frame.ease
            self.easeComboBox.setCurrentText(ease.name.lower())

    def _update_animation_ease(self, event):
        """update state of 'ease' at current key-frame to reflect GUI state"""
        self.animation.current_key_frame.ease = self.get_easing_func()
