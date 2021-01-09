from qtpy.QtWidgets import QWidget, QFormLayout, QSpinBox


class FrameWidget(QWidget):
    """Widget for interatviely making animations using the napari viewer.
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._layout = QFormLayout(parent=self)
        self.stepsSpinBox = QSpinBox()
        self.stepsSpinBox.setValue(15)

        self.frameSpinBox = QSpinBox()
        self.frameSpinBox.setValue(0)

        self._layout.addRow('Steps', self.stepsSpinBox)
        self._layout.addRow('Frame', self.frameSpinBox)
