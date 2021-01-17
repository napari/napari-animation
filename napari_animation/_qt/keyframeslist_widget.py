from qtpy.QtWidgets import QListWidget, QListWidgetItem
from qtpy.QtGui import QImage, QIcon, QPixmap
from qtpy.QtCore import QSize

from napari.utils.events import EventedList

# NOT IMPLEMENTED YET
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
        self._key_frame_id_to_label = {}

        self._connect_key_frame_events()
        self.setDragDropMode(super().InternalMove)
        self.setIconSize(QSize(64, 64))
        self.itemClicked.connect(self._on_click_callback)

    def _connect_key_frame_events(self):
        """Connect events on the key frame list to their callbacks
        """
        self.animation.key_frames.events.removed.connect(self._update_frontend)
        self.animation.key_frames.events.moved.connect(self._update_frontend)
        self.animation.key_frames.events.changed.connect(self._update_frontend)
        self.animation.key_frames.events.reordered.connect(self._update_frontend)

    def dropEvent(self, event):
        """update animation state on 'drop' of frame in key frames list
        """
        super().dropEvent(event)
        self._update_backend()

    def _on_click_callback(self, item):
        self._update_animation_frame()

    def add_key_frame(self, *args):
        """Generate list item for current keyframe and store its unique id
        """
        key_frame_idx = self.animation.frame
        self.insertItem(key_frame_idx, self._generate_list_item(key_frame_idx))
        self._store_key_frame_id(key_frame_idx)
        self._frame_counter += 1

    def _update_backend(self):
        """push current GUI state to self.animation
        """
        new_key_frames = [self._label_to_key_frame(label) for label in
                          self.frontend_key_frame_labels]

        # recreating the EventedList here and reconnecting events simplifies handling events
        # which fire when we modify the list in place
        self.animation.key_frames = EventedList(new_key_frames)
        self._connect_key_frame_events()
        self._update_animation_frame()

    def _update_frontend(self, *args):
        """update GUI state from self.animation state
        """
        # can't use a list comprehension because self.addItems() only takes labels,
        # not QListWidgetItem objects
        self.clear()
        for idx, _ in enumerate(self.frontend_items):
            self.addItem(self._generate_list_item(idx))

    def _update_animation_frame(self):
        """update the frame number of self.animation based on selected item in frontend
        """
        [item] = self.selectedItems()
        selected_index = self.indexFromItem(item).row()
        self.animation.frame = selected_index

    def _generate_list_item(self, key_frame_idx):
        """Generate a QListWidgetItem from a key frame at key_frame_idx
        """
        item = QListWidgetItem(self._generate_label(key_frame_idx))
        key_frame = self._get_key_frame(key_frame_idx)
        item.setIcon(self._icon_from_key_frame(key_frame))
        return item

    def _store_key_frame_id(self, key_frame_idx):
        """Store the unique id of the key frame at key_frame_idx in a dict of {id: key_frame_label}
        """
        key_frame_id = id(self._get_key_frame(key_frame_idx))
        self._key_frame_id_to_label[key_frame_id] = self._generate_label(key_frame_idx)

    def _icon_from_key_frame(self, key_frame):
        """Generate QIcon from a key frame
        """
        thumbnail = key_frame['thumbnail']
        thumbnail = QImage(
            thumbnail,
            thumbnail.shape[1],
            thumbnail.shape[0],
            QImage.Format_RGBA8888,
        )
        icon = QIcon(QPixmap.fromImage(thumbnail))
        return icon

    def _get_key_frame(self, key_frame_idx):
        """Get key frame dict from key frames list at key_frame_idx
        """
        return self.animation.key_frames[key_frame_idx]

    def _generate_label(self, key_frame_idx):
        """Generate a label for a given key frame list index
        """
        key_frame_id = id(self._get_key_frame(key_frame_idx))

        if key_frame_id in self._key_frame_id_to_label.keys():
            label = self._key_frame_id_to_label[key_frame_id]
        else:
            label = f'key frame {self._frame_counter}'
        return label

    def _label_to_key_frame(self, label):
        """gets the key frame associated with a given label in the frontend
        """
        return self.labels_to_key_frames[label]

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
        return [self._key_frame_id_to_label[id(key_frame)] for key_frame in self.animation.key_frames]

    @property
    def labels_to_key_frames(self):
        """a dict of {label : key_frame}
        """
        return {label: key_frame for label, key_frame in zip(self.backend_key_frame_labels,
                                                             self.animation.key_frames)}
