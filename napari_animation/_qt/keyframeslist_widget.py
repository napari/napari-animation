from qtpy.QtWidgets import QWidget, QHBoxLayout

from qtpy.QtWidgets import QListWidget, QFormLayout, QAbstractItemView, QPushButton

# NOT IMPLEMENTED YET
class KeyFramesListWidget(QListWidget):
    """List of Key Frames.
    """
    def __init__(self, animation, parent=None):
        super().__init__(parent=parent)

        self.animation = animation
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self._id_to_label = {}

    def add_current_keyframe(self):
        """generate label for current keyframe and add id to id_to_label dict
        """
        key_frame_id = id(self.animation.key_frames[self.animation.frame])
        label = f'key frame {self.animation.frame}'
        self.addItem(label)
        self._id_to_label[key_frame_id] = label

    def _update_from_animation(self):
        """update GUI state from self.animation state
        """
        self.keyframeslist.clear()
        self.keyframeslist.addItems(self.key_frame_labels)

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
