from napari._qt._constants import LoopMode
from napari._qt.dialogs.qt_modal import QtPopup
from napari._qt.widgets.qt_dims_slider import QtCustomDoubleSpinBox
from napari.utils.translations import trans
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPushButton,
)


class QtPlayButton(QPushButton):
    """Play button, included in the FrameSliderWidget, to control playback.
    The button also owns the QtModalPopup that controls the playback settings.
    """

    play_requested = Signal()  # fps
    stop_requested = Signal()

    def __init__(self, reverse=False, fps=20, mode=LoopMode.LOOP):
        super().__init__()

        self.reverse = reverse
        self.fps = fps
        self.mode = mode
        self.setProperty("reverse", str(reverse))  # for styling
        self.setProperty("playing", "False")  # for styling

        self.setToolTip(
            trans._("Right click on button for playback setting options.")
        )

        # build popup modal form

        self.popup = QtPopup(self)
        form_layout = QFormLayout()
        self.popup.frame.setLayout(form_layout)

        fpsspin = QtCustomDoubleSpinBox(self.popup)
        fpsspin.setObjectName("fpsSpinBox")
        fpsspin.setAlignment(Qt.AlignCenter)
        fpsspin.setValue(self.fps)
        if hasattr(fpsspin, "setStepType"):
            # this was introduced in Qt 5.12.  Totally optional, just nice.
            fpsspin.setStepType(QDoubleSpinBox.AdaptiveDecimalStepType)
        fpsspin.setMaximum(500)
        fpsspin.setMinimum(0)
        form_layout.insertRow(
            0,
            QLabel(trans._("frames per second:"), parent=self.popup),
            fpsspin,
        )
        self.fpsspin = fpsspin

        revcheck = QCheckBox(self.popup)
        revcheck.setObjectName("playDirectionCheckBox")
        form_layout.insertRow(
            1, QLabel(trans._("play direction:"), parent=self.popup), revcheck
        )
        self.reverse_check = revcheck

        mode_combo = QComboBox(self.popup)
        mode_combo.addItems([str(i).replace("_", " ") for i in LoopMode])
        form_layout.insertRow(
            2, QLabel(trans._("play mode:"), parent=self.popup), mode_combo
        )
        mode_combo.setCurrentText(str(self.mode).replace("_", " "))
        self.mode_combo = mode_combo

    def mouseReleaseEvent(self, event):
        """Show popup for right-click, toggle animation for right click.
        Parameters
        ----------
        event : qtpy.QtCore.QEvent
            Event from the qt context.
        """
        # using this instead of self.customContextMenuRequested.connect and
        # clicked.connect because the latter was not sending the
        # rightMouseButton release event.
        if event.button() == Qt.RightButton:
            self.popup.show_above_mouse()
        elif event.button() == Qt.LeftButton:
            self._on_click()

    def _on_click(self):
        """Toggle play/stop animation control."""
        if self.property("playing") == "True":
            self.stop_requested.emit()
        else:
            self.play_requested.emit()

    def _handle_start(self):
        """On animation start, set playing property to True & update style."""
        self.setProperty("playing", "True")
        self.style().unpolish(self)
        self.style().polish(self)

    def _handle_stop(self):
        """On animation stop, set playing property to False & update style."""
        self.setProperty("playing", "False")
        self.style().unpolish(self)
        self.style().polish(self)
