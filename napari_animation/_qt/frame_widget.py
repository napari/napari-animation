from qtpy.QtCore import Qt
from qtpy.QtWidgets import QComboBox, QWidget, QFormLayout, QSpinBox

from ..easing import Easing
from ..utils import _easing_func_to_name

class FrameWidget(QWidget):
    """Widget for interatviely making animations using the napari viewer.
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.animation = self.parentWidget().animation
        self._layout = QFormLayout(parent=self)
        self._init_steps()
        self._init_ease()
        self._add_callbacks()

    def _init_steps(self):
        self.stepsSpinBox = QSpinBox()
        self.stepsSpinBox.setValue(15)
        self._layout.addRow('Steps', self.stepsSpinBox)

    def _init_ease(self):
        self.easeComboBox = QComboBox()
        self.easeComboBox.addItems([e.name.lower() for e in Easing])
        index = self.easeComboBox.findText(
            'linear', Qt.MatchFixedString
        )
        self.easeComboBox.setCurrentIndex(index)
        self._layout.addRow('Ease', self.easeComboBox)

    def get_easing_func(self):
        easing_name = str(self.easeComboBox.currentText())
        easing_func = Easing[easing_name.upper()].value
        return easing_func

    def update_from_animation(self):
        """update state of self to reflect animation state at current key frame
        """
        self._update_steps_spin_box()
        self._update_ease_combo_box()

    def _update_steps_spin_box(self):
        """update state of steps spin box to reflect animation state at current key frame
        """
        self.stepsSpinBox.setValue(self.animation.current_key_frame['steps'])

    def _update_animation_steps(self, event):
        """update state of 'steps' at current key-frame to reflect GUI state
        """
        self.animation.current_key_frame['steps'] = self.stepsSpinBox.value()

    def _update_ease_combo_box(self):
        """update state of ease combo box to reflect animation state at current key frame
        """
        ease = self.animation.current_key_frame['ease']
        name = _easing_func_to_name(ease)
        index = self.easeComboBox.findText(
            name , Qt.MatchFixedString
        )
        self.easeComboBox.setCurrentIndex(index)

    def _update_animation_ease(self, event):
        """update state of 'ease' at current key-frame to reflect GUI state
        """
        self.animation.current_key_frame['ease'] = self.get_easing_func()

    def _add_callbacks(self):
        """add callbacks to steps and ease widgets
        """
        self.stepsSpinBox.valueChanged.connect(self._update_animation_steps)
        self.easeComboBox.currentIndexChanged.connect(self._update_animation_ease)
