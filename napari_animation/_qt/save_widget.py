from qtpy.QtWidgets import QWidget, QVBoxLayout


class SaveWidget(QWidget):
    """Save animation widget.
    """
    def __init__(self, animation, parent=None):
        super().__init__(parent=parent)
