from qtpy.QtWidgets import QWidget, QHBoxLayout

from qtpy.QtWidgets import QListWidget, QFormLayout

# NOT IMPLEMENTED YET
class KeyFramesListWidget(QListWidget):
    """List of Key Frames.
    """
    def __init__(self, animation, parent=None):
        super().__init__(parent=parent)

        self._layout = QFormLayout(parent=self)

        self.keyframeslist = QListWidget()
        self.populate_keyframeslist(animation)

    def populate_keyframeslist(self, animation):
        key_frames = [key_frame for key_frame in animation.key_frames]
        self.keyframeslist.addItems(key_frames)
