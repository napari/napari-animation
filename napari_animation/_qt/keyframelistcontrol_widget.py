from qtpy.QtWidgets import QFrame, QHBoxLayout, QPushButton


class KeyFrameListControlWidget(QFrame):
    """Controls for a KeyFrameListWidget
    """
    def __init__(self, animation, parent=None):
        super().__init__(parent=parent)
        self.animation = animation

        layout = QHBoxLayout()
        self.captureButton = KeyFrameCaptureButton(self.animation)
        self.deleteButton = KeyFrameDeleteButton(self.animation)
        layout.addWidget(self.captureButton)
        layout.addWidget(self.deleteButton)

        self.setLayout(layout)


class KeyFrameDeleteButton(QPushButton):
    def __init__(self, animation):
        super().__init__()

        self.animation = animation
        self.setToolTip('Delete selected key-frame')
        self.setText('Delete')


class KeyFrameCaptureButton(QPushButton):
    def __init__(self, animation):
        super().__init__()

        self.animation = animation
        self.setToolTip('Capture key-frame')
        self.setText('Capture')
