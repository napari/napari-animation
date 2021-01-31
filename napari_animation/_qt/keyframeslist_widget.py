from napari.utils.events import EventedList
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
        self._frame_counter = 0
        self._key_frame_id_to_label_map = {}
        self._label_to_qlistwidgetitem_map = {}

        self._connect_key_frame_callbacks()
        self.setDragDropMode(super().InternalMove)

        self.itemClicked.connect(self._selection_callback)

    def _init_styling(self):
        self.setIconSize(QSize(64, 64))
        stylesheet = '\n'.join(
            [self._item_background_color, self._transparent_background]
        )
        self.setStyleSheet(stylesheet)

    def _connect_key_frame_callbacks(self):
        """Connect events on the key frame list to their callbacks
        """
        self.animation.key_frames.events.removed.connect(self._remove)
        self.animation.key_frames.events.moved.connect(self._update_frontend)
        self.animation.key_frames.events.changed.connect(self._update_frontend)
        self.animation.key_frames.events.reordered.connect(self._reorder)

    def dropEvent(self, event):
        """update animation state on 'drop' of frame in key frames list
        """
        super().dropEvent(event)
        self._update_backend()

    def _selection_callback(self, event):
        self._update_frame_number()
        self.animation.set_to_current_keyframe()
        self.parentWidget()._update_frame_widget_from_animation()

    def _add(self):
        """Generate QListWidgetItem for current keyframe, store its unique id and add it to self
        """
        key_frame_idx = self.animation.frame
        item = self._generate_list_item(key_frame_idx)

        self.insertItem(key_frame_idx, item)

        self._map_key_frame_to_id(key_frame_idx)
        self._map_label_to_qlistwidgetitem(key_frame_idx)
        self._frame_counter += 1

    def insertItem(self, row, item):
        """overrides QListWidget.insertItem to also update current index and frame number
        """
        super().insertItem(row, item)
        self.setCurrentIndex(self.indexFromItem(item))
        self._update_frame_number()

    def _remove(self, event):
        """Remove QListWidgetItem at event.index
        """
        self.takeItem(event.index)
        self._remove_key_frame_id(event.value)
        self._update_frame_number()

    def _remove_key_frame_id(self, key_frame):
        """Remove key-frame id from self._key_frame_id_to_label_map
        """
        self._key_frame_id_to_label_map.pop(id(key_frame))

    def _reorder(self, event):
        """Reorder QListWidgetItems
        """
        self.clear()
        for idx, _ in enumerate(self.animation.key_frames):
            self.addItem(self._generate_list_item(idx))

    def _update_backend(self):
        """push current GUI state to self.animation
        """
        new_key_frames = [self._label_to_key_frame(label) for label in
                          self.frontend_key_frame_labels]

        # recreating the EventedList here and reconnecting events simplifies handling events
        # which fire when we modify the list in place
        self.animation.key_frames = EventedList(new_key_frames)
        self._connect_key_frame_callbacks()
        self._update_frame_number()

    def _update_frontend(self, *args):
        """update GUI state from self.animation state
        """
        # can't use self.addItems() and a list comprehension because self.addItems() only takes
        # labels, not QListWidgetItem objects
        self.clear()
        for idx, _ in enumerate(self.animation.key_frames):
            self.addItem(self._generate_list_item(idx))

    def _update_frame_number(self):
        """update the frame number of self.animation based on selected item in frontend
        """
        self.animation.frame = self._get_selected_index()

    def _generate_list_item(self, key_frame_idx):
        """Generate a QListWidgetItem from a key frame at key_frame_idx
        """
        item = QListWidgetItem(self._generate_label(key_frame_idx))
        key_frame = self._get_key_frame(key_frame_idx)
        item.setIcon(self._icon_from_key_frame(key_frame))
        return item

    def _map_key_frame_to_id(self, key_frame_idx):
        """Store the unique id of the key frame at key_frame_idx in a dict of {id: key_frame_label}
        """
        key_frame_id = id(self._get_key_frame(key_frame_idx))
        self._key_frame_id_to_label_map[key_frame_id] = self._generate_label(key_frame_idx)

    def _map_label_to_qlistwidgetitem(self, key_frame_idx):
        """Store the qlistwidgetitem associated with a particular label in a dict of
        {label: qlistwidgetitem}
        """
        label = self._generate_label(key_frame_idx)
        item = self.item(key_frame_idx)
        self._label_to_qlistwidgetitem_map[label] = item

    def _icon_from_key_frame(self, key_frame):
        """Generate QIcon from a key frame
        """
        thumbnail = key_frame['thumbnail']
        thumbnail = QImage(thumbnail, thumbnail.shape[1], thumbnail.shape[0],
                           QImage.Format_RGBA8888)
        icon = QIcon(QPixmap.fromImage(thumbnail))
        return icon

    def _get_key_frame(self, key_frame_idx):
        """Get key frame dict from key frames list at key_frame_idx
        """
        return self.animation.key_frames[key_frame_idx]

    def _get_selected_index(self):
        """Get index of currently selected row
        """
        idxs = self.selectedIndexes()
        if len(idxs) == 0:
            return -1
        else:
            return idxs[-1].row()

    def _generate_label(self, key_frame_idx):
        """Generate a label for a given key frame list index
        """
        key_frame = self._get_key_frame(key_frame_idx)
        try:
            label = self._key_frame_to_label(key_frame)
        except KeyError:
            label = f'key frame {self._frame_counter}'
        return label

    def _label_to_key_frame(self, label):
        """gets the key frame associated with a given label in the frontend
        """
        return self.labels_to_key_frames[label]

    def _label_to_qlistwidgetitem(self, label):
        return self._label_to_qlistwidgetitem_map[label]

    def _key_frame_to_label(self, key_frame):
        """gets the label associated with a key frame
        """
        key_frame_id = id(key_frame)
        return self._key_frame_id_to_label_map[key_frame_id]

    def _update_theme(self, theme):
        """
        Update styling based on the napari theme dictionary and any other attributes

        Parameters
        ----------
        theme : dict
                theme dict from napari
        """
        deselected_bg_color = theme['foreground']
        deselected_bg_color_qss = f'QListView::item:deselected' \
                                  f'{{background-color: {deselected_bg_color};}}'

        selected_bg_color = theme['current']
        selected_bg_color_qss = f'QListView::item:selected' \
                                f'{{background-color: {selected_bg_color};}}'

        transparent_background_qss = 'QListView{background: transparent;}'

        style_sheet_components = [
            deselected_bg_color_qss,
            selected_bg_color_qss,
            transparent_background_qss
        ]
        style_sheet = '\n'.join(style_sheet_components)

        self.setStyleSheet(style_sheet)
        self.setIconSize(QSize(64, 64))
        self.setSpacing(2)
        print(self.styleSheet())

    @property
    def frontend_items(self):
        """Iterate over frontend_items in the keyframes list
        """
        for i in range(self.count()):
            yield self.item(i)

    @property
    def frontend_key_frame_labels(self):
        """Labels for items currently in the keyframes list
        """
        for item in self.frontend_items:
            yield item.text()

    @property
    def backend_key_frame_labels(self):
        """labels for key frames in the order present in the backend
        """
        return [self._key_frame_id_to_label_map[id(key_frame)] for key_frame in
                self.animation.key_frames]

    @property
    def labels_to_key_frames(self):
        """a dict of {label : key_frame}
        """
        return {label: key_frame for label, key_frame in zip(self.backend_key_frame_labels,
                                                             self.animation.key_frames)}
