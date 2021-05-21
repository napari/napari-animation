from napari._qt.containers import QtListModel, QtListView
from qtpy.QtCore import QModelIndex, QSize, Qt
from qtpy.QtGui import QImage


class KeyFrameModel(QtListModel):
    """Model for QtListView of KeyFrames"""

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        """Return data at `index` for the requested `role`.

        see https://doc.qt.io/qt-5/model-view-programming.html#item-roles
        """
        if role == Qt.EditRole:
            return index.data(Qt.UserRole).name
        if role == Qt.DecorationRole:  # thumbnail
            key_frame = index.data(Qt.UserRole)
            return QImage(
                key_frame.thumbnail,
                key_frame.thumbnail.shape[1],
                key_frame.thumbnail.shape[0],
                QImage.Format_RGBA8888,
            )
        if role == Qt.SizeHintRole:  # determines size of item
            return QSize(160, 34)
        return super().data(index, role)

    def setData(self, index, value, role) -> bool:
        """Set data at `index` for `role` to `value`."""
        if value and role == Qt.EditRole:
            # user has double-clicked on the keyframe name
            key_frame = index.data(Qt.UserRole)
            key_frame.name = value
        return super().setData(index, value, role=role)


class KeyFramesListWidget(QtListView):
    """QtListView comes from napari and works with SelectableEventedList."""

    def __init__(self, root, parent=None):
        super().__init__(root, parent=parent)
        self.setModel(KeyFrameModel(root))
        self.setStyleSheet("KeyFramesListWidget::item { padding: 0px; }")
