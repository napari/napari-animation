from skimage.transform import resize
from skimage import img_as_ubyte
import numpy as np

from qtpy.QtWidgets import QListWidget, QListWidgetItem
from qtpy.QtGui import QImage, QIcon, QPixmap
from qtpy.QtCore import QSize


# NOT IMPLEMENTED YET
class KeyFramesListWidget(QListWidget):
    """List of Key Frames.
    """

    def __init__(self, animation, parent=None):
        super().__init__(parent=parent)

        self.animation = animation
        self._id_to_label = {}

        self._connect_key_frame_events()
        self.setDragDropMode(super().InternalMove)
        self.setIconSize(QSize(64, 64))

    def _connect_key_frame_events(self):
        """Connect events on the key frame list to their callbacks
        """
        self.animation.key_frames.events.inserted.connect(self._add_key_frame)
        self.animation.key_frames.events.removed.connect(self._update_frontend)
        self.animation.key_frames.events.moved.connect(self._update_frontend)
        self.animation.key_frames.events.changed.connect(self._update_frontend)
        self.animation.key_frames.events.reordered.connect(self._update_frontend)

    def dropEvent(self, event):
        """update animation state on 'drop' of frame in key frames list
        """
        super().dropEvent(event)
        self._update_backend()

    def _update_backend(self):
        """push current GUI state to self.animation
        """
        new_key_frames = [self.labels_to_key_frames[label] for label in
                          self.frontend_key_frame_labels]
        self.animation.key_frames = new_key_frames

    def _update_frontend(self, *args):
        """update GUI state from self.animation state
        """
        list_items = [self._generate_list_item(idx) for idx, _ in enumerate(self.frontend_items)]
        self.clear()
        self.addItems(list_items)

    def _add_key_frame(self, *args):
        """Generate list item for current keyframe and store its unique id
        """
        # +1 because insertion happens prior to incrementation of 'frame' attribute
        key_frame_idx = self.animation.frame + 1
        self.addItem(self._generate_list_item(key_frame_idx))
        self._store_key_frame_id(key_frame_idx)

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
        self._id_to_label[key_frame_id] = self._generate_label(key_frame_idx)

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
        """Generate a label for a given list index
        """
        return f'key frame {key_frame_idx}'

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
        return [self._id_to_label[id(key_frame)] for key_frame in self.animation.key_frames]

    @property
    def labels_to_key_frames(self):
        """a dict of {label : key_frame}
        """
        return {label: key_frame for label, key_frame in zip(self.backend_key_frame_labels,
                                                             self.animation.key_frames)}
