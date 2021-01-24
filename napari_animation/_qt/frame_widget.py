from qtpy.QtCore import Qt
from qtpy.QtWidgets import QComboBox, QWidget, QFormLayout, QSpinBox

from ..easing import Easing


class FrameWidget(QWidget):
    """Widget for interatviely making animations using the napari viewer.
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.animation = self.parentWidget().animation
        self._layout = QFormLayout(parent=self)
        self._init_steps()
        self._init_ease()

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
        # self._layout.addRow('Frame', self.frameSpinBox)
