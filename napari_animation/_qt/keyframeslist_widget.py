from qtpy.QtWidgets import QWidget, QHBoxLayout

from qtpy.QtWidgets import QListWidget, QFormLayout, QPushButton

# NOT IMPLEMENTED YET
class KeyFramesListWidget(QListWidget):
    """List of Key Frames.
    """
    def __init__(self, animation, parent=None):
        super().__init__(parent=parent)

        self._layout = QFormLayout(parent=self)

        self.animation = animation

        self.keyframeslist = QListWidget()
        self.keyframeslist.itemClicked.connect(self._click_item_callback)
        self.keyframeslist.itemDoubleClicked.connect(self._doubleclick_item_callback)

        self._layout.addRow(self.keyframeslist)

        self._id_to_label = {}

    def add_current_keyframe(self):
        """generate label for current keyframe and add id to id_to_label dict
        """
        key_frame_id = id(self.animation.key_frames[self.animation.frame])
        label = f'key frame {self.animation.frame}'
        self.keyframeslist.addItem(label)
        self._id_to_label[key_frame_id] = label

    def _update_from_animation(self):
        """update keyframelist with labels from animation
        """
        labels = [self._id_to_label[id(obj)] for obj in self.animation.key_frames]
        self.keyframeslist.clear()
        self.keyframeslist.addItems(labels)

    def _update_animation(self):
        """push state of keyframeslist to self.animation
        """
        pass

    def _click_item_callback(self, item):
        pass

    def _doubleclick_item_callback(self, item):
        """on doubleclick, activate changing parameters for the current key frame
        """
        pass

    def _move_item_callback(self):
        """on move item, update state of animation.key_frames
        """

    def _delete_item_callback(self):
        """on delete item, update state of animation.key_frames
        """

    @property
    def _keyframeslist_items(self):
        """iterate over items in the keyframes list
        """
        for i in range(self.keyframeslist.count()):
            yield self.keyframeslist.item(i)

    @property
    def _keyframeslist_text(self):
        """text representation items in keyframes list
        """
        for item in self._keyframeslist_items:
            yield item.text()

