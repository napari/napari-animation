from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton


class KeyFrameListControlWidget(QFrame):
    """Controls for a KeyFrameListWidget
    """
    def __init__(self, animation, animation_widget, parent=None):
        super().__init__(parent=parent)
        self.animation = animation

        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(KeyFrameDeleteButton(self.animation, animation_widget))

        self.setLayout(layout)


class KeyFrameDeleteButton(QPushButton):
    def __init__(self, animation, animation_widget):
        super().__init__()

        self.animation = animation
        self.animation_widget = animation_widget
        self.clicked.connect(self._remove_current_key_frame)
        self.setToolTip('Delete selected key-frame')
        self.setText('Delete')

    def _remove_current_key_frame(self, event):
        if len(self.animation.key_frames) > 0:
            self.animation.key_frames.pop(self.animation.frame)
        if len(self.animation.key_frames) == 0:
            self.animation_widget.keyframesListControlWidget.hide()
