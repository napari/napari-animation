from napari import Viewer
from napari_threedee.visualization import QtCameraSpline
from qtpy.QtWidgets import QVBoxLayout, QWidget
from superqt import QCollapsible


class CameraSplineWidget(QWidget):
    """Wrap the QtCameraSpline widget in a collapsible frame."""

    def __init__(self, viewer: Viewer, parent=None):
        super().__init__(parent=parent)

        self.spline_widget = QtCameraSpline(viewer=viewer)

        self.collapsible_widget = QCollapsible("camera spline path")
        self.collapsible_widget.addWidget(self.spline_widget)
        self.collapsible_widget.toggled.connect(self._on_expand_or_collapse)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.collapsible_widget)

    def _on_expand_or_collapse(self, event=None):
        """Make sure the spline widget is deactivated whenever the
        collapsible is toggled.
        """
        self.spline_widget.deactivate()
