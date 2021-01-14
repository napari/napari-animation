from skimage.transform import resize
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
        self.setIconSize(QSize(32, 32))

    def _capture_key_frame(self, *args):
        """generate label for current keyframe and add id to id_to_label dict
        """
        # +1 because insertion happens prior to incrementation of 'frame'
        key_frame_id = id(self.animation.key_frames[self.animation.frame + 1])
        label = f'key frame {self.animation.frame + 1}'
        item = QListWidgetItem(label)
        item.setIcon(self._generate_thumbnail())
        self.addItem(label)
        self._id_to_label[key_frame_id] = label

    def _generate_thumbnail(self):
        """generate icon from viewer
        """
        screenshot = self.animation.viewer.screenshot(canvas_only=True)
        thumbnail = resize(screenshot, (32, 32), anti_aliasing=True).astype(np.uint8)
        print(thumbnail.shape, thumbnail.dtype)
        thumbnail = QImage(
            thumbnail,
            thumbnail.shape[1],
            thumbnail.shape[0],
            QImage.Format_RGBA8888,
        )
        thumbnail = QIcon(QPixmap.fromImage(thumbnail))
        return thumbnail

    def dropEvent(self, event):
        """update animation state on 'drop' of frame in key frames list
        """
        super().dropEvent(event)
        self._update_animation()

    def _update_animation(self):
        """push current GUI state to self.animation
        """
        new_key_frames = [self.animation_state_map[label] for label in self.gui_labels]
        self.animation.key_frames = new_key_frames
        print('updating animation!')

    def _update_from_animation(self, *args):
        """update GUI state from self.animation state
        """
        self.clear()
        self.addItems(self.key_frame_labels)

    def _connect_key_frame_events(self):
        self.animation.key_frames.events.inserted.connect(self._capture_key_frame)
        self.animation.key_frames.events.removed.connect(self._update_from_animation)
        self.animation.key_frames.events.moved.connect(self._update_from_animation)
        self.animation.key_frames.events.changed.connect(self._update_from_animation)
        self.animation.key_frames.events.reordered.connect(self._update_from_animation)

    @property
    def items(self):
        """iterate over items in the keyframes list
        """
        for i in range(self.count()):
            yield self.item(i)

    @property
    def gui_labels(self):
        """text representation of items in keyframes list
        """
        for item in self.items:
            yield item.text()

    @property
    def key_frame_labels(self):
        """current gui_labels according to key frames of animation
        """
        return [self._id_to_label[id(obj)] for obj in self.animation.key_frames]

    @property
    def animation_state_map(self):
        return {label : state for label, state in zip(self.key_frame_labels,
                                                      self.animation.key_frames)}
