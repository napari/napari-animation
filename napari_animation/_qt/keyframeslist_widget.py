from qtpy.QtWidgets import QWidget, QHBoxLayout

from qtpy.QtWidgets import QWidget, QFormLayout, QSpinBox


class KeyFramesListWidget(QWidget):
    """List of Key Frames.
    """
    def __init__(self, animation, parent=None):
        super().__init__(parent=parent)
