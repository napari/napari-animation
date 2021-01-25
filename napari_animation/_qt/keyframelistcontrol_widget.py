from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton


class KeyFrameListControlWidget(QFrame):
    """Controls for a KeyFrameListWidget
    """
    def __init__(self, animation, parent=None):
        super().__init__(parent=parent)
        self.animation = animation

        layout = QHBoxLayout()
        layout.addStretch(1)
        self.keyframeDeleteButton = KeyFrameDeleteButton(self.animation)
        layout.addWidget(self.keyframeDeleteButton)

        self.setLayout(layout)


class KeyFrameDeleteButton(QPushButton):
    def __init__(self, animation):
        super().__init__()

        self.animation = animation
        self.setToolTip('Delete selected key-frame')
        self.setText('Delete')
