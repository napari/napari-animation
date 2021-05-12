from qtpy.QtCore import QSize
from qtpy.QtGui import QIcon, QImage, QPixmap
from qtpy.QtWidgets import QListWidget, QListWidgetItem


class KeyFramesListWidget(QListWidget):
    """List of key frames for an animation

    Parameters
    ----------
    animation : napari_animation.Animation
        napari-animation animation to be synced with the GUI.

    Attributes
    ----------
    animation : napari_animation.Animation
        napari-animation animation in sync with the GUI.
    """

    def __init__(self, animation, parent=None):
        super().__init__(parent=parent)

        self.animation = animation
        self._frame_count = 0
        self._item_id_to_key_frame = {}
        self._key_frame_id_to_item = {}

        self._connect_key_frame_callbacks()
        self.setDragDropMode(super().InternalMove)

        self.itemSelectionChanged.connect(self._selection_callback)

    def _connect_key_frame_callbacks(self):
        """Connect events on the key frame list to their callbacks"""
        self.animation.key_frames.events.inserted.connect(self._add)
        self.animation.key_frames.events.removed.connect(self._remove)
        self.animation.key_frames.events.reordered.connect(
            self._reorder_frontend
        )

    def dropEvent(self, event):
        """update backend state on 'drop' of frame in key frames list"""
        super().dropEvent(event)
        self._reorder_backend()
        self._update_frame_number()

    def _selection_callback(self):
        self._update_frame_number()
        if self.animation.frame != -1:
            self.animation.set_to_current_keyframe()
            self.parentWidget()._update_frame_widget_from_animation()

    def _add(self, event):
        """Generate QListWidgetItem for current keyframe, store its unique id and add it to self"""
        key_frame, idx = event.value, event.index
        item = self._generate_list_item(key_frame)
        self.insertItem(idx, item)
        self._add_mappings(key_frame, item)
        self._frame_count += 1

    def _add_mappings(self, key_frame, item):
        self._item_id_to_key_frame[id(item)] = key_frame
        self._key_frame_id_to_item[id(key_frame)] = item

    def _remove(self, event):
        """Remove QListWidgetItem at event.index"""
        self.takeItemBlockingSignals(event.index)
        self._update_frame_number()

    def _reorder_frontend(self, event=None):
        """Reorder items in frontend based on current state in backend"""
        for idx, key_frame in enumerate(self.animation.key_frames):
            item = self._key_frame_id_to_item[id(key_frame)]
            self.takeItem(idx)
            self.insertItem(item, idx)

    def _reorder_backend(self):
        """reorder key frames in backend based on current state in frontend"""
        for idx, key_frame in enumerate(self.frontend_key_frames):
            self.animation.key_frames[idx] = key_frame

    def insertItem(self, row, item):
        """overrides QListWidget.insertItem to also update index to newly inserted item"""
        super().insertItem(row, item)
        self.setCurrentIndex(self.indexFromItem(item))

    def _update_frame_number(self):
        """update the frame number of self.animation based on selected item in frontend"""
        self.animation.frame = self._get_selected_index()

    def _generate_list_item(self, key_frame):
        """Generate a QListWidgetItem from a key-frame"""
        item = QListWidgetItem(f"key-frame {self._frame_count}")
        item.setIcon(self._icon_from_key_frame(key_frame))
        return item

    def _icon_from_key_frame(self, key_frame):
        """Generate QIcon from a key frame"""
        thumbnail = key_frame["thumbnail"]
        thumbnail = QImage(
            thumbnail,
            thumbnail.shape[1],
            thumbnail.shape[0],
            QImage.Format_RGBA8888,
        )
        icon = QIcon(QPixmap.fromImage(thumbnail))
        return icon

    def _get_key_frame(self, key_frame_idx):
        """Get key frame dict from key frames list at key_frame_idx"""
        return self.animation.key_frames[key_frame_idx]

    def _get_selected_index(self):
        """Get index of currently selected row"""
        idxs = self.selectedIndexes()
        if len(idxs) == 0:
            return -1
        else:
            return idxs[-1].row()

    def _update_theme(self, theme_name):
        """
        Update styling based on the napari theme dictionary and any other attributes

        Parameters
        ----------
        theme : str
            name of napari theme
        """
        from napari.utils.theme import get_theme, template

        qss_template = """
        QListView::item:deselected {
            background-color: {{ foreground }};
        }
        QListView::item:selected {
            background-color: {{ current }};
        }
        QListView {
            background: transparent;
        }
        QListView::item {
            margin: 0px;
            padding: 0px;
            min-height:
            32px;
            max-height: 32px;
        }
        QImage {
            margin: 0px;
            padding: 0px;
            qproperty-alignment: AlignLeft;
        }
        """

        self.setStyleSheet(template(qss_template, **get_theme(theme_name)))
        self.setIconSize(QSize(64, 64))
        self.setSpacing(2)

    @property
    def frontend_items(self):
        """Iterate over frontend_items in the keyframes list"""
        for i in range(self.count()):
            yield self.item(i)

    @property
    def frontend_key_frames(self):
        for item in self.frontend_items:
            yield self._item_id_to_key_frame[id(item)]

    def setCurrentRowBlockingSignals(self, row: int) -> None:
        return self.callMethodBlockingSignals(self.setCurrentRow, row)

    def takeItemBlockingSignals(self, row: int) -> QListWidgetItem:
        return self.callMethodBlockingSignals(self.takeItem, row)

    def callMethodBlockingSignals(self, method, *args, **kwargs):
        """Call 'method' without emitting events to avoid side effects"""
        self.blockSignals(True)
        output = method(*args, **kwargs)
        self.blockSignals(False)
        return output
