from qtpy.QtWidgets import QWidget, QHBoxLayout

from qtpy.QtWidgets import QListWidget

# NOT IMPLEMENTED YET
class KeyFramesListWidget(QListWidget):
    """List of Key Frames.
    """
    def __init__(self, animation, parent=None):
        super().__init__(parent=parent)
